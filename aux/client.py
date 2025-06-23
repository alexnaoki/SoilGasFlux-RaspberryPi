import usocket as socket
import utime as time
import network

# WiFi settings
WIFI_SSID = "name12"
WIFI_PASSWORD = "password"

# Server settings
SERVER_IP = "192.168.4.1"
SERVER_PORT = 80

class TransmitData:
    """Class to handle data transmission over WiFi"""
    
    def __init__(self, ssid, password, server_ip, server_port, wdt_obj=None):
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip
        self.server_port = server_port
        self.wdt_obj = wdt_obj  # Watchdog timer object, if needed
            
    def connect_to_wifi(self):
        """Connect to WiFi with 10 second timeout"""
        print("Connecting to WiFi...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print(wlan.isconnected())
        
        if not wlan.isconnected():
            wlan.connect(self.ssid, self.password)
            
            # Try to connect for 10 seconds maximum
            connection_timeout = 10
            start_time = time.time()
            
            while not wlan.isconnected() and (time.time() - start_time) < connection_timeout:
                print("Waiting for connection...")
                time.sleep(1)
                if self.wdt_obj:  # Feed watchdog timer if available
                    self.wdt_obj.feed()
            
            if wlan.isconnected():
                print("WiFi connected!")
            else:
                print(f"WiFi connection failed after {connection_timeout} seconds - continuing without WiFi")
        else:
            print("WiFi already connected!")
        
        return wlan

    def send_simple_data(self, id, datatype=None, data=None):
        """Send simple test messages"""
        wlan = self.connect_to_wifi()
        
        # Check if WiFi connection was successful
        if not wlan.isconnected():
            print("No WiFi connection - skipping data transmission")
            return False
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to {self.server_ip}:{self.server_port}...")
            
            client_socket.connect((self.server_ip, self.server_port))
            print("Connected!")
            
            # Send simple messages
            if datatype is None:
                for i in range(2):
                    message = f"Message {i+1} from client: {id}"
                    client_socket.send(message.encode('utf-8'))
                    print(f"Sent: {message}")
                    time.sleep(1)
            if datatype == 'Starting':
                print('Sending starting message...')
                message = f"STARTING:{id}"
                client_socket.send(message.encode('utf-8'))
                print(f"Sent: {message}")
                time.sleep(1)
            if datatype == 'Measurement':
                print('Sending measurement data...')
                message = f"MEASUREMENT:{id}:{data}"
                client_socket.send(message.encode('utf-8'))
                print(f"Sent: {message}")
                time.sleep(1)
            
            print("Finished sending messages")
            return True
            
        except OSError as e:
            print(f"Connection error: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            try:
                client_socket.close()
                print("Connection closed")
            except:
                pass
            
            # Turn off WiFi
            print("Turning off WiFi...")
            wlan.active(False)
            print("WiFi turned off")

if __name__ == "__main__":
    print("Starting simple client...")
    transmit_data = TransmitData(WIFI_SSID, WIFI_PASSWORD, SERVER_IP, SERVER_PORT, wdt_obj=None)

    transmit_data.send_simple_data(id='test01')
