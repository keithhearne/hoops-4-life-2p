import sys
f, blk = sys.argv[1], sys.argv[2]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

# ===== sound engine =====
once("// ---------- dunk effects: thunder, breaking glass", open(blk).read() + "\n// ---------- dunk effects: thunder, breaking glass")

# ===== windmill: under and over =====
once('''  if(dk.t<RISE){
    const u=Math.min(1,Math.max(0,(dk.t-dk.w0)/Math.max(0.08,RISE-dk.w0))), th=-Math.PI/2-Math.PI*u;
    return {x:sx+dir*Math.cos(th)*L, y:sy+Math.sin(th)*L};
  }
  const u=Math.min(1,(dk.t-RISE)/SLAM), th=Math.PI/2-Math.PI*0.9*u, k=u*u;''',
'''  if(dk.t<RISE){
    // under and over: the ball drops down by the hip, then swings back behind and up over the top
    const u=Math.min(1,Math.max(0,(dk.t-dk.w0)/Math.max(0.08,RISE-dk.w0)));
    const down={x:sx, y:sy+L};
    if(u<0.22){const k=u/0.22, from={x:e.x+dir*10,y:e.y-96}; return {x:from.x+(down.x-from.x)*k, y:from.y+(down.y-from.y)*k};}
    const th=Math.PI/2+Math.PI*((u-0.22)/0.78);   // down -> behind -> straight up
    return {x:sx+dir*Math.cos(th)*L, y:sy+Math.sin(th)*L};
  }
  const u=Math.min(1,(dk.t-RISE)/SLAM), th=-Math.PI/2+Math.PI*0.45*u, k=u*u;   // from up, forward and down into the rim''')

# ===== jump ball =====
once("function takeBall(e){", '''// ---------- jump ball to start a game: the referee whistles and tosses the ball up between the two players ----------
const TIP_X=422, TIP_TOSS_AT=1.0, TIP_WHISTLE_AT=0.55;
let tip={on:false,t:0,tt:0,tossed:false,whistled:false,cpuAt:99,fade:0};
const REF_LOOK={dir:1,jersey:"#F4F4F1",trim:"#22232B",shorts:"#22232B",skin:"#C98F66",skinDark:"#A8714E",hair:"#2A2A2A",hairHi:"#4A4A4A",
  brow:"#2A2A2A",eye:"#3A2A1A",style:"crop",gapTeeth:false,bigEars:false,num:"",numCol:"#22232B",shoe:"#22232B",sole:"#F4F4F1",sock:"#22232B",stripes:true};
function startTip(){
  owner=null; ball.state="tip"; ball.x=TIP_X; ball.y=FLOOR-62; ball.vx=0; ball.vy=0;
  p.x=TIP_X-26; d.x=TIP_X+26; d.jumped=false;
  // when the computer jumps: the perfect moment, plus a random error that gets smaller on later levels
  const ideal=0.4;
  tip={on:true,t:0,tt:0,tossed:false,whistled:false,fade:0,
    cpuAt: Math.random()<SKILL.noReact*0.5 ? 99 : ideal+(Math.random()*2-1)*SKILL.timingNoise*0.55};
  say("JUMP BALL!","Tap JUMP as the ball comes down to win it",C.warn); msg.t=2.4;
}
function updateTip(dt){
  tip.t+=dt;
  if(!tip.whistled && tip.t>=TIP_WHISTLE_AT){tip.whistled=true; play("whistle");}
  if(!tip.tossed){
    ball.x=TIP_X; ball.y=FLOOR-62;
    if(tip.t>=TIP_TOSS_AT){tip.tossed=true; tip.tt=0; ball.vy=-Math.sqrt(2*GB*(FLOOR-62-135));}   // up to about head-and-a-half height
    return;
  }
  tip.tt+=dt;
  ball.vy+=GB*dt; ball.y+=ball.vy*dt; ball.rot=(ball.rot||0)+dt*3;
  if(!d.jumped && d.ground && tip.tt>=tip.cpuAt){cpuJump(-380); d.willDbl=false; d.jumped=true;}
  // whoever gets a hand to it first tips it to himself
  const ph=!p.ground?{x:p.x+20,y:p.y-84}:null, ch=!d.ground?{x:d.x-20,y:d.y-84}:null;
  const pt=ph && Math.hypot(ball.x-ph.x,ball.y-ph.y)<22, ct=ch && Math.hypot(ball.x-ch.x,ball.y-ch.y)<22;
  if(pt||ct){
    const w=(pt&&ct)?(ph.y<ch.y?p:(ch.y<ph.y?d:(Math.random()<0.5?p:d))):(pt?p:d);
    endTip(w); return;
  }
  if(ball.vy>0 && ball.y>FLOOR-70) endTip(null);   // nobody touched it
}
function endTip(w){
  tip.on=false; tip.fade=0.6;
  if(w){
    play("smack"); takeBall(w);
    say((w===p?NAME.p:NAME.d)+" wins the tip!", w===p?"Your ball, go score on the right hoop":"Get in front of him: JUMP to block, or STEAL", w===p?C.info:C.warn);
  } else {
    ball.state="free"; ball.vx=(Math.random()-0.5)*80; ball.vy=0; ball.timer=0.2; ball.live=false;
    say("Nobody got it!","Loose ball, go and grab it",C.warn);
  }
}
function drawRef(){
  if(!(tip.on||tip.fade>0)) return;
  ctx.save(); ctx.globalAlpha=tip.on?1:Math.max(0,tip.fade/0.6);
  const holding=tip.on && !tip.tossed, rx=TIP_X-(tip.on?0:(0.6-tip.fade)*90);   // walks off after the tip
  const hand=holding?{x:0,y:-62+0}:{x:2,y:-90}, other={x:7,y:-62};   // other hand at the whistle
  ctx.translate(0,-4); ctx.globalAlpha*=0.95;
  drawAthlete({x:rx,y:FLOOR,lean:0,spd:tip.on?0:60,run:performance.now()/90},REF_LOOK,hand,other,false,false);
  ctx.restore();
}
function takeBall(e){''')
once('''  inbound("p"); screen="play";
  if(mode==="level")''', '''  inbound("p"); screen="play"; tip.on=false; tip.fade=0;
  if(cpuOn) startTip();
  else if(mode==="level")''')
once('''  else if(cpuOn) say(NAME.p+" vs "+NAME.d,"First to "+WIN+" wins",C.ink);
  else say("Shooting practice"''', '''  else say("Shooting practice"''')
# players stay put during the jump ball (they can only jump)
once("    p.x=clamp(p.x+joy*(charge.on?70:170)*dt,24,812);", "    if(!tip.on) p.x=clamp(p.x+joy*(charge.on?70:170)*dt,24,812);")
once('''function cpuUpdate(dt){
  if(cdunk.on){''', '''function cpuUpdate(dt){
  if(tip.on){ updateTip(dt); body(d,dt); return; }
  if(cdunk.on){''')
once("  updateNets(dt); updateFx(dt);", "  updateNets(dt); updateFx(dt); if(tip.fade>0) tip.fade-=dt;")
# arms up while jumping for the tip
once("  if(stealSwipe>0 && owner!==p){hx=(Math.sign(d.x-p.x)||1)*26; hy=-24;}",
     "  if(tip.on && !p.ground){hx=20; hy=-84;}\n  else if(stealSwipe>0 && owner!==p){hx=(Math.sign(d.x-p.x)||1)*26; hy=-24;}")
once('''  if(cdunk.on && cdunk.wind && !cdunk.resolved){hx=ball.x-d.x;''', '''  if(tip.on && !d.ground){hx=-20; hy=-84;}
  else if(cdunk.on && cdunk.wind && !cdunk.resolved){hx=ball.x-d.x;''')
# referee drawn behind the players
once("  drawCourt(); drawNetLayer(false); drawCpu();", "  drawCourt(); drawNetLayer(false); drawRef(); drawCpu();")
# striped referee shirt
once("  ctx.quadraticCurveTo(-10,-44,-8,-51); ctx.closePath(); ctx.fill();",
     "  ctx.quadraticCurveTo(-10,-44,-8,-51); ctx.closePath(); ctx.fill();\n"
     "  if(lk.stripes){ctx.save(); ctx.clip(); ctx.fillStyle=\"#22232B\"; for(let x=-12;x<13;x+=6) ctx.fillRect(x,-52,3,23); ctx.restore();}")
# the info bar during the jump ball
once('''  if(cpuOn && playerDefending()){
    text("DEFENSE · FIRST TO "+WIN''', '''  if(tip.on){
    text("JUMP BALL",cx,26,BODY(11,900),C.warn,"center");
    text("Tap JUMP as the ball comes down. Highest hand wins it",cx,42,BODY(13,900),C.ink,"center");
  } else if(cpuOn && playerDefending()){
    text("DEFENSE · FIRST TO "+WIN''')

# ===== sound hooks =====
# phones need a tap before any sound, and buttons click
once("cv.addEventListener(\"pointerdown\",e=>{\n  const q=toLocal(e); let role=null;", "cv.addEventListener(\"pointerdown\",e=>{\n  audioInit();\n  const q=toLocal(e); let role=null;")
once("      if(q.x>=u.x&&q.x<=u.x+u.w&&q.y>=u.y&&q.y<=u.y+u.h){u.fn(); e.preventDefault(); return;}}",
     "      if(q.x>=u.x&&q.x<=u.x+u.w&&q.y>=u.y&&q.y<=u.y+u.h){play(\"click\"); u.fn(); e.preventDefault(); return;}}")
once("  keys.add(k); keyJoyUpdate();", "  audioInit(); keys.add(k); keyJoyUpdate();")
# ball on the floor, the rim and the glass
once("    if(ball.vy>0){ball.vy=-ball.vy*BOUNCE.floor; ball.vx*=0.9;}", "    if(ball.vy>0){play(\"bounce\",ball.vy); ball.vy=-ball.vy*BOUNCE.floor; ball.vx*=0.9;}")
once('''    for(const [px,py] of h.edges) if(hitPoint(px,py,2.5,BOUNCE.rim)){hit="rim"; netKick(h.net,1.5,0);}''',
     '''    for(const [px,py] of h.edges) if(hitPoint(px,py,2.5,BOUNCE.rim)){hit="rim"; netKick(h.net,1.5,0); play("rim",Math.hypot(ball.vx,ball.vy)/BOUNCE.rim);}''')
once("ball.x=h.face-BALL_R; ball.vx=-ball.vx*BOUNCE.board; ball.vy*=0.92; hit=hit||\"board\";}",
     "ball.x=h.face-BALL_R; ball.vx=-ball.vx*BOUNCE.board; ball.vy*=0.92; hit=hit||\"board\"; play(\"board\",Math.abs(ball.vx)/BOUNCE.board);}")
once("ball.x=h.face+BALL_R; ball.vx=-ball.vx*BOUNCE.board; ball.vy*=0.92; hit=hit||\"board\";}",
     "ball.x=h.face+BALL_R; ball.vx=-ball.vx*BOUNCE.board; ball.vy*=0.92; hit=hit||\"board\"; play(\"board\",Math.abs(ball.vx)/BOUNCE.board);}")
# dribbling: a bounce each time the ball touches the floor
once('''  e.drib=(e.drib||0)+dt*(7+Math.min(6,Math.abs(e.spd||0)*0.03));''',
     '''  const before=Math.floor((e.drib||0)/Math.PI+0.5);
  e.drib=(e.drib||0)+dt*(7+Math.min(6,Math.abs(e.spd||0)*0.03));
  if(Math.floor(e.drib/Math.PI+0.5)!==before) play("dribble");''')
# baskets: swish and the crowd; dunks get the slam; the final basket gets the long whistle
once('''    netKick(byP?1:0, ball.dunk?9:3, ball.dunk?(byP?2:-2):0); // swish, or a hard yank on a dunk''',
     '''    netKick(byP?1:0, ball.dunk?9:3, ball.dunk?(byP?2:-2):0); // swish, or a hard yank on a dunk
    if(ball.dunk) play("slam"); else play("swish");
    play("cheer", ball.wind?1.6:(ball.dunk?1.3:(ball.far?1.5:(ball.pts===3?1.1:0.7))));''')
once('''      msg.t=3; gameOverT=3;''', '''      msg.t=3; gameOverT=3; SND.last.whistle=0; play("whistle",true);''')
# lightning, glass and the cracked screen
once('''  boardFx={t:T,T,side,shatter:wind,shards,bolts:makeBolts(side),flash:0.32,boltT:wind?0.7:0.5};''',
     '''  boardFx={t:T,T,side,shatter:wind,shards,bolts:makeBolts(side),flash:0.32,boltT:wind?0.7:0.5};
  play("thunder"); play("glass",wind);''')
once('''  crackFx={t:CRACK_T,T:CRACK_T,lines,rings,branches,cx,cy,shook:false};''',
     '''  crackFx={t:CRACK_T,T:CRACK_T,lines,rings,branches,cx,cy,shook:false};
  play("crack");''')
once("crackFx.shook=true; shakeT=Math.max(shakeT,0.3);", "crackFx.shook=true; shakeT=Math.max(shakeT,0.3); SND.last.glass=0; play(\"glass\",true);")
# blocks, saves, steals and jumps
once('''function blocked(by,save){
  const shooterDir''', '''function blocked(by,save){
  play("smack");
  const shooterDir''')
once("    stats.stl++; owner=p; ball.state=\"held\";", "    play(\"swipe\"); play(\"squeak\"); play(\"cheer\",0.8);\n    stats.stl++; owner=p; ball.state=\"held\";")
once('''    stealMsg={text:pick("stealMiss"),t:1};''', '''    play("swipe"); stealMsg={text:pick("stealMiss"),t:1};''')
once("    if(jumpQueued && p.ground){p.vy=-380;p.ground=false;p.dbl=false;}", "    if(jumpQueued && p.ground){p.vy=-380;p.ground=false;p.dbl=false; play(\"squeak\");}")
# a tick when the power bar enters the green zone, to help with timing
once('''      charge.power+=dt/FILL*100; charge.holdT+=dt;''', '''      const before=charge.power; charge.power+=dt/FILL*100; charge.holdT+=dt;
      {const z=zoneFor(p.x,RR), lo=(charge.fade?z.f:z.n)[0]; if(before<lo && charge.power>=lo) play("tick");}''')
# the crowd groans at your misses
once('''      say(pick(ball.missType), tip+(cpuOn?" · grab the rebound!":""), C.warn);''',
     '''      say(pick(ball.missType), tip+(cpuOn?" · grab the rebound!":""), C.warn); play("groan");''')

# ===== sound on/off: title screen and pause menu, remembered on the phone =====
once('''  text(BOYS.zackie.name+"  "+at("zackie")+"     "+BOYS.keelan.name+"  "+at("keelan"),cx,346,BODY(15,900),C.ink,"center");''',
     '''  text(BOYS.zackie.name+"  "+at("zackie")+"     "+BOYS.keelan.name+"  "+at("keelan"),cx,346,BODY(15,900),C.ink,"center");
  button(cx-60,358,120,26,SND.on?"SOUND ON":"SOUND OFF",{size:12,outline:"rgba(255,255,255,0.3)"},toggleSound);''')
once('''  button(bx,248,300,44,"MAIN MENU",{outline:"rgba(255,255,255,0.3)"},toMap);
}''', '''  button(bx,248,300,44,"MAIN MENU",{outline:"rgba(255,255,255,0.3)"},toMap);
  button(bx,302,300,40,SND.on?"SOUND: ON":"SOUND: OFF",{outline:"rgba(255,255,255,0.3)",size:15},toggleSound);
}
function toggleSound(){SND.on=!SND.on; saveGame(); if(SND.on){audioInit(); SND.last.click=0; play("click");}}''')
once("JSON.stringify({kits,human,wins,progress})", "JSON.stringify({kits,human,wins,progress,sound:SND.on})")
once("    if(s.progress) progress=Object.assign({zackie:0,keelan:0},s.progress);",
     "    if(s.progress) progress=Object.assign({zackie:0,keelan:0},s.progress);\n    if(s.sound===false) SND.on=false;")

open(f, "w").write(s)
print("patched")
