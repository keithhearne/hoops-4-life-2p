// ---------- bosses: game 7 of every level is a boss with his own abilities and a signature move ----------
const ABIL={speed:"Speedster",hops:"Sky Hopper",giant:"Giant",arms:"Long Arms",sharp:"Sharpshooter",deep:"Deep Range",
  quick:"Quick Release",block:"Shot Blocker",dbl:"Double Jumper",glue:"Glue Defender",pick:"Pickpocket",
  ankle:"Ankle Breaker",dunk:"Dunk Master",fade:"Fade-Away King",reb:"Rebounder"};
// sk = which kind of signature move, sv = how that boss does it
const BOSSES=[
  {name:"Big Benny",ab:["giant"],sig:"Skyscraper Block",sk:"block",sv:{}},
  {name:"Captain Quickstep",ab:["speed"],sig:"Fast Break",sk:"fast",sv:{}},
  {name:"Blaze",ab:["sharp"],sig:"Heat Check",sk:"shot",sv:{repeat:3,spot:"mid"}},
  {name:"Peak Pete",ab:["hops"],sig:"Mountain Leap",sk:"leap",sv:{}},
  {name:"Sparky",ab:["quick"],sig:"Lightning Shot",sk:"shot",sv:{quick:true}},
  {name:"The Duke",ab:["glue"],sig:"Royal Guard",sk:"guard",sv:{}},
  {name:"Nova",ab:["arms"],sig:"Northern Reach",sk:"block",sv:{reach:true}},
  {name:"Comet Carl",ab:["ankle"],sig:"Comet Crossover",sk:"cross",sv:{}},
  {name:"Sunny Swipes",ab:["pick"],sig:"Early Bird",sk:"steal",sv:{}},
  {name:"The Iceberg",ab:["block"],sig:"Freeze",sk:"block",sv:{catch:true}},
  {name:"Timber",ab:["giant","reb"],sig:"Tall Tree",sk:"reb",sv:{}},
  {name:"Iron Max",ab:["glue","arms"],sig:"Steel Trap",sk:"guard",sv:{steal:true}},
  {name:"Astro",ab:["hops","dbl"],sig:"Moonwalk",sk:"leap",sv:{dbl:true}},
  {name:"Falcon",ab:["speed","dunk"],sig:"Dive Bomb",sk:"fast",sv:{}},
  {name:"Splash",ab:["deep","quick"],sig:"Cannonball",sk:"shot",sv:{spot:"deep",quick:true}},
  {name:"Rockslide",ab:["giant","block"],sig:"Landslide",sk:"block",sv:{}},
  {name:"Flicker",ab:["ankle","pick"],sig:"Lights Out",sk:"cross",sv:{thenSteal:true}},
  {name:"Shadow",ab:["speed","pick"],sig:"Vanish",sk:"steal",sv:{}},
  {name:"Thunder",ab:["hops","dunk"],sig:"Thunderclap",sk:"fast",sv:{wind:true}},
  {name:"Prism",ab:["sharp","fade"],sig:"Rainbow Fade",sk:"shot",sv:{fade:true}},
  {name:"Magma",ab:["giant","dunk","reb"],sig:"Eruption",sk:"reb",sv:{dunk:true}},
  {name:"Orbit",ab:["arms","dbl","block"],sig:"Gravity",sk:"block",sv:{dbl:true}},
  {name:"King Crusher",ab:["speed","glue","pick"],sig:"Crown Grab",sk:"steal",sv:{fast:true}},
  {name:"Tsunami",ab:["sharp","deep","quick"],sig:"Tidal Wave",sk:"shot",sv:{spot:"far"}},
  {name:"Bullseye",ab:["sharp","fade","ankle"],sig:"Arrow Step",sk:"shot",sv:{cross:true,fade:true}},
  {name:"Solar Flare",ab:["speed","hops","dunk"],sig:"Supernova",sk:"fast",sv:{wind:true}},
  {name:"The Wall",ab:["giant","arms","glue"],sig:"Drawbridge",sk:"guard",sv:{}},
  {name:"Stardust",ab:["deep","quick","ankle"],sig:"Shooting Star",sk:"shot",sv:{cross:true,spot:"deep",quick:true}},
  {name:"Titan",ab:["giant","block","reb"],sig:"Titan Swat",sk:"dunkblock",sv:{}},
  {name:"The Legend",ab:["speed","hops","arms","sharp","pick"],sig:"Legend Mode",sk:"legend",sv:{}}
];
const SIG_INFO={block:"blocks your next shot",fast:"sprints in for a dunk",shot:"a shot that almost always goes in",
  leap:"a giant jump",guard:"won't let you past",cross:"crosses you over",steal:"steals the ball",
  reb:"grabs the rebound",dunkblock:"blocks your dunk",legend:"gets even stronger at the end"};
const BOSS_SKIN=[["#F2C6A8","#D9A285"],["#E8B48F","#C99470"],["#C68B5E","#A56E44"],["#A86E45","#875532"],["#7A4B2E","#5E3820"],["#5A3622","#432616"]];
const BOSS_HAIR=[["#1E1A18","#4A403A"],["#3B2A1E","#6A5240"],["#6B4A32","#9A7556"],["#C9A15A","#E6C784"],["#B5462A","#D9774F"],["#2A2A2A","#555555"],["#E8E4DA","#FFFFFF"]];
const BOSS_EYE=["#3A2A1E","#5A3A22","#4F6B3A","#3D5A80","#2A1E14"];
let BOSS=null, BS=null;
const isBossLevel=n=>n%STOPS===STOPS-1;
function bossTier(i){return i<10?1:(i<20?2:(i<29?3:4));}
function bossLook(i,avoid){
  const a=ARENAS[i], b=BOSSES[i], sk=BOSS_SKIN[(i*7+3)%6], hr=BOSS_HAIR[(i*5+1)%7];
  const dist=(x,y)=>{const A=hex2rgb(x),B=hex2rgb(y);return Math.hypot(A[0]-B[0],A[1]-B[1],A[2]-B[2]);};
  let jersey=a.p, trim=a.s;
  if(avoid && dist(jersey,avoid)<110){jersey=a.s; trim=a.p;}
  if(dist(jersey,trim)<90) trim=inkOn(jersey);
  return {who:"d",dir:-1,name:b.name,num:String(i+1),skin:sk[0],skinDark:sk[1],hair:hr[0],hairHi:hr[1],brow:mix(hr[0],"#000000",0.3),
    eye:BOSS_EYE[i%5],style:i%2?"quiff":"crop",gapTeeth:i%4===2,bigEars:i%3===0,
    jersey,trim,shorts:mix(jersey,"#000000",0.18),numCol:trim,shoe:trim==="#FFFFFF"?"#1B2340":"#FFFFFF",sole:"#1B2340",sock:"#FFFFFF",band:trim,
    armL:b.ab.includes("arms")?1.25:1, size:b.ab.includes("giant")?1.2+0.04*bossTier(i):1};
}
// turn the boss's abilities into numbers the game uses
function bossStats(i){
  const b=BOSSES[i], t=bossTier(i), s=[0,0.15,0.25,0.35,0.45][t], has=k=>b.ab.includes(k);
  return {s, size:has("giant")?1.2+0.04*t:1, arm:has("arms")?1.18+0.06*t:1, jump:has("hops")?Math.sqrt(1+s*2):1,
    hold:has("quick")?Math.max(0.4,1-s*1.4):1, blockR:has("block")?18+s*22:18, deep:has("deep")?s:0, glue:has("glue")?s:0,
    pick:has("pick")?s:0, ankle:has("ankle")?s:0, fade:has("fade")?s:0, reb:has("reb")?s:0, speed:has("speed")?Math.min(1.45,1+s+0.1):1};
}
function bossSkill(sk,i){
  const b=BOSSES[i], s=BS.s, has=k=>b.ab.includes(k);
  if(has("speed")) for(const k of ["atkSpeed","defSpeed","chaseSpeed"]) sk[k]*=BS.speed;
  if(has("sharp")) sk.acc*=1+s*1.3;
  if(has("block")){sk.noReact*=0.3; sk.timingNoise*=Math.max(0.3,1-s*1.5); sk.saveChance=Math.min(0.9,sk.saveChance+s*1.2); sk.blockDunk=Math.min(0.85,sk.blockDunk+s);}
  if(has("dbl")) sk.dblChance=0.92;
  if(has("glue")) sk.defSpeed*=1+s*1.5;
  if(has("dunk")){sk.dunkTry=Math.min(0.8,sk.dunkTry+s*1.6); sk.dunkMake=Math.min(0.85,sk.dunkMake+s); sk.windTry=Math.min(0.8,sk.windTry+s);}
  if(has("fade")) sk.fadeChance=0.95;
  if(has("pick")) sk.stealChance*=Math.max(0.5,1-s);   // he protects the ball better too
  return sk;
}
// boss moves and signature moves
let sig={wait:12,on:null,t:0,flash:0,n:0,x:0,next:null}, bossStealCool=0, ankleCool=0, pStun=0, cpuBurst=0, cpuSwipe=0, legendOn=false;
function resetBoss(){sig={wait:10+Math.random()*6,on:null,t:0,flash:0,n:0,x:0,next:null}; bossStealCool=2; ankleCool=2; pStun=0; cpuBurst=0; cpuSwipe=0; legendOn=false;}
function sigKind(){return sig.next||(BOSS&&BOSS.sk);}
function sigReady(k){return BOSS && !sig.on && (sig.wait<=0||sig.next===k) && sigKind()===k && gameOverT<=0 && !tip.on;}
function fireSig(){sig.on=sigKind(); sig.next=null; sig.t=0; sig.flash=2.4; sig.stole=false; sig.wait=18+Math.random()*12; play("cheer",0.75); setMood(d,"happy",2);}
function endSig(){sig.on=null;}
function bossTick(dt){
  if(!BOSS) return;
  if(sig.wait>0) sig.wait-=dt;
  if(sig.flash>0) sig.flash-=dt;
  if(sig.on) sig.t+=dt;
  if(bossStealCool>0) bossStealCool-=dt;
  if(ankleCool>0) ankleCool-=dt;
  if(pStun>0) pStun-=dt;
  if(cpuBurst>0) cpuBurst-=dt;
  if(cpuSwipe>0) cpuSwipe-=dt;
  // a signature move that can't happen right now times out
  const lim={block:4,dunkblock:3,fast:5,shot:40,leap:2.5,guard:3,steal:1.8,reb:3.5,cross:0.1,legend:2.8}[sig.on];
  if(sig.on && sig.t>lim) endSig();
  if(sig.on==="leap" && d.ground && sig.t>0.25) endSig();
  // The Legend: everything gets stronger for the last 5 points
  if(BOSS.sk==="legend" && !legendOn && (stats.cpu>=WIN-5||stats.score>=WIN-5)){
    legendOn=true; sig.next=null; sig.on="legend"; sig.t=0; sig.flash=2.8; play("cheer",1.4);
    for(const k of ["atkSpeed","defSpeed","chaseSpeed"]) SKILL[k]*=1.15;
    SKILL.acc*=1.15; BS.jump*=1.08; BS.arm*=1.08; BS.pick+=0.1;
  }
}
function bossSteal(sure){
  bossStealCool=1.4; cpuSwipe=0.3; play("swipe");
  if(sure || Math.random()<BS.pick*1.4){
    owner=d; ball.state="held"; ball.live=false; charge.on=false; needRelease=true;
    say("STOLEN!",NAME.d+" picked your pocket!",C.warn); play("gasp");
    setMood(p,"shock"); setMood(d,"happy"); lastShot="Stolen by "+NAME.d;
    setCpuPlan();
    if(sig.on==="steal" && BOSS.sv.fast){cpu.dunk=true; cpu.spot=115+Math.random()*30; cpuBurst=2;}
    if(sig.on==="steal") endSig();
    return true;
  }
  lastShot=NAME.d+" swiped at the ball and missed"; return false;
}
function crossover(){
  ankleCool=3.5; pStun=0.55+Math.max(BS.ankle,0.2); cpuBurst=0.9;
  if(cpu.spot>p.x-40) cpu.spot=clamp(p.x-70,115,cpu.spot);   // drive past him
  say("ANKLES BROKEN!",NAME.d+" crossed you over!",C.warn); play("squeak"); play("gasp");
  setMood(p,"shock"); setMood(d,"happy");
}
// called from the computer's update: the boss's extra moves
function bossAttack(dt){   // he has the ball
  if(cpu.charging) return;
  const close=p.x<d.x && d.x-p.x<110;
  if(close && sigReady("cross")){fireSig(); crossover(); if(BOSS.sv.thenSteal) sig.next="steal"; sig.wait=Math.max(sig.wait,4); endSig(); return;}
  if(BS.ankle && close && ankleCool<=0 && Math.random()<dt*(0.5+BS.ankle*2)) crossover();
}
function bossDefend(dt){   // you have the ball
  const gap=Math.abs(d.x-p.x);
  if(!charge.on && !dunk.on && p.ground && gap<260 && sigReady("steal")) fireSig();
  if(sig.on==="steal"){
    const target=p.x+18, step=SKILL.defSpeed*3*dt;
    d.x+=Math.abs(target-d.x)<step?target-d.x:Math.sign(target-d.x)*step;
    if(Math.abs(d.x-p.x)<STEAL_REACH && !charge.on && !dunk.on){bossSteal(true);}
    return true;
  }
  if(gap<140 && sigReady("guard")) fireSig();
  if(sig.on==="guard"){
    const target=p.x+34, step=SKILL.defSpeed*2.2*dt;
    d.x+=Math.abs(target-d.x)<step?target-d.x:Math.sign(target-d.x)*step;
    if(BOSS.sv.steal && sig.t>1 && !sig.stole && !charge.on && !dunk.on){sig.stole=true; if(Math.random()<0.7) bossSteal(true); else bossSteal(false);}
    if(sig.t>3) endSig();
    return true;
  }
  if(BS.pick && bossStealCool<=0 && !charge.on && !dunk.on && p.ground && gap<STEAL_REACH*BS.arm+6 && Math.random()<dt*2.2) bossSteal(false);
  return false;
}
// how fast the player can move: frozen after a crossover, slowed when a glue defender is in the way
function playerSpeedK(joy){
  if(!BOSS) return 1;
  if(pStun>0) return 0;
  const inWay=owner===p && d.ground && d.x>p.x && d.x-p.x<46 && joy>0;
  if(inWay && sig.on==="guard") return 0.12;
  if(inWay && BS.glue) return Math.max(0.25,1-BS.glue*2);
  return 1;
}
function drawSigFlash(){
  if(!BOSS || sig.flash<=0) return;
  const a=Math.min(1,sig.flash*2.5, (2.4-sig.flash+0.2)*6);
  ctx.save(); ctx.globalAlpha=Math.max(0,a);
  const t1=NAME.d.toUpperCase(), t2=(BOSS.sig+"!").toUpperCase();
  ctx.font=DISP(22); const w=Math.max(ctx.measureText(t2).width,180)+50;
  ctx.fillStyle="rgba(16,21,43,0.94)"; rr(W/2-w/2,62,w,58,14); ctx.fill();
  ctx.strokeStyle=C.p2; ctx.lineWidth=4; ctx.stroke();
  drawCrown(W/2,63,13);
  text(t1+" · SIGNATURE MOVE",W/2,77,BODY(11,900),C.muted,"center");
  text(t2,W/2,101,DISP(22),C.warn,"center");
  ctx.restore();
}
function drawCrown(x,y,s){   // a little gold crown sitting on a point
  ctx.save(); ctx.translate(x,y); ctx.fillStyle="#FFC93C"; ctx.strokeStyle="#7A4A00"; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.moveTo(-s,-0); ctx.lineTo(-s,-s*0.9); ctx.lineTo(-s*0.5,-s*0.4); ctx.lineTo(0,-s*1.1); ctx.lineTo(s*0.5,-s*0.4); ctx.lineTo(s,-s*0.9); ctx.lineTo(s,0); ctx.closePath();
  ctx.fill(); ctx.stroke(); ctx.restore();
}
function bossCard(i,x,y,w,h){
  const b=BOSSES[i], lk=bossLook(i,MAINS[kits[human].main]);
  ctx.fillStyle="rgba(27,35,64,0.97)"; rr(x,y,w,h,18); ctx.fill();
  ctx.strokeStyle=lk.jersey; ctx.lineWidth=4; ctx.stroke();
  ctx.save(); rr(x,y,w,h,18); ctx.clip();
  ctx.fillStyle=lk.jersey; ctx.globalAlpha=0.22; ctx.beginPath(); ctx.arc(x+80,y+h-60,80,0,Math.PI*2); ctx.fill(); ctx.globalAlpha=1;
  const k=1.95*Math.min(lk.size,1.2); ctx.translate(x+80,y+h-12); ctx.scale(k,k);
  drawAthlete({x:0,y:0,lean:0,spd:0,run:0},Object.assign({},lk,{dir:1}),{x:14*lk.armL,y:-34},{x:-12,y:-26},false,false);
  ctx.restore();
  ctx.fillStyle=C.warn; rr(x+12,y+12,84,24,12); ctx.fill(); text("BOSS",x+54,y+24,BODY(12,900),C.navy,"center");
  drawCrown(x+105,y+30,9);
  const tx=x+160; let fs=24; ctx.font=DISP(fs); while(fs>14 && ctx.measureText(b.name.toUpperCase()).width>w-176){fs-=2; ctx.font=DISP(fs);}
  text(b.name.toUpperCase(),tx,y+30,DISP(fs),C.ink);
  text("ABILITIES",tx,y+62,BODY(12,900),C.muted);
  b.ab.forEach((a,j)=>{const cx=tx+(j%2)*112, cy=y+84+Math.floor(j/2)*28;
    ctx.fillStyle=mix(lk.jersey,"#1B2340",0.35); rr(cx,cy-11,106,22,11); ctx.fill();
    let f=11; ctx.font=BODY(f,900); while(f>8 && ctx.measureText(ABIL[a]).width>98){f--; ctx.font=BODY(f,900);}
    text(ABIL[a],cx+53,cy,BODY(f,900),C.ink,"center");});
  const sy=y+84+Math.ceil(b.ab.length/2)*28+10;
  text("SIGNATURE MOVE",tx,sy,BODY(12,900),C.muted);
  text(b.sig,tx,sy+22,DISP(16),C.warn);
  text(SIG_INFO[b.sk],tx,sy+42,BODY(12,800),C.ink);
  text("Beat him to finish Level "+(i+1),tx,y+h-22,BODY(12,800),C.muted);
}
