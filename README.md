# VM Fan Control System

This project provides a solution to control fan speed based on GPU monitoring for a V100 GPU in a Proxmox environment. It consists of two components:

1. A Python script running on the Ubuntu VM that monitors GPU power usage and temperature
2. A Python script running on the Proxmox host that controls the fan speed using the monitored data

## System Overview

The system uses GPU passthrough to give the Ubuntu VM direct access to a V100 GPU. The Proxmox host controls a fan connected to a motherboard header that cools the GPU.

## Features

- **Adaptive GPU Monitoring**: GPU monitoring interval adjusts based on temperature
  - Low temperature: Monitor every 30 seconds (MAX_MONITOR_INTERVAL)
  - High temperature: Monitor every 1 second (MIN_MONITOR_INTERVAL) 
- **Temperature-based Fan Control**: Fan speed smoothly increases with GPU temperature
- **Configurable Parameters**: Easy to customize temperature ranges, fan speeds, and monitoring intervals
- **Network Communication**: Secure TCP communication between VM and host

## Requirements

### On Ubuntu VM:
- Python 3
- nvidia-smi (NVIDIA drivers installed)
- Network access to Proxmox host

### On Proxmox Host:
- Python 3
- Fan control permissions for writing to sysfs interface
- Access to `/sys/class/hwmon/hwmon3/pwm1` for fan control

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
MAX_TEMP = 80        # Temperature at which to reach maximum speed
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
- When temperature is low, it monitors every 30 seconds (MAX_MONITOR_INTERVAL)
- When temperature is high, it monitors every 1 second (MIN_MONITOR_INTERVAL) 
- Data is sent via TCP socket to the Proxmox host
- Multiple readings are averaged for smoother fan control

### Fan Control (Host Side)
- Receives GPU data from VM through TCP socket
- Calculates fan speed based on temperature using a linear curve between minimum and maximum temperatures
- Sets fan speed using the sysfs interface: `echo <speed> | tee /sys/class/hwmon/hwmon3/pwm1`
- Speed values are converted from percentage (0-100) to PWM value (0-255)

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
- The fan control implementation in `set_fan_speed()` uses: `echo <speed> | tee /sys/class/hwmon/hwmon3/pwm1`
- You'll need to ensure you have proper permissions to write to the sysfs interface
- For your specific setup, fan speed values range from 0 to 255 (converted from percentage)