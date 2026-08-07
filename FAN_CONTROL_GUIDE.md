# Fan Control Implementation Guide

The fan control functionality in `host_controller.py` currently uses a placeholder implementation. You'll need to customize it based on your specific hardware and fancontrol setup.

## Common Fan Control Methods

### 1. Using pwmconfig/fancontrol (Linux)
If you're using the standard Linux fancontrol utilities:

```python
def set_fan_speed(self, speed):
    """Set fan speed using fancontrol"""
    try:
        # Example command - adjust based on your system
        result = subprocess.run([
            'pwmconfig',  # or just 'fancontrol'
            '--set',
            f'fan1={speed}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Fan speed set to {speed}% successfully")
        else:
            print(f"Failed to set fan speed: {result.stderr}")
    except Exception as e:
        print(f"Error setting fan speed: {e}")
```

### 2. Direct Hardware Access
For direct hardware control, you might need to use:

```python
def set_fan_speed(self, speed):
    """Set fan speed using direct hardware access"""
    try:
        # Example for SMBus interface
        import smbus
        bus = smbus.SMBus(1)  # I2C bus number
        
        # Write to appropriate register (this is just an example)
        # You'll need to research your specific hardware registers
        bus.write_byte_data(0x2e, 0x00, speed)  # Adjust address and register
        
    except Exception as e:
        print(f"Error setting fan speed: {e}")
```

### 3. Using sysfs (Linux)
Some systems expose fan control through sysfs:

```python
def set_fan_speed(self, speed):
    """Set fan speed using sysfs"""
    try:
        # Path to your fan's PWM control file
        pwm_file = "/sys/class/hwmon/hwmon0/pwm1"
        
        with open(pwm_file, 'w') as f:
            f.write(str(speed))
            
        print(f"Fan speed set to {speed}%")
    except Exception as e:
        print(f"Error setting fan speed: {e}")
```

## Finding Your Fan Control Method

### Step 1: Check Available Tools
```bash
# Check if fancontrol is installed
which fancontrol

# Check for pwmconfig
which pwmconfig

# List hardware sensors
sensors
```

### Step 2: Identify Fan Hardware
```bash
# Check what hardware you have
ls -la /sys/class/hwmon/
cat /sys/class/hwmon/*/name
```

### Step 3: Configure fancontrol (if using it)
```bash
# Run pwmconfig to auto-detect your hardware
sudo pwmconfig

# This will generate a configuration file in /etc/fancontrol
```

## Important Notes

1. **Permissions**: You'll likely need to run the host controller with `sudo` or configure appropriate permissions.

2. **Hardware Compatibility**: The exact method depends on your motherboard and fan controller hardware.

3. **Testing**: Always test fan control commands manually before implementing them in the script.

4. **Safety**: Be careful when modifying fan speeds - ensure you don't damage your hardware.