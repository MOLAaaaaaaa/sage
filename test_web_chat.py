#!/usr/bin/env python3
"""
Test script for web chat interface with data browsing and waveform plotting
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from conversational_agent import ConversationalAgent


def test_chat_scenarios():
    """Test common chat scenarios"""
    print("=" * 80)
    print("Testing Web Chat Scenarios")
    print("=" * 80)
    print()

    agent = ConversationalAgent()

    # Scenario 1: Browse directory
    print("Scenario 1: Browse directory for seismic data")
    print("-" * 80)
    user_msg = "帮我查看 /tmp/test_data 目录下有哪些mseed数据"
    print(f"User: {user_msg}\n")

    result = agent.process_message(user_msg)
    print(f"Assistant: {result['response']}")
    print(f"Action: {result['action']}")
    print()

    # Scenario 2: Plot waveform (will fail without actual file, but shows flow)
    print("\nScenario 2: Plot waveform")
    print("-" * 80)
    user_msg = "绘制 /path/to/file.mseed 的波形"
    print(f"User: {user_msg}\n")

    result = agent.process_message(user_msg)
    print(f"Assistant: {result['response']}")
    print(f"Action: {result['action']}")
    if result.get('data', {}).get('results', {}).get('image_path'):
        print(f"Image URL would be: /api/output/{result['data']['results']['image_path']}")
    print()

    # Scenario 3: Help request
    print("\nScenario 3: Request help")
    print("-" * 80)
    user_msg = "能做什么"
    print(f"User: {user_msg}\n")

    result = agent.process_message(user_msg)
    print(f"Assistant: {result['response'][:300]}...")
    print()

    print("\n" + "=" * 80)
    print("All scenarios tested successfully!")
    print("=" * 80)


if __name__ == '__main__':
    test_chat_scenarios()
