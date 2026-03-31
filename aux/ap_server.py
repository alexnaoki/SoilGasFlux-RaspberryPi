import network
import usocket as socket
import ujson as json
import time


# Maximum number of recent readings held in RAM
_MAX_POINTS = 300

_HTML_PAGE = """\
HTTP/1.0 200 OK\r
Content-Type: text/html\r
Connection: close\r
\r
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CO2 Monitor</title>
<style>
body{font-family:sans-serif;margin:20px;background:#1a1a2e;color:#e0e0e0}
h1{color:#0ff;font-size:1.4em}
canvas{width:100%%;height:320px;background:#16213e;border-radius:8px;display:block;margin-top:10px}
.stats{display:flex;gap:20px;margin-top:12px;flex-wrap:wrap}
.stat{background:#16213e;padding:10px 16px;border-radius:8px;min-width:100px}
.stat .label{font-size:.75em;color:#888}
.stat .value{font-size:1.5em;font-weight:bold;color:#0ff}
#status{margin-top:8px;font-size:.8em;color:#888}
</style>
</head>
<body>
<h1>CO2 Monitor — Live</h1>
<canvas id="chart"></canvas>
<div class="stats">
  <div class="stat"><div class="label">Latest CO2</div><div class="value" id="cur">--</div></div>
  <div class="stat"><div class="label">Min</div><div class="value" id="mn">--</div></div>
  <div class="stat"><div class="label">Max</div><div class="value" id="mx">--</div></div>
  <div class="stat"><div class="label">Samples</div><div class="value" id="cnt">0</div></div>
</div>
<div id="status">Connecting…</div>
<script>
var times=[],vals=[];
var canvas=document.getElementById('chart');
var ctx=canvas.getContext('2d');

function resize(){canvas.width=canvas.clientWidth;canvas.height=canvas.clientHeight}
window.addEventListener('resize',resize);resize();

function draw(){
  var W=canvas.width,H=canvas.height,pad=40;
  ctx.clearRect(0,0,W,H);
  if(vals.length<2)return;
  var mn=Math.min.apply(null,vals),mx=Math.max.apply(null,vals);
  if(mn===mx){mn-=50;mx+=50}
  var rng=mx-mn;mn-=rng*.05;mx+=rng*.05;rng=mx-mn;
  // grid
  ctx.strokeStyle='#2a2a4a';ctx.lineWidth=1;
  for(var g=0;g<5;g++){
    var gy=pad+(H-2*pad)*g/4;
    ctx.beginPath();ctx.moveTo(pad,gy);ctx.lineTo(W-10,gy);ctx.stroke();
    ctx.fillStyle='#888';ctx.font='11px sans-serif';
    ctx.fillText(Math.round(mx-rng*g/4)+' ppm',2,gy+4);
  }
  // line
  ctx.strokeStyle='#0ff';ctx.lineWidth=2;ctx.beginPath();
  for(var i=0;i<vals.length;i++){
    var x=pad+(W-pad-10)*i/(vals.length-1);
    var y=pad+(H-2*pad)*(1-(vals[i]-mn)/rng);
    if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  }
  ctx.stroke();
  // time labels
  ctx.fillStyle='#888';ctx.font='10px sans-serif';
  var step=Math.max(1,Math.floor(times.length/6));
  for(var i=0;i<times.length;i+=step){
    var x=pad+(W-pad-10)*i/(vals.length-1);
    ctx.fillText(times[i].substring(11,19),x-20,H-4);
  }
}

function poll(){
  fetch('/data').then(function(r){return r.json()}).then(function(d){
    times=d.t;vals=d.v;
    document.getElementById('status').textContent='Last update: '+new Date().toLocaleTimeString();
    if(vals.length){
      document.getElementById('cur').textContent=vals[vals.length-1]+' ppm';
      document.getElementById('mn').textContent=Math.min.apply(null,vals)+' ppm';
      document.getElementById('mx').textContent=Math.max.apply(null,vals)+' ppm';
      document.getElementById('cnt').textContent=vals.length;
    }
    draw();
  }).catch(function(e){
    document.getElementById('status').textContent='Error: '+e;
  });
}
setInterval(poll,2000);
poll();
</script>
</body>
</html>
"""

_JSON_HDR = "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n"
_404 = "HTTP/1.0 404 Not Found\r\nConnection: close\r\n\r\nNot Found"


class APServer:
    """Create a WiFi access point and serve a live CO2 chart."""

    def __init__(self, ssid='CO2Monitor', password='co2monitor', port=80, wdt_obj=None):
        self.ssid = ssid
        self.password = password
        self.port = port
        self.wdt = wdt_obj
        self._times = []   # datetime strings
        self._values = []  # CO2 integer values
        self._srv = None
        self.ap = None
        self.ip = None

    # ---- Access Point ----

    def start_ap(self):
        """Activate the access point and return the IP address."""
        self.ap = network.WLAN(network.AP_IF)
        self.ap.config(essid=self.ssid, password=self.password)
        self.ap.active(True)

        # Wait for AP to become active
        for _ in range(20):
            if self.ap.active():
                break
            time.sleep(0.5)
            if self.wdt:
                self.wdt.feed()

        self.ip = self.ap.ifconfig()[0]
        print(f'AP active: SSID={self.ssid}  IP={self.ip}')
        return self.ip

    # ---- Data buffer ----

    def add_reading(self, dt_utc_str, co2_value):
        """Push a new CO2 reading into the ring buffer."""
        if co2_value is None:
            return
        self._times.append(dt_utc_str)
        self._values.append(co2_value)
        # Trim oldest when buffer is full
        if len(self._values) > _MAX_POINTS:
            self._times = self._times[-_MAX_POINTS:]
            self._values = self._values[-_MAX_POINTS:]

    # ---- HTTP server ----

    def start_server(self):
        """Bind the non-blocking HTTP server socket."""
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(('0.0.0.0', self.port))
        self._srv.listen(2)
        self._srv.setblocking(False)
        print(f'HTTP server listening on {self.ip}:{self.port}')

    def poll(self):
        """Check for an incoming HTTP request and respond (non-blocking)."""
        if self._srv is None:
            return
        try:
            cl, addr = self._srv.accept()
        except OSError:
            # No pending connection
            return

        try:
            cl.settimeout(2)
            request = cl.recv(1024).decode('utf-8')
            path = '/'
            if request:
                first_line = request.split('\r\n', 1)[0]
                parts = first_line.split(' ')
                if len(parts) >= 2:
                    path = parts[1]

            if path == '/data':
                payload = json.dumps({'t': self._times, 'v': self._values})
                cl.send(_JSON_HDR)
                # Send payload in chunks to be gentle on RAM
                mv = memoryview(payload.encode('utf-8'))
                i = 0
                while i < len(mv):
                    sent = cl.send(mv[i:i + 512])
                    i += sent
            elif path == '/' or path.startswith('/index'):
                cl.send(_HTML_PAGE)
            else:
                cl.send(_404)
        except Exception as e:
            print(f'HTTP error: {e}')
        finally:
            try:
                cl.close()
            except Exception:
                pass
