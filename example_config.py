#!/usr/bin/env python3
"""
Configuration file for VM Fan Control System
"""

# Network configuration
VM_HOST_IP = "192.168.1.68"  # Replace with actual Proxmox host IP
VM_HOST_PORT = 8888

# GPU monitoring parameters
GPU_MONITOR_INTERVAL = 10  # seconds (default interval)
MIN_MONITOR_INTERVAL = 1   # Minimum monitoring interval in seconds (when temp is high)
MAX_MONITOR_INTERVAL = 20  # Maximum monitoring interval in seconds (when temp is low)

# Fan control parameters
MIN_FAN_SPEED = 0    # Minimum fan speed percentage (0% for idle)
MAX_FAN_SPEED = 100  # Maximum fan speed percentage (100% for max temp)
MIN_TEMP = 60        # Temperature at which to start increasing speed
MAX_TEMP = 77        # Temperature at which to reach maximum speed

# Ramp trigger - as soon as this temperature is hit, the fan immediately
# jumps to RAMP_TRIGGER_FAN_SPEED and continues ramping steeply toward
# MAX_FAN_SPEED, instead of waiting for the gentle curve below MIN_TEMP..RAMP_TRIGGER_TEMP
RAMP_TRIGGER_TEMP = 65        # Temperature (°C) that triggers an immediate ramp-up
RAMP_TRIGGER_FAN_SPEED = 60   # Fan speed (%) to jump to as soon as RAMP_TRIGGER_TEMP is reached
CURVE_EXPONENT = 2.5          # Steepness of the ramp between RAMP_TRIGGER_TEMP and MAX_TEMP (>1 = steeper)

# Advanced settings
TEMP_HISTORY_SIZE = 10  # Number of temperature readings to average