"""Ball-on-rim and backboard hits from real CC0 basketball recordings.
usage: python3 -I make_rim.py <rink_audio_dir> <sounds_dir>"""
import sys, os, subprocess, base64, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
src, out = sys.argv[1], sys.argv[2]; SR=22050
def load(p):
    sr,x=wavfile.read(p); assert sr==SR; return x.astype(np.float32)/32768.0 if x.dtype==np.int16 else x.astype(np.float32)
lp=lambda x,f,o=2:sosfilt(butter(o,f,"low",fs=SR,output="sos"),x)
hp=lambda x,f:sosfilt(butter(2,f,"high",fs=SR,output="sos"),x)
norm=lambda x,p=0.89:x/(np.abs(x).max()+1e-9)*p
def onset(x,thr=0.1): return int(np.argmax(np.abs(x)>thr*np.abs(x).max()))
def fade(x,a=0.001,b=0.06):
    x=x.copy(); na,nb=int(a*SR),int(b*SR); x[:na]*=np.linspace(0,1,na); x[-nb:]*=np.linspace(1,0,nb); return x
bang=load(os.path.join(src,"backboard_bang.wav")); bang=bang[max(0,onset(bang)-10):]
ball=load(os.path.join(out,"bounce1.wav")); ball=ball[max(0,onset(ball)-10):]
def hit(rattle_secs, bright, thump, seed):
    n=int((rattle_secs+0.12)*SR); t=np.arange(n)/SR
    r=bang[:n].copy() if len(bang)>=n else np.pad(bang,(0,n-len(bang)))
    r=lp(r,bright,4)*np.exp(-np.maximum(0,t-rattle_secs*0.6)/0.05)   # the real impact and rattle, softened, cut short
    b=np.zeros(n); bb=lp(ball,1500)[:n]; b[:len(bb)]=bb                 # the rubber "thump" of the ball itself
    y=norm(r)*0.8+norm(b)*thump
    return fade(norm(hp(y,70)),0.001,0.05)
S={"rim1":hit(0.16,2400,0.75,1),     # a soft "clunk" off the rim
   "rim2":hit(0.30,3200,0.6,2),      # a harder hit: you hear the hoop rattle a little
   "board":fade(norm(hp(lp(bang[:int(0.55*SR)],4200,4),60)),0.001,0.12)}   # the real ball-on-backboard bang
js={}
for k,v in S.items():
    wp=os.path.join(out,k+".wav"); wavfile.write(wp,SR,(np.clip(v,-1,1)*32767).astype(np.int16))
    mp=os.path.join(out,k+".mp3"); subprocess.run(["ffmpeg","-v","error","-y","-i",wp,"-ac","1","-b:a","48k",mp],check=True)
    js[k]=base64.b64encode(open(mp,"rb").read()).decode(); print(k,round(len(v)/SR,2),"s")
json.dump(js,open(os.path.join(out,"rim.json"),"w"))
