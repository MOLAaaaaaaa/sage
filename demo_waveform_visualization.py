#!/usr/bin/env python3
"""
Demonstration script for waveform visualization and data browsing features

This script shows how to use the conversational agent to:
1. Browse directories for seismic data files
2. Plot waveforms using natural language commands
3. Chain multiple operations in a conversation
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from conversational_agent import ConversationalAgent


def demo_intent_recognition():
    """Demonstrate intent recognition for various commands"""
    print("=" * 80)
    print("Demo 1: Intent Recognition")
    print("=" * 80)
    print()

    agent = ConversationalAgent()

    test_commands = [
        "帮我查看 /data/seismic 目录下有哪些mseed数据",
        "浏览 /path/to/data 目录",
        "绘制波形",
        "plot waveform from /data/file.mseed",
        "显示 file.sac 的波形图",
        "画一下这个文件",
        "帮我拾取震相",
        "关联地震事件",
    ]

    print("Testing intent classification:\n")
    for command in test_commands:
        result = agent.process_message(command)
        intent = agent.intent_classifier.classify(command)
        print(f"Command: {command}")
        print(f"  → Intent: {intent['intent']} (confidence: {intent['confidence']:.2f})")
        if 'file_paths' in intent['entities']:
            print(f"  → Files: {intent['entities']['file_paths']}")
        print()


def demo_data_browsing():
    """Demonstrate data browsing functionality"""
    print("=" * 80)
    print("Demo 2: Data Browsing")
    print("=" * 80)
    print()

    agent = ConversationalAgent()

    # Simulate browsing a directory
    test_directory = "/tmp/test_seismic_data"

    print(f"Simulating: '查看 {test_directory} 目录'\n")

    # Create some dummy files for demonstration
    import os
    os.makedirs(test_directory, exist_ok=True)
    dummy_files = [
        "station1.mseed",
        "station2.mseed",
        "station3.sac",
    ]
    for fname in dummy_files:
        Path(test_directory, fname).touch()

    # Process the browse command
    result = agent.process_message(f"查看 {test_directory} 目录")

    print(f"Assistant response:")
    print(result['response'])
    print()

    # Clean up
    import shutil
    shutil.rmtree(test_directory)


def demo_waveform_plotting():
    """Demonstrate waveform plotting workflow"""
    print("=" * 80)
    print("Demo 3: Waveform Plotting Workflow")
    print("=" * 80)
    print()

    agent = ConversationalAgent()

    print("Example workflow:\n")

    # Step 1: User wants to plot a waveform
    command1 = "绘制 /data/station1.mseed 的波形"
    print(f"User: {command1}")

    result = agent.process_message(command1)
    print(f"Assistant: {result['response']}")
    print()

    # Step 2: Show what happens with missing file
    command2 = "绘制 /nonexistent/file.mseed"
    print(f"User: {command2}")

    result = agent.process_message(command2)
    print(f"Assistant: {result['response']}")
    print()


def demo_multi_turn_conversation():
    """Demonstrate multi-turn conversation"""
    print("=" * 80)
    print("Demo 4: Multi-turn Conversation")
    print("=" * 80)
    print()

    agent = ConversationalAgent()

    conversation = [
        ("你好", "Greeting"),
        ("能做什么", "Help request"),
        ("帮我查看 /data/seismic 目录", "Data browsing"),
        ("绘制第1个文件", "Waveform plotting"),
        ("对这个文件进行震相检测", "Phase picking"),
    ]

    print("Simulating conversation:\n")
    for user_msg, description in conversation:
        print(f"[{description}]")
        print(f"User: {user_msg}")

        result = agent.process_message(user_msg)
        print(f"Assistant: {result['response'][:200]}...")  # Truncate long responses
        print()


def demo_error_handling():
    """Demonstrate error handling"""
    print("=" * 80)
    print("Demo 5: Error Handling")
    print("=" * 80)
    print()

    agent = ConversationalAgent()

    error_cases = [
        ("查看不存在的目录", "Non-existent directory"),
        ("绘制不存在的文件", "Non-existent file"),
        ("随机文本无意义", "Unknown intent"),
    ]

    print("Testing error handling:\n")
    for command, description in error_cases:
        print(f"[{description}]")
        print(f"User: {command}")

        result = agent.process_message(command)
        print(f"Assistant: {result['response']}")
        print()


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SeismicX Waveform Visualization Demo" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    demos = [
        ("Intent Recognition", demo_intent_recognition),
        ("Data Browsing", demo_data_browsing),
        ("Waveform Plotting", demo_waveform_plotting),
        ("Multi-turn Conversation", demo_multi_turn_conversation),
        ("Error Handling", demo_error_handling),
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 80)
    print("Demo completed!")
    print("=" * 80)
    print("\nTo use these features:")
    print("1. CLI: python conversational_agent.py")
    print("2. Web: cd web_app && python app.py")
    print("\nExample commands:")
    print('  - "帮我查看 /path/to/data 目录下有哪些mseed数据"')
    print('  - "绘制 /path/to/file.mseed 的波形"')
    print('  - "画一下这个文件"')
    print()


if __name__ == '__main__':
    main()
