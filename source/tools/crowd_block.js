// ---------- the crowd: three looping layers that follow the play ----------
// Layer 1 murmur (people talking), layer 2 the big hall's room tone, layer 3 an excited roar.
// All three start on the same audio-clock time and loop for the whole game. Every frame the game works out
// how close the ball is to the hoop it's heading for, and the layers' volume, pitch (playback rate) and
// brightness glide to match, so the crowd is quiet at centre court and builds as you drive to the basket.
const LOOP_KEYS=["murmur","room","anticip","celeb"];
// a seamless loop made in the browser: trim the ends (MP3 adds a little silence there),
// then cross-fade the tail into the head with an equal-power fade, so the join can't click
function makeLoop(b,trim,xf){
  const sr=b.sampleRate, s0=Math.floor(trim*sr), n=b.length-2*s0, x=Math.floor(xf*sr), len=n-x;
  const out=SND.ctx.createBuffer(1,len,sr), o=out.getChannelData(0), d=b.getChannelData(0);
  for(let i=0;i<len;i++) o[i]=d[s0+i];
  for(let i=0;i<x;i++){const t=i/x; o[i]=d[s0+i]*Math.sin(t*Math.PI/2)+d[s0+len+i]*Math.cos(t*Math.PI/2);}
  return out;
}
const CROWD={nodes:null,level:0,target:0,boost:0,deflate:0,lastAp:-1};
// The mix at a given level (0 = centre court, 1 = at the rim). Volumes are set in decibels and follow a smooth
// S-curve (smootherstep), because ears hear loudness in decibels: equal steps in dB sound like an even build.
// The build is a long exponential: from the centre-court floor it creeps up past the 3-point line, then
// climbs more and more steeply into the basket. (k sets how late the climb comes; bigger = later.)
const dB=v=>Math.pow(10,v/20), CROWD_K=2.0;
function ease(u){ const v=clamp((u-CROWD_FLOOR)/(1-CROWD_FLOOR),0,1); return (Math.exp(CROWD_K*v)-1)/(Math.exp(CROWD_K)-1); }
const CROWD_MIX={
  room:   L=>dB(-26),
  murmur: L=>dB(-30+9*ease(L)),           // people talking: always there, a little busier near the basket
  anticip:L=>dB(-26+18*ease(L)),          // the roar: a soft undertone at centre court, the main build near the rim
  rateM:  L=>0.98+0.05*ease(L),
  rateA:  L=>0.96+0.08*ease(L),
  bright: L=>1500+4500*ease(L)
};
function crowdStart(){
  const c=SND.ctx; if(!c || CROWD.nodes || !SND.loop || !SND.loop.murmur || !SND.loop.room || !SND.loop.anticip) return;
  const t0=c.currentTime+0.05, L=CROWD.level=0;
  const out=c.createGain(); glideInit(out.gain,0,t0); glide(out.gain,1,t0,1.5); out.connect(SND.master);
  const N={out,t0}, src=k=>{const s=c.createBufferSource(); s.buffer=SND.loop[k]; s.loop=true; return s;};
  N.room=src("room"); N.mur=src("murmur"); N.ant=src("anticip"); N.cel=src("celeb");
  N.gRoom=c.createGain(); N.gMur=c.createGain(); N.gAnt=c.createGain(); N.lp=c.createBiquadFilter();
  N.lp.type="lowpass"; N.lp.Q.value=0.5;
  glideInit(N.gRoom.gain,CROWD_MIX.room(L),t0); glideInit(N.gMur.gain,CROWD_MIX.murmur(L),t0); glideInit(N.gAnt.gain,CROWD_MIX.anticip(L),t0);
  glideInit(N.mur.playbackRate,CROWD_MIX.rateM(L),t0); glideInit(N.ant.playbackRate,CROWD_MIX.rateA(L),t0);
  glideInit(N.lp.frequency,CROWD_MIX.bright(L),t0);
  N.room.connect(N.gRoom); N.gRoom.connect(out);
  N.mur.connect(N.gMur); N.gMur.connect(out);
  N.ant.connect(N.lp); N.lp.connect(N.gAnt); N.gAnt.connect(out);
  // the celebration layer (yeahs, whistles, applause) runs silently all game on the same clock, ready to swell in
  N.gCel=c.createGain(); N.gCel.gain.value=0; N.cel.connect(N.gCel); N.gCel.connect(out);
  // same clock, different starting points in each loop so the layers never line up the same way twice
  N.room.start(t0,Math.random()*SND.loop.room.duration);
  N.mur.start(t0,Math.random()*SND.loop.murmur.duration);
  N.ant.start(t0,Math.random()*SND.loop.anticip.duration);
  N.cel.start(t0,Math.random()*SND.loop.celeb.duration);
  CROWD.nodes=N; CROWD.lastAp=-1; CROWD.boost=0; CROWD.deflate=0; CROWD.chantWait=12+Math.random()*15; CROWD.chant=null;
}
function crowdStop(){
  const N=CROWD.nodes; if(!N) return; CROWD.nodes=null;
  try{const t=SND.ctx.currentTime; glide(N.out.gain,0,t,0.6,true); const end=N.out.gain.__g.t+0.05;   // stop only once it's silent
    for(const s of [N.room,N.mur,N.ant,N.cel]) s.stop(end);}catch(_){}
  chantStop(0.15);
}
// glide an audio setting to a new value with a chain of straight ramps. Each ramp starts exactly where the
// last one ended (we remember where that was), so nothing is ever cancelled and the value can't jump.
// (Cancelling a ramp half-way and holding the value clicked in testing; this doesn't.)
function glideInit(param,v,t){ param.value=v; param.setValueAtTime(v,t); param.__g={t,v}; }
// after=true waits for the ramp already running to finish first (used to fade out after a fade-in);
// otherwise the new ramp always ends "secs" from now, so the sound never falls behind the game.
function glide(param,v,now,secs,after){
  const st=param.__g||(param.__g={t:0,v:param.value});
  if(now>st.t) param.setValueAtTime(st.v,now);   // the last ramp has finished: start the new one from its end value
  const T=after?Math.max(now,st.t)+secs:Math.max(now+secs,st.t+0.005);
  param.linearRampToValueAtTime(v,T); st.t=T; st.v=v;
}
// how close the play is to the basket: 0 at centre court, 1 at the rim.
// The distance (in canvas pixels) between the ball and the hoop it's heading for, as a fraction of the way from
// centre court to the rim. It never goes below the level a third of the way from centre court to the 3-point
// line, so there's always a soft undertone of crowd.
const CROWD_FAR=Math.hypot(HALF-RR.x,285-RR.y), CROWD_NEAR=60;
const crowdU=dist=>clamp((CROWD_FAR-dist)/(CROWD_FAR-CROWD_NEAR),0,1);
const CROWD_FLOOR=crowdU(Math.hypot(HALF+(THREE-HALF)/3-RR.x,285-RR.y));
function crowdProximity(){
  let x,y,hoop;
  if(tip.on) return CROWD_FLOOR;
  if(ball.state==="held" && owner){ x=ball.x; y=ball.y; hoop=owner===p?RR:RL; }
  else if(ball.state==="flight"){ x=ball.x; y=ball.y; hoop=ball.shooter===p?RR:RL; }
  else if(ball.state==="made"||ball.state==="drop") return 1;   // stays at full while the ball drops through the net
  else return Math.max(CROWD_FLOOR,0.3);   // loose ball: a buzz while someone goes for it
  return Math.max(CROWD_FLOOR,crowdU(Math.hypot(x-hoop.x,y-hoop.y)));
}
// called from update() every frame
function crowdUpdate(dt){
  const c=SND.ctx, want=SND.on && c && c.state==="running" && (screen==="play"||screen==="pause"||screen==="over") && cpuOn;
  if(!want){ if(CROWD.nodes) crowdStop(); return; }
  if(!CROWD.nodes){ crowdStart(); if(!CROWD.nodes) return; }
  let target = screen==="play" ? crowdProximity() : (screen==="pause"?0.05:0.3);
  if(CROWD.deflate>0){ CROWD.deflate-=dt; target*=0.35; }   // a miss: the air goes out of the crowd
  // the chant: 2-4 seconds after the opponent gets the ball (on about 3 of every 4 of his possessions),
  // and it fades as soon as you get the ball back
  const defending=screen==="play" && !tip.on && (owner===d || (ball.state==="flight"&&ball.shooter===d));
  if(defending && !CROWD.wasDef){ CROWD.chantWait=2+Math.random()*2; CROWD.chantArmed=Math.random()<0.75; }
  CROWD.wasDef=defending;
  if(defending && CROWD.chantArmed){ CROWD.chantWait-=dt; if(CROWD.chantWait<=0){ chantStart(); CROWD.chantArmed=false; } }
  else if(!defending && CROWD.chant && owner===p) chantStop(0.3);
  // smooth in JavaScript first (time constant about 0.35 s), then hand the audio thread short straight ramps
  CROWD.level+=(target-CROWD.level)*Math.min(1,dt/(target>CROWD.level?0.7:0.35));   // builds slowly, settles faster
  const now=c.currentTime;
  if(now-CROWD.lastAp<0.04) return;   // about 25 updates a second is plenty and keeps the audio thread calm
  CROWD.lastAp=now;
  const N=CROWD.nodes, L=CROWD.level, ramp=0.06;
  glide(N.gMur.gain,CROWD_MIX.murmur(L),now,ramp);
  glide(N.gAnt.gain,CROWD_MIX.anticip(L),now,ramp);
  glide(N.mur.playbackRate,CROWD_MIX.rateM(L),now,ramp);
  glide(N.ant.playbackRate,CROWD_MIX.rateA(L),now,ramp);
  glide(N.lp.frequency,CROWD_MIX.bright(L),now,ramp);
}
// a basket: the roar swells under the cheer and applause, then settles
// Each basket gets its own volume control on the roar, with its whole swell planned in one go, so a second
// basket never has to interrupt the first one; they simply add up. The rise is a fast exponential approach
// (most of the way there in about a quarter of a second), then it holds and dies away the same way.
function crowdCelebrate(size){
  const N=CROWD.nodes; if(!N) return;
  const c=SND.ctx, now=c.currentTime+0.01, peak=Math.min(0.12,0.03+0.04*size), hold=0.35*size, g=c.createGain();
  g.gain.value=0;   // a new gain starts at 1: silence it before it's connected, or it blips for a moment
  g.gain.setValueAtTime(0,now); g.gain.setTargetAtTime(peak,now,0.08);   // quick exponential rise
  g.gain.setTargetAtTime(0,now+0.3+hold,0.8);                              // then a slow exponential fade
  N.ant.connect(g); g.connect(N.out);   // the swell rides on the same roar, without the muffling filter
  // and the celebration layer comes in: a fast exponential rise, held, then a long fade
  const cg=N.gCel.gain, cpk=Math.min(0.14,0.03+0.045*size);
  // (cancelling is safe here: target curves always start from wherever the value is right now)
  cg.cancelScheduledValues(now); cg.setTargetAtTime(cpk,now,0.09); cg.setTargetAtTime(0,now+0.5+hold,1.1);
  CROWD.deflate=0; chantStop(0.4);
}
function crowdDeflate(){ CROWD.deflate=1.6; }
// "DE-FENSE!" — now and then, while the computer has the ball, the home crowd starts the chant
function chantStart(){
  const N=CROWD.nodes, b=SND.buf.defense; if(!N||!b||CROWD.chant) return;
  const c=SND.ctx, t=c.currentTime+0.02, s=c.createBufferSource(), g=c.createGain();
  s.buffer=b; g.gain.value=0; g.gain.setValueAtTime(0,t); g.gain.setTargetAtTime(0.06,t,0.05);   // in the background, under the play
  s.connect(g); g.connect(N.out); s.start(t); s.stop(t+b.duration+0.05);
  CROWD.chant={s,g}; s.onended=()=>{if(CROWD.chant&&CROWD.chant.s===s) CROWD.chant=null;};
}
function chantStop(tau){
  const ch=CROWD.chant; if(!ch) return; CROWD.chant=null;
  try{const t=SND.ctx.currentTime; ch.g.gain.cancelScheduledValues(t+0.01); ch.g.gain.setTargetAtTime(0,t+0.01,tau); ch.s.stop(t+0.01+tau*6);}catch(_){}
}
