import sys
f = sys.argv[1]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

# --- joystick now also reads up/down (only used for the steal move) ---
once("let keyJoy=0, touchJoy=0, jumpQueued=false, shootKey=false, shootTouch=false;",
     "let keyJoy=0, touchJoy=0, keyJoyY=0, touchJoyY=0, jumpQueued=false, shootKey=false, shootTouch=false;\n"
     "// stealing: on defence the SHOOT button becomes STEAL\n"
     "const STEAL_REACH=48, STEAL_COOLDOWN=0.8;\n"
     "let stealCool=0, stealSwipe=0, prevAction=false, stealMsg={text:\"\",t:0};")
once("""  else if(q.x<HALF && q.y>200){role="joy";touchJoy=clamp((q.x-JOY.x)/40,-1,1);}""",
     """  else if(q.x<HALF && q.y>200){role="joy";touchJoy=clamp((q.x-JOY.x)/40,-1,1);touchJoyY=clamp((q.y-JOY.y)/40,-1,1);}""")
once("""  if(roles.get(e.pointerId)==="joy"){const q=toLocal(e);touchJoy=clamp((q.x-JOY.x)/40,-1,1);}""",
     """  if(roles.get(e.pointerId)==="joy"){const q=toLocal(e);touchJoy=clamp((q.x-JOY.x)/40,-1,1);touchJoyY=clamp((q.y-JOY.y)/40,-1,1);}""")
once("""  if(role==="joy") touchJoy=0;""", """  if(role==="joy"){touchJoy=0; touchJoyY=0;}""")
once("""function keyJoyUpdate(){keyJoy=((keys.has("ArrowRight")||keys.has("d"))?1:0)-((keys.has("ArrowLeft")||keys.has("a"))?1:0);}""",
     """function keyJoyUpdate(){keyJoy=((keys.has("ArrowRight")||keys.has("d"))?1:0)-((keys.has("ArrowLeft")||keys.has("a"))?1:0);
  keyJoyY=(keys.has("ArrowDown")||keys.has("s"))?1:0;}""")
once("""cv.addEventListener("blur",()=>{keys.clear();keyJoy=0;shootKey=false;});""",
     """cv.addEventListener("blur",()=>{keys.clear();keyJoy=0;keyJoyY=0;shootKey=false;});""")
once("""  if(["ArrowLeft","ArrowRight","ArrowUp"," ","a","d","w","k"].includes(k)) e.preventDefault();""",
     """  if(["ArrowLeft","ArrowRight","ArrowUp","ArrowDown"," ","a","d","w","s","k"].includes(k)) e.preventDefault();""")

# --- the steal itself, checked every frame in the game loop ---
once("""  const joy=clamp(touchJoy||keyJoy,-1,1);
  const shootDown=shootKey||shootTouch;""",
     """  const joy=clamp(touchJoy||keyJoy,-1,1), joyY=clamp(touchJoyY||keyJoyY,-1,1);
  const shootDown=shootKey||shootTouch;
  // STEAL: on defence, close to the ball handler, joystick pulled down and towards him, then press STEAL
  if(stealCool>0) stealCool-=dt;
  if(stealSwipe>0) stealSwipe-=dt;
  if(stealMsg.t>0) stealMsg.t-=dt;
  const pressed=shootDown && !prevAction; prevAction=shootDown;
  if(pressed && cpuOn && owner===d && ball.state==="held" && !cdunk.on) trySteal(joy,joyY);""")
once("// ---------- player shooting ----------", """// ---------- stealing ----------
function trySteal(joy,joyY){
  if(stealCool>0) return;
  const toward=Math.sign(d.x-p.x)||1;
  const diagonal = joyY>0.45 && joy*toward>0.3;   // down and towards the ball handler
  stealSwipe=0.3; stealCool=STEAL_COOLDOWN;
  if(!diagonal){stealMsg={text:"Pull the joystick down towards him!",t:1.2}; return;}
  if(Math.abs(d.x-p.x)>STEAL_REACH){stealMsg={text:"Too far away!",t:1}; return;}
  // he can only lose it while dribbling, not once the ball is up for a shot
  const chance = (cpu.charging||!d.ground) ? 0 : SKILL.stealChance;
  if(Math.random()<chance){
    stats.stl++; owner=p; ball.state="held"; ball.live=false; needRelease=true;
    cpu.charging=false; charge.on=false;
    say(pick("steal"),"You stole it from "+NAME.d+"!",C.info);
    setMood(p,"happy"); setMood(d,"shock"); celebrateFor(p);
    lastShot="Steal by "+NAME.p;
  } else {
    stealMsg={text:pick("stealMiss"),t:1};
  }
}

// ---------- player shooting ----------""")
once('''  lucky:["Shooter's roll!",''', '''  steal:["PICKPOCKET!","STOLEN!","Hand in the cookie jar!","Too slow!","Snatched it!","Ball don't lie... it's MINE!"],
  stealMiss:["Missed the steal!","Just missed it!","Swipe and a miss!","He held on!"],
  lucky:["Shooter's roll!",''')

# --- how good a steal chance is: easier on early levels ---
once("let SKILL=Object.assign({},SKILL_BASE);", "SKILL_BASE.stealChance=0.45;\nlet SKILL=Object.assign({},SKILL_BASE);")
once("    dblChance:L(0.05,0.5)};", "    dblChance:L(0.05,0.5), stealChance:L(0.6,0.3)};")

# --- stats ---
once("const stats={score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0};",
     "const stats={score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0,stl:0};")
once("  Object.assign(stats,{score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0});",
     "  Object.assign(stats,{score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0,stl:0});\n  stealCool=0; stealSwipe=0; stealMsg.t=0; prevAction=true;")
once('''["Best streak",String(stats.best)],["Wins vs computer",String(wins[human]||0)]];''',
     '''["Best streak",String(stats.best)],["Steals",String(stats.stl)]];''')

# --- the swipe: the front arm reaches down for the ball ---
once("""  let hx=12, hy=-26, ox=-12, oy=-24;
  if(dunk.on){""", """  let hx=12, hy=-26, ox=-12, oy=-24;
  if(stealSwipe>0 && owner!==p){hx=(Math.sign(d.x-p.x)||1)*26; hy=-24;}
  else if(dunk.on){""")

# --- controls: knob moves both ways; SHOOT becomes STEAL on defence ---
once("""  const jx=JOY.x+clamp(touchJoy||keyJoy,-1,1)*26;
  ctx.fillStyle=C.chalk; ctx.beginPath(); ctx.arc(jx,JOY.y,24,0,Math.PI*2); ctx.fill();""",
     """  const jx=JOY.x+clamp(touchJoy||keyJoy,-1,1)*26, jy=JOY.y+clamp(touchJoyY||keyJoyY,-1,1)*20;
  if(cpuOn && owner===d){   // on defence: little arrows show the steal directions
    ctx.strokeStyle=C.info; ctx.lineWidth=2.5;
    for(const sx of [-1,1]){ctx.beginPath(); ctx.moveTo(JOY.x+sx*22,JOY.y+30); ctx.lineTo(JOY.x+sx*32,JOY.y+40);
      ctx.moveTo(JOY.x+sx*32,JOY.y+32); ctx.lineTo(JOY.x+sx*32,JOY.y+40); ctx.lineTo(JOY.x+sx*24,JOY.y+40); ctx.stroke();}
  }
  ctx.fillStyle=C.chalk; ctx.beginPath(); ctx.arc(jx,jy,24,0,Math.PI*2); ctx.fill();""")
once("""  const canShoot=owner===p && ball.state==="held" && !dunk.on;""",
     """  if(cpuOn && (owner===d || (ball.state==="flight" && ball.shooter===d))){   // defence: STEAL instead of SHOOT
    const near=Math.abs(d.x-p.x)<=STEAL_REACH && owner===d, down=shootKey||shootTouch;
    ctx.globalAlpha=stealCool>0?0.5:1;
    if(near){const pulse=4+Math.sin(performance.now()/120)*3;
      ctx.strokeStyle=C.green; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(SHOOT.x,SHOOT.y,SHOOT.r+pulse,0,Math.PI*2); ctx.stroke();}
    ctx.fillStyle="#14A3B8"; ctx.beginPath(); ctx.arc(SHOOT.x,SHOOT.y,down?39:SHOOT.r,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle=down?C.warn:C.ink; ctx.lineWidth=3; ctx.stroke();
    text("STEAL",SHOOT.x,SHOOT.y-4,DISP(14),C.ink,"center");
    text(near?"in reach!":"get closer",SHOOT.x,SHOOT.y+14,BODY(10,900),C.ink,"center");
    ctx.globalAlpha=1;
    return;
  }
  const canShoot=owner===p && ball.state==="held" && !dunk.on;""")

# --- defence hint and the steal message over the player ---
once('''    text("Stay in front, JUMP to block, tap again at the top for a double jump",cx,42,BODY(12,900),C.ink,"center");''',
     '''    text("JUMP to block · joystick down towards him + STEAL to steal",cx,42,BODY(12,900),C.ink,"center");''')
once('''  if(dblMiss>0){ctx.globalAlpha''', '''  if(stealMsg.t>0){ctx.globalAlpha=Math.min(1,stealMsg.t*3); text(stealMsg.text,p.x,p.y-112,BODY(13,900),C.warn,"center"); ctx.globalAlpha=1;}
  if(dblMiss>0){ctx.globalAlpha''')

open(f, "w").write(s)
print("patched")
