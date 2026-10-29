import sys
f, blk = sys.argv[1], sys.argv[2]
s = open(f, encoding="utf-8").read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:110])
    s = s.replace(a, b)

# the match code goes right after the lobby code
once("function drawTitle(){", open(blk, encoding="utf-8").read() + "function drawTitle(){")

# --- the lobby: PLAY starts a match; intros carry the boss look; match messages are routed ---
once('''      button(W/2+150,326,150,44,"PLAY",{fill:"#2F6FE4",disabled:true,sub:"matches coming next"});''',
     '''      if(LINK.role==="host") button(W/2+150,326,150,44,"PLAY",{fill:"#2F6FE4",sub:"Random arena"},twoStartAsHost);
      else text("Waiting for "+BOYS[LINK.other.boy].name+" to start…",W/2+225,348,BODY(12,900),C.ink,"center");''')
once('''function sendIntro(){ const k=kits[human]; netSend({t:"intro",boy:human,main:k.main,trim:k.trim}); }''',
     '''function sendIntro(){ const k=kits[human]; netSend({t:"intro",boy:human,main:k.main,trim:k.trim,skin:skinOf[human]||null}); }''')
once('''  if(!m || typeof m!=="object" || typeof m.t!=="string") return;
  if(m.t==="hello"){''', '''  if(!m || typeof m!=="object" || typeof m.t!=="string") return;
  if(onTwoMessage(m)) return;   // match messages
  if(m.t==="hello"){''')
once('''    if(m.s==="joined"){ LINK.peer=true; LINK.stage="meeting"; sendIntro(); play("tick"); }
    else if(m.s==="left"){''', '''    if(m.s==="joined"){ LINK.peer=true; LINK.stage="meeting"; sendIntro(); play("tick"); twoPeerBack(); }
    else if(m.s==="left"){ twoPeerLeft();''')
once('''    LINK.other={boy:m.boy,main,trim}; LINK.stage="connected"; LINK.note=""; play("cheer",0.8);''',
     '''    LINK.other={boy:m.boy,main,trim,skin:okSkin(m.skin)}; LINK.stage="connected"; LINK.note=""; if(!TWO.on) play("cheer",0.8);''')
once('''    LINK.peer=false; LINK.stage="lost"; LINK.note="Connection lost. Reconnecting…";''',
     '''    LINK.peer=false; LINK.stage="lost"; LINK.note="Connection lost. Reconnecting…"; twoPeerLeft();''')

# --- the game loop: the guest only draws; the host sends updates; the second player is the guest's ---
once("function update(dt){\n  crowdUpdate(dt);   // the crowd follows the play\n",
     "function update(dt){\n  crowdUpdate(dt);   // the crowd follows the play\n"
     "  if(isGuest()){ guestUpdate(dt); return; }   // 2 Player guest: draw what the host sends\n"
     "  if(isHost()) twoHostTick(dt);\n")
once("  if(cpuOn){ bossTick(dt); cpuUpdate(dt); }\n", "  if(isHost()) remoteUpdate(dt);   // 2 Player: the other phone's controls\n  else if(cpuOn){ bossTick(dt); cpuUpdate(dt); }\n")
once("      if(apexWindow()){p.vy=-380*(PS?PS.jump:1); p.dbl=true; dblFx={t:0.45,x:p.x,y:p.y};}",
     "      if(apexWindow()){p.vy=-380*(PS?PS.jump:1); p.dbl=true; dblFx={t:0.45,x:p.x,y:p.y}; if(isHost()) TWO.ev.push([\"j\",\"p\",n1(p.x),n1(p.y)]);}")
# in 2 Player the other player is a person: he only stuffs a dunk if he's really up there at the rim
once("    ? (cpuOn && Math.abs(d.x-dunkX)<(sig.on===\"dunkblock\"?140:80) && Math.random()<(sig.on===\"dunkblock\"?1:SKILL.blockDunk))",
     "    ? (TWO.on ? (!d.ground && Math.abs(d.x-dunkX)<75 && Math.random()<0.5)\n       : (cpuOn && Math.abs(d.x-dunkX)<(sig.on===\"dunkblock\"?140:80) && Math.random()<(sig.on===\"dunkblock\"?1:SKILL.blockDunk)))")
once("function endGame(){\n", "function endGame(){\n  if(TWO.on){ twoHostEnd(); return; }\n")

# --- events the host passes on to the guest ---
once('''function play(name,arg){''', '''function play(name,arg){
  if(isHost() && !["dribble","tick","click"].includes(name)) TWO.ev.push(["s",name,arg===undefined?null:arg]);
  if(TWO.mute) return;''')
once('''function say(text,sub,color){msg={text,sub:sub||"",t:1.9,color:color||C.ink};}''',
     '''function say(text,sub,color){msg={text,sub:sub||"",t:1.9,color:color||C.ink}; if(isHost()) TWO.ev.push(["m",text,sub||"",color||C.ink]);}''')
once('''function celebrateFor(e,t){celebrate={who:e===p?"p":"d",t:t||2.2,T:t||2.2};}''',
     '''function celebrateFor(e,t){celebrate={who:e===p?"p":"d",t:t||2.2,T:t||2.2}; if(isHost()) TWO.ev.push(["c",celebrate.who,celebrate.t]);}''')
once("function netKick(i,down,side){", "function netKick(i,down,side){\n  if(isHost()) TWO.ev.push([\"n\",i,down,side]);")
once("function startBoardFx(side,wind){", "function startBoardFx(side,wind){\n  if(isHost()) TWO.ev.push([\"b\",side,wind?1:0]);")
once("function startCrackFx(){", "function startCrackFx(){\n  if(isHost()) TWO.ev.push([\"k\"]);")

# --- drawing: the arena and its ball, the guest's meter and buttons, the match info, pause and end screens ---
once("function currentArena(){\n", "function currentArena(){\n  if(TWO.on && (screen===\"play\"||screen===\"pause\"||screen===\"over\")) return ARENAS[TWO.arena];\n")
once("  drawBallAt(x,y,R,ballOf(human),ball.rot||0);", "  drawBallAt(x,y,R,TWO.on?ballList()[TWO.arena+1]:ballOf(human),ball.rot||0);   // 2 Player: the arena's own ball")
once("function drawMeter(){\n", "function drawMeter(){\n  if(isGuest()){ drawGuestMeter(); return; }\n")
once("function drawControls(){\n", "function drawControls(){\n  if(isGuest()){ drawGuestControls(); return; }\n")
once('''  if(tip.on){
    text("JUMP BALL",cx,26,BODY(11,900),C.warn,"center");''', '''  if(TWO.on && !tip.on){
    const mine=isGuest()?d:p, theirs=isGuest()?p:d, def=owner===theirs||(ball.state==="flight"&&ball.shooter===theirs);
    text("2 PLAYER · "+(isGuest()?"YOU'RE ON THE RIGHT":"YOU'RE ON THE LEFT")+" · FIRST TO 21",cx,26,BODY(11,900),def?C.warn:C.muted,"center");
    text(def?"JUMP to block · joystick down towards him + STEAL":(owner===mine?"Score on the "+(isGuest()?"LEFT":"RIGHT")+" hoop":"Loose ball? Run to it"),cx,42,BODY(12,900),C.ink,"center");
  } else if(tip.on){
    text("JUMP BALL",cx,26,BODY(11,900),C.warn,"center");''')
once('''    if(screen==="pause") drawPause();
    else if(screen==="over") drawOver();''', '''    if(screen==="pause") (TWO.on?drawTwoPause:drawPause)();
    else if(screen==="over") (TWO.on?drawTwoOver:drawOver)();''')

# --- pausing in 2 Player pauses both phones ---
once('''    screen="pause"; touchJoy=0; shootTouch=false; roles.clear(); e.preventDefault(); return;''',
     '''    if(TWO.on) twoPause(); else screen="pause";
    touchJoy=0; shootTouch=false; roles.clear(); e.preventDefault(); return;''')
once('''  if(k==="Escape"||k==="p"){ if(screen==="play") screen="pause"; else if(screen==="pause") screen="play"; return; }''',
     '''  if(k==="Escape"||k==="p"){
    if(TWO.on){ if(screen==="play") twoPause(); else if(screen==="pause" && !TWO.waiting) twoResume(); return; }
    if(screen==="play") screen="pause"; else if(screen==="pause") screen="play"; return; }''')
once('''  if(k==="Enter"){
    if(screen==="title")''', '''  if(k==="Enter" && TWO.on){ if(screen==="pause" && !TWO.waiting) twoResume(); return; }
  if(k==="Enter"){
    if(screen==="title")''')

# --- the crowd cheers for whoever is playing on this phone ---
once('''  const defending=screen==="play" && !tip.on && (owner===d || (ball.state==="flight"&&ball.shooter===d));''',
     '''  const defending=screen==="play" && !tip.on && (owner===foeE() || (ball.state==="flight"&&ball.shooter===foeE()));''')
once('''  else if(!defending && CROWD.chant && owner===p) chantStop(0.3);''', '''  else if(!defending && CROWD.chant && owner===meE()) chantStop(0.3);''')

# --- the head-to-head record is saved with everything else ---
once("shoesOwned,sound:SND.on,crowd:SND.crowd}", "shoesOwned,h2h,sound:SND.on,crowd:SND.crowd}")
once("    if(s.crowd===false) SND.crowd=false;", "    if(s.crowd===false) SND.crowd=false;\n"
     "    if(s.h2h) for(const b of [\"zackie\",\"keelan\"]) if(s.h2h[b]) h2h[b]={w:Math.max(0,s.h2h[b].w|0),l:Math.max(0,s.h2h[b].l|0)};")

once('''    if(LINK.peer) sendIntro();
  } else if(m.t==="peer"){''', '''    if(LINK.peer){ sendIntro(); twoPeerBack(); }
  } else if(m.t==="peer"){''')

open(f, "w", encoding="utf-8").write(s)
print("patched")
