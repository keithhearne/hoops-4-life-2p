import sys
f, blk = sys.argv[1], sys.argv[2]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

once("// ---------- stealing ----------", open(blk).read() + "\n// ---------- stealing ----------")

# windmill: joystick up while rising on a dunk
once("  if(dunk.on) updateDunk(dt);",
     """  if(dunk.on && !dunk.wind && !dunk.resolved && dunk.t<RISE*0.8 && joyY<-0.5){
    dunk.wind=true; dunk.w0=dunk.t; dunk.success=Math.random()<WIND_MAKE; lastShot="WINDMILL! · 40% chance";
  }
  if(dunk.on) updateDunk(dt);""")
once("  updateNets(dt);\n  if(msg.t>0) msg.t-=dt;", "  updateNets(dt); updateFx(dt);\n  if(msg.t>0) msg.t-=dt;")
once("Object.assign(dunk,{on:true,t:0,x0:p.x,success:Math.random()<0.5,resolved:false,hang:0});",
     "Object.assign(dunk,{on:true,t:0,x0:p.x,success:Math.random()<0.5,resolved:false,hang:0,wind:false,w0:0});")
once("Object.assign(cdunk,{on:true,t:0,x0:d.x,success:Math.random()<SKILL.dunkMake,resolved:false,hang:0});",
     "const wind=Math.random()<SKILL.windTry;   // the computer sometimes goes for a windmill too\n"
     "  Object.assign(cdunk,{on:true,t:0,x0:d.x,success:Math.random()<(wind?WIND_MAKE:SKILL.dunkMake),resolved:false,hang:0,wind,w0:0.06});")
once("SKILL_BASE.stealChance=0.45;", "SKILL_BASE.stealChance=0.45; SKILL_BASE.windTry=0.25;")
once("stealChance:L(0.6,0.3), saveChance:L(0.08,0.45)};", "stealChance:L(0.6,0.3), saveChance:L(0.08,0.45), windTry:L(0.1,0.4)};")

# the ball follows the windmill arm
once("""    if(owner===p && dunk.on){
      const a={x:p.x+10,y:p.y-96};""", """    if(owner===p && dunk.on && dunk.wind) h=windmillHand(dunk,p,1,RR);
    else if(owner===d && cdunk.on && cdunk.wind) h=windmillHand(cdunk,d,-1,RL);
    else if(owner===p && dunk.on){
      const a={x:p.x+10,y:p.y-96};""")
once("""  else if(dunk.on){
    if(dunk.t<RISE){hx=10;hy=-96;ox=-16;oy=-66;}""", """  else if(dunk.on && dunk.wind && !dunk.resolved){hx=ball.x-p.x; hy=ball.y-p.y; ox=-14; oy=-64;}
  else if(dunk.on){
    if(dunk.t<RISE){hx=10;hy=-96;ox=-16;oy=-66;}""")
once("""  if(cdunk.on){
    if(cdunk.t<RISE){hx=-10;hy=-96;ox=16;oy=-66;}""", """  if(cdunk.on && cdunk.wind && !cdunk.resolved){hx=ball.x-d.x; hy=ball.y-d.y; ox=14; oy=-64;}
  else if(cdunk.on){
    if(cdunk.t<RISE){hx=-10;hy=-96;ox=16;oy=-66;}""")

# made dunks: thunder and glass; windmills shatter the board and crack the screen
once("""  Object.assign(ball,{shooter:e,make:dk.success,pts:2,far:false,fade:false,dunk:true});
  if(dk.success){ arrive(0); }""", """  Object.assign(ball,{shooter:e,make:dk.success,pts:2,far:false,fade:false,dunk:true,wind:!!dk.wind});
  if(dk.success){ startBoardFx(byP?"R":"L",dk.wind); if(dk.wind) startCrackFx(); arrive(0); }""")
assert s.count('ball.lucky?"lucky":(ball.dunk?"dunk":') == 2
s = s.replace('ball.lucky?"lucky":(ball.dunk?"dunk":', 'ball.lucky?"lucky":ball.wind?"windmill":(ball.dunk?"dunk":')
once('const BIG_PLAYS=["dunk","three","half","fire"];', 'const BIG_PLAYS=["dunk","windmill","three","half","fire"];')
once('''  save:["SAVED!",''', '''  windmill:["WINDMILL DUNK!"],
  save:["SAVED!",''')
once("    shooter:p,missType,dunk:false,lucky:false,live:false,saveTried:false,",
     "    shooter:p,missType,dunk:false,wind:false,lucky:false,live:false,saveTried:false,")
once('''    shooter:d,missType:over?"long":"short",dunk:false,lucky:false,live:false,''',
     '''    shooter:d,missType:over?"long":"short",dunk:false,wind:false,lucky:false,live:false,''')

# a shattered backboard is gone for a moment
once("""  ctx.fillStyle=C.chalk; rr(boardX,140,7,62,2); ctx.fill();""",
     """  if(!boardGone(side)){ctx.fillStyle=C.chalk; rr(boardX,140,7,62,2); ctx.fill();}
  else {ctx.fillStyle="rgba(205,235,255,0.8)"; ctx.fillRect(boardX,140,7,6); ctx.fillRect(boardX,196,7,6);}   // only jagged edges left""")

# drawing order: glass and lightning over the court, flash and screen cracks over everything
once("  drawPlayer(); drawBall(); drawNetLayer(true);", "  drawPlayer(); drawBall(); drawNetLayer(true); drawBoardFx();")
once("  drawMeter(); drawHUD(); drawControls(); drawMsg();\n}", "  drawMeter(); drawHUD(); drawControls(); drawMsg(); drawScreenFx();\n}")
once("  stealCool=0; stealSwipe=0; stealMsg.t=0; prevAction=true;",
     "  stealCool=0; stealSwipe=0; stealMsg.t=0; prevAction=true; boardFx.t=0; crackFx.t=0;")

# the dunk-zone hint mentions the windmill
once('''    text("Tap DUNK · 50% chance to slam it in",cx,42,BODY(13,900),C.ink,"center");''',
     '''    text("Tap DUNK (50%) · push joystick UP in the air for a WINDMILL",cx,42,BODY(12,900),C.ink,"center");''')

open(f, "w").write(s)
print("patched")
