import usocket as socket
import utime as time
import ujson as json
import network

# WiFi settings
WIFI_SSID = "name12"
WIFI_PASSWORD = "password"

# Server settings
SERVER_IP = "192.168.4.1"
SERVER_PORT = 80
TCP_PORT = 8080

class TransmitData:
    """Class to handle data transmission over WiFi"""
    
    def __init__(self, ssid, password, server_ip, server_port, tcp_port=8080, wdt_obj=None):
        self.ssid = ssid
        self.password = password
        self.server_ip = server_ip
        self.server_port = server_port
        self.tcp_port = tcp_port
        self.wdt_obj = wdt_obj
        self.wlan = None
        self.wifi_available = False
        self._stream_socket = None
            
    def connect_to_wifi(self):
        """Connect to WiFi with 10 second timeout. Returns True if connected."""
        print("Connecting to WiFi...")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        if not self.wlan.isconnected():
            self.wlan.connect(self.ssid, self.password)
            
            connection_timeout = 10
            start_time = time.time()
            
            while not self.wlan.isconnected() and (time.time() - start_time) < connection_timeout:
                print("Waiting for connection...")
                time.sleep(1)
                if self.wdt_obj:
                    self.wdt_obj.feed()
            
            if self.wlan.isconnected():
                print("WiFi connected!")
                self.wifi_available = True
            else:
                print(f"WiFi connection failed after {connection_timeout} seconds - continuing without WiFi")
                self.wlan.active(False)
                self.wifi_available = False
        else:
            print("WiFi already connected!")
            self.wifi_available = True
        
        return self.wifi_available

    def send_simple_data(self, id, datatype=None, data=None):
        """Send a single message over a new TCP connection."""
        if not self.wifi_available:
            print("No WiFi connection - skipping data transmission")
            return False
        
        client_socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_ip, self.server_port))
            
            if datatype == 'Starting':
                message = f"STARTING:{id}"
            elif datatype == 'Measurement':
                message = f"MEASUREMENT:{id}:{data}"
            else:
                message = f"MSG:{id}"
            
            client_socket.send(message.encode('utf-8'))
            print(f"Sent: {message}")
            return True
            
        except Exception as e:
            print(f"Send error: {e}")
            return False
        finally:
            if client_socket is not None:
                try:
                    client_socket.close()
                except:
                    pass

    def stream_reading(self, id, sample, co2, pressure, temp_bmp, temp_si, humidity, dt_utc_str, timestamp=None):
        """Stream a single sensor reading as newline-delimited JSON over a persistent TCP connection."""
        if not self.wifi_available:
            return False

        reading = {
            "id": id,
            "co2": co2,
            "temperature": temp_bmp,
            "humidity": humidity,
            "pressure": pressure,
            "temp_si": temp_si,
            "sample": sample,
            "dt_utc": dt_utc_str,
            "timestamp": timestamp if timestamp is not None else int(time.time()),
        }

        # Try sending on existing persistent socket, reconnect once on failure
        for attempt in range(2):
            if self._stream_socket is None:
                if not self._connect_stream():
                    return False

            try:
                line = json.dumps(reading) + "\n"
                self._stream_socket.send(line.encode("utf-8"))
                return True
            except Exception as e:
                print(f"Stream send error (attempt {attempt + 1}): {e}")
                self._close_stream()

        return False

    def _connect_stream(self):
        """Open a persistent TCP socket to the server's sensor-data port."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.server_ip, self.tcp_port))
            self._stream_socket = s
            print(f"Stream connected to {self.server_ip}:{self.tcp_port}")
            return True
        except Exception as e:
            print(f"Stream connect error: {e}")
            self._stream_socket = None
            return False

    def _close_stream(self):
        """Close the persistent stream socket."""
        if self._stream_socket is not None:
            try:
                self._stream_socket.close()
            except Exception:
                pass
            self._stream_socket = None

    def disconnect_wifi(self):
        """Turn off WiFi and close any open stream."""
        self._close_stream()
        if self.wlan:
            self.wlan.active(False)
            self.wifi_available = False
            print("WiFi turned off")

if __name__ == "__main__":
    print("Starting simple client...")
    transmit_data = TransmitData(WIFI_SSID, WIFI_PASSWORD, SERVER_IP, SERVER_PORT,
                                 tcp_port=TCP_PORT, wdt_obj=None)

    if transmit_data.connect_to_wifi():
        transmit_data.send_simple_data(id='test01')
        transmit_data.disconnect_wifi()
    else:
        print("Could not connect to WiFi")
