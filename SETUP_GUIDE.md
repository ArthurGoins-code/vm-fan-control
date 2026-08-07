# VM Fan Control System Boot Setup Guide

This guide explains how to set up the fan control system to run automatically at boot on both Proxmox host and Ubuntu VM.

## Prerequisites

1. Ensure Python 3 is installed on both systems
2. Make sure the scripts have proper permissions
3. Verify network connectivity between systems

## Proxmox Host Setup (Host Controller)

### Step 1: Copy Service File to System Directory

```bash
sudo cp /home/arthur/GitHub\ Projects/vm-fan-control/host_controller.service /etc/systemd/system/
```

### Step 2: Reload systemd and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable host_controller.service
```

### Step 3: Start the Service

```bash
sudo systemctl start host_controller.service
```

### Step 4: Check Status

```bash
sudo systemctl status host_controller.service
```

## Ubuntu VM Setup (VM Monitor)

### Step 1: Copy Service File to System Directory

```bash
sudo cp /home/arthur/GitHub\ Projects/vm-fan-control/vm_monitor.service /etc/systemd/system/
```

### Step 2: Modify IP Address (Important!)

Before enabling the service, you need to update the VM monitor to use the correct Proxmox host IP address:

1. Edit the service file:
```bash
sudo nano /etc/systemd/system/vm_monitor.service
```

2. Change the IP address in `ExecStart` line from `192.168.1.68` to your actual Proxmox host IP address.

### Step 3: Reload systemd and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable vm_monitor.service
```

### Step 4: Start the Service

```bash
sudo systemctl start vm_monitor.service
```

### Step 5: Check Status

```bash
sudo systemctl status vm_monitor.service
```

## Testing the Setup

After enabling both services:

1. Reboot your systems to test automatic startup
2. Check that both services are running:
   - On Proxmox host: `systemctl status host_controller.service`
   - On Ubuntu VM: `systemctl status vm_monitor.service`
3. Verify fan control is working by monitoring GPU temperature and fan speed

## Troubleshooting

### Common Issues:

1. **Permission Denied**: Ensure scripts have execute permissions
2. **Network Issues**: Verify connectivity between systems
3. **Path Issues**: Make sure all paths in service files are correct
4. **Python Path**: Ensure Python 3 is available at `/usr/bin/python3`

### Check Logs:

```bash
# For host controller
sudo journalctl -u host_controller.service -f

# For VM monitor  
sudo journalctl -u vm_monitor.service -f
```

## Configuration Notes

Both service files use default parameters:
- Host Controller: Listens on port 8888
- VM Monitor: Sends data to `192.168.1.68:8888` (update this for your setup)

Remember to update the IP address in `vm_monitor.service` to match your actual Proxmox host IP address.