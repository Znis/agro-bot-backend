import serial
import serial.tools.list_ports
import threading
import time

class CNCConnection:
    def __init__(self):
        self.logs = []
        self.position = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        self.serial_conn = self.connect_serial()

        if self.serial_conn:
            threading.Thread(target=self.read_serial, daemon=True).start()

    def connect_serial(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "USB" in port.description:
                try:
                    conn = serial.Serial(port.device, 115200, timeout=1)
                    self.log(f"Connected to {port.device}")
                    return conn
                except serial.SerialException as e:
                    self.log(f"Error connecting: {e}")
        self.log("No CNC device found.")
        return None

    def send_command_and_wait_response(self, command, timeout=2):
        if not self.serial_conn:
            return "Error: No CNC connection."
        
        self.serial_conn.reset_input_buffer()  # Clear old junk
        self.serial_conn.write((command + "\n").encode())
        self.log(f"TX: {command}")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.serial_conn.in_waiting:
                response = self.serial_conn.readline().decode().strip()
                self.log(f"RX: {response}")
                return response
            time.sleep(0.1)  # wait 100ms between checks
        
        return "Timeout: No response from CNC."

    def read_serial(self):
        while True:
            if self.serial_conn and self.serial_conn.in_waiting:
                response = self.serial_conn.readline().decode().strip()
                self.log(f"RX: {response}")
                if "MPos:" in response:
                    try:
                        pos_data = response.split("MPos:")[1].split(",")
                        self.position = {
                            "X": float(pos_data[0]),
                            "Y": float(pos_data[1]),
                            "Z": float(pos_data[2])
                        }
                    except Exception as e:
                        self.log(f"Position error: {e}")
            time.sleep(0.5)

    def log(self, message):
        print(message)
        self.logs.append(message)

# Create a singleton instance
cnc = CNCConnection() 