#!/usr/bin/env python3
"""Test script to verify Lab Platform communication."""

import json
import time
import sys
import uuid
import paho.mqtt.client as mqtt


class SystemTester:
    def __init__(self, mqtt_host="192.168.1.63", mqtt_port=1883, 
                 mqtt_user="tasmota", mqtt_pass="1234"):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.client = mqtt.Client()
        self.client.username_pw_set(mqtt_user, mqtt_pass)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.responses = {}
        self.device_status = {}
        
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✓ Connected to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            # Subscribe to relevant topics
            client.subscribe("/lab/device/+/status")
            client.subscribe("/lab/device/+/meta")
            client.subscribe("/lab/device/+/evt")
            client.subscribe("/lab/orchestrator/registry")
        else:
            print(f"✗ Failed to connect to MQTT broker (code: {rc})")
            
    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            
            # Track device status
            if "/status" in msg.topic:
                device_id = msg.topic.split("/")[3]
                self.device_status[device_id] = payload
                
            # Track command responses
            if "/evt" in msg.topic and "req_id" in payload:
                self.responses[payload["req_id"]] = payload
                
        except Exception as e:
            pass
            
    def connect(self):
        """Connect to MQTT broker."""
        print(f"Connecting to MQTT broker at {self.mqtt_host}:{self.mqtt_port}...")
        self.client.connect(self.mqtt_host, self.mqtt_port, 60)
        self.client.loop_start()
        time.sleep(2)  # Wait for connection
        
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        
    def test_device_ping(self, device_id="rpi-lab-01"):
        """Test device ping command."""
        print(f"\nTesting ping to device: {device_id}")
        
        req_id = str(uuid.uuid4())
        command = {
            "req_id": req_id,
            "actor": "test",
            "action": "ping",
            "params": {},
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        # Send command
        topic = f"/lab/device/{device_id}/cmd"
        self.client.publish(topic, json.dumps(command))
        print(f"  → Sent ping command (req_id: {req_id[:8]}...)")
        
        # Wait for response
        timeout = 5
        start = time.time()
        while time.time() - start < timeout:
            if req_id in self.responses:
                response = self.responses[req_id]
                if response.get("ok"):
                    print(f"  ✓ Device responded: {response.get('details', {})}")
                else:
                    print(f"  ✗ Device error: {response.get('error')}")
                return True
            time.sleep(0.1)
            
        print(f"  ✗ No response after {timeout} seconds")
        return False
        
    def test_module_status(self, device_id="rpi-lab-01", module="ndi"):
        """Test module status command."""
        print(f"\nTesting {module} module status on device: {device_id}")
        
        req_id = str(uuid.uuid4())
        command = {
            "req_id": req_id,
            "actor": "test",
            "action": "status",
            "params": {},
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        # Send command
        topic = f"/lab/device/{device_id}/{module}/cmd"
        self.client.publish(topic, json.dumps(command))
        print(f"  → Sent status command to {module} module")
        
        # Wait for response
        timeout = 5
        start = time.time()
        while time.time() - start < timeout:
            if req_id in self.responses:
                response = self.responses[req_id]
                if response.get("ok"):
                    print(f"  ✓ Module responded with status")
                    details = response.get("details", {})
                    if details:
                        print(f"    Current source: {details.get('current_source', 'None')}")
                        print(f"    Processes: {details.get('processes', {})}")
                else:
                    print(f"  ✗ Module error: {response.get('error')}")
                return True
            time.sleep(0.1)
            
        print(f"  ✗ No response after {timeout} seconds")
        return False
        
    def list_devices(self):
        """List all connected devices."""
        print("\nConnected Devices:")
        
        if not self.device_status:
            print("  No devices found")
            return
            
        for device_id, status in self.device_status.items():
            online = status.get("online", False)
            state = "Online" if online else "Offline"
            print(f"  • {device_id}: {state}")
            
    def run_tests(self):
        """Run all system tests."""
        print("\n" + "="*50)
        print("Lab Platform System Test")
        print("="*50)
        
        # Connect to MQTT
        self.connect()
        
        # Wait for device discovery
        print("\nWaiting for device discovery...")
        time.sleep(3)
        
        # List devices
        self.list_devices()
        
        # Test device ping
        if self.device_status:
            device_id = list(self.device_status.keys())[0]
            self.test_device_ping(device_id)
            
            # Test NDI module
            self.test_module_status(device_id, "ndi")
            
            # Test Projector module
            self.test_module_status(device_id, "projector")
        else:
            print("\n⚠ No devices found. Make sure the device agent is running.")
            
        # Disconnect
        print("\n" + "="*50)
        print("Test Complete")
        print("="*50)
        self.disconnect()


def main():
    """Main entry point."""
    print("Lab Platform System Tester")
    print("MQTT Broker: 192.168.1.63:1883")
    print("")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python test_system.py [mqtt_host]")
            print("  mqtt_host: MQTT broker host (default: 192.168.1.63)")
            return
        mqtt_host = sys.argv[1]
    else:
        mqtt_host = "192.168.1.63"
    
    # Run tests
    tester = SystemTester(mqtt_host=mqtt_host)
    try:
        tester.run_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        tester.disconnect()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        tester.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    main()
