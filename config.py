#!/usr/bin/env python3
"""
Configuration file for VM Fan Control System
"""

# Network configuration
VM_HOST_IP = "192.168.1.100"  # Replace with actual VM IP
VM_HOST_PORT = 8888

# GPU monitoring parameters
GPU_MONITOR_INTERVAL = 30  # seconds

# Fan control parameters
MIN_FAN_SPEED = 30   # Minimum fan speed percentage
MAX_FAN_SPEED = 100  # Maximum fan speed percentage
MIN_TEMP = 60        # Temperature at which to start increasing speed
MAX_TEMP = 85        # Temperature at which to reach maximum speed

# Advanced settings
TEMP_HISTORY_SIZE = 10  # Number of temperature readings to average