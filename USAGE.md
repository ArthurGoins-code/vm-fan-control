# Usage Guide for VM Fan Control System

## Overview

This system consists of two components:
1. **VM Monitor**: Runs on the Ubuntu VM to monitor GPU temperature and power usage
2. **Host Controller**: Runs on the Proxmox host to control fan speed based on GPU data

## Setup Instructions

### 1. Configure Network Access
- Ensure the Ubuntu VM can reach the Proxmox host over the network
- Note the IP address of your Proxmox host (e.g., `192.168.1.50`)

### 2. Update Configuration
Edit `config.py` to match your setup:
```python
# Network configuration
VM_HOST_IP = "192.168.1.50"  # Replace with actual Proxmox host IP

# Fan control parameters
MIN_TEMP = 60        # Temperature at which to start increasing speed
MAX_TEMP = 85        # Temperature at which to reach maximum speed
```

### 3. Run the Components

#### On Proxmox Host:
```bash
python3 host_controller.py 8888
```

#### On Ubuntu VM:
```bash
python3 vm_monitor.py 192.168.1.50 8888
```

## How It Works

### GPU Monitoring (VM Side)
- The VM monitor runs `nvidia-smi` with an adjustable interval based on GPU temperature
- When temperature is low, it monitors every 60 seconds (MAX_MONITOR_INTERVAL)
- When temperature is high, it monitors every 5 seconds (MIN_MONITOR_INTERVAL) 
- Data is sent via TCP socket to the Proxmox host
- Multiple readings are averaged for smoother fan control

### Fan Control (Host Side)
- Receives GPU data from VM through TCP socket
- Calculates fan speed based on temperature using a linear curve between minimum and maximum temperatures
- Sets fan speed using system commands (you'll need to customize this part for your specific fancontrol setup)

## Customization Options

### Adjusting Temperature Ranges
Modify `MIN_TEMP` and `MAX_TEMP` in config.py to set the temperature range for fan speed control.

### Changing Monitoring Interval
Adjust `MIN_MONITOR_INTERVAL` and `MAX_MONITOR_INTERVAL` in config.py to change how frequently GPU data is collected based on temperature:
- When temperature is at or below MIN_TEMP: monitor every MAX_MONITOR_INTERVAL seconds
- When temperature is at or above MAX_TEMP: monitor every MIN_MONITOR_INTERVAL seconds
- Between MIN_TEMP and MAX_TEMP: interval is interpolated between the two values

### Modifying Fan Curve
The current implementation uses a linear interpolation between min and max temperatures. You can modify the `get_fan_speed()` function in `host_controller.py` to implement different fan curves.

## Troubleshooting

### Connection Issues
- Ensure the Proxmox host IP address is correct
- Verify network connectivity between VM and host
- Check that port 8888 is not blocked by firewall

### Fan Control Not Working
- The fan control implementation in `set_fan_speed()` is a placeholder
- You'll need to replace it with actual commands for your system's fancontrol setup
- Common commands include: `pwmconfig`, `fancontrol`, or direct hardware interface commands

## Requirements

### On Ubuntu VM:
- Python 3
- nvidia-smi (NVIDIA drivers installed)
- Network access to Proxmox host

### On Proxmox Host:
- Python 3
- fancontrol utility installed
- Appropriate permissions for controlling fan hardware