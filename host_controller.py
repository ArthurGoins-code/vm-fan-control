#!/usr/bin/env python3
"""
Fan Controller Script for Proxmox Host
This script receives GPU data from VM and controls fan speed using adjustable curve
"""

import socket
import json
import time
import subprocess
import sys
from datetime import datetime

sys.path.append('.')
import config

class FanController:
    def __init__(self, port, max_temp=None, min_temp=None):
        self.port = port
        self.max_temp = max_temp if max_temp is not None else config.MAX_TEMP
        self.min_temp = min_temp if min_temp is not None else config.MIN_TEMP
        self.min_fan_speed = config.MIN_FAN_SPEED
        self.max_fan_speed = config.MAX_FAN_SPEED
        # Temperature/speed at which the fan should immediately ramp up,
        # rather than waiting for the gentle part of the curve
        self.ramp_trigger_temp = config.RAMP_TRIGGER_TEMP
        self.ramp_trigger_fan_speed = config.RAMP_TRIGGER_FAN_SPEED
        self.curve_exponent = config.CURVE_EXPONENT
        self.socket = None
        self.hwmon_path = config.HWMON_PATH
        self.pwm_channels = config.PWM_CHANNELS
        self.cpu_temp_sensor_label = config.CPU_TEMP_SENSOR_LABEL
        for channel in self.pwm_channels:
            pwm_enable_file = f"{self.hwmon_path}/pwm{channel}_enable"
            with open(pwm_enable_file, 'w') as f:
                f.write('1')  # Enable manual fan control
        
    def get_fan_speed(self, temperature):
        """Calculate fan speed using a two-stage, adjustable fan curve.

        - Below min_temp: idle (min_fan_speed)
        - min_temp .. ramp_trigger_temp: gentle linear ramp up to ramp_trigger_fan_speed
        - At/above ramp_trigger_temp: fan speed immediately jumps to
          ramp_trigger_fan_speed and then climbs steeply toward max_fan_speed
          as it approaches max_temp
        """
        # If temperature is below minimum, use minimum speed
        if temperature <= self.min_temp:
            return self.min_fan_speed
        elif temperature >= self.max_temp:
            return self.max_fan_speed

        if temperature < self.ramp_trigger_temp:
            # Gentle ramp from min_fan_speed up to ramp_trigger_fan_speed
            temp_range = self.ramp_trigger_temp - self.min_temp
            temp_ratio = (temperature - self.min_temp) / temp_range
            fan_speed = self.min_fan_speed + temp_ratio * (
                self.ramp_trigger_fan_speed - self.min_fan_speed
            )
        else:
            # Immediate, steep ramp from ramp_trigger_fan_speed up to max_fan_speed.
            # Exponent < 1 makes the curve rise fast right after the trigger point
            # then level off as it nears max_temp.
            temp_range = self.max_temp - self.ramp_trigger_temp
            temp_ratio = (temperature - self.ramp_trigger_temp) / temp_range
            fan_speed = self.ramp_trigger_fan_speed + (
                temp_ratio ** (1 / self.curve_exponent)
            ) * (self.max_fan_speed - self.ramp_trigger_fan_speed)

        # Ensure we don't go below minimum or above maximum
        fan_speed = max(self.min_fan_speed, min(self.max_fan_speed, fan_speed))

        return round(fan_speed)

    def get_cpu_temperature(self):
        """Read the host CPU temperature (e.g. k10temp 'Tccd1') via `sensors`"""
        try:
            result = subprocess.run(
                ['sensors', '-j'], capture_output=True, text=True, check=True
            )
            data = json.loads(result.stdout)

            for chip_readings in data.values():
                for label, values in chip_readings.items():
                    if self.cpu_temp_sensor_label not in label:
                        continue
                    for key, value in values.items():
                        if key.endswith('_input'):
                            return float(value)

        except Exception as e:
            print(f"Error reading CPU temperature: {e}")

        return None
    
    def set_fan_speed(self, speed):
        """Set fan speed on all configured PWM channels using sysfs interface"""
        # Convert percentage to PWM value (0-255)
        pwm_value = int((speed / 100.0) * 255)
        print(f"Setting fan speed to {speed}% ({pwm_value}/255) on pwm{self.pwm_channels}")

        for channel in self.pwm_channels:
            try:
                # The path may vary based on your system - adjust accordingly
                pwm_file = f"{self.hwmon_path}/pwm{channel}"

                with open(pwm_file, 'w') as f:
                    f.write(str(pwm_value))

                print(f"pwm{channel} set to {speed}% successfully")

            except Exception as e:
                print(f"Error setting pwm{channel} speed: {e}")
                print("Make sure you have proper permissions and the correct sysfs path")
    
    def process_gpu_data(self, data):
        """Process GPU data and adjust fan speed based on the hotter of the
        GPU and host CPU temperatures"""
        try:
            gpu_temp = data['temperature']
            cpu_temp = self.get_cpu_temperature()

            if cpu_temp is not None:
                print(f"GPU Temperature: {gpu_temp:.1f}°C | CPU ({self.cpu_temp_sensor_label}) Temperature: {cpu_temp:.1f}°C")
                effective_temp = max(gpu_temp, cpu_temp)
            else:
                print(f"GPU Temperature: {gpu_temp:.1f}°C | CPU ({self.cpu_temp_sensor_label}) Temperature: unavailable")
                effective_temp = gpu_temp

            # Calculate fan speed based on the hotter of the two temperatures
            fan_speed = self.get_fan_speed(effective_temp)
            print(f"Setting fan speed to {fan_speed}%")
            
            # Set the fan speed
            self.set_fan_speed(fan_speed)
            
        except Exception as e:
            print(f"Error processing GPU data: {e}")
    
    def start_server(self):
        """Start the server to listen for GPU data"""
        print("Starting fan controller server...")
        
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(1)
            
            print(f"Server listening on port {self.port}")
            
            while True:
                try:
                    conn, addr = self.socket.accept()
                    print(f"Connection from {addr}")
                    
                    # Receive data
                    data = b""
                    while True:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        data += chunk
                        
                        # Check if we have a complete message (ending with newline)
                        if data.endswith(b'\n'):
                            break
                    
                    if data:
                        try:
                            gpu_data = json.loads(data.decode())
                            print(f"Received GPU data: {gpu_data}")
                            self.process_gpu_data(gpu_data)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"Error handling connection: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("Stopping server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python host_controller.py <port>")
        sys.exit(1)
    
    port = int(sys.argv[1])
    
    controller = FanController(port)
    controller.start_server()