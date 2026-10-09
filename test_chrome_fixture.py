import sys,tempfile,threading,http.server
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser import chromium
from session import ChromeSession
with tempfile.TemporaryDirectory() as d:
 root=Path(d);(root/'index.html').write_text('<html><body style="background:blue"><h1>Fixture home</h1><a href="/next.html">Open next</a><a href="javascript:alert(1)">Unsafe scheme</a></body></html>');(root/'next.html').write_text('<html><body style="background:green"><h1>Next page verified</h1></body></html>')
 class Handler(http.server.SimpleHTTPRequestHandler):
  def __init__(self,*args,**kwargs):super().__init__(*args,directory=d,**kwargs)
  def log_message(self,*a):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
 try:
  with ChromeSession(chromium()) as chrome:
   profile=chrome.root;image=chrome.navigate(url+'/index.html');assert image.size==(960,2400);rows=chrome.links();assert len(rows)==1 and rows[0]['text']=='Open next';next_image=chrome.navigate(rows[0]['url']);assert 'Next page verified' in chrome.evaluate('document.body.innerText');assert chrome.location().endswith('/next.html');next_image.save('/tmp/browser-links-fixture.png');print('Real sandboxed Chrome HTTP link navigation and scheme rejection pass')
  assert not profile.exists();print('Temporary profile cleanup pass')
 finally:server.shutdown();server.server_close()
