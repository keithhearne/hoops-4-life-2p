import sys, re
f = sys.argv[1]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

# ===== 1. behind the basket: no scoring =====
once('''  far:{name:"Past half court", n:[75,80], f:[76,79], pts:3, cpu:0.2}''',
     '''  far:{name:"Past half court", n:[75,80], f:[76,79], pts:3, cpu:0.2, fill:0.7},
  behind:{name:"Behind the basket", n:[0,0], f:[0,0], pts:2, cpu:0, behind:true}''')
once("function zoneFor(x,rim){const xx=rim.dir>0?x:W-x; return xx>THREE?ZONES.inside:(xx>HALF?ZONES.mid:ZONES.far);}",
     "function zoneFor(x,rim){\n"
     "  if((rim.dir>0 && x>rim.x+4)||(rim.dir<0 && x<rim.x-4)) return ZONES.behind;   // past the rim: the backboard is in the way\n"
     "  const xx=rim.dir>0?x:W-x; return xx>THREE?ZONES.inside:(xx>HALF?ZONES.mid:ZONES.far);\n}")
once("const KEY={x0:684,x1:804},", "const KEY={x0:684,x1:762},")   # dunk zone only in front of the rim
once('''  const make=!auto && pw>=range[0] && pw<=range[1];
  const tx=targetFor(pw,range,auto), sp=shotPath(h.x,h.y,tx,RR.y);
  const missType=auto?"auto":(pw<range[0]?(pw<range[0]-25?"air":"short"):"long");''',
     '''  const make=!auto && !z.behind && pw>=range[0] && pw<=range[1];
  const tx=z.behind?RR.x:targetFor(pw,range,auto), sp=shotPath(h.x,h.y,tx,RR.y);   // from behind it flies at the hoop and hits the back of the board
  const missType=z.behind?"behind":(auto?"auto":(pw<range[0]?(pw<range[0]-25?"air":"short"):"long"));''')
once('''  lastShot = auto ? "Held too long: the ball flew off at 100"''',
     '''  lastShot = z.behind ? "No shot from behind the basket: get in front of it" : auto ? "Held too long: the ball flew off at 100"''')
# the back of the backboard is solid too
once('''      if(h.faceDir<0 && ball.x+BALL_R>h.face && ball.x<h.face+7 && ball.vx>0){''',
     '''      const back=h.face-h.faceDir*7;   // the back of the board
      if(h.faceDir<0 && ball.x-BALL_R<back && ball.x>h.face+3 && ball.vx<0){ball.x=back+BALL_R; ball.vx=-ball.vx*BOUNCE.board; hit=hit||"board"; play("board",Math.abs(ball.vx)/BOUNCE.board);}
      if(h.faceDir>0 && ball.x+BALL_R>back && ball.x<h.face-3 && ball.vx>0){ball.x=back-BALL_R; ball.vx=-ball.vx*BOUNCE.board; hit=hit||"board"; play("board",Math.abs(ball.vx)/BOUNCE.board);}
      if(h.faceDir<0 && ball.x+BALL_R>h.face && ball.x<h.face+7 && ball.vx>0){''')
once("function checkRollIn(prevY){", "function checkRollIn(prevY){\n  if(ball.missType===\"behind\") return;   // a shot from behind can't sneak in")
once('''  stealMiss:["Missed the steal!",''', '''  behind:["Off the back of the board!","Wrong side of the glass!","You can't shoot through the backboard!"],
  stealMiss:["Missed the steal!",''')
s = s.replace('''const tip={auto:"Let go before the bar is full",''', '''const tip={behind:"Get in front of the basket to shoot",auto:"Let go before the bar is full",''')
# the power bar says there's no shot from back there
once('''  const by=y+h*(1-range[1]/100), bh=h*(range[1]-range[0])/100;
  ctx.fillStyle="rgba(61,220,151,0.8)"; ctx.fillRect(x,by,w,bh);
  ctx.fillStyle=C.ink; ctx.fillRect(x,by-1.5,w,3); ctx.fillRect(x,by+bh-1.5,w,3);
  ctx.fillStyle=C.red; ctx.fillRect(x,y,w,4);
  ctx.restore();
  text("100",x+38,y+2,BODY(11,900),"#FF8A8A");
  text(String(range[1]),x+38,by-3,BODY(11,900),C.green);
  text(String(range[0]),x+38,by+bh+5,BODY(11,900),C.green);''',
'''  const by=y+h*(1-range[1]/100), bh=h*(range[1]-range[0])/100;
  if(!z.behind){
    ctx.fillStyle="rgba(61,220,151,0.8)"; ctx.fillRect(x,by,w,bh);
    ctx.fillStyle=C.ink; ctx.fillRect(x,by-1.5,w,3); ctx.fillRect(x,by+bh-1.5,w,3);
  }
  ctx.fillStyle=C.red; ctx.fillRect(x,y,w,4);
  ctx.restore();
  text("100",x+38,y+2,BODY(11,900),"#FF8A8A");
  if(!z.behind){
    text(String(range[1]),x+38,by-3,BODY(11,900),C.green);
    text(String(range[0]),x+38,by+bh+5,BODY(11,900),C.green);
  } else text("NO SHOT",x+38,y+h/2,BODY(12,900),C.warn);''')
# the info bar too
once('''    const z=zoneFor(p.x,RR);
    text((cpuOn?"YOUR BALL · ":"PRACTICE · ")+z.name.toUpperCase(),cx,26,BODY(11,900),C.muted,"center");
    text("sweet spot "+z.n[0]+"–"+z.n[1]+" · fade "+z.f[0]+"–"+z.f[1],cx,42,BODY(13,900),C.ink,"center");''',
     '''    const z=zoneFor(p.x,RR);
    text((cpuOn?"YOUR BALL · ":"PRACTICE · ")+z.name.toUpperCase(),cx,26,BODY(11,900),z.behind?C.warn:C.muted,"center");
    text(z.behind?"Can't score from here: move in front of the basket":"sweet spot "+z.n[0]+"–"+z.n[1]+" · fade "+z.f[0]+"–"+z.f[1]+(z.fill?" · fast bar!":""),cx,42,BODY(13,900),C.ink,"center");''')

# ===== 2. past half court the power bar fills faster =====
once("const before=charge.power; charge.power+=dt/FILL*100; charge.holdT+=dt;",
     "const before=charge.power; charge.power+=dt/(zoneFor(p.x,RR).fill||FILL)*100; charge.holdT+=dt;")
once("const z=charge.zone, est=(z.n[0]+z.n[1])/200*FILL;", "const z=charge.zone, est=(z.n[0]+z.n[1])/200*(z.fill||FILL);")

# ===== 3. jump ball: no referee, the ball hangs at centre court with a 3-2-1 countdown, then drops =====
a = s.index("function startTip(){"); b = s.index("function endTip(w){")
s = s[:a] + '''function startTip(){
  owner=null; ball.state="tip"; ball.x=TIP_X; ball.y=TIP_Y; ball.vx=0; ball.vy=0;
  p.x=TIP_X-26; d.x=TIP_X+26; d.jumped=false; msg.t=0;
  // when the computer jumps after the drop: the perfect moment, plus a random error that gets smaller on later levels
  const ideal=0.1;
  tip={on:true,t:0,tt:0,tossed:false,whistled:false,beeps:0,fade:0,
    cpuAt: Math.random()<SKILL.noReact*0.5 ? 99 : Math.max(0,ideal+(Math.random()*2-1)*SKILL.timingNoise*0.55)};
}
function updateTip(dt){
  tip.t+=dt;
  if(!tip.tossed){
    ball.x=TIP_X; ball.y=TIP_Y+Math.sin(tip.t*5)*2; ball.rot=(ball.rot||0)+dt*1.5;   // hovering, gently bobbing
    if(tip.t>=tip.beeps && tip.beeps<TIP_COUNT){tip.beeps++; play("beep");}
    if(tip.t>=TIP_COUNT){tip.tossed=true; tip.tt=0; ball.vy=0; ball.y=TIP_Y; play("whistle");}
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
function drawCountdown(){
  if(!tip.on || tip.tossed) return;
  const n=Math.max(1,TIP_COUNT-Math.floor(tip.t)), frac=tip.t%1, size=58+(1-frac)*26;
  ctx.save(); ctx.globalAlpha=Math.min(1,(1-frac)*3);
  ctx.font=DISP(size); ctx.textAlign="center"; ctx.textBaseline="middle";
  ctx.lineWidth=8; ctx.lineJoin="round"; ctx.strokeStyle=C.navy; ctx.strokeText(String(n),TIP_X,TIP_Y+70);
  ctx.fillStyle=C.warn; ctx.fillText(String(n),TIP_X,TIP_Y+70);
  ctx.restore();
}
''' + s[b:]
once("const TIP_X=422, TIP_TOSS_AT=1.0, TIP_WHISTLE_AT=0.55;", "const TIP_X=422, TIP_Y=70, TIP_COUNT=3;   // the ball hangs this high, then drops after a 3-2-1 countdown")
once("  drawCourt(); drawNetLayer(false); drawRef(); drawCpu();", "  drawCourt(); drawNetLayer(false); drawCpu();")
once("  drawPlayer(); drawBall(); drawNetLayer(true); drawBoardFx();", "  drawPlayer(); drawBall(); drawNetLayer(true); drawBoardFx(); drawCountdown();")
once('''    text("Tap JUMP as the ball comes down. Highest hand wins it",cx,42,BODY(13,900),C.ink,"center");''',
     '''    text("The ball drops after the countdown: tap JUMP to win it",cx,42,BODY(13,900),C.ink,"center");''')
once("  tick(){ tone(1500,0.06,{vol:0.13});", "  beep(){ tone(880,0.14,{vol:0.16,type:\"triangle\"}); },\n  tick(){ tone(1500,0.06,{vol:0.13});")
# the referee is no longer used
a = s.index("const REF_LOOK="); b = s.index("\n", s.index("brow:\"#2A2A2A\"", a)) + 1
s = s[:a] + s[b:]
a = s.index("function drawRef(){"); b = s.index("function takeBall(e){")
s = s[:a] + s[b:]

open(f, "w").write(s)
print("patched")
