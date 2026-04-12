#!/usr/bin/env python3
"""
SeismicX Web Interface

Flask-based web application for seismic analysis skills:
- Phase picking
- Phase association
- Polarity analysis

Usage:
    python web_app/app.py [--port PORT] [--host HOST]
"""

import os
import sys
import subprocess
import threading
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for

# Add parent directory to path for config_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config_manager import get_config_manager
except ImportError:
    class DummyConfigManager:
        def is_first_run(self): return False
        def interactive_setup(self): pass
        def get_llm_config(self): return {}
        def set_llm_provider(self, p): pass
        def set_llm_model(self, m): pass
        def set_api_key(self, k): pass
        def set_api_base(self, b): pass
        def mark_first_run_complete(self): pass
        def check_ollama_available(self): return False
        def get_ollama_models(self): return []
        def pull_ollama_model(self, m): return False
        def get_recommended_models(self): return {}
    def get_config_manager():
        return DummyConfigManager()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'web_app/uploads'
app.config['OUTPUT_FOLDER'] = 'web_app/outputs'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Task status tracking
tasks = {}


def run_task(task_id, command, task_type):
    """Run a seismic processing task in background"""
    try:
        tasks[task_id]['status'] = 'running'
        tasks[task_id]['start_time'] = datetime.now().isoformat()

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        tasks[task_id]['end_time'] = datetime.now().isoformat()
        tasks[task_id]['returncode'] = result.returncode
        tasks[task_id]['stdout'] = result.stdout[-5000:] if result.stdout else ""  # Last 5000 chars
        tasks[task_id]['stderr'] = result.stderr[-5000:] if result.stderr else ""

        if result.returncode == 0:
            tasks[task_id]['status'] = 'completed'
        else:
            tasks[task_id]['status'] = 'failed'

    except subprocess.TimeoutExpired:
        tasks[task_id]['status'] = 'timeout'
        tasks[task_id]['stderr'] = "Task timed out (1 hour limit)"
    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['stderr'] = str(e)


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/picker')
def picker_page():
    """Phase picking interface"""
    return render_template('picker.html')


@app.route('/associator')
def associator_page():
    """Phase association interface"""
    return render_template('associator.html')


@app.route('/polarity')
def polarity_page():
    """Polarity analysis interface"""
    return render_template('polarity.html')


@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """List all tasks"""
    return jsonify({
        'tasks': {k: {kk: vv for kk, vv in v.items() if kk not in ['stdout', 'stderr']}
                  for k, v in tasks.items()}
    })


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get task status and results"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = tasks[task_id].copy()
    # Include logs
    task['logs'] = {
        'stdout': task.get('stdout', ''),
        'stderr': task.get('stderr', '')
    }
    # Remove raw stdout/stderr from main response
    task.pop('stdout', None)
    task.pop('stderr', None)

    return jsonify(task)


@app.route('/api/pick', methods=['POST'])
def submit_picking():
    """Submit phase picking job"""
    data = request.json

    if not data.get('input_dir'):
        return jsonify({'error': 'Input directory required'}), 400

    task_id = f"pick_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"

    # Build command
    cmd = f"python pnsn/picker.py"
    cmd += f" -i {data['input_dir']}"
    cmd += f" -o {app.config['OUTPUT_FOLDER']}/{task_id}"
    cmd += f" -m {data.get('model', 'pnsn/pickers/pnsn.v3.jit')}"
    cmd += f" -d {data.get('device', 'cpu')}"

    # Initialize task
    tasks[task_id] = {
        'id': task_id,
        'type': 'phase_picking',
        'status': 'queued',
        'command': cmd,
        'parameters': data,
        'created_at': datetime.now().isoformat()
    }

    # Start task in background
    thread = threading.Thread(target=run_task, args=(task_id, cmd, 'picking'))
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id, 'message': 'Task submitted'})


@app.route('/api/associate', methods=['POST'])
def submit_association():
    """Submit phase association job"""
    data = request.json

    if not data.get('input_file'):
        return jsonify({'error': 'Input file required'}), 400

    if not data.get('station_file'):
        return jsonify({'error': 'Station file required'}), 400

    task_id = f"assoc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"

    # Select method
    method_scripts = {
        'fastlink': 'pnsn/fastlinker.py',
        'real': 'pnsn/reallinker.py',
        'gamma': 'pnsn/gammalink.py'
    }

    script = method_scripts.get(data.get('method', 'fastlink'), 'pnsn/fastlinker.py')

    # Build command
    cmd = f"python {script}"
    cmd += f" -i {data['input_file']}"
    cmd += f" -o {app.config['OUTPUT_FOLDER']}/{task_id}.txt"
    cmd += f" -s {data['station_file']}"

    if data.get('method') == 'fastlink':
        cmd += f" -d {data.get('device', 'cpu')}"

    # Initialize task
    tasks[task_id] = {
        'id': task_id,
        'type': 'phase_association',
        'status': 'queued',
        'command': cmd,
        'parameters': data,
        'created_at': datetime.now().isoformat()
    }

    # Start task in background
    thread = threading.Thread(target=run_task, args=(task_id, cmd, 'association'))
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id, 'message': 'Task submitted'})


@app.route('/api/polarity', methods=['POST'])
def submit_polarity():
    """Submit polarity analysis job"""
    data = request.json

    if not data.get('input_file'):
        return jsonify({'error': 'Input file required'}), 400

    if not data.get('waveform_dir'):
        return jsonify({'error': 'Waveform directory required'}), 400

    task_id = f"polar_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"

    # For now, use CLI tool
    cmd = f"python seismic_cli.py polarity"
    cmd += f" -i {data['input_file']}"
    cmd += f" -w {data['waveform_dir']}"
    cmd += f" -o {app.config['OUTPUT_FOLDER']}/{task_id}_polarity.txt"
    cmd += f" --model {data.get('model', 'pnsn/pickers/polar.onnx')}"
    cmd += f" --min-confidence {data.get('min_confidence', 0.5)}"
    cmd += f" --phase {data.get('phase', 'Pg')}"

    # Initialize task
    tasks[task_id] = {
        'id': task_id,
        'type': 'polarity_analysis',
        'status': 'queued',
        'command': cmd,
        'parameters': data,
        'created_at': datetime.now().isoformat()
    }

    # Start task in background
    thread = threading.Thread(target=run_task, args=(task_id, cmd, 'polarity'))
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id, 'message': 'Task submitted'})


@app.route('/api/output/<filename>', methods=['GET'])
def download_output(filename):
    """Download output file"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_tasks': sum(1 for t in tasks.values() if t['status'] == 'running')
    })


# ==================== LLM Configuration Endpoints ====================

@app.route('/llm-settings')
def llm_settings_page():
    """LLM settings page"""
    return render_template('llm_settings.html')


# ==================== Chat Endpoints ====================

@app.route('/chat')
def chat_page():
    """Chat interface page"""
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def chat_message():
    """Process chat message"""
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Message required'}), 400

    # Import and use conversational agent
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from conversational_agent import get_agent

        agent = get_agent()
        result = agent.process_message(user_message)

        # If the action is to display a plot, add image URL
        if result.get('action') == 'display_plot' and result.get('data', {}).get('results', {}).get('image_path'):
            image_path = result['data']['results']['image_path']
            # Convert to relative path for web access
            if os.path.isabs(image_path):
                rel_path = os.path.relpath(image_path, app.config['OUTPUT_FOLDER'])
            else:
                rel_path = image_path
            result['image_url'] = f'/api/output/{rel_path}'

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'response': f'抱歉，处理您的消息时出错: {str(e)}',
            'action': 'error',
            'data': {}
        }), 500


@app.route('/api/llm/config', methods=['GET'])
def get_llm_config():
    """Get current LLM configuration"""
    config = get_config_manager()
    llm_config = config.get_llm_config()
    
    # Hide API key for security
    if 'api_key' in llm_config and llm_config['api_key']:
        llm_config['api_key_masked'] = '****' + llm_config['api_key'][-4:] if len(llm_config['api_key']) > 4 else '****'
    
    return jsonify({
        'config': llm_config,
        'first_run': config.is_first_run(),
        'ollama_available': config.check_ollama_available()
    })


@app.route('/api/llm/config', methods=['POST'])
def update_llm_config():
    """Update LLM configuration"""
    data = request.json
    config = get_config_manager()
    
    try:
        if 'provider' in data:
            config.set_llm_provider(data['provider'])
        
        if 'model' in data:
            config.set_llm_model(data['model'])
        
        if 'api_key' in data and data['api_key']:
            config.set_api_key(data['api_key'])
        
        if 'api_base' in data:
            config.set_api_base(data['api_base'])
        
        if 'temperature' in data:
            config.config['llm']['temperature'] = data['temperature']
            config.save_config()
        
        if 'max_tokens' in data:
            config.config['llm']['max_tokens'] = data['max_tokens']
            config.save_config()
        
        # Mark first run complete if this is the first setup
        if config.is_first_run():
            config.mark_first_run_complete()
        
        return jsonify({'message': 'Configuration updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/llm/ollama/models', methods=['GET'])
def get_ollama_models():
    """Get available Ollama models"""
    config = get_config_manager()
    models = config.get_ollama_models()
    recommended = config.get_recommended_models().get('ollama', [])
    
    return jsonify({
        'installed': models,
        'recommended': recommended,
        'ollama_available': config.check_ollama_available()
    })


@app.route('/api/llm/ollama/pull', methods=['POST'])
def pull_ollama_model():
    """Pull an Ollama model"""
    data = request.json
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'Model name required'}), 400
    
    config = get_config_manager()
    
    # Start pulling in background thread
    def pull_in_background():
        success = config.pull_ollama_model(model_name)
        # Could add a status tracking mechanism here
    
    thread = threading.Thread(target=pull_in_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': f'Started pulling model: {model_name}'})


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='SeismicX Web Interface')
    parser.add_argument('--port', type=int, default=5010, help='Port to run on (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print("=" * 80)
    print("SeismicX Web Interface")
    print("=" * 80)
    print(f"\nStarting server on http://{args.host}:{args.port}")
    print("\nAvailable endpoints:")
    print("  - Main Dashboard:   http://localhost:{}/".format(args.port))
    print("  - Phase Picker:     http://localhost:{}/picker".format(args.port))
    print("  - Associator:       http://localhost:{}/associator".format(args.port))
    print("  - Polarity:         http://localhost:{}/polarity".format(args.port))
    print("  - LLM Settings:     http://localhost:{}/llm-settings".format(args.port))
    print("  - API Docs:         http://localhost:{}/api/tasks".format(args.port))
    print("\nPress Ctrl+C to stop\n")

    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
