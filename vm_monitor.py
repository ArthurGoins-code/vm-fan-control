#!/usr/bin/env python3
"""
GPU Monitor Script for Ubuntu VM
This script monitors GPU power usage and temperature and sends data to Proxmox host
"""

import subprocess
import json
import socket
import time
import sys
from datetime import datetime

class GPUMonitor:
    def __init__(self, host_ip, host_port):
        self.host_ip = host_ip
        self.host_port = host_port
        self.socket = None
        
    def get_gpu_data(self):
        """Get GPU power usage and temperature using nvidia-smi"""
        try:
            # Run nvidia-smi command to get GPU data
            result = subprocess.run([
                'nvidia-smi', 
                '--query-gpu=power.draw,temperature.gpu', 
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, check=True)
            
            # Parse the output
            lines = result.stdout.strip().split('\n')
            if not lines:
                return None
                
            # For single GPU, take first line
            data = lines[0].strip().split(', ')
            if len(data) >= 2:
                power_draw = float(data[0])
                temperature = float(data[1])
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'power_draw': power_draw,
                    'temperature': temperature
                }
            
        except subprocess.CalledProcessError as e:
            print(f"Error running nvidia-smi: {e}")
        except Exception as e:
            print(f"Error getting GPU data: {e}")
            
        return None
    
    def send_data(self, data):
        """Send GPU data to Proxmox host"""
        try:
            # Create socket connection
            if not self.socket:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host_ip, self.host_port))
            
            # Send data as JSON
            message = json.dumps(data) + '\n'
            self.socket.send(message.encode())
            
        except Exception as e:
            print(f"Error sending data: {e}")
            # Try to reconnect
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host_ip, self.host_port))
                self.socket.send(message.encode())
            except Exception as e2:
                print(f"Failed to reconnect: {e2}")
    
    def run(self):
        """Main monitoring loop"""
        print("Starting GPU monitor...")
        
        while True:
            try:
                gpu_data = self.get_gpu_data()
                if gpu_data:
                    print(f"GPU Data - Power: {gpu_data['power_draw']}W, Temp: {gpu_data['temperature']}°C")
                    self.send_data(gpu_data)
                
                # Wait before next reading (30 seconds)
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("Stopping monitor...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vm_monitor.py <host_ip> <host_port>")
        sys.exit(1)
    
    host_ip = sys.argv[1]
    host_port = int(sys.argv[2])
    
    monitor = GPUMonitor(host_ip, host_port)
    monitor.run()