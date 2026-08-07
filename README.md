# VM Fan Control System

This project provides a solution to control fan speed based on GPU monitoring. It consists of two components:

1. A Python script running on the Ubuntu VM that monitors GPU power usage and temperature
2. A Python script running on the Proxmox host that controls the fan speed using the monitored data

## Requirements

- Ubuntu VM with GPU passthrough and nvidia-smi installed
- Proxmox host with fancontrol installed
- Network connectivity between VM and host