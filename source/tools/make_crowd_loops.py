"""Crowd bed loops from CC0 recordings (Freesound via RinkGM credits).
usage: python3 -I make_crowd_loops.py <src_audio_dir> <out_dir>"""
import sys, os, subprocess, base64, json
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True); SR=22050
def load(n):
    sr,x=wavfile.read(os.path.join(src,n+".wav")); assert sr==SR
    return x.astype(np.float32)/32768.0 if x.dtype==np.int16 else x.astype(np.float32)
lp=lambda x,f:sosfilt(butter(2,f,"low",fs=SR,output="sos"),x)
hp=lambda x,f:sosfilt(butter(2,f,"high",fs=SR,output="sos"),x)
def loudnorm(x,rms=0.12):   # match loudness (RMS), not peaks, so the layers mix evenly
    x=x-np.mean(x); r=np.sqrt(np.mean(x**2))+1e-9; y=x*rms/r; pk=np.abs(y).max()
    return y*(0.95/pk) if pk>0.95 else y
L={}
L["murmur"]=loudnorm(hp(load("crowd_murmur"),90))
r=lp(hp(load("arena_room"),60),2500); L["room"]=loudnorm(r[:int(6.6*SR)],0.10)   # a different length from the others, so the layers drift past each other
# the anticipation roar: a steady "wall" of crowd built from many short overlapping slices (grains) of a real
# cheer, each from a random spot and very slightly re-pitched, so no single shout, clap or whistle repeats in a
# pattern and the whole thing has no swell that comes round again
rng=np.random.default_rng(7)
c=load("crowd_cheer"); body=hp(c[int(0.9*SR):int(5.0*SR)],110)
OUT=int(14.0*SR); roar=np.zeros(OUT+SR); t=0
while t<OUT:
    g=int(rng.uniform(0.45,1.0)*SR); st=int(rng.uniform(0,len(body)-g*1.1))
    rate=rng.uniform(0.94,1.06); idx=st+np.arange(int(g))*rate
    grain=np.interp(idx,np.arange(len(body)),body)*np.hanning(int(g))*rng.uniform(0.7,1.0)
    roar[t:t+len(grain)]+=grain; t+=int(g/5)            # about five grains overlap at any moment
roar=roar[int(1.0*SR):OUT]   # skip the first second, before the grains have built up
roar=lp(roar,2800)                                       # soften it: claps and whistles lose their edge
env=np.sqrt(np.convolve(roar**2,np.ones(int(0.6*SR))/int(0.6*SR),"same"))+1e-4
roar=roar/np.maximum(env,np.median(env)*0.5)*np.median(env)   # even out any slow swells
L["anticip"]=loudnorm(roar)
js={}
for k,v in L.items():
    wp=os.path.join(out,"loop_"+k+".wav"); wavfile.write(wp,SR,(np.clip(v,-1,1)*32767).astype(np.int16))
    mp=os.path.join(out,"loop_"+k+".mp3"); subprocess.run(["ffmpeg","-v","error","-y","-i",wp,"-ac","1","-b:a","40k",mp],check=True)
    js[k]=base64.b64encode(open(mp,"rb").read()).decode(); print(k,round(len(v)/SR,2),"s",os.path.getsize(mp),"bytes")
json.dump(js,open(os.path.join(out,"loops.json"),"w"))

# ---- a celebration layer: the excited part of the cheer (yeahs, whistles) and real applause, as a steady loop ----
rng=np.random.default_rng(11)
def grains(srcs,secs,glen=(0.4,0.9),dens=5,rate=(0.95,1.05)):
    OUT=int((secs+1)*SR); y=np.zeros(OUT+2*SR); t=0
    while t<OUT:
        src=srcs[rng.integers(len(srcs))]; g=int(rng.uniform(*glen)*SR); st=int(rng.uniform(0,len(src)-g*1.1))
        r=rng.uniform(*rate); gr=np.interp(st+np.arange(g)*r,np.arange(len(src)),src)*np.hanning(g)*rng.uniform(0.7,1.0)
        y[t:t+g]+=gr; t+=int(g/dens)
    y=y[int(1.0*SR):int(1.0*SR)+int(secs*SR)]
    env=np.sqrt(np.convolve(y**2,np.ones(int(0.6*SR))/int(0.6*SR),"same"))+1e-4
    return y/np.maximum(env,np.median(env)*0.5)*np.median(env)
cheer_all=hp(load("crowd_cheer")[int(0.3*SR):int(5.4*SR)],120); clap=hp(load("crowd_applause")[int(0.3*SR):int(4.2*SR)],150)
L["celeb"]=loudnorm(lp(grains([cheer_all,cheer_all,clap],11.0,(0.5,1.1),4),6000))

# ---- "DE-FENSE!" — an arena organ (stacked sine "drawbars" with a spinning-speaker wobble), the crowd shouting the
# two syllables (the real cheer recording shaped into short shouts) and two stomps, four times round ----
def organ(freq,dur,vol=1.0):
    n=int(dur*SR); t=np.arange(n)/SR; y=np.zeros(n)
    for h,a in [(0.5,0.8),(1,1.0),(1.5,0.6),(2,0.5),(3,0.25),(4,0.18)]:    # drawbars: sub, fundamental, fifth, octaves
        y+=a*np.sin(2*np.pi*freq*h*t*(1+0.0025*np.sin(2*np.pi*6.6*t)))
    y+=0.5*np.sin(2*np.pi*freq*3*t)*np.exp(-t/0.12)                      # the organ's click of "percussion" at the start
    y*=1+0.18*np.sin(2*np.pi*6.6*t+1.0)                                   # spinning speaker
    env=np.minimum(1,t/0.008)*np.minimum(1,(dur-t)/0.04); y=np.tanh(1.6*y/3)*env*vol
    return y
def stomp(dur=0.35):
    n=int(dur*SR); t=np.arange(n)/SR; body=np.sin(2*np.pi*(70*np.exp(-t/0.12)+45)*t)*np.exp(-t/0.09)
    noise=lp(rng.standard_normal(n),900)*np.exp(-t/0.05)*0.6
    return (body+noise)*0.9
def shout(dur,ess=False):   # many voices shouting together: a slice of the crowd recording with a sharp start
    n=int(dur*SR); st=int(rng.uniform(0.5,3.5)*SR); y=c[st:st+n].copy() if len(c)>st+n else np.zeros(n)
    y=sosfilt(butter(2,[350,2600],"band",fs=SR,output="sos"),y)
    t=np.arange(n)/SR; env=np.minimum(1,t/0.03)*np.exp(-np.maximum(0,t-dur*0.55)/0.06)
    y=y*env
    if ess: s=hp(rng.standard_normal(n),3500)*0.25*np.exp(-((t-dur*0.8)/0.05)**2); y=y/np.abs(y).max()+s   # the "s" of "fense"
    return y/(np.abs(y).max()+1e-9)
c=load("crowd_cheer")
BEAT=0.5; bar=int(4*BEAT*SR); song=np.zeros(bar*4+SR)
G4,E4=392.0,329.6
for k in range(4):
    b0=k*bar
    for off,f,d,word,ess in [(0,G4,0.32,0.30,False),(BEAT,E4,0.42,0.38,True)]:
        i=b0+int(off*SR); o=organ(f,d,0.55); song[i:i+len(o)]+=o
        sh=shout(word,ess)*0.75; song[i:i+len(sh)]+=sh
    for off in (2*BEAT,3*BEAT):
        i=b0+int(off*SR); s_=stomp(); song[i:i+len(s_)]+=s_
song=lp(hp(song,50),7000)
# a touch of arena echo
ir=rng.standard_normal(int(0.6*SR))*np.exp(-np.arange(int(0.6*SR))/SR/0.15); ir=lp(ir,3000); ir[0]=0
wet=np.convolve(song,ir)[:len(song)]; wet*=0.25*np.abs(song).max()/(np.abs(wet).max()+1e-9)
song=song+wet; fade=int(0.3*SR); song[-fade:]*=np.linspace(1,0,fade)
song=song/np.abs(song).max()*0.89
for k in ["celeb","defense"]:
    v=L[k] if k in L else song
    wp=os.path.join(out,"loop_"+k+".wav"); wavfile.write(wp,SR,(np.clip(v,-1,1)*32767).astype(np.int16))
    mp=os.path.join(out,"loop_"+k+".mp3"); subprocess.run(["ffmpeg","-v","error","-y","-i",wp,"-ac","1","-b:a","48k",mp],check=True)
    js[k]=base64.b64encode(open(mp,"rb").read()).decode(); print(k,round(len(v)/SR,2),"s",os.path.getsize(mp),"bytes")
json.dump(js,open(os.path.join(out,"loops.json"),"w"))
