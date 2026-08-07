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
from collections import deque

class FanController:
    def __init__(self, port, max_temp=85, min_temp=60):
        self.port = port
        self.max_temp = max_temp  # Maximum temperature for full speed
        self.min_temp = min_temp  # Minimum temperature for minimum speed
        self.socket = None
        self.gpu_data_history = deque(maxlen=10)  # Keep last 10 readings
        pwm_enable_file = "/sys/class/hwmon/hwmon3/pwm1_enable"
        with open(pwm_enable_file, 'w') as f:
            f.write('1')  # Enable manual fan control
        
    def get_fan_speed(self, temperature):
        """Calculate fan speed based on temperature using aggressive curve"""
        # If temperature is below minimum, use minimum speed (0%)
        if temperature <= self.min_temp:
            return 0  # Minimum 0% speed at idle
        elif temperature >= self.max_temp:
            return 100  # Maximum 100% speed at max temperature
        
        # Calculate aggressive fan curve - ramp up quickly and sharply
        # Using quadratic curve for more aggressive response
        temp_range = self.max_temp - self.min_temp
        temp_ratio = (temperature - self.min_temp) / temp_range
        
        # Quadratic curve for more aggressive ramp-up
        # This makes it go from 0% to 100% very quickly as temperature approaches max
        fan_speed = 100 * (temp_ratio ** 2.5)  # More aggressive exponential curve
        
        # Ensure we don't go below minimum or above maximum
        fan_speed = max(0, min(100, fan_speed))
        
        return round(fan_speed)
    
    def set_fan_speed(self, speed):
        """Set fan speed using sysfs interface"""
        try:
            # Convert percentage to PWM value (0-255)
            pwm_value = int((speed / 100.0) * 255)
            print(f"Setting fan speed to {speed}% ({pwm_value}/255)")
            
            # Write to the sysfs interface for fan control
            # The path may vary based on your system - adjust accordingly
            pwm_file = "/sys/class/hwmon/hwmon3/pwm1"
            
            with open(pwm_file, 'w') as f:
                f.write(str(pwm_value))
                
            print(f"Fan speed set to {speed}% successfully")
            
        except Exception as e:
            print(f"Error setting fan speed: {e}")
            print("Make sure you have proper permissions and the correct sysfs path")
    
    def process_gpu_data(self, data):
        """Process GPU data and adjust fan speed"""
        try:
            temperature = data['temperature']
            
            # Store in history for averaging
            self.gpu_data_history.append(temperature)
            
            # Calculate average temperature from recent readings
            if len(self.gpu_data_history) > 0:
                avg_temp = sum(self.gpu_data_history) / len(self.gpu_data_history)
            else:
                avg_temp = temperature
                
            print(f"Average GPU Temperature: {avg_temp:.1f}°C")
            
            # Calculate fan speed based on temperature
            fan_speed = self.get_fan_speed(avg_temp)
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