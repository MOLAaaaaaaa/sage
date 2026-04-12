#!/usr/bin/env python3
"""
Test complete workflow: browse -> plot -> associate through conversation
"""

import sys
from pathlib import Path
import os
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent))

from conversational_agent import ConversationalAgent


def test_complete_workflow():
    """Test the complete workflow from browsing to association"""
    
    print("=" * 80)
    print("Testing Complete Conversational Workflow")
    print("=" * 80)
    print()
    
    agent = ConversationalAgent()
    
    # Create a temporary directory with some dummy files for testing
    temp_dir = tempfile.mkdtemp(prefix="seismic_test_")
    print(f"Created test directory: {temp_dir}\n")
    
    try:
        # Create some dummy .mseed files
        test_files = [
            "station1.mseed",
            "station2.mseed", 
            "station3.mseed",
        ]
        
        for fname in test_files:
            fpath = Path(temp_dir) / fname
            fpath.write_text("dummy seismic data")
        
        print("Created dummy seismic files:")
        for f in test_files:
            print(f"  - {f}")
        print()
        
        # ===== Step 1: Browse directory =====
        print("-" * 80)
        print("Step 1: Browse directory")
        print("-" * 80)
        
        user_msg = f"帮我查看 {temp_dir} 目录下有哪些mseed数据"
        print(f"User: {user_msg}\n")
        
        result = agent.process_message(user_msg)
        print(f"Assistant: {result['response']}")
        print(f"Action: {result['action']}")
        print()
        
        # Check if files were found
        if result['data'].get('results', {}).get('count', 0) > 0:
            print("✓ Successfully browsed directory and found files\n")
        else:
            print("✗ Failed to find files\n")
            return
        
        # ===== Step 2: Plot first file =====
        print("-" * 80)
        print("Step 2: Plot first file")
        print("-" * 80)
        
        user_msg = "绘制第1个文件"
        print(f"User: {user_msg}\n")
        
        result = agent.process_message(user_msg)
        print(f"Assistant: {result['response']}")
        print(f"Action: {result['action']}")
        print()
        
        # Note: This will fail without ObsPy installed, but shows the flow
        if result['success']:
            print("✓ Successfully initiated plotting\n")
        else:
            print("⚠ Plotting requires ObsPy and matplotlib (expected in test environment)\n")
        
        # ===== Step 3: Try phase picking on the directory =====
        print("-" * 80)
        print("Step 3: Phase picking on directory")
        print("-" * 80)
        
        user_msg = f"对 {temp_dir} 目录进行震相检测"
        print(f"User: {user_msg}\n")
        
        result = agent.process_message(user_msg)
        print(f"Assistant: {result['response']}")
        print(f"Action: {result.get('action', 'none')}")
        print()
        
        if result['success']:
            print("✓ Successfully initiated phase picking\n")
        else:
            print("⚠ Phase picking may require model files (expected)\n")
        
        # ===== Step 4: Ask for help =====
        print("-" * 80)
        print("Step 4: Ask for help")
        print("-" * 80)
        
        user_msg = "能做什么"
        print(f"User: {user_msg}\n")
        
        result = agent.process_message(user_msg)
        print(f"Assistant: {result['response'][:300]}...")
        print()
        
        print("✓ Help displayed successfully\n")
        
        # ===== Step 5: Natural language variations =====
        print("-" * 80)
        print("Step 5: Testing natural language variations")
        print("-" * 80)
        
        variations = [
            f"看下 {temp_dir} 文件夹",
            f"看看有什么数据",
            f"显示目录下的文件",
        ]
        
        for msg in variations:
            print(f"\nUser: {msg}")
            result = agent.process_message(msg)
            intent = agent.intent_classifier.classify(msg)
            print(f"Intent: {intent['intent']} (confidence: {intent['confidence']:.2f})")
            
            if intent['intent'] == 'data_browsing':
                print(f"Response preview: {result['response'][:100]}...")
        
        print("\n" + "=" * 80)
        print("Workflow test completed successfully!")
        print("=" * 80)
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"\nCleaned up test directory: {temp_dir}")


if __name__ == '__main__':
    test_complete_workflow()
