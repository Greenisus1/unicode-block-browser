#!/usr/bin/env python3
"""Webpage screenshots and HTTP/HTTPS link navigation as Unicode half-blocks."""
import argparse,curses,os,shutil,subprocess,tempfile,urllib.parse
from pathlib import Path
VERSION='1.1.0'
PALETTE=((0,0,0),(205,49,49),(13,188,121),(229,229,16),(36,114,200),(188,63,188),(17,168,205),(229,229,229))
def valid_url(value):
 if not isinstance(value,str) or len(value)>4096 or any(ord(c)<32 for c in value):raise ValueError('Use an HTTP/HTTPS URL, maximum4096 characters.')
 parsed=urllib.parse.urlsplit(value)
 if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username is not None or parsed.password is not None:raise ValueError('Use HTTP/HTTPS without embedded credentials.')
 return value
def chromium():
 return next((p for name in ('chromium','chromium-browser','google-chrome') if (p:=shutil.which(name))),None)
def render_page(url,target,timeout=25):
 valid_url(url);binary=chromium()
 if not binary:raise RuntimeError('Chromium missing. Install chromium through your distribution.')
 with tempfile.TemporaryDirectory(prefix='block-browser-') as profile:
  command=[binary,'--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-extensions','--hide-scrollbars','--window-size=960,2400','--virtual-time-budget=1500','--user-data-dir='+profile,'--screenshot='+str(target),url]
  # Never disable Chromium sandbox. Fresh profile cannot use the owner's saved cookies.
  try:result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
  except subprocess.TimeoutExpired as exc:raise RuntimeError('Page timed out after25 seconds.') from exc
  if result.returncode or not Path(target).is_file():raise RuntimeError('Chromium failed; sandbox must remain enabled. Try as a non-root account.')
  from PIL import Image
  image=Image.open(target).convert('RGB');image.load();return image

def nearest(rgb):return min(range(8),key=lambda i:sum((rgb[n]-PALETTE[i][n])**2 for n in range(3)))
def blocks(image,width):
 width=max(1,min(240,width));height=max(1,round(image.height*width/image.width))
 resized=image.resize((width,height));return [[nearest(resized.getpixel((x,y))) for x in range(width)] for y in range(height)]
def put(s,y,x,v,attr=0):
 h,w=s.getmaxyx()
 if 0<=y<h and 0<=x<w-1:
  try:s.addnstr(y,x,v,w-x-1,attr)
  except curses.error:pass
def prompt(s,current):
 h,w=s.getmaxyx();s.move(h-2,0);s.clrtoeol();put(s,h-2,0,'URL: ');curses.echo();curses.curs_set(1)
 try:return s.getstr(h-2,5,min(4096,max(1,w-7))).decode('utf-8').strip()
 finally:curses.noecho();curses.curs_set(0)
def choose_link(s,rows):
 if not rows:
  s.erase();put(s,2,1,'No HTTP/HTTPS links found. Press any key.');s.refresh();s.getch();return None
 n=0
 while True:
  s.erase();h,w=s.getmaxyx();page=max(1,h-5);offset=max(0,n-page+1)
  put(s,0,1,'Choose link: Up/Down, Enter open, Esc cancel',curses.A_BOLD)
  for i,row in enumerate(rows[offset:offset+page],offset):put(s,2+i-offset,1,str(i+1)+'. '+row['text'],curses.A_REVERSE if i==n else 0)
  put(s,h-2,1,rows[n]['url']);s.refresh();k=s.getch()
  if k==27:return None
  if k in (10,13):return rows[n]['url']
  if k==curses.KEY_DOWN:n=min(len(rows)-1,n+1)
  elif k==curses.KEY_UP:n=max(0,n-1)
  elif k==curses.KEY_NPAGE:n=min(len(rows)-1,n+page)
  elif k==curses.KEY_PPAGE:n=max(0,n-page)
def run(s,url):
 s.keypad(True);curses.curs_set(0);colors=curses.has_colors()
 if colors:
  curses.start_color()
  colors=curses.COLORS>=8 and curses.COLOR_PAIRS>=65
  if colors:
   for fg in range(8):
    for bg in range(8):curses.init_pair(1+fg*8+bg,fg,bg)
 image=None;pixels=[];offset=0;message='U enter URL | temporary profile, no saved login';lastw=0
 from session import ChromeSession
 with ChromeSession(chromium()) as browser:
  if url:
   put(s,3,0,'Rendering webpage, up to25 seconds...');s.refresh()
   try:image=browser.navigate(url);url=browser.location();message='Snapshot, first2400 vertical pixels. U URL; R refresh. L choose link. No forms.'
   except (ValueError,RuntimeError,ImportError,OSError) as exc:message=str(exc)
  while True:
   h,w=s.getmaxyx();s.erase();put(s,0,0,'UNICODE BLOCK BROWSER '+VERSION+' - screenshot + links',curses.A_BOLD);put(s,1,0,url or 'No page open');put(s,h-3,0,message);put(s,h-1,0,'U URL | Up/Down/PgUp/PgDn scroll | L links | R reload | Esc/Q exit')
   if h<12 or w<40:put(s,3,0,'Resize to40x12.')
   elif image is not None:
    if w!=lastw:pixels=blocks(image,w-1);lastw=w
    visible=max(1,h-6);offset=max(0,min(offset,max(0,(len(pixels)+1)//2-visible)))
    for row in range(visible):
     y=(offset+row)*2
     if y>=len(pixels):break
     for x,top in enumerate(pixels[y]):
      bottom=pixels[min(y+1,len(pixels)-1)][x]
      attr=curses.color_pair(1+top*8+bottom) if colors else 0
      mark='▀' if colors else '█' if top<4 else '░'
      put(s,3+row,x,mark,attr)
   s.refresh();key=s.getch()
   if key in (27,ord('q'),ord('Q')):return
   if key in (curses.KEY_DOWN,ord('j')):offset+=2
   elif key in (curses.KEY_UP,ord('k')):offset-=2
   elif key==curses.KEY_NPAGE:offset+=max(1,h-6)
   elif key==curses.KEY_PPAGE:offset-=max(1,h-6)
   elif key in (ord('l'),ord('L')):
    try:
     rows=browser.links();candidate=choose_link(s,rows)
     if candidate:
      image=browser.navigate(candidate);url=browser.location();offset=0;lastw=0;message='Link opened. L links; U URL. No forms.'
    except Exception as exc:message=str(exc)
   elif key in (ord('u'),ord('U'),ord('r'),ord('R')):
    if key in (ord('u'),ord('U')):
     candidate=prompt(s,url)
     if not candidate:continue
    else:candidate=url
    try:
     valid_url(candidate);put(s,h-3,0,'Rendering webpage, up to25 seconds...');s.refresh();new=browser.navigate(candidate);image=new;url=browser.location();offset=0;lastw=0;message='Snapshot, first2400 vertical pixels. U URL; R refresh. L choose link. No forms.'
    except (ValueError,RuntimeError,ImportError,OSError) as exc:message=str(exc)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('url',nargs='?',default='');p.add_argument('--version',action='store_true');a=p.parse_args()
 if a.version:print(VERSION);return 0
 if a.url:
  try:valid_url(a.url)
  except ValueError as exc:print(exc);return 1
 if not os.isatty(0) or not os.isatty(1):print('Needs an interactive Unicode terminal.');return 1
 try:
  import PIL
  if not chromium():raise RuntimeError('Chromium is required. Install it through your distribution.')
  curses.wrapper(run,a.url);return 0
 except (RuntimeError,ImportError,curses.error) as exc:print('Browser unavailable:',exc);return 1
 except KeyboardInterrupt:return 0
if __name__=='__main__':raise SystemExit(main())
