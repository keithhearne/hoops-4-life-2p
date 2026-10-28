// ---------- 2 PLAYER MATCH: the host phone runs the game, the guest phone sends its controls ----------
// Host (player one) = the left player "p", attacking the right hoop. Guest (player two) = the right player "d",
// attacking the left hoop. Both phones show the same court. The host runs every rule (scores, blocks, steals),
// and about 20 times a second sends the guest where everything is, plus events (sounds, messages, effects).
// The guest moves its own player straight away and times its own power bar, so its shots are judged
// exactly as it saw them, however slow the connection.
const TWO={on:false,role:null,arena:0,pBoy:"zackie",dBoy:"keelan",
  rin:{jx:0,jy:0}, jumpReq:false, stealCool:0, ev:[], sendT:0, seq:0,
  snaps:[], last:null, paused:false, pausedBy:"", waiting:false, ended:false, winner:null, mute:false,
  gc:{on:false,power:0,fade:false,shown:0,lastPower:0,range:null,zone:null,sentFade:false,auto:false},
  predX:null, lastIn:0, lastJy:0, sentWind:false, needUp:false, prevShoot:false, h2hDone:false};
let h2h={zackie:{w:0,l:0},keelan:{w:0,l:0}};   // head-to-head record of each boy in 2 Player matches
const isHost=()=>TWO.on&&TWO.role==="host", isGuest=()=>TWO.on&&TWO.role==="guest";
const meE=()=>isGuest()?d:p, foeE=()=>isGuest()?p:d;
const n1=v=>Math.round(v*10)/10;
const num=(v,lo,hi,def)=>{v=+v; return Number.isFinite(v)?clamp(v,lo,hi):def;};
const okSkin=s=>typeof s==="string" && /^boss\d{1,2}$/.test(s) && +s.slice(4)<BOSSES.length ? s : null;
const okKit=k=>({main:MAINS[k&&k.main]?k.main:"blue", trim:TRIMS[k&&k.trim]?k.trim:"white"});
function inKeyL(x){return x>=W-KEY.x1 && x<=W-KEY.x0;}   // the left hoop's dunk zone
function lookOf(boy,skin,kit,dir){
  let b=BOYS[boy];
  if(skin){const i=+skin.slice(4), bl=bossLook(i); b=Object.assign({},b,{name:BOSSES[i].name,num:bl.num,skin:bl.skin,skinDark:bl.skinDark,
    hair:bl.hair,hairHi:bl.hairHi,brow:bl.brow,eye:bl.eye,style:bl.style,gapTeeth:bl.gapTeeth,bigEars:bl.bigEars,band:bl.band});}
  return kitLook(b,kit,dir);
}

// --- starting a match ---
function twoStartAsHost(){
  if(!LINK.other || !LINK.ws) return;
  const arena=Math.floor(Math.random()*ARENAS.length);
  const s={t:"start",arena,pBoy:human,pKit:okKit(kits[human]),pSkin:skinOf[human]||null,
    dBoy:LINK.other.boy,dKit:okKit({main:LINK.other.main,trim:LINK.other.trim}),dSkin:LINK.other.skin||null};
  netSend(s); beginMatch("host",s);
}
function beginMatch(role,s){
  TWO.on=true; TWO.role=role; TWO.arena=s.arena; TWO.pBoy=s.pBoy; TWO.dBoy=s.dBoy;
  TWO.ended=false; TWO.winner=null; TWO.paused=false; TWO.waiting=false; TWO.snaps=[]; TWO.last=null; TWO.ev=[];
  TWO.gc.on=false; TWO.gc.shown=0; TWO.predX=null; TWO.h2hDone=false; TWO.rin={jx:0,jy:0}; TWO.jumpReq=false;
  BOSS=null; BS=null; PS=null; mode="2p";
  LOOK.p=lookOf(s.pBoy,s.pSkin,s.pKit,1); LOOK.p.who="p";
  LOOK.d=lookOf(s.dBoy,s.dSkin,s.dKit,-1); LOOK.d.who="d";
  C.p1=MAINS[s.pKit.main]; C.p2=MAINS[s.dKit.main]; NAME.p=LOOK.p.name; NAME.d=LOOK.d.name;
  if(C.p1===C.p2) C.p2=mix(C.p2,"#000000",0.3);   // same jersey colour: darken one so the scoreboard tells them apart
  Object.assign(stats,{score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0,stl:0});
  stealCool=0; stealSwipe=0; stealMsg.t=0; prevAction=true; boardFx.t=0; crackFx.t=0;
  SKILL=Object.assign({},SKILL_BASE); WIN=21; resetBoss(); cpuOn=true;
  pendingInbound=null; gameOverT=0; celebrate.t=0; charge.shown=0; dblFx.t=0; cpuFx.t=0;
  moods.p.m=moods.d.m="happy"; moods.p.t=moods.d.t=0;
  touchJoy=0; touchJoyY=0; shootTouch=false; shootKey=false; needRelease=true;
  lastShot=role==="host"?"You're on the left: score on the right hoop":"You're on the right: score on the left hoop";
  inbound("p"); screen="play"; tip.on=false; tip.fade=0;
  if(role==="host"){ startTip(); tip.cpuAt=99; }   // nobody's computer jumps: the guest jumps for himself
  else { tip.on=true; tip.t=0; tip.tossed=false; }
}

// --- the host: the guest's player is driven by the guest's controls ---
function remoteUpdate(dt){
  if(TWO.stealCool>0) TWO.stealCool-=dt;
  const jx=TWO.rin.jx;
  if(TWO.jumpReq){ TWO.jumpReq=false;
    if(d.ground && !cdunk.on){ d.vy=-380; d.ground=false; d.dbl=false; d.jumped=true; play("squeak"); }
    else if(!d.ground && !d.dbl && (owner===p||(ball.state==="flight"&&ball.shooter===p)) && Math.abs(d.vy)<APEX_VY*2.5){ d.vy=-380; d.dbl=true; cpuFx={t:0.45,x:d.x,y:d.y}; TWO.ev.push(["j","d",n1(d.x),n1(d.y)]); }
    else if(!d.ground) d.dbl=true;
  }
  if(tip.on){ updateTip(dt); body(d,dt); return; }
  if(cdunk.on){ runDunk(cdunk,d,-1,RL,CPU_DUNK_X,dt); return; }
  d.x=clamp(d.x+jx*(cpu.charging?70:170)*dt,24,812);
  if(cpu.charging && !d.ground){ d.vy = d.vy<0 ? d.vy+G*dt : Math.min(d.vy+G*0.15*dt,55); d.y+=d.vy*dt; if(d.y>=FLOOR){d.y=FLOOR; d.vy=0; d.ground=true;} }
  else body(d,dt);
  if(cpu.charging && owner!==d) cpu.charging=false;
  d.lean+=(((cpu.charging&&cpu.fade)?0.25:0)-d.lean)*Math.min(1,dt*12);
}
function remoteRelease(pw,fade,auto){
  if(!(owner===d && ball.state==="held" && cpu.charging)) return;
  const z=zoneFor(d.x,RL), range=fade?z.f:z.n, h=handPos(d,-1,true);
  const make=!auto && !z.behind && pw>=range[0] && pw<=range[1];
  // misses mirror the host's: just early lands on the front of the rim, just late on the back
  const tx=z.behind?RL.x:(auto?RL.x-80:(make?RL.x:(pw<range[0]?RL.x+(20+(range[0]-pw)*1.5):RL.x-Math.min(15,11.8+Math.random()*2.6+(pw-range[1])*0.4))));
  const sp=shotPath(h.x,h.y,tx,RL.y);
  const missType=z.behind?"behind":(auto?"auto":(pw<range[0]?(pw<range[0]-25?"air":"short"):"long"));
  Object.assign(ball,{state:"flight",x0:h.x,y0:h.y,x:h.x,y:h.y,vx:sp.vx,vy:sp.vy,T:sp.T,t:0,make,pts:z.pts,timer:0,
    shooter:d,missType,dunk:false,wind:false,lucky:false,live:false,saveTried:false,fade:!!fade,far:z===ZONES.far});
  owner=null; cpu.charging=false; cpu.fade=false;
  lastShot=NAME.d+" shot from "+z.name.toLowerCase()+(fade?" with a fade-away":"");
}
function remoteDunk(){
  if(!(owner===d && ball.state==="held" && d.ground && !cdunk.on && inKeyL(d.x))) return;
  Object.assign(cdunk,{on:true,t:0,x0:d.x,success:Math.random()<0.5,resolved:false,hang:0,wind:false,w0:0});
  d.ground=false; d.vy=0; cpu.charging=false; p.jumped=false;
  lastShot=NAME.d+" is going for the dunk!";
}
function remoteWindmill(){
  if(cdunk.on && !cdunk.wind && !cdunk.resolved && cdunk.t<RISE*0.8){ cdunk.wind=true; cdunk.w0=cdunk.t; cdunk.success=Math.random()<WIND_MAKE; }
}
function remoteSteal(jx,jy){
  if(TWO.stealCool>0 || !(owner===p && ball.state==="held" && !dunk.on)) return;
  TWO.stealCool=STEAL_COOLDOWN; cpuSwipe=0.3;
  const toward=Math.sign(p.x-d.x)||-1, diagonal=jy>0.45 && jx*toward>0.3;
  if(!diagonal){ TWO.ev.push(["sm","Pull the joystick down towards him!"]); return; }
  if(Math.abs(d.x-p.x)>STEAL_REACH){ TWO.ev.push(["sm","Too far away!"]); return; }
  const chance=(charge.on||!p.ground)?0:SKILL_BASE.stealChance;
  if(Math.random()<chance){
    play("swipe"); play("squeak"); play("gasp");
    owner=d; ball.state="held"; ball.live=false; charge.on=false; needRelease=true;
    say(pick("steal"),NAME.d+" stole it from "+NAME.p+"!",C.warn);
    setMood(d,"happy"); setMood(p,"shock"); celebrateFor(d);
    lastShot="Steal by "+NAME.d;
  } else { play("swipe"); TWO.ev.push(["sm",pick("stealMiss")]); }
}
// everything the guest sends is checked before it's used
function onTwoMessage(m){
  if(isHost()){
    if(m.t==="in"){ TWO.rin.jx=num(m.jx,-1,1,0); TWO.rin.jy=num(m.jy,-1,1,0); return true; }
    if(screen!=="play" && ["jp","cs","cf","rl","dk","wm","st"].includes(m.t)) return true;   // paused: controls are ignored
    if(m.t==="jp"){ TWO.jumpReq=true; return true; }
    if(m.t==="cs"){ if(owner===d && ball.state==="held" && !cdunk.on){ cpu.charging=true; cpu.fade=false; } return true; }
    if(m.t==="cf"){ cpu.fade=!!m.v; return true; }
    if(m.t==="rl"){ remoteRelease(num(m.pw,0,100,0),!!m.fade,!!m.auto); return true; }
    if(m.t==="dk"){ remoteDunk(); return true; }
    if(m.t==="wm"){ remoteWindmill(); return true; }
    if(m.t==="st"){ remoteSteal(num(m.jx,-1,1,0),num(m.jy,-1,1,0)); return true; }
  }
  if(isGuest()){
    if(m.t==="s"){ onSnapshot(m); return true; }
    if(m.t==="end"){ guestEnd(m); return true; }
  }
  if(m.t==="start" && LINK.role==="guest" && !isGuest()){
    const s={arena:num(m.arena,0,ARENAS.length-1,0)|0, pBoy:BOYS[m.pBoy]?m.pBoy:"zackie", dBoy:BOYS[m.dBoy]?m.dBoy:"keelan",
      pKit:okKit(m.pKit), dKit:okKit(m.dKit), pSkin:okSkin(m.pSkin), dSkin:okSkin(m.dSkin)};
    beginMatch("guest",s); return true;
  }
  if(m.t==="start" && isGuest() && TWO.ended){ TWO.on=false; return onTwoMessage(m); }   // a rematch
  if(m.t==="pz" && TWO.on){ TWO.paused=true; TWO.waiting=false; TWO.pausedBy=m.by==="d"?NAME.d:NAME.p; if(screen==="play") screen="pause"; return true; }
  if(m.t==="resume" && TWO.on){ TWO.paused=false; if(screen==="pause") screen="play"; needRelease=true; return true; }
  if(m.t==="leave" && TWO.on){ twoQuit((isHost()?NAME.d:NAME.p)+" left the match"); return true; }
  return false;
}
// --- the host sends the state about 20 times a second ---
function twoHostTick(dt){
  TWO.sendT-=dt; if(TWO.sendT>0) return; TWO.sendT=0.05;
  if(screen!=="play" && !TWO.ev.length) return;
  const E=e=>[n1(e.x),n1(e.y),e.face||0,n1(e.lean||0),e.ground?1:0,e.dbl?1:0];
  const DK=k=>k.on?[1,n1(k.t),k.wind?1:0,k.resolved?1:0,n1(k.hang),n1(k.w0||0)]:0;
  const st={"held":1,"flight":2,"free":3,"made":4,"drop":5,"tip":6}[ball.state]||0;
  netSend({t:"s",q:++TWO.seq,p:E(p),d:E(d),b:[n1(ball.x),n1(ball.y),n1(ball.rot||0),st],o:owner===p?1:owner===d?2:0,
    sc:[stats.score,stats.cpu],ch:[charge.on?1:0,charge.fade?1:0],cc:[cpu.charging?1:0,cpu.fade?1:0],
    dk:DK(dunk),cdk:DK(cdunk),tp:[tip.on?1:0,n1(tip.t),tip.tossed?1:0],sh:n1(shakeT),md:[moods.p.m,moods.d.m],
    ft:ball.shooter===d?2:1,ev:TWO.ev.splice(0,20)});
}
// --- the guest: draw what the host sends, smoothly ---
function onSnapshot(m){
  if(!Array.isArray(m.p)||!Array.isArray(m.d)||!Array.isArray(m.b)) return;
  m.r=performance.now(); TWO.snaps.push(m); if(TWO.snaps.length>12) TWO.snaps.shift();
  TWO.last=m; TWO.waiting=false;
  for(const ev of (Array.isArray(m.ev)?m.ev:[])) guestEvent(ev);
}
const STATES=["held","held","flight","free","made","drop","tip"];
function guestEvent(ev){
  if(!Array.isArray(ev)) return;
  const k=ev[0];
  if(k==="s" && typeof ev[1]==="string" && SFX[ev[1]]){
    let name=ev[1], arg=ev[2];
    if(name==="dribble") return;                                  // the guest makes its own dribble sounds
    if(name==="groan") return;                                     // the host missing isn't a sad moment for the guest
    if(name==="gasp"){ name="cheer"; arg=0.75; }                   // the guest's own block or steal: a cheer
    play(name,typeof arg==="number"||typeof arg==="boolean"?arg:undefined);
  } else if(k==="m" && typeof ev[1]==="string"){
    // the host's commentary; lines written to the host ("You ...") are left off
    const sub=typeof ev[2]==="string" && !/\b(you|your)\b/i.test(ev[2]) ? ev[2] : "";
    msg={text:ev[1].slice(0,60),sub:sub.slice(0,80),t:1.9,color:typeof ev[3]==="string"?ev[3]:C.ink};
  } else if(k==="c" && (ev[1]==="p"||ev[1]==="d")){ celebrate={who:ev[1],t:num(ev[2],0.5,4,2.2),T:num(ev[2],0.5,4,2.2)}; }
  else if(k==="n"){ netKick(ev[1]?1:0,num(ev[2],0,12,3),num(ev[3],-3,3,0)); }
  else if(k==="b"){ TWO.mute=true; startBoardFx(ev[1]==="L"?"L":"R",!!ev[2]); TWO.mute=false; }
  else if(k==="k"){ startCrackFx(); }
  else if(k==="j"){ const fx={t:0.45,x:num(ev[2],0,W,0),y:num(ev[3],0,H,0)}; if(ev[1]==="d") cpuFx=fx; else dblFx=fx; }
  else if(k==="sm" && typeof ev[1]==="string"){ stealMsg={text:ev[1].slice(0,40),t:1.1}; }
}
function lerpE(e,a,b,u){
  e.x=a[0]+(b[0]-a[0])*u; e.y=a[1]+(b[1]-a[1])*u; e.face=b[2]||e.face; e.lean=a[3]+(b[3]-a[3])*u; e.ground=!!b[4]; e.dbl=!!b[5];
}
function guestUpdate(dt){
  const S=TWO.last;
  // local timers
  if(msg.t>0) msg.t-=dt; if(celebrate.t>0) celebrate.t-=dt; if(dblFx.t>0) dblFx.t-=dt; if(cpuFx.t>0) cpuFx.t-=dt;
  if(stealMsg.t>0) stealMsg.t-=dt; if(TWO.gc.shown>0) TWO.gc.shown-=dt; if(tip.fade>0) tip.fade-=dt; if(cpuSwipe>0) cpuSwipe-=dt;
  updateNets(dt); updateFx(dt);
  if(!S || screen!=="play"){ return; }
  // where things were 110 ms ago, smoothly between the two snapshots around that time
  const rt=performance.now()-110; let a=S,b=S,u=1;
  for(let i=TWO.snaps.length-1;i>0;i--){ if(TWO.snaps[i-1].r<=rt){ a=TWO.snaps[i-1]; b=TWO.snaps[i]; u=clamp((rt-a.r)/Math.max(1,b.r-a.r),0,1); break; } }
  lerpE(p,a.p,b.p,u); const dx=d.x; lerpE(d,a.d,b.d,u);
  owner=S.o===1?p:S.o===2?d:null; ball.state=STATES[S.b[3]]||"free";
  ball.shooter=S.ft===2?d:p;
  stats.score=S.sc[0]|0; stats.cpu=S.sc[1]|0;
  charge.on=!!S.ch[0]; charge.fade=!!S.ch[1];
  const setDK=(k,v)=>{ if(v){k.on=true; k.t=v[1]; k.wind=!!v[2]; k.resolved=!!v[3]; k.hang=v[4]; k.w0=v[5];} else k.on=false; };
  setDK(dunk,S.dk); setDK(cdunk,S.cdk);
  tip.on=!!S.tp[0]; tip.t=S.tp[1]; tip.tossed=!!S.tp[2]; shakeT=S.sh||0;
  if(Array.isArray(S.md)){ moods.p.m=S.md[0]; moods.d.m=S.md[1]; }
  // my own player moves as soon as I push the joystick; the host's position pulls it back if they drift apart
  const jx=clamp(touchJoy||keyJoy,-1,1), jy=clamp(touchJoyY||keyJoyY,-1,1);
  const serverX=d.x;
  if(tip.on||cdunk.on||TWO.predX===null) TWO.predX=serverX;
  else {
    TWO.predX=clamp(TWO.predX+jx*(TWO.gc.on?70:170)*dt,24,812);
    const err=serverX-TWO.predX;
    if(Math.abs(err)>70) TWO.predX+=err*0.3; else if(Math.abs(jx)<0.2) TWO.predX+=err*Math.min(1,dt*4);
  }
  d.x=TWO.predX;
  // the ball: in my hands it follows my player straight away
  if(owner===d && ball.state==="held" && !cdunk.on){ const h=TWO.gc.on?handPos(d,-1,true):dribblePos(d,d.face||-1,dt); ball.x=h.x; ball.y=h.y; }
  else { ball.x=a.b[0]+(b.b[0]-a.b[0])*u; ball.y=a.b[1]+(b.b[1]-a.b[1])*u; }
  ball.rot=S.b[2];
  cpu.charging=TWO.gc.on || !!S.cc[0]; cpu.fade=TWO.gc.on?TWO.gc.fade:!!S.cc[1];
  d.lean=(cpu.charging&&cpu.fade)?0.25:d.lean;
  trackRun(dt);
  guestControls(dt,jx,jy);
}
// the guest's buttons: shooting, dunks, windmills, steals and jumps all go to the host
function guestControls(dt,jx,jy){
  const now=performance.now();
  if(now-TWO.lastIn>45 || Math.abs(jx-TWO.rin.jx)>0.3 || Math.abs(jy-TWO.rin.jy)>0.3){ netSend({t:"in",jx:n1(jx),jy:n1(jy)}); TWO.lastIn=now; TWO.rin={jx,jy}; }
  if(jumpQueued){ jumpQueued=false; netSend({t:"jp"}); }
  const shootDown=shootKey||shootTouch, pressed=shootDown && !TWO.prevShoot; TWO.prevShoot=shootDown;
  if(!shootDown) TWO.needUp=false;
  const gc=TWO.gc, mine=owner===d && ball.state==="held";
  if(cdunk.on && jy<-0.5 && !TWO.sentWind){ TWO.sentWind=true; netSend({t:"wm"}); }
  if(!cdunk.on) TWO.sentWind=false;
  if(owner===p && pressed){ netSend({t:"st",jx:n1(jx),jy:n1(jy)}); cpuSwipe=0.3; }
  if(mine && !cdunk.on && !gc.on && shootDown && !TWO.needUp){
    if(d.ground && inKeyL(d.x)){ netSend({t:"dk"}); TWO.needUp=true; }
    else { Object.assign(gc,{on:true,power:0,fade:false,sentFade:false,zone:zoneFor(d.x,RL)}); netSend({t:"cs"}); }
  }
  if(gc.on){
    if(!mine){ gc.on=false; return; }   // lost the ball (stolen) while powering up
    const z=zoneFor(d.x,RL), before=gc.power; gc.zone=z;
    gc.power+=dt/(z.fill||FILL)*100;
    gc.fade=jx>0.35;   // pull away from the hoop (to the right) for a fade-away
    if(gc.fade!==gc.sentFade){ gc.sentFade=gc.fade; netSend({t:"cf",v:gc.fade?1:0}); }
    const range=gc.fade?z.f:z.n; if(before<range[0] && gc.power>=range[0]) play("tick");
    const auto=gc.power>=100;
    if(!shootDown || auto){
      if(auto) gc.power=100;
      netSend({t:"rl",pw:Math.round(gc.power*10)/10,fade:gc.fade?1:0,auto:auto?1:0});
      gc.lastPower=gc.power; gc.range=range; gc.shown=1.2; gc.on=false; TWO.needUp=true;
      lastShot=z.behind?"No shot from behind the basket: get in front of it":auto?"Held too long: the ball flew off at 100":"Let go at "+Math.round(gc.power)+" · needed "+range[0]+"–"+range[1]+(gc.fade?" (fade-away)":"");
    }
  }
}
// --- end of the match, pausing, leaving ---
function twoHostEnd(){
  const youWin=stats.score>=WIN; overWinner=youWin?"p":"d";
  recordH2H(TWO.pBoy,youWin); netSend({t:"end",w:overWinner,sc:[stats.score,stats.cpu]}); TWO.ended=true; screen="over";
}
function guestEnd(m){
  overWinner=m.w==="d"?"d":"p"; if(Array.isArray(m.sc)){stats.score=m.sc[0]|0; stats.cpu=m.sc[1]|0;}
  recordH2H(TWO.dBoy,overWinner==="d"); TWO.ended=true; screen="over";
}
function recordH2H(boy,won){ if(TWO.h2hDone) return; TWO.h2hDone=true; const r=h2h[boy]||(h2h[boy]={w:0,l:0}); if(won) r.w++; else r.l++; saveGame(); }
function twoPause(){ if(!TWO.on||TWO.ended) return; TWO.paused=true; TWO.pausedBy=isGuest()?NAME.d:NAME.p; screen="pause"; netSend({t:"pz",by:isGuest()?"d":"p"}); }
function twoResume(){ TWO.paused=false; screen="play"; needRelease=true; TWO.needUp=true; netSend({t:"resume"}); }
function twoQuit(note){
  netSend({t:"leave"}); TWO.on=false; TWO.role=null; mode="vs";
  applyLooks(); screen="online"; LINK.note=note||""; if(LINK.ws && LINK.peer) LINK.stage="connected";
}
// the other phone dropped out mid-match: pause and wait for it
function twoPeerLeft(){ if(TWO.on && !TWO.ended){ TWO.waiting=true; TWO.paused=true; TWO.pausedBy=""; if(screen==="play") screen="pause"; } }
function twoPeerBack(){ if(TWO.on && TWO.waiting){ TWO.waiting=false; netSend({t:"pz",by:isGuest()?"d":"p"}); } }   // back: both phones show RESUME
function drawTwoPause(){
  ui=[]; shade(0.75);
  bigTitle(TWO.waiting?"WAITING…":"PAUSED",W/2,92,40);
  const who=isGuest()?NAME.p:NAME.d;
  text(TWO.waiting?"The other phone lost its connection. Waiting for "+who+" to come back…":(TWO.pausedBy?"Paused by "+TWO.pausedBy:"Paused"),W/2,134,BODY(14,900),C.ink,"center");
  const bx=W/2-150;
  if(!TWO.waiting) button(bx,160,300,50,"RESUME",{fill:"#2F6FE4"},twoResume);
  button(bx,220,300,44,"LEAVE MATCH",{outline:"rgba(255,255,255,0.3)"},()=>twoQuit(""));
  button(bx,274,146,40,SND.on?"SOUND: ON":"SOUND: OFF",{outline:"rgba(255,255,255,0.3)",size:14},toggleSound);
  button(bx+154,274,146,40,SND.crowd?"CROWD: ON":"CROWD: OFF",{outline:"rgba(255,255,255,0.3)",size:14,disabled:!SND.on},toggleCrowd);
}
function drawTwoOver(){
  ui=[]; shade(0.84);
  const myBoy=isGuest()?TWO.dBoy:TWO.pBoy, iWon=(overWinner==="p")===!isGuest(), winName=overWinner==="p"?NAME.p:NAME.d;
  faceBadge(overWinner==="p"?LOOK.p:LOOK.d,180,186,112,overWinner==="p"?C.p1:C.p2);
  let size=40; ctx.font=DISP(size); const head=winName.toUpperCase()+" WINS!";
  while(size>24 && ctx.measureText(head).width>470){size-=2; ctx.font=DISP(size);}
  bigTitle(head,330,62,size,"left");
  text(NAME.p+"  "+stats.score+"  –  "+stats.cpu+"  "+NAME.d,332,104,BODY(20,900),C.ink);
  text("2 PLAYER · "+ARENAS[TWO.arena].name.toUpperCase(),332,140,BODY(12,900),C.muted);
  const r=h2h[myBoy]||{w:0,l:0};
  ctx.fillStyle="rgba(46,56,102,0.9)"; rr(332,166,460,96,14); ctx.fill();
  text("HEAD-TO-HEAD",348,188,BODY(12,900),C.muted);
  text(BOYS[myBoy].name+": "+r.w+(r.w===1?" win":" wins")+" · "+r.l+(r.l===1?" loss":" losses"),348,218,DISP(18),iWon?C.green:C.ink);
  text(iWon?"Nice one!":"Get him next time!",348,246,BODY(13,900),C.ink);
  if(isHost()) button(332,300,220,50,"REMATCH",{fill:"#F26B1D",ink:C.navy,sub:"New random arena",disabled:!(LINK.ws&&LINK.peer)},()=>{TWO.on=false; twoStartAsHost();});
  else text("Waiting for "+NAME.p+" to start a rematch…",332,325,BODY(14,900),C.ink);
  button(564,300,160,50,"LEAVE",{outline:"rgba(255,255,255,0.3)"},()=>twoQuit(""));
}
// the guest's power bar (its own, timed on its own phone)
function drawGuestMeter(){
  const gc=TWO.gc; if(!(gc.on||gc.shown>0)) return;
  const z=gc.zone||zoneFor(d.x,RL), fade=gc.on?gc.fade:false, range=gc.on?(fade?z.f:z.n):(gc.range||z.n), pw=gc.on?gc.power:gc.lastPower;
  const x=W-170,y=86,w=30,h=180;
  text("POWER",x,y-12,BODY(12,900),C.ink);
  ctx.fillStyle=C.panel; rr(x,y,w,h,8); ctx.fill();
  ctx.save(); rr(x,y,w,h,8); ctx.clip();
  ctx.fillStyle=C.ball; ctx.fillRect(x,y+h*(1-pw/100),w,h*pw/100);
  const by=y+h*(1-range[1]/100), bh=h*(range[1]-range[0])/100;
  if(!z.behind){ ctx.fillStyle="rgba(61,220,151,0.8)"; ctx.fillRect(x,by,w,bh); ctx.fillStyle=C.ink; ctx.fillRect(x,by-1.5,w,3); ctx.fillRect(x,by+bh-1.5,w,3); }
  ctx.fillStyle=C.red; ctx.fillRect(x,y,w,4); ctx.restore();
  text("100",x-8,y+2,BODY(11,900),"#FF8A8A","right");
  if(!z.behind){ text(String(range[1]),x-8,by-3,BODY(11,900),C.green,"right"); text(String(range[0]),x-8,by+bh+5,BODY(11,900),C.green,"right"); }
  else text("NO SHOT",x-8,y+h/2,BODY(12,900),C.warn,"right");
  text(Math.round(pw)+"%",x,y+h+16,DISP(16),(pw>=range[0]&&pw<=range[1])?C.green:C.ink);
}
// the guest's on-screen buttons (the same layout; steal when the host has the ball)
function drawGuestControls(){
  ctx.fillStyle="rgba(27,35,64,0.8)"; ctx.beginPath(); ctx.arc(JOY.x,JOY.y,JOY.r,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle="rgba(255,255,255,0.5)"; ctx.lineWidth=3; ctx.stroke();
  const jx=JOY.x+clamp(touchJoy||keyJoy,-1,1)*26, jy=JOY.y+clamp(touchJoyY||keyJoyY,-1,1)*20;
  ctx.fillStyle=C.chalk; ctx.beginPath(); ctx.arc(jx,jy,24,0,Math.PI*2); ctx.fill(); ctx.strokeStyle=C.ink; ctx.lineWidth=3; ctx.stroke();
  const defending=owner===p||(ball.state==="flight"&&ball.shooter===p);
  ctx.fillStyle=d.ground?"rgba(46,56,102,0.9)":"rgba(61,220,151,0.5)"; ctx.beginPath(); ctx.arc(JUMP.x,JUMP.y,JUMP.r,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle=defending?C.warn:"rgba(255,255,255,0.5)"; ctx.lineWidth=3; ctx.stroke();
  line(JUMP.x,JUMP.y+2,JUMP.x,JUMP.y-14,C.ink,3);
  ctx.beginPath(); ctx.moveTo(JUMP.x-7,JUMP.y-8); ctx.lineTo(JUMP.x,JUMP.y-15); ctx.lineTo(JUMP.x+7,JUMP.y-8); ctx.stroke();
  text(defending?"BLOCK":"JUMP",JUMP.x,JUMP.y+14,BODY(11,900),C.ink,"center");
  const down=shootKey||shootTouch;
  if(owner===p){
    const near=Math.abs(d.x-p.x)<=STEAL_REACH;
    if(near){const pulse=4+Math.sin(performance.now()/120)*3; ctx.strokeStyle=C.green; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(SHOOT.x,SHOOT.y,SHOOT.r+pulse,0,Math.PI*2); ctx.stroke();}
    ctx.fillStyle="#14A3B8"; ctx.beginPath(); ctx.arc(SHOOT.x,SHOOT.y,down?39:SHOOT.r,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle=down?C.warn:C.ink; ctx.lineWidth=3; ctx.stroke();
    text("STEAL",SHOOT.x,SHOOT.y-4,DISP(14),C.ink,"center"); text(near?"in reach!":"get closer",SHOOT.x,SHOOT.y+14,BODY(10,900),C.ink,"center");
    return;
  }
  const can=owner===d && ball.state==="held" && !cdunk.on, dunkReady=can && !TWO.gc.on && d.ground && inKeyL(d.x);
  ctx.globalAlpha=can?1:0.4;
  if(dunkReady){ ctx.fillStyle=C.info; ctx.beginPath(); ctx.arc(SHOOT.x,SHOOT.y,SHOOT.r,0,Math.PI*2); ctx.fill(); ctx.strokeStyle=C.ink; ctx.lineWidth=3; ctx.stroke(); text("DUNK!",SHOOT.x,SHOOT.y+1,DISP(15),C.ink,"center"); }
  else { ctx.fillStyle=C.ball; ctx.beginPath(); ctx.arc(SHOOT.x,SHOOT.y,down&&can?39:SHOOT.r,0,Math.PI*2); ctx.fill(); ctx.strokeStyle=down?C.warn:C.seam; ctx.lineWidth=4; ctx.stroke(); text("SHOOT",SHOOT.x,SHOOT.y+1,DISP(14),C.navy,"center"); }
  ctx.globalAlpha=1;
}
