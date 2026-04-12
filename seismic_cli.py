#!/usr/bin/env python3
"""
SeismicX CLI - Command Line Interface for Seismic Analysis Skills

Unified command-line interface for:
- Phase picking (seismic-phase-picker)
- Phase association (seismic-phase-associator)
- Polarity analysis (seismic-polarity-analyzer)

Usage:
    python seismic_cli.py pick [options]
    python seismic_cli.py associate [options]
    python seismic_cli.py polarity [options]
"""

import argparse
import sys
import os
from pathlib import Path

# Import config manager
try:
    from config_manager import get_config_manager
except ImportError:
    # If config_manager not available, create a dummy one
    class DummyConfigManager:
        def is_first_run(self):
            return False
        def interactive_setup(self):
            print("Config manager not available")
        def get_llm_config(self):
            return {}
    def get_config_manager():
        return DummyConfigManager()


def setup_llm_parser(subparsers):
    """Setup LLM configuration subcommand"""
    parser = subparsers.add_parser(
        'llm',
        help='Configure LLM model settings',
        description='Manage LLM provider and model configuration'
    )

    subparsers_llm = parser.add_subparsers(dest='llm_command', help='LLM commands')

    # Setup command
    setup_parser = subparsers_llm.add_parser('setup', help='Interactive setup wizard')

    # Show command
    show_parser = subparsers_llm.add_parser('show', help='Show current configuration')

    # Set provider command
    set_provider = subparsers_llm.add_parser('set-provider', help='Set LLM provider')
    set_provider.add_argument(
        'provider',
        choices=['ollama', 'openai', 'anthropic', 'azure', 'custom'],
        help='LLM provider name'
    )

    # Set model command
    set_model = subparsers_llm.add_parser('set-model', help='Set LLM model')
    set_model.add_argument('model', help='Model name')

    # List models command
    list_models = subparsers_llm.add_parser('list-models', help='List available Ollama models')

    return parser


def handle_llm_command(args):
    """Handle LLM configuration commands"""
    config = get_config_manager()

    if args.llm_command is None:
        # Default to interactive setup
        config.interactive_setup()
    elif args.llm_command == 'setup':
        config.interactive_setup()
    elif args.llm_command == 'show':
        llm_config = config.get_llm_config()
        print("Current LLM Configuration:")
        print("-" * 40)
        for key, value in llm_config.items():
            if key == 'api_key' and value:
                print(f"{key}: {'*' * 8} (hidden)")
            else:
                print(f"{key}: {value}")
    elif args.llm_command == 'set-provider':
        config.set_llm_provider(args.provider)
        print(f"✓ LLM provider set to: {args.provider}")
    elif args.llm_command == 'set-model':
        config.set_llm_model(args.model)
        print(f"✓ LLM model set to: {args.model}")
    elif args.llm_command == 'list-models':
        models = config.get_ollama_models()
        if models:
            print("Available Ollama models:")
            for model in models:
                print(f"  - {model}")
        else:
            print("No Ollama models found. Make sure Ollama is running.")
            print("Run 'ollama list' to check.")


def setup_pick_parser(subparsers):
    """Setup phase picking subcommand"""
    parser = subparsers.add_parser(
        'pick',
        help='Detect seismic phases from waveform data',
        description='Run deep learning models to detect Pg, Sg, Pn, Sn phases from continuous waveforms'
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input directory containing waveform files (mseed/sac format)'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output filename prefix (generates .txt, .log, .err files)'
    )
    parser.add_argument(
        '-m', '--model',
        default='pnsn/pickers/pnsn.v3.jit',
        help='Model file path (.jit or .onnx). Default: pnsn/pickers/pnsn.v3.jit'
    )
    parser.add_argument(
        '-d', '--device',
        default='cpu',
        choices=['cpu', 'cuda', 'cuda:0', 'cuda:1', 'mps'],
        help='Device for inference. Default: cpu'
    )
    parser.add_argument(
        '--config',
        default='pnsn/config/picker.py',
        help='Configuration file path. Default: pnsn/config/picker.py'
    )
    parser.add_argument(
        '--prob-thresh',
        type=float,
        default=None,
        help='Confidence threshold (0-1). Overrides config file'
    )
    parser.add_argument(
        '--nms-window',
        type=int,
        default=None,
        help='NMS window in samples. Overrides config file'
    )
    parser.add_argument(
        '--enable-polarity',
        action='store_true',
        help='Enable first-motion polarity detection'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate waveform plots with picks'
    )

    return parser


def setup_associate_parser(subparsers):
    """Setup phase association subcommand"""
    parser = subparsers.add_parser(
        'associate',
        help='Associate phase picks into earthquake events',
        description='Group phase picks from multiple stations into coherent earthquake events'
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Phase picking result file (.txt from picker)'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output event file name'
    )
    parser.add_argument(
        '-s', '--station',
        required=True,
        help='Station file with coordinates (format: NET STA LOC lon lat elev)'
    )
    parser.add_argument(
        '-m', '--method',
        default='fastlink',
        choices=['fastlink', 'real', 'gamma'],
        help='Association method. Default: fastlink'
    )
    parser.add_argument(
        '-d', '--device',
        default='cpu',
        choices=['cpu', 'cuda', 'cuda:0', 'cuda:1', 'mps'],
        help='Device for neural network (FastLink only). Default: cpu'
    )
    parser.add_argument(
        '--min-phases',
        type=int,
        default=None,
        help='Minimum total phases per event'
    )
    parser.add_argument(
        '--min-p',
        type=int,
        default=None,
        help='Minimum P phases per event'
    )
    parser.add_argument(
        '--min-s',
        type=int,
        default=None,
        help='Minimum S phases per event'
    )

    return parser


def setup_polarity_parser(subparsers):
    """Setup polarity analysis subcommand"""
    parser = subparsers.add_parser(
        'polarity',
        help='Analyze first-motion polarity of P-waves',
        description='Detect upward/downward initial motion of P-waves using deep learning'
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Phase picking result file with picks'
    )
    parser.add_argument(
        '-w', '--waveform-dir',
        required=True,
        help='Directory containing waveform files'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output file for polarity results (default: update input file)'
    )
    parser.add_argument(
        '--model',
        default='pnsn/pickers/polar.onnx',
        help='Polarity model file. Default: pnsn/pickers/polar.onnx'
    )
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0.5,
        help='Minimum confidence threshold. Default: 0.5'
    )
    parser.add_argument(
        '--phase',
        default='Pg',
        choices=['Pg', 'Pn', 'P'],
        help='Phase type to analyze. Default: Pg'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate polarity visualization plots'
    )
    parser.add_argument(
        '--plot-dir',
        default='output/plots',
        help='Directory for plot output. Default: output/plots'
    )

    return parser


def run_picking(args):
    """Execute phase picking workflow"""
    print("=" * 80)
    print("SeismicX Phase Picker")
    print("=" * 80)

    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input directory not found: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        sys.exit(1)

    # Update config if needed
    if args.prob_thresh is not None or args.nms_window is not None or args.enable_polarity or args.plot:
        update_picker_config(
            args.config,
            prob=args.prob_thresh,
            nmslen=args.nms_window,
            polar=args.enable_polarity,
            ifplot=args.plot
        )

    # Build command
    cmd = f"python pnsn/picker.py -i {args.input} -o {args.output} -m {args.model} -d {args.device}"

    print(f"\nRunning command:")
    print(f"  {cmd}\n")

    # Execute
    import subprocess
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print(f"\n✓ Phase picking completed successfully!")
        print(f"  Results: {args.output}.txt")
        print(f"  Log: {args.output}.log")
        print(f"  Errors: {args.output}.err")
    else:
        print(f"\n✗ Phase picking failed with code {result.returncode}")
        sys.exit(1)


def run_association(args):
    """Execute phase association workflow"""
    print("=" * 80)
    print(f"SeismicX Phase Associator ({args.method.upper()})")
    print("=" * 80)

    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.station):
        print(f"Error: Station file not found: {args.station}")
        sys.exit(1)

    # Select association script
    method_scripts = {
        'fastlink': 'pnsn/fastlinker.py',
        'real': 'pnsn/reallinker.py',
        'gamma': 'pnsn/gammalink.py'
    }

    script = method_scripts[args.method]
    if not os.path.exists(script):
        print(f"Error: Association script not found: {script}")
        sys.exit(1)

    # Build command
    cmd = f"python {script} -i {args.input} -o {args.output} -s {args.station}"
    if args.method == 'fastlink':
        cmd += f" -d {args.device}"

    print(f"\nRunning command:")
    print(f"  {cmd}\n")

    # Execute
    import subprocess
    result = subprocess.run(cmd, shell=True)

    if result.returncode == 0:
        print(f"\n✓ Phase association completed successfully!")
        print(f"  Events: {args.output}")
    else:
        print(f"\n✗ Phase association failed with code {result.returncode}")
        sys.exit(1)


def run_polarity(args):
    """Execute polarity analysis workflow"""
    print("=" * 80)
    print("SeismicX Polarity Analyzer")
    print("=" * 80)

    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not os.path.exists(args.waveform_dir):
        print(f"Error: Waveform directory not found: {args.waveform_dir}")
        sys.exit(1)

    if not os.path.exists(args.model):
        print(f"Error: Polarity model not found: {args.model}")
        sys.exit(1)

    # Create output directory if needed
    if args.plot and not os.path.exists(args.plot_dir):
        os.makedirs(args.plot_dir, exist_ok=True)

    print(f"\nAnalyzing polarity for {args.phase} phases...")
    print(f"  Input: {args.input}")
    print(f"  Waveforms: {args.waveform_dir}")
    print(f"  Model: {args.model}")
    print(f"  Min confidence: {args.min_confidence}")

    # Run polarity analysis
    try:
        import obspy
        import numpy as np
        import onnxruntime as ort

        # Load model
        sess = ort.InferenceSession(args.model, providers=['CPUExecutionProvider'])

        # Read picks
        picks_by_station = {}
        current_file = None

        with open(args.input, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    current_file = line.strip()[1:]
                    continue

                parts = line.strip().split(',')
                if len(parts) < 7:
                    continue

                phase_name = parts[0]
                station = parts[6]

                if phase_name != args.phase:
                    continue

                if station not in picks_by_station:
                    picks_by_station[station] = []

                picks_by_station[station].append({
                    'file': current_file,
                    'rel_time': float(parts[1]),
                    'confidence': float(parts[2]),
                    'abs_time': parts[3],
                    'line': line.strip()
                })

        # Process each station
        results = []
        for station, picks in picks_by_station.items():
            print(f"\nProcessing station: {station} ({len(picks)} picks)")

            # Find waveform file
            sample_pick = picks[0]
            waveform_path = os.path.join(args.waveform_dir,
                                        os.path.basename(sample_pick['file']))

            if not os.path.exists(waveform_path):
                print(f"  Warning: Waveform not found: {waveform_path}")
                continue

            try:
                st = obspy.read(waveform_path)
                tr_z = st.select(component='Z')

                if len(tr_z) == 0:
                    print(f"  Warning: No vertical component found")
                    continue

                tr_z = tr_z[0]
                data = tr_z.data.astype(np.float32)

                for pick in picks:
                    pick_idx = int(pick['rel_time'] * tr_z.stats.sampling_rate)

                    # Check bounds
                    if pick_idx < 512 or pick_idx > len(data) - 512:
                        results.append({
                            'station': station,
                            'time': pick['abs_time'],
                            'polarity': 'N',
                            'prob': 0.0,
                            'reason': 'out_of_bounds'
                        })
                        continue

                    # Extract window
                    pdata = data[pick_idx-512:pick_idx+512]

                    # Ensure correct length
                    if len(pdata) < 1024:
                        pdata = np.pad(pdata, (0, 1024-len(pdata)))
                    elif len(pdata) > 1024:
                        pdata = pdata[:1024]

                    # Run inference
                    prob, = sess.run(["prob"], {"wave": pdata})
                    polarity_id = np.argmax(prob)
                    polarity = "U" if polarity_id == 0 else "D"
                    confidence = np.max(prob)

                    # Apply threshold
                    if confidence < args.min_confidence:
                        polarity = "N"

                    results.append({
                        'station': station,
                        'time': pick['abs_time'],
                        'polarity': polarity,
                        'prob': float(confidence),
                        'reason': 'ok'
                    })

                    print(f"  {pick['abs_time']}: {polarity} ({confidence:.3f})")

            except Exception as e:
                print(f"  Error processing {station}: {e}")
                continue

        # Write results
        output_file = args.output if args.output else args.input.replace('.txt', '_polarity.txt')

        with open(output_file, 'w') as f:
            f.write("# Station, Time, Polarity, Confidence\n")
            for r in results:
                f.write(f"{r['station']},{r['time']},{r['polarity']},{r['prob']:.3f}\n")

        print(f"\n✓ Polarity analysis completed!")
        print(f"  Results: {output_file}")
        print(f"  Total analyzed: {len(results)}")
        print(f"  Upward (U): {sum(1 for r in results if r['polarity'] == 'U')}")
        print(f"  Downward (D): {sum(1 for r in results if r['polarity'] == 'D')}")
        print(f"  Uncertain (N): {sum(1 for r in results if r['polarity'] == 'N')}")

    except ImportError as e:
        print(f"Error: Required package not installed: {e}")
        print("Install with: pip install obspy numpy onnxruntime")
        sys.exit(1)


def update_picker_config(config_path, prob=None, nmslen=None, polar=None, ifplot=None):
    """Update picker configuration file"""
    if not os.path.exists(config_path):
        print(f"Warning: Config file not found: {config_path}")
        return

    with open(config_path, 'r') as f:
        lines = f.readlines()

    modified = False
    new_lines = []

    for line in lines:
        if prob is not None and line.strip().startswith('prob ='):
            new_lines.append(f"    prob = {prob}                   # Confidence threshold\n")
            modified = True
        elif nmslen is not None and line.strip().startswith('nmslen ='):
            new_lines.append(f"    nmslen = {nmslen}                # NMS window in samples\n")
            modified = True
        elif polar is not None and 'polar =' in line and '#' in line:
            new_lines.append(f"    polar = {'True' if polar else 'False'} # Enable polarity detection\n")
            modified = True
        elif ifplot is not None and line.strip().startswith('ifplot ='):
            new_lines.append(f"    ifplot = {'True' if ifplot else 'False'}               # Generate plots\n")
            modified = True
        else:
            new_lines.append(line)

    if modified:
        with open(config_path, 'w') as f:
            f.writelines(new_lines)
        print(f"Updated config: {config_path}")


def main():
    # Check for first run and LLM configuration
    config = get_config_manager()
    if config.is_first_run():
        print("=" * 80)
        print("Welcome to SeismicX!")
        print("=" * 80)
        print()
        print("This appears to be your first time using SeismicX.")
        print("Let's configure your LLM (Large Language Model) settings.")
        print()
        print("You can:")
        print("  - Use Ollama for local models (recommended for privacy)")
        print("  - Use online APIs like OpenAI GPT-4 or Anthropic Claude")
        print()

        setup_choice = input("Would you like to set up LLM configuration now? (y/n) [y]: ").strip().lower()
        if setup_choice != 'n':
            config.interactive_setup()
        else:
            config.mark_first_run_complete()
            print()
            print("You can configure LLM settings later with:")
            print("  python seismic_cli.py llm setup")

        print()
        print("=" * 80)
        print()

    parser = argparse.ArgumentParser(
        description='SeismicX CLI - Unified interface for seismic analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configure LLM settings
  python seismic_cli.py llm setup
  python seismic_cli.py llm show
  python seismic_cli.py llm list-models

  # Phase picking
  python seismic_cli.py pick -i data/waveforms -o results/picks -m pnsn/pickers/pnsn.v3.jit -d cpu

  # Phase association with FastLink
  python seismic_cli.py associate -i results/picks.txt -o results/events.txt -s data/stations.txt -m fastlink

  # Phase association with REAL
  python seismic_cli.py associate -i results/picks.txt -o results/events.txt -s data/stations.txt -m real

  # Polarity analysis
  python seismic_cli.py polarity -i results/picks.txt -w data/waveforms -o results/polarity.txt

For more information, see the skill documentation in .lingma/skills/
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Setup subcommands
    setup_llm_parser(subparsers)
    setup_pick_parser(subparsers)
    setup_associate_parser(subparsers)
    setup_polarity_parser(subparsers)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Execute appropriate command
    if args.command == 'llm':
        handle_llm_command(args)
    elif args.command == 'pick':
        run_picking(args)
    elif args.command == 'associate':
        run_association(args)
    elif args.command == 'polarity':
        run_polarity(args)


if __name__ == '__main__':
    main()
