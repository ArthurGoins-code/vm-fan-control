# VM Fan Control System

This project provides a solution to control fan speed based on GPU monitoring. It consists of two components:

1. A Python script running on the Ubuntu VM that monitors GPU power usage and temperature
2. A Python script running on the Proxmox host that controls the fan speed using the monitored data

## Features

- **Adaptive Monitoring**: GPU monitoring interval adjusts based on temperature
  - Low temperature: Monitor every 60 seconds (MAX_MONITOR_INTERVAL)
  - High temperature: Monitor every 5 seconds (MIN_MONITOR_INTERVAL)
- **Temperature-based Fan Control**: Fan speed smoothly increases with GPU temperature
- **Configurable Parameters**: Easy to customize temperature ranges, fan speeds, and monitoring intervals

## Requirements

- Ubuntu VM with GPU passthrough and nvidia-smi installed
- Proxmox host with fancontrol installed
- Network connectivity between VM and host