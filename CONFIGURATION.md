# Configuration Guide for VM Fan Control System

## Overview

This document explains how to configure the fan control system for your Proxmox host and Ubuntu VM setup.

## Host Controller Configuration (Proxmox Host)

### 1. Update IP Address in config.py

Edit `/home/arthur/GitHub Projects/vm-fan-control/config.py`:

```python
# Network configuration
VM_HOST_IP = "192.168.1.68"  # Replace with actual Proxmox host IP
VM_HOST_PORT = 8888
```

### 2. Verify Fan Control Hardware Paths

The system assumes fan control via:
```
/sys/class/hwmon/hwmon3/pwm1_enable
/sys/class/hwmon/hwmon3/pwm1
```

If your hardware uses different paths, update these in `host_controller.py`:

```python
# Line 30 in host_controller.py
pwm_enable_file = "/sys/class/hwmon/hwmon3/pwm1_enable"

# Line 80 in host_controller.py  
pwm_file = "/sys/class/hwmon/hwmon3/pwm1"
```

## VM Monitor Configuration (Ubuntu VM)

### 1. Update Host IP Address

Edit `/home/arthur/GitHub Projects/vm-fan-control/vm_monitor.py`:

```python
# Line 20 in vm_monitor.py
self.host_ip = "192.168.1.68"  # Replace with actual Proxmox host IP
```

### 2. Verify NVIDIA Driver Setup

Ensure nvidia-smi is working on the VM:

```bash
nvidia-smi --query-gpu=power.draw,temperature.gpu --format=csv,noheader,nounits
```

If this fails, install NVIDIA drivers:
```bash
sudo apt update
sudo apt install nvidia-driver-XXX  # Replace with appropriate driver version
```

## Service Configuration

### Proxmox Host Service (host_controller.service)

This service runs the host controller on port 8888:

```ini
[Unit]
Description=VM Fan Control Host Controller
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/arthur/GitHub Projects/vm-fan-control
ExecStart=/usr/bin/python3 /home/arthur/GitHub Projects/vm-fan-control/host_controller.py 8888
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Ubuntu VM Service (vm_monitor.service)

This service runs the VM monitor to send data to the Proxmox host:

```ini
[Unit]
Description=VM GPU Monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/arthur/GitHub Projects/vm-fan-control
ExecStart=/usr/bin/python3 /home/arthur/GitHub Projects/vm-fan-control/vm_monitor.py 192.168.1.68 8888
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Network Setup

### Required Ports

- Port 8888: TCP - Used by host controller for receiving GPU data from VM

### Firewall Configuration (Proxmox Host)

If you have a firewall enabled, allow incoming connections on port 8888:

```bash
sudo ufw allow 8888/tcp
# or if using iptables:
sudo iptables -A INPUT -p tcp --dport 8888 -j ACCEPT
```

## Testing the Configuration

### Step 1: Test Individual Components

On Proxmox host:
```bash
python3 /home/arthur/GitHub\ Projects/vm-fan-control/host_controller.py 8888
```

On Ubuntu VM:
```bash
python3 /home/arthur/GitHub\ Projects/vm-fan-control/vm_monitor.py 192.168.1.68 8888
```

### Step 2: Test with Services

Enable and start services:
```bash
sudo systemctl enable host_controller.service
sudo systemctl enable vm_monitor.service
sudo systemctl start host_controller.service
sudo systemctl start vm_monitor.service
```

### Step 3: Monitor Logs

Check service status:
```bash
sudo systemctl status host_controller.service
sudo systemctl status vm_monitor.service
```

## Troubleshooting

### Common Issues:

1. **Fan Control Not Working**: Check hardware paths in `host_controller.py`
2. **Connection Refused**: Verify network connectivity and port 8888 is open
3. **NVIDIA Driver Issues**: Ensure nvidia-smi works on VM
4. **Permission Denied**: Make sure scripts are executable and have proper permissions

### Debug Commands:

```bash
# Check if service files are valid
sudo systemctl daemon-reload

# View service logs
sudo journalctl -u host_controller.service
sudo journalctl -u vm_monitor.service

# Test network connectivity
telnet 192.168.1.68 8888
```