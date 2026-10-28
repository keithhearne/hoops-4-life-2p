// ---------- sound: everything is made on the fly with the Web Audio API, no sound files ----------
const SND={ctx:null,on:true,master:null,noise:null,last:{}};
function audioInit(){   // phones only allow sound after the first tap, so this runs on every tap/key
  try{
    if(SND.ctx){ if(SND.ctx.state==="suspended") SND.ctx.resume(); return; }
    const AC=window.AudioContext||window.webkitAudioContext; if(!AC) return;
    SND.ctx=new AC(); SND.master=SND.ctx.createGain(); SND.master.gain.value=0.55; SND.master.connect(SND.ctx.destination);
    const n=SND.ctx.sampleRate, buf=SND.ctx.createBuffer(1,n,n), d=buf.getChannelData(0);
    for(let i=0;i<n;i++) d[i]=Math.random()*2-1;
    SND.noise=buf;
  }catch(_){}
}
// a single tone with a quick attack and a fall-off; f2 slides the pitch
function tone(f,dur,o){
  o=o||{}; const c=SND.ctx, t=c.currentTime+(o.at||0), osc=c.createOscillator(), g=c.createGain();
  osc.type=o.type||"sine"; osc.frequency.setValueAtTime(f,t);
  if(o.f2) osc.frequency.exponentialRampToValueAtTime(o.f2,t+dur);
  g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(o.vol||0.3,t+(o.atk||0.005));
  g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
  osc.connect(g); g.connect(o.dest||SND.master); osc.start(t); osc.stop(t+dur+0.05);
  return {osc,g,t};
}
// a burst of filtered noise; f2 sweeps the filter
function hiss(dur,o){
  o=o||{}; const c=SND.ctx, t=c.currentTime+(o.at||0), src=c.createBufferSource(), fl=c.createBiquadFilter(), g=c.createGain();
  src.buffer=SND.noise; src.loop=true;
  fl.type=o.filter||"bandpass"; fl.frequency.setValueAtTime(o.f||1000,t); fl.Q.value=o.q||1;
  if(o.f2) fl.frequency.exponentialRampToValueAtTime(o.f2,t+dur);
  g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(o.vol||0.3,t+(o.atk||0.005));
  if(o.hold) g.gain.setValueAtTime(o.vol||0.3,t+o.hold);
  g.gain.exponentialRampToValueAtTime(0.0001,t+dur);
  src.connect(fl); fl.connect(g); g.connect(o.dest||SND.master); src.start(t,Math.random()*0.5); src.stop(t+dur+0.05);
  return {src,fl,g,t};
}
const SFX={
  whistle(long){   // a referee's pea whistle: high note that warbles fast
    const dur=long?0.95:0.45, r=tone(2900,dur,{vol:0.22,atk:0.02,type:"sine"});
    const lfo=SND.ctx.createOscillator(), lg=SND.ctx.createGain(); lfo.frequency.value=32; lg.gain.value=170;
    lfo.connect(lg); lg.connect(r.osc.frequency); lfo.start(r.t); lfo.stop(r.t+dur+0.05);
    if(long) r.g.gain.setValueAtTime(0.22,r.t+dur-0.12);
    hiss(dur,{f:3200,q:4,vol:0.05,atk:0.02});
  },
  dribble(){ tone(130,0.09,{f2:60,vol:0.22}); hiss(0.03,{filter:"lowpass",f:500,vol:0.08}); },
  bounce(v){ const k=Math.min(1,v/700); if(k<0.08) return; tone(120,0.12,{f2:55,vol:0.3*k+0.03}); hiss(0.04,{filter:"lowpass",f:600,vol:0.12*k}); },
  rim(v){ const k=Math.min(1,(v||400)/600)*0.8+0.2;   // a metal clank: a few out-of-tune ringing notes
    for(const [f,a] of [[523,1],[1187,0.7],[1874,0.5],[2593,0.35]]) tone(f*(0.98+Math.random()*0.04),0.45,{vol:0.09*a*k});
    hiss(0.03,{f:3000,q:0.7,vol:0.12*k}); },
  board(v){ const k=Math.min(1,(v||400)/600)*0.8+0.2; tone(190,0.14,{f2:110,vol:0.28*k}); hiss(0.06,{f:900,q:1,vol:0.12*k}); },
  swish(){ hiss(0.38,{f:6500,f2:2200,q:0.9,vol:0.22,atk:0.03}); },
  cheer(size){ size=size||1;   // a crowd: noise shaped like voices, swelling up and dying away
    const dur=1.2+size*0.9;
    for(const [f,v] of [[520,0.12],[1150,0.1],[2300,0.06]]){
      const h=hiss(dur,{f,q:0.8,vol:v*size,atk:0.25,hold:dur*0.45});
      const lfo=SND.ctx.createOscillator(), lg=SND.ctx.createGain(); lfo.frequency.value=6+Math.random()*4; lg.gain.value=v*size*0.4;
      lfo.connect(lg); lg.connect(h.g.gain); lfo.start(h.t); lfo.stop(h.t+dur);
    }
  },
  groan(){ hiss(0.9,{f:420,f2:300,q:1.2,vol:0.09,atk:0.12}); },
  thunder(){   // a sharp crack, then a long low rumble
    hiss(0.12,{filter:"highpass",f:1800,vol:0.35,atk:0.002});
    const r=hiss(1.8,{filter:"lowpass",f:160,q:0.7,vol:0.55,atk:0.04,hold:0.3});
    const lfo=SND.ctx.createOscillator(), lg=SND.ctx.createGain(); lfo.frequency.value=9; lg.gain.value=0.18;
    lfo.connect(lg); lg.connect(r.g.gain); lfo.start(r.t); lfo.stop(r.t+1.8);
  },
  glass(big){   // shattering glass: a crash plus lots of little tinkles
    hiss(big?0.35:0.18,{filter:"highpass",f:2500,vol:big?0.35:0.2,atk:0.002});
    const n=big?34:12;
    for(let i=0;i<n;i++) tone(2800+Math.random()*4500,0.05+Math.random()*0.14,{vol:0.05+Math.random()*0.05,at:Math.random()*(big?0.7:0.35)});
  },
  crack(){ for(let i=0;i<7;i++) hiss(0.025,{filter:"highpass",f:2200,vol:0.18,at:i*0.02+Math.random()*0.01}); tone(1600,0.06,{vol:0.06}); },
  slam(){ SFX.rim(900); tone(95,0.25,{f2:45,vol:0.45}); hiss(0.08,{filter:"lowpass",f:800,vol:0.25}); },
  smack(){ hiss(0.06,{f:1300,q:1,vol:0.3}); tone(300,0.06,{f2:180,vol:0.22}); },
  swipe(){ hiss(0.16,{f:700,f2:2600,q:1.4,vol:0.16,atk:0.02}); },
  squeak(){ tone(2300,0.11,{f2:3100,vol:0.07,type:"triangle"}); },
  tick(){ tone(1500,0.06,{vol:0.13}); tone(2250,0.05,{vol:0.07,at:0.01}); },
  click(){ tone(900,0.03,{vol:0.12}); }
};
function play(name,arg){
  if(!SND.on||!SND.ctx||SND.ctx.state!=="running") return;
  const now=performance.now(); if(now-(SND.last[name]||0)<45) return;   // the same sound can't stack up in one moment
  SND.last[name]=now;
  try{ SFX[name](arg); }catch(_){}
}
