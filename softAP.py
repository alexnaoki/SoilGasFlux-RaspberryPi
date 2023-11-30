import network, socket, asyncio

class SoftAP:
    def __init__(self, ssid, password):
        """
            Description: This is a function to activate AP mode
            
            Parameters:
            
            ssid[str]: The name of your internet connection
            password[str]: Password for your internet connection
            
            Returns: Nada
        """
        # Just making our internet connection
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=ssid, password=password)
        ap.active(True)
        
        while ap.active() == False:
            pass
        print('AP Mode Is Active, You can Now Connect')
        print('IP Address To Connect to:: ' + ap.ifconfig()[0])
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
        self.s.bind(('', 80))
        self.s.listen(5)
    
    def web_page(self, data):
        html = f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="10"></head>
                  <body><h1>Hello World<p>{data}</p></h1></body></html>
               """
        return html
    
    async def handle_connection(self, conn, addr, sensor):
        print('Got a connection from %s' % str(addr))
        request = await asyncio.to_thread(conn.recv, 1024)
        print('Content = %s' % str(request))
        response = self.web_page2()
        await asyncio.to_thread(conn.send, response.encode())
        conn.close()

    async def run(self, sensor):
        sensor = sensor
        while True:
            conn, addr = await asyncio.to_thread(self.s.accept)
            asyncio.create_task(self.handle_connection(conn, addr, sensor))
          
          
if __name__ == '__main__':
    ap = SoftAP(ssid='NAME',
                password='PASSWORD')
    asyncio.run(ap.run(sensor=None))