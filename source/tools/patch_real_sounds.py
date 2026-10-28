import sys
f, data_js = sys.argv[1], sys.argv[2]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

def cut(a_marker, b_marker, new):
    global s
    a = s.index(a_marker); b = s.index(b_marker, a)
    s = s[:a] + new + s[b:]

# the recordings ride along in their own script tag, ahead of the game
once("<script>\n", "<script>\n" + open(data_js).read() + "</script>\n<script>\n")

once("// ---------- sound: everything is made on the fly with the Web Audio API, no sound files ----------\nconst SND={ctx:null,on:true,master:null,noise:null,last:{}};",
     "// ---------- sound: real recordings (CC0, from Freesound) for the crowd, whistle, ball and rim; little synth effects for the rest ----------\nconst SND={ctx:null,on:true,master:null,noise:null,last:{},buf:{}};")

# a soft limiter on the master so big moments never clip; then decode the recordings
once("""    SND.ctx=new AC(); SND.master=SND.ctx.createGain(); SND.master.gain.value=0.55; SND.master.connect(SND.ctx.destination);""",
     """    SND.ctx=new AC(); SND.master=SND.ctx.createGain(); SND.master.gain.value=0.55;
    const lim=SND.ctx.createDynamicsCompressor(); lim.threshold.value=-8; lim.knee.value=6; lim.ratio.value=12; lim.attack.value=0.003; lim.release.value=0.2;
    SND.master.connect(lim); lim.connect(SND.ctx.destination);
    loadSamples();""")

cut("const SFX={", "  groan(){", r'''function loadSamples(){
  if(typeof SND_DATA==="undefined") return;
  for(const k in SND_DATA){
    try{
      const bin=atob(SND_DATA[k]), bytes=new Uint8Array(bin.length);
      for(let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
      const ok=b=>{SND.buf[k]=b;}, p=SND.ctx.decodeAudioData(bytes.buffer,ok,()=>{});
      if(p && p.catch) p.catch(()=>{});
    }catch(_){}
  }
}
// play a recording: vol, rate (pitch/speed), at (delay), off (start offset), dur (fade out by then)
function sample(name,o){
  o=o||{}; const b=SND.buf[name]; if(!b) return null;
  const c=SND.ctx, t=c.currentTime+(o.at||0), src=c.createBufferSource(), g=c.createGain(), v=o.vol==null?1:o.vol;
  src.buffer=b; src.playbackRate.value=o.rate||1;
  g.gain.setValueAtTime(v,t);
  if(o.dur){ const end=t+o.dur, fd=Math.min(0.9,o.dur*0.35); g.gain.setValueAtTime(v,end-fd); g.gain.linearRampToValueAtTime(0.0001,end); src.stop(end+0.05); }
  src.connect(g); g.connect(o.dest||SND.master); src.start(t,o.off||0);
  return {src,g,t};
}
const vary=(a)=>1+(Math.random()*2-1)*a;   // a touch of random pitch so repeats don't sound copy-pasted
const SFX={
  whistle(long){   // a real referee's pea whistle in a gym; game over gets two blasts
    sample("whistle",{vol:0.75,rate:vary(0.015)});
    if(long) sample("whistle",{vol:0.85,rate:0.985,at:0.42});
  },
  dribble(){ sample("bounce"+(1+Math.floor(Math.random()*3)),{vol:0.55,rate:vary(0.04)}); },
  bounce(v){ const k=Math.min(1,v/700); if(k<0.08) return;
    sample("bounce"+(1+Math.floor(Math.random()*3)),{vol:0.15+0.7*k,rate:vary(0.04)}); },
  rim(v){ const k=Math.min(1,(v||400)/600);   // ball on the rim: a rubber thump with a short, choked clank
    sample(k>0.55?"rim2":"rim1",{vol:0.3+0.55*k,rate:vary(0.05)}); },
  board(v){ const k=Math.min(1,(v||400)/600); sample("board",{vol:0.3+0.6*k,rate:vary(0.04)}); },
  swish(){ hiss(0.38,{f:6500,f2:2200,q:0.9,vol:0.2,atk:0.03}); },
  cheer(size){   // a real arena crowd: bigger plays get a louder, longer, fuller roar
    size=size||1;
    const big=size>=1.35, mid=size>=1.1;
    const dur=big?5.6:(mid?4:2.6);
    sample("cheer",{vol:big?0.95:(mid?0.75:0.45),dur,rate:vary(0.02),off:mid?0:0.4});
    sample("applause",{vol:big?0.55:(mid?0.45:0.55),dur:dur+0.4,at:0.25,rate:vary(0.02)});
    if(size>=1.6) sample("cheer",{vol:0.5,dur:dur-0.6,at:0.35,rate:1.05,off:0.8});   // a second section of the stands joins in
  },
''')

once("  groan(){ hiss(0.9,{f:420,f2:300,q:1.2,vol:0.09,atk:0.12}); },",
     "  groan(){ sample(\"ooh\",{vol:0.4,dur:2.4,rate:vary(0.03)}); },   // the crowd goes \"ooooh\"\n"
     "  gasp(){ sample(\"gasp\",{vol:0.35,dur:1.6,rate:vary(0.03)}); },")
once("  slam(){ SFX.rim(900); tone(95,0.25,{f2:45,vol:0.45}); hiss(0.08,{filter:\"lowpass\",f:800,vol:0.25}); },",
     "  slam(){ sample(\"rim2\",{vol:1,rate:0.92}); tone(95,0.25,{f2:45,vol:0.4}); },")

# the old home-made clapping track is gone
cut("let applause=null;\nfunction applauseBuf(){", "// a low murmur", "")

# the arena murmur: a real crowd loop
once("""      const c=SND.ctx, src=c.createBufferSource(), fl=c.createBiquadFilter(), fl2=c.createBiquadFilter(), g=c.createGain();
      src.buffer=SND.noise; src.loop=true; fl.type="bandpass"; fl.frequency.value=500; fl.Q.value=0.6; fl2.type="lowpass"; fl2.frequency.value=1400;
      g.gain.setValueAtTime(0.0001,c.currentTime); g.gain.exponentialRampToValueAtTime(0.035,c.currentTime+1.2);
      const lfo=c.createOscillator(), lg=c.createGain(); lfo.frequency.value=0.25; lg.gain.value=0.01; lfo.connect(lg); lg.connect(g.gain);
      src.connect(fl); fl.connect(fl2); fl2.connect(g); g.connect(SND.master); src.start(); lfo.start();
      amb={src,lfo,g};""",
     """      const c=SND.ctx, b=SND.buf.murmur; if(!b) return;
      const src=c.createBufferSource(), g=c.createGain();
      src.buffer=b; src.loop=true; src.loopStart=0.1; src.loopEnd=b.duration-0.1;
      g.gain.setValueAtTime(0.0001,c.currentTime); g.gain.exponentialRampToValueAtTime(0.16,c.currentTime+1.5);
      src.connect(g); g.connect(SND.master); src.start(0,0.1);
      amb={src,g};""")
once("    try{const t=SND.ctx.currentTime; amb.g.gain.setTargetAtTime(0.0001,t,0.2); amb.src.stop(t+1); amb.lfo.stop(t+1);}catch(_){}",
     "    try{const t=SND.ctx.currentTime; amb.g.gain.setTargetAtTime(0.0001,t,0.2); amb.src.stop(t+1);}catch(_){}")

# a block on a shot gets a gasp from the crowd
once("""  play("smack");\n""", """  play("smack"); play("gasp");\n""")

open(f, "w").write(s)
print("patched")
