"""Temporary local sandboxed Chrome session. HTTP/HTTPS link navigation only."""
import base64,json,subprocess,tempfile,time,urllib.request,urllib.parse
from pathlib import Path
class ChromeSession:
 def __init__(self,binary):
  import websocket
  self.work=tempfile.TemporaryDirectory(prefix='block-browser-session-');self.root=Path(self.work.name);self.id=0
  self.proc=subprocess.Popen([binary,'--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-extensions','--hide-scrollbars','--remote-debugging-port=0','--user-data-dir='+str(self.root),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  try:
   deadline=time.monotonic()+15;portfile=self.root/'DevToolsActivePort'
   while not portfile.exists():
    if self.proc.poll() is not None:raise RuntimeError('Chromium stopped. Keep sandbox enabled and run non-root.')
    if time.monotonic()>deadline:raise RuntimeError('Chromium did not start within15 seconds.')
    time.sleep(.05)
   port=int(portfile.read_text().splitlines()[0])
   with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/json/list',timeout=5) as r:tabs=json.load(r)
   tab=next(x for x in tabs if x.get('type')=='page')
   self.ws=websocket.create_connection(tab['webSocketDebuggerUrl'],timeout=25,suppress_origin=True)
   self.command('Page.enable');self.command('Runtime.enable');self.command('Emulation.setDeviceMetricsOverride',{'width':960,'height':2400,'deviceScaleFactor':1,'mobile':False})
  except BaseException:self.close();raise
 def command(self,method,params=None):
  self.id+=1;ident=self.id;self.ws.send(json.dumps({'id':ident,'method':method,'params':params or {}}))
  deadline=time.monotonic()+25
  while time.monotonic()<deadline:
   result=json.loads(self.ws.recv())
   if result.get('id')==ident:
    if 'error' in result:raise RuntimeError('Chrome: '+result['error'].get('message','command failed'))
    return result.get('result',{})
  raise RuntimeError('Chrome command timed out')
 def navigate(self,url):
  from browser import valid_url
  valid_url(url);r=self.command('Page.navigate',{'url':url})
  if r.get('errorText'):raise RuntimeError(r['errorText'])
  deadline=time.monotonic()+15
  while time.monotonic()<deadline:
   state=self.evaluate('document.readyState')
   if state=='complete':break
   time.sleep(.1)
  # Allow one bounded render settling period; no automatic refreshing.
  time.sleep(.4)
  return self.capture()
 def evaluate(self,expression):
  r=self.command('Runtime.evaluate',{'expression':expression,'returnByValue':True})
  if 'exceptionDetails' in r:raise RuntimeError('Page inspection failed')
  return r.get('result',{}).get('value')
 def capture(self):
  from PIL import Image
  import io
  data=self.command('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']
  image=Image.open(io.BytesIO(base64.b64decode(data))).convert('RGB');image.load();return image
 def location(self):
  from browser import valid_url
  return valid_url(self.evaluate('location.href'))
 def links(self):
  rows=self.evaluate("JSON.stringify(Array.from(document.querySelectorAll('a[href]')).map(a=>({text:(a.innerText||a.getAttribute('aria-label')||a.href).trim(),url:a.href})).filter(a=>a.text).slice(0,500))")
  out=[]
  from browser import valid_url
  for row in json.loads(rows or '[]'):
   try:valid_url(row['url'])
   except ValueError:continue
   row['text']=''.join(c for c in row['text'] if c.isprintable())[:200];out.append(row)
  return out
 def close(self):
  if hasattr(self,'ws'):
   try:self.ws.close()
   except Exception:pass
  if hasattr(self,'proc'):
   self.proc.terminate()
   try:self.proc.wait(timeout=3)
   except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
  if hasattr(self,'work'):self.work.cleanup()
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
