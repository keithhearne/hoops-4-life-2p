import sys
f, blk = sys.argv[1], sys.argv[2]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:100])
    s = s.replace(a, b)

def cut(a_marker, b_marker, new):
    global s
    a = s.index(a_marker); b = s.index(b_marker, a)
    s = s[:a] + new + s[b:]

# the boss code sits just after the level settings
once("let pickByPlayer=false;", open(blk).read() + "let pickByPlayer=false;")

# every game is first to 21
once("function levelTarget(n){const lv=Math.floor(n/STOPS); return lv<10?11:(lv<20?15:21);}   // longer games in later levels",
     "function levelTarget(n){return 21;}   // every game is first to 21")
once('''const at=b=>progress[b]>=LEVELS?"done!":"L"+(Math.floor(progress[b]/STOPS)+1)+" · P"+(progress[b]%STOPS+1);''',
     '''const at=b=>progress[b]>=LEVELS?"done!":"L"+(Math.floor(progress[b]/STOPS)+1)+" · G"+(progress[b]%STOPS+1);''')

# a giant boss holds and shoots the ball higher; long arms reach further
once("function handPos(e,dir,charging){return rot(charging?dir*4:dir*14, charging?-74:-58, e.lean, e.x, e.y);}",
     "function handPos(e,dir,charging){const k=(e===d&&BOSS)?BS.size:1; return rot((charging?dir*4:dir*14)*k, (charging?-74:-58)*k, e.lean, e.x, e.y);}")
once("function cpuHand(){return {x:d.x+20*(d.face||-1),y:d.y-84};}",
     "function cpuHand(){const S=BOSS?BS.size:1, A=BOSS?BS.arm*(sig.on===\"block\"&&BOSS.sv.reach?1.3:1):1; return {x:d.x+20*A*(d.face||-1),y:d.y-84*S-(A-1)*30};}")
once("""function pickSpot(){
  const r=Math.random();""", """function pickSpot(){
  const r=Math.random();
  if(BOSS && BS.deep) return r<0.25?130+Math.random()*140:(r<0.8?300+Math.random()*110:430+Math.random()*50);   // Deep Range likes the long ones""")

# jumps
once("function cpuJump(v){d.vy=v; d.ground=false; d.dbl=false; d.willDbl=Math.random()<SKILL.dblChance;}",
     """function cpuJump(v){
  if(BOSS){ v*=BS.jump; if(cpuDefending() && sigReady("leap")) fireSig(); if(sig.on==="leap") v*=1.3; }
  d.vy=v; d.ground=false; d.dbl=false;
  d.willDbl=Math.random()<SKILL.dblChance || !!(BOSS && BOSS.sv.dbl && (sig.on==="leap"||sig.on==="block"));
}""")
once("    d.vy=-380; d.dbl=true; cpuFx={t:0.45,x:d.x,y:d.y};", "    d.vy=-380*(BOSS?BS.jump:1); d.dbl=true; cpuFx={t:0.45,x:d.x,y:d.y};")

# each time he gets the ball: maybe a signature shot or a fast break
once("""  cpu.spot=cpu.dunk ? 115+Math.random()*40 : pickSpot();
}""", """  cpu.spot=cpu.dunk ? 115+Math.random()*40 : pickSpot();
  if(BOSS){
    if(sig.on==="shot" && sig.n>0){cpu.dunk=false; cpu.spot=sig.x;}   // Heat Check: the same spot again
    else if(sigReady("shot")){
      fireSig(); sig.n=BOSS.sv.repeat||1; sig.crossed=false; cpu.dunk=false; const sp=BOSS.sv.spot;
      sig.x=sp==="mid"?300+Math.random()*80:(sp==="deep"?380+Math.random()*50:(sp==="far"?440+Math.random()*40:pickSpot()));
      cpu.spot=sig.x;
    }
    else if(sigReady("fast")){fireSig(); cpu.dunk=true; cpu.spot=115+Math.random()*30; cpuBurst=3;}
  }
}""")

# attacking
once("""    if(!cpu.charging){
      const step=SKILL.atkSpeed*dt;""", """    if(BOSS) bossAttack(dt);
    if(!cpu.charging){
      const step=SKILL.atkSpeed*dt*(cpuBurst>0?1.7:1);""")
once("        cpu.charging=true; cpu.t=0; cpu.hold=0.9+Math.random()*0.5;\n        cpu.fade = p.x<d.x && d.x-p.x<75 && Math.random()<SKILL.fadeChance;",
     """        cpu.charging=true; cpu.t=0; cpu.hold=(0.9+Math.random()*0.5)*(BOSS?BS.hold*((sig.on==="shot"&&BOSS.sv.quick)?0.5:1):1);
        cpu.fade = (p.x<d.x && d.x-p.x<75 && Math.random()<SKILL.fadeChance) || !!(sig.on==="shot" && BOSS.sv.fade);
        if(sig.on==="shot" && BOSS.sv.cross && !sig.crossed){sig.crossed=true; crossover();}""")
once("      cpu.t+=dt; if(cpu.fade) d.x=Math.min(d.x+40*dt,800);",
     "      cpu.t+=dt; if(cpu.fade) d.x=Math.min(d.x+(40+(BOSS?BS.fade*150:0))*dt,800);")
# loose balls: Rebounder gets there first
once("""  } else if(ball.state==="free"){
    const step=SKILL.chaseSpeed*dt;""", """  } else if(ball.state==="free"){
    const step=SKILL.chaseSpeed*dt*(BOSS?(1+BS.reb*2)*(sig.on==="reb"?2.4:1):1);""")
# defending
once("""    const target=clamp(p.x+60,60,800), step=SKILL.defSpeed*dt;
    if(Math.abs(target-d.x)<step) d.x=target; else d.x+=Math.sign(target-d.x)*step;""",
     """    let target=clamp(p.x+60-(BOSS?BS.glue*60:0),60,800), step=SKILL.defSpeed*dt;
    if(sig.on==="dunkblock"){target=DUNK_X+24; step*=2.5;}
    if(!(BOSS && bossDefend(dt))){ if(Math.abs(target-d.x)<step) d.x=target; else d.x+=Math.sign(target-d.x)*step; }""")

# the signature block: he reads your shot perfectly
once("  d.react = Math.random()<SKILL.noReact ? null : Math.max(0.2, est-0.2+(Math.random()*2-1)*SKILL.timingNoise);",
     "  d.react = Math.random()<SKILL.noReact ? null : Math.max(0.2, est-0.2+(Math.random()*2-1)*SKILL.timingNoise);\n"
     "  if(BOSS && Math.abs(d.x-p.x)<140 && sigReady(\"block\")){fireSig(); d.react=Math.max(0.2,est-0.12);}")
once("""  p.ground=false; p.vy=0; needRelease=true; stats.att++; d.jumped=false;
  lastShot="Dunk attempt · 50% chance";""", """  p.ground=false; p.vy=0; needRelease=true; stats.att++; d.jumped=false;
  lastShot="Dunk attempt · 50% chance";
  if(BOSS && sigReady("dunkblock")) fireSig();""")
once("    ? (cpuOn && Math.abs(d.x-dunkX)<80 && Math.random()<SKILL.blockDunk)",
     "    ? (cpuOn && Math.abs(d.x-dunkX)<(sig.on===\"dunkblock\"?140:80) && Math.random()<(sig.on===\"dunkblock\"?1:SKILL.blockDunk))")
once("""  const wind=Math.random()<SKILL.windTry;   // the computer sometimes goes for a windmill too
  Object.assign(cdunk,{on:true,t:0,x0:d.x,success:Math.random()<(wind?WIND_MAKE:SKILL.dunkMake),resolved:false,hang:0,wind,w0:0.06});""",
     """  const wind=Math.random()<SKILL.windTry || !!(sig.on==="fast" && BOSS.sv.wind);   // the computer sometimes goes for a windmill too
  const boost=(sig.on==="fast"||sig.on==="reb")?0.3:0;
  Object.assign(cdunk,{on:true,t:0,x0:d.x,success:Math.random()<(wind?WIND_MAKE:SKILL.dunkMake)+boost,resolved:false,hang:0,wind,w0:0.06});
  if(boost) endSig();""")
once("  const chance=Math.min(0.95,z.cpu*SKILL.acc*(cpu.fade?0.85:1)), make=Math.random()<chance;",
     """  let chance=Math.min(0.95,z.cpu*SKILL.acc*(cpu.fade?0.85:1)*(BOSS&&BS.deep&&z!==ZONES.inside?1+BS.deep*1.5:1));
  if(sig.on==="shot"){chance=z===ZONES.far?0.6:0.9; sig.n--; if(sig.n<=0) endSig();}
  const make=Math.random()<chance;""")
# block reach
once("      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<18){blocked(d,!early);return;}",
     "      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<(BOSS?BS.blockR+(sig.on===\"block\"?12:0):18)){blocked(d,!early);return;}")
once("      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<18){blocked(p,!early);return;}",
     "      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<(ball.fade&&BOSS&&BS.fade?18*Math.max(0.35,1-BS.fade*1.3):18)){blocked(p,!early);return;}")
once("  setMood(by===d?p:d,\"shock\"); setMood(by,\"happy\"); celebrateFor(by);\n}",
     "  setMood(by===d?p:d,\"shock\"); setMood(by,\"happy\"); celebrateFor(by);\n"
     "  if(by===d && sig.on===\"block\"){ if(BOSS.sv.catch) takeBall(d); endSig(); }   // Freeze: he catches it\n}")
once("function missNow(){\n  const byP=ball.shooter===p;",
     "function missNow(){\n  const byP=ball.shooter===p;\n  if(BOSS && sigReady(\"reb\") && (!BOSS.sv.dunk || !byP)) fireSig();")
once("""  if(e===d){setCpuPlan(); d.lean=0; say(NAME.d+"'s ball!","Get in front of him: JUMP to block, or STEAL",C.warn);}""",
     """  if(e===d){setCpuPlan(); d.lean=0; say(NAME.d+"'s ball!","Get in front of him: JUMP to block, or STEAL",C.warn);
    if(sig.on==="reb"){ if(BOSS.sv.dunk && d.x<300){cpu.dunk=true; cpu.spot=clamp(d.x,115,155); cpuBurst=1.5;} else endSig(); }}""")
once("        if(Math.abs(ball.x-e.x)<24 && ball.y>e.y-92){takeBall(e);break;}",
     "        const R=(e===d&&BOSS)?24+BS.reb*40+(sig.on===\"reb\"?30:0):24, Hh=(e===d&&BOSS)?92*BS.size+(BS.arm-1)*30:92;\n"
     "        if(Math.abs(ball.x-e.x)<R && ball.y>e.y-Hh){takeBall(e);break;}")
# the player: frozen after a crossover, slowed by a glue defender
once("    if(!tip.on) p.x=clamp(p.x+joy*(charge.on?70:170)*dt,24,812);",
     "    if(!tip.on) p.x=clamp(p.x+joy*(charge.on?70:170)*dt*playerSpeedK(joy),24,812);")
once("  p.lean+=(((charge.on&&charge.fade)?-0.25:0)-p.lean)*Math.min(1,dt*12);",
     "  p.lean+=(((charge.on&&charge.fade)?-0.25:0)-p.lean)*Math.min(1,dt*12);\n  if(BOSS && pStun>0) p.lean=Math.sin(performance.now()/45)*0.14;   // wobbly ankles")
once("  if(cpuOn) cpuUpdate(dt);\n", "  if(cpuOn){ bossTick(dt); cpuUpdate(dt); }\n")
once("      const a={x:d.x-10,y:d.y-96};", "      const k=BOSS?BS.size:1, a={x:d.x-10*k,y:d.y-96*k};")

# drawing: a bigger boss, longer arms, a headband
cut("function drawCpu(){", "// pebbled leather texture", """function drawCpu(){
  if(!cpuOn) return;
  shadow(d);
  const S=BOSS?BS.size:1, A=BOSS?BS.arm:1;
  let hx=-16, hy=-24, ox=16, oy=-24;
  if(tip.on && !d.ground){hx=-20; hy=-84;}
  else if(cpuSwipe>0 && owner!==d){hx=-26*A/S; hy=-24;}
  else if(cdunk.on && cdunk.wind && !cdunk.resolved){hx=(ball.x-d.x)/S; hy=(ball.y-d.y)/S; ox=14; oy=-64;}
  else if(cdunk.on){
    if(cdunk.t<RISE){hx=-10;hy=-96;ox=16;oy=-66;}
    else if(cdunk.t<RISE+SLAM+cdunk.hang || !cdunk.resolved){hx=-12;hy=-86;ox=14;oy=-64;}
    else {hx=-16;hy=-70;ox=16;oy=-60;}
  }
  else if(owner===d && ball.state==="held"){
    if(cpu.charging||!d.ground){hx=cpu.charging?-4:-14; hy=cpu.charging?-74:-58;}
    else {hx=-15; hy=Math.min(-24,(ball.y-d.y-9)/S);}
  }
  else if(cpuArmUp()){const h=cpuHand(); hx=-Math.abs(h.x-d.x)/S; hy=(h.y-d.y)/S;}
  const hang=cdunk.on && cdunk.resolved && cdunk.t-RISE-SLAM<cdunk.hang;
  const F=-(d.face||-1);   // 1 = his usual way (left), -1 = turned round
  ctx.save(); ctx.translate(d.x,d.y); ctx.scale(S,S); ctx.translate(-d.x,-d.y);
  drawAthlete(d,F===1?LOOK.d:Object.assign({},LOOK.d,{dir:-LOOK.d.dir}),{x:hx*F,y:hy},{x:ox*F,y:oy},!d.ground,hang);
  ctx.restore();
  if(BOSS && BS.speed>1 && Math.abs(d.spd||0)>150){   // Speedster streaks
    const dir=Math.sign(d.spd); ctx.strokeStyle="rgba(255,255,255,0.55)"; ctx.lineWidth=2.5; ctx.lineCap="round";
    for(let i=0;i<3;i++){const y=d.y-30-i*18*S; ctx.beginPath(); ctx.moveTo(d.x-dir*(20+i*4),y); ctx.lineTo(d.x-dir*(46+i*8),y); ctx.stroke();}
  }
  if(BOSS && !tip.on) drawCrown(d.x,d.y-(84*S+10),8);
}
""")
once("  limb(shB.x,shB.y,other.x,other.y,17,0,1,5.5,5,lk.skinDark);", "  const AL=17*(lk.armL||1);\n  limb(shB.x,shB.y,other.x,other.y,AL,0,1,5.5,5,lk.skinDark);")
once("  limb(shF.x,shF.y,hand.x,hand.y,17,0,1,6,5.2,lk.skin);", "  limb(shF.x,shF.y,hand.x,hand.y,AL,0,1,6,5.2,lk.skin);")
once("""  // eyebrows: happy, shocked (raised) or grumpy (angled down)""", """  if(lk.band){   // a boss headband
    ctx.save(); ctx.beginPath(); ctx.ellipse(hx,hy,R+0.6,R*1.05+0.6,0,0,Math.PI*2); ctx.clip();
    ctx.fillStyle=lk.band; ctx.fillRect(hx-14,hy-10.5,28,3.6); ctx.restore();
  }
  // eyebrows: happy, shocked (raised) or grumpy (angled down)""")

# start / end of a game
once("""function startGame(){
  applyLooks();""", """function startGame(){
  const lv=Math.floor(level/STOPS);
  BOSS=(mode==="level" && isBossLevel(level)) ? BOSSES[lv] : null;
  BS=BOSS ? bossStats(lv) : null;
  applyLooks();""")
once("  if(mode===\"level\"){SKILL=levelSkill(level); WIN=levelTarget(level);}\n  else {SKILL=Object.assign({},SKILL_BASE); WIN=21;}",
     "  if(mode===\"level\"){SKILL=levelSkill(level); WIN=levelTarget(level); if(BOSS) SKILL=bossSkill(SKILL,lv);}\n  else {SKILL=Object.assign({},SKILL_BASE); WIN=21;}\n  resetBoss();")
once("""  NAME.p=BOYS[human].name; NAME.d=BOYS[o].name;""", """  NAME.p=BOYS[human].name; NAME.d=BOYS[o].name;
  if(BOSS){const i=BOSSES.indexOf(BOSS); LOOK.d=bossLook(i,C.p1); C.p2=LOOK.d.jersey; NAME.d=BOSS.name;}""")
once("""  if(mode==="level" && youWin && level>=progress[human]){
    progress[human]=Math.min(LEVELS,level+1);
    newRoad = progress[human]<LEVELS && progress[human]%STOPS===0;
  }""", """  if(mode==="level" && youWin && level>=progress[human]){
    progress[human]=Math.min(LEVELS,level+1);
    newRoad = progress[human]<LEVELS && progress[human]%STOPS===0;
  }
  // lose to a boss: back to game 6, win it again to get another shot at him
  if(mode==="level" && !youWin && BOSS && level>=progress[human]) progress[human]=level-1;""")
once("function toMap(){screen=\"title\"; mapScroll=null;}", "function toMap(){screen=\"title\"; mapScroll=null; BOSS=null; applyLooks();}")

# the end screen
once("""  const youWin=overWinner==="p", boy=youWin?human:other();
  portraitBadge(boy,180,186,112);""", """  const youWin=overWinner==="p", boy=youWin?human:other();
  if(!youWin && BOSS){faceBadge(LOOK.d,180,186,112,C.p2); drawCrown(180,72,22);} else portraitBadge(boy,180,186,112);""")
once("""  if(lv) text(levelName(level).toUpperCase()+(newRoad?"   ·   LEVEL "+(Math.floor(progress[human]/STOPS)+1)+" OPEN + NEW BALL!":""),332,140,BODY(12,900),newRoad?C.warn:C.muted);""",
     """  if(lv && BOSS && !youWin) text("BOSS WINS · WIN GAME 6 AGAIN FOR ANOTHER SHOT AT "+BOSS.name.toUpperCase(),332,140,BODY(12,900),C.warn);
  else if(lv) text((BOSS&&youWin?"BOSS BEATEN!   ·   ":"")+levelName(level).toUpperCase()+(newRoad?"   ·   LEVEL "+(Math.floor(progress[human]/STOPS)+1)+" OPEN + NEW BALL!":""),332,140,BODY(12,900),newRoad||BOSS?C.warn:C.muted);""")
once("""    else button(332,312,220,50,youWin?"PLAY AGAIN":"TRY AGAIN",{fill:"#F26B1D",ink:C.navy},()=>startGame());""",
     """    else if(BOSS && !youWin) button(332,312,220,50,"PLAY GAME 6",{fill:"#F26B1D",ink:C.navy,sub:levelName(level-1)},()=>{level--; startGame();});
    else button(332,312,220,50,youWin?"PLAY AGAIN":"TRY AGAIN",{fill:"#F26B1D",ink:C.navy},()=>startGame());""")

# celebration pop-up: the boss shows his own face
once("""  if(img.complete && img.naturalWidth) ctx.drawImage(img,70,8,260,260,cx-r,cy-r,r*2,r*2);
  ctx.restore();
  ctx.strokeStyle=C.ink; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.stroke();
  // commentary""", """  if(BOSS && who==="d"){ctx.restore(); faceBadge(LOOK.d,cx,cy,r,col);}
  else {if(img.complete && img.naturalWidth) ctx.drawImage(img,70,8,260,260,cx-r,cy-r,r*2,r*2); ctx.restore();}
  ctx.strokeStyle=C.ink; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.stroke();
  // commentary""")
# scoreboard: long boss names shrink to fit
once("""    text(name.toUpperCase(),x+43,34,BODY(13,900),ink); text(String(score),x+w-10,35,DISP(24),ink,"right");""",
     """    let fs=13; ctx.font=BODY(fs,900); while(fs>8 && ctx.measureText(name.toUpperCase()).width>w-86){fs--; ctx.font=BODY(fs,900);}
    text(name.toUpperCase(),x+43,34,BODY(fs,900),ink); text(String(score),x+w-10,35,DISP(24),ink,"right");""")
once("  drawMeter(); drawHUD(); drawControls(); drawMsg(); drawScreenFx();\n}", "  drawMeter(); drawHUD(); drawControls(); drawMsg(); drawSigFlash(); drawScreenFx();\n}")
once("  ctx.fillStyle=C.warn; ctx.fillText(String(n),TIP_X,TIP_Y+70);\n  ctx.restore();",
     "  ctx.fillStyle=C.warn; ctx.fillText(String(n),TIP_X,TIP_Y+70);\n  ctx.restore();\n"
     "  if(BOSS){ctx.save(); ctx.font=DISP(18); ctx.textAlign=\"center\"; ctx.textBaseline=\"middle\"; ctx.lineWidth=6; ctx.lineJoin=\"round\";\n"
     "    ctx.strokeStyle=C.navy; ctx.strokeText(\"BOSS GAME: \"+NAME.d.toUpperCase(),TIP_X,TIP_Y+128); ctx.fillStyle=C.ink; ctx.fillText(\"BOSS GAME: \"+NAME.d.toUpperCase(),TIP_X,TIP_Y+128); ctx.restore();}")

# the level map: game 7 is a crowned boss circle with the boss's face
once("""      const sp=stopPos(r,i), n=r*STOPS+i, done=n<prog, cur=n===prog, R=cur?STOP_R*1.1:STOP_R;""",
     """      const sp=stopPos(r,i), n=r*STOPS+i, done=n<prog, cur=n===prog, boss=i===STOPS-1, R=(cur?STOP_R*1.1:STOP_R)*(boss?1.25:1);""")
once("""      text(String(i+1),sp.x,sp.y+1,DISP(18),(done||cur)?inkOn(road.col):"rgba(255,255,255,0.45)","center");""",
     """      if(boss){ faceBadge(bossLook(r,MAINS[kits[human].main]),sp.x,sp.y,R-3,(done||cur)?road.col:locked);
        if(!(done||cur)){ctx.fillStyle="rgba(16,21,43,0.55)"; ctx.beginPath(); ctx.arc(sp.x,sp.y,R-3,0,Math.PI*2); ctx.fill();}
        drawCrown(sp.x,sp.y-R+2,10); }
      else text(String(i+1),sp.x,sp.y+1,DISP(18),(done||cur)?inkOn(road.col):"rgba(255,255,255,0.45)","center");""")
once("""        ctx.lineWidth=4; ctx.lineJoin="round"; ctx.strokeStyle=C.navy; ctx.strokeText("PLAY",tx,sp.y+1);
        ctx.fillStyle=C.warn; ctx.fillText("PLAY",tx,sp.y+1);}""", """        const lab=boss?"BOSS!":"PLAY";
        ctx.lineWidth=4; ctx.lineJoin="round"; ctx.strokeStyle=C.navy; ctx.strokeText(lab,tx,sp.y+1);
        ctx.fillStyle=C.warn; ctx.fillText(lab,tx,sp.y+1);}""")

# the setup screen before a boss game: your card and the boss's card
once("""  playerCard("zackie",22,62,390,262);
  playerCard("keelan",432,62,390,262);""", """  if(mode==="level" && isBossLevel(level)){
    playerCard(human,22,62,390,262);
    bossCard(Math.floor(level/STOPS),432,62,390,262);
    if(pickByPlayer) button(W/2-95,336,190,42,"PLAY AS "+BOYS[other()].name.toUpperCase(),{size:13,outline:"rgba(255,255,255,0.3)"},()=>{human=other(); level=Math.min(progress[human],LEVELS-1);});
  } else {
  playerCard("zackie",22,62,390,262);
  playerCard("keelan",432,62,390,262);
  }""")
once("""    level:[levelName(level).toUpperCase(),BOYS[human].name+" vs the computer at "+ARENAS[Math.floor(level/STOPS)].name+" · first to "+levelTarget(level)+(pickByPlayer?" · tap a card to choose who plays":"")]};""",
     """    level:[levelName(level).toUpperCase()+(isBossLevel(level)?" · BOSS GAME":""),isBossLevel(level)?BOYS[human].name+" vs "+BOSSES[Math.floor(level/STOPS)].name+" at "+ARENAS[Math.floor(level/STOPS)].name+" · first to "+levelTarget(level):BOYS[human].name+" vs the computer at "+ARENAS[Math.floor(level/STOPS)].name+" · first to "+levelTarget(level)+(pickByPlayer?" · tap a card to choose who plays":"")]};""")
once("  const clash=mode!==\"practice\" && kits.zackie.main===kits.keelan.main;",
     "  const clash=mode!==\"practice\" && !(mode===\"level\"&&isBossLevel(level)) && kits.zackie.main===kits.keelan.main;")
once("function tryStart(){ if(mode!==\"practice\" && kits.zackie.main===kits.keelan.main) return; saveGame(); startGame(); }",
     "function tryStart(){ if(mode!==\"practice\" && !(mode===\"level\"&&isBossLevel(level)) && kits.zackie.main===kits.keelan.main) return; saveGame(); startGame(); }")

open(f, "w").write(s)
print("patched")
