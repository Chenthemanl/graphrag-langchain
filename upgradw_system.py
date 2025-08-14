#!/usr/bin/env python3
"""
Upgrade system script to restart with enhanced intelligence
"""

import subprocess
import sys
import os

def upgrade_system():
    """Restart the system with enhanced intelligence"""
    print("🧠 Upgrading GraphRAG System to Enhanced Intelligence")
    print("=" * 55)
    
    print("🔄 Step 1: Force reprocessing with enhanced algorithms...")
    try:
        # Force reprocess with enhanced settings
        subprocess.run([
            sys.executable, "run_system.py", "--process"
        ], input="3\n", text=True, check=True)
        
        print("✅ Enhanced processing complete!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Processing failed: {e}")
        print("🔧 Try manual process:")
        print("   python run_system.py --process")
        print("   Choose option 3")
        return False
    
    print("\n🌐 Step 2: Starting enhanced web interface...")
    try:
        subprocess.run([sys.executable, "run_system.py", "--web"])
    except KeyboardInterrupt:
        print("\n👋 System upgrade complete!")
    except Exception as e:
        print(f"❌ Web interface error: {e}")
    
    return True

if __name__ == "__main__":
    upgrade_system()