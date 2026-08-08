#!/usr/bin/env python3
"""
Configuration file for VM Fan Control System
"""

# Network configuration
VM_HOST_IP = "192.168.1.68"  # Replace with actual Proxmox host IP
VM_HOST_PORT = 8888

# GPU monitoring parameters
MIN_MONITOR_INTERVAL = 250   # Minimum monitoring interval in milliseconds (when temp is high)
MAX_MONITOR_INTERVAL = 2000  # Maximum monitoring interval in milliseconds (when temp is low)

# Fan control parameters
MIN_FAN_SPEED = 10    # Minimum fan speed percentage (0% for idle)
MAX_FAN_SPEED = 100  # Maximum fan speed percentage (100% for max temp)
MIN_TEMP = 60        # Temperature at which to start increasing speed
MAX_TEMP = 77        # Temperature at which to reach maximum speed

# Ramp trigger - as soon as this temperature is hit, the fan immediately
# jumps to RAMP_TRIGGER_FAN_SPEED and continues ramping steeply toward
# MAX_FAN_SPEED, instead of waiting for the gentle curve below MIN_TEMP..RAMP_TRIGGER_TEMP
RAMP_TRIGGER_TEMP = 65        # Temperature (°C) that triggers an immediate ramp-up
RAMP_TRIGGER_FAN_SPEED = 75   # Fan speed (%) to jump to as soon as RAMP_TRIGGER_TEMP is reached
CURVE_EXPONENT = 2.5          # Steepness of the ramp between RAMP_TRIGGER_TEMP and MAX_TEMP (>1 = steeper)

# PWM hwmon channels to control. All channels listed here are enabled for
# manual control and driven together using the same fan curve.
HWMON_PATH = "/sys/class/hwmon/hwmon3"
PWM_CHANNELS = [1, 2, 3, 4, 7]  # e.g. pwm1, pwm2, pwm3

# Host CPU temperature monitoring (read locally via `sensors` on the Proxmox
# host). The label below is matched against `sensors -j` output (e.g. the
# k10temp "Tctl" chiplet die temp on AMD CPUs). This temperature drives the
# same fan curve as the GPU temperature - whichever is hotter wins.
CPU_TEMP_SENSOR_LABEL = "Tctl"

# Independent fan control options
# Set to True to enable independent control of GPU and CPU fans
# When False (default), uses joint control mode where both temperatures are considered together
INDEPENDENT_FAN_CONTROL = False

# For independent control, define separate parameters for GPU and CPU
GPU_MIN_TEMP = 60
GPU_MAX_TEMP = 77
GPU_MIN_FAN_SPEED = 10
GPU_MAX_FAN_SPEED = 100
GPU_RAMP_TRIGGER_TEMP = 65
GPU_RAMP_TRIGGER_FAN_SPEED = 75
GPU_CURVE_EXPONENT = 2.5

CPU_MIN_TEMP = 60
CPU_MAX_TEMP = 77
CPU_MIN_FAN_SPEED = 10
CPU_MAX_FAN_SPEED = 100
CPU_RAMP_TRIGGER_TEMP = 65
CPU_RAMP_TRIGGER_FAN_SPEED = 75
CPU_CURVE_EXPONENT = 2.5
