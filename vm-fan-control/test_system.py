#!/usr/bin/env python3
"""
Test script to verify fan control system components
"""

import subprocess
import sys
import time

def test_nvidia_smi():
    """Test if nvidia-smi is available and working"""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=power.draw,temperature.gpu', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, check=True)
        print("✓ nvidia-smi is working correctly")
        print(f"  Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print("✗ nvidia-smi failed:")
        print(f"  Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ nvidia-smi not found - please install NVIDIA drivers")
        return False

def test_python_imports():
    """Test that all required Python modules can be imported"""
    required_modules = ['socket', 'json', 'subprocess', 'time', 'sys']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} module available")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {e}")
            return False
    
    print("✓ All Python modules available")
    return True

def main():
    """Run all tests"""
    print("Testing VM Fan Control System Components")
    print("=" * 40)
    
    success = True
    success &= test_python_imports()
    print()
    success &= test_nvidia_smi()
    
    print()
    if success:
        print("✓ All tests passed - system is ready to run!")
    else:
        print("✗ Some tests failed - please check the errors above")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())