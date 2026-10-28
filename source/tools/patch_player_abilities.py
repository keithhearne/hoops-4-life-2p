import sys
f = sys.argv[1]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:100])
    s = s.replace(a, b)

def every(a, b, n):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)

# ---- wheel prizes: crowns are always +1, medals +1 to +5 ----
for old in ['med:[2,3,4,6],cr:[1]', 'med:[4,6,8,12],cr:[1,2]', 'med:[8,12,16,24],cr:[1,2]', 'med:[12,20,30,40],cr:[1,2,3]']:
    once(old, 'med:[1,2,3,4,5],cr:[1]')

# ---- the player's abilities when he plays as a boss he won ----
once("let BOSS=null, BS=null;", """let BOSS=null, BS=null;
// PS = the player's own boss abilities (when he plays as a boss he won from a trophy), same strengths as that boss
let PS=null, dStun=0, dStunCool=0, pJoyLast=0;
function playerStats(i){const st=bossStats(i), ab=BOSSES[i].ab; st.ab=ab; st.has=k=>ab.includes(k); return st;}
// the sweet spot: Sharpshooter makes it wider everywhere, Deep Range on long shots, Fade-Away King on fades
function pRange(z,fade){
  const r=(fade?z.f:z.n).slice(); if(!PS || z.behind) return r;
  let w=0; if(PS.has("sharp")) w+=Math.round(PS.s*12); if(PS.deep && z!==ZONES.inside) w+=Math.round(PS.deep*14); if(fade && PS.fade) w+=3;
  r[0]=Math.max(1,r[0]-w); r[1]=Math.min(99,r[1]+w); return r;
}
function pDunkChance(){return PS&&PS.has("dunk")?Math.min(0.92,0.5+PS.s*1.0):0.5;}
function pWindChance(){return PS&&PS.has("dunk")?Math.min(0.85,WIND_MAKE+PS.s*0.8):WIND_MAKE;}""")
once("function resetBoss(){sig=", "function resetBoss(){dStun=0; dStunCool=0; pJoyLast=0; sig=")
once("  BS=BOSS ? bossStats(lv) : null;", "  BS=BOSS ? bossStats(lv) : null;\n  PS=skinOf[human] ? playerStats(+skinOf[human].slice(4)) : null;")

# size, reach, jumps, speed
once("function handPos(e,dir,charging){const k=(e===d&&BOSS)?BS.size:1;",
     "function handPos(e,dir,charging){const k=(e===d&&BOSS)?BS.size:((e===p&&PS)?PS.size:1);")
once("function playerHand(){return {x:p.x+20*(p.face||1),y:p.y-84};}",
     "function playerHand(){const S=PS?PS.size:1, A=PS?PS.arm:1; return {x:p.x+20*A*(p.face||1),y:p.y-84*S-(A-1)*30};}")
once("    if(jumpQueued && p.ground){p.vy=-380;p.ground=false;p.dbl=false; play(\"squeak\");}",
     "    if(jumpQueued && p.ground){p.vy=-380*(PS?PS.jump:1);p.ground=false;p.dbl=false; play(\"squeak\");}")
once("      if(apexWindow()){p.vy=-380; p.dbl=true; dblFx={t:0.45,x:p.x,y:p.y};}",
     "      if(apexWindow()){p.vy=-380*(PS?PS.jump:1); p.dbl=true; dblFx={t:0.45,x:p.x,y:p.y};}")
once("function apexWindow(){return !p.ground && !p.dbl && !dunk.on && !charge.on && playerDefending() && Math.abs(p.vy)<APEX_VY;}",
     "function apexWindow(){return !p.ground && !p.dbl && !dunk.on && !charge.on && playerDefending() && Math.abs(p.vy)<APEX_VY*(PS&&PS.has(\"dbl\")?2.2:1);}")
once("    if(!tip.on) p.x=clamp(p.x+joy*(charge.on?70:170)*dt*playerSpeedK(joy),24,812);",
     "    if(!tip.on) p.x=clamp(p.x+joy*(charge.on?70:170)*dt*playerSpeedK(joy)*(PS?PS.speed*(ball.state===\"free\"?1+PS.reb*1.5:1):1),24,812);")
once("      const a={x:p.x+10,y:p.y-96};", "      const kp=PS?PS.size:1, a={x:p.x+10*kp,y:p.y-96*kp};")
once("        const R=(e===d&&BOSS)?24+BS.reb*40+(sig.on===\"reb\"?30:0):24, Hh=(e===d&&BOSS)?92*BS.size+(BS.arm-1)*30:92;",
     "        const R=(e===d&&BOSS)?24+BS.reb*40+(sig.on===\"reb\"?30:0):((e===p&&PS)?24+PS.reb*40:24);\n"
     "        const Hh=(e===d&&BOSS)?92*BS.size+(BS.arm-1)*30:((e===p&&PS)?92*PS.size+(PS.arm-1)*30:92);")

# shooting: wider sweet spots, quick release beats the defender, fade-aways are hard to block
every("charge.fade?z.f:z.n", "pRange(z,charge.fade)", 3)
once("  const range=charge.on?(fade?z.f:z.n):(charge.range||z.n);", "  const range=charge.on?pRange(z,fade):(charge.range||pRange(z,false));")
once('''"sweet spot "+z.n[0]+"–"+z.n[1]+" · fade "+z.f[0]+"–"+z.f[1]''', '''"sweet spot "+pRange(z,false)[0]+"–"+pRange(z,false)[1]+" · fade "+pRange(z,true)[0]+"–"+pRange(z,true)[1]''')
once("  if(BOSS && Math.abs(d.x-p.x)<140 && sigReady(\"block\")){fireSig(); d.react=Math.max(0.2,est-0.12);}",
     "  if(PS && PS.hold<1 && Math.random()<PS.s*1.6) d.react=null;   // Quick Release: the shot is gone before he can jump\n"
     "  if(BOSS && Math.abs(d.x-p.x)<140 && sigReady(\"block\")){fireSig(); d.react=Math.max(0.2,est-0.12);}")
once("      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<(BOSS?BS.blockR+(sig.on===\"block\"?12:0):18)){blocked(d,!early);return;}",
     "      const fadeK=(ball.fade&&PS&&PS.fade)?Math.max(0.35,1-PS.fade*1.3):1;\n"
     "      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<(BOSS?BS.blockR+(sig.on===\"block\"?12:0):18)*fadeK){blocked(d,!early);return;}")
once("      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<(ball.fade&&BOSS&&BS.fade?18*Math.max(0.35,1-BS.fade*1.3):18)){blocked(p,!early);return;}",
     "      if(Math.hypot(ball.x-hd.x,ball.y-hd.y)<(PS?PS.blockR:18)*(ball.fade&&BOSS&&BS.fade?Math.max(0.35,1-BS.fade*1.3):1)){blocked(p,!early);return;}")

# dunks
once("  Object.assign(dunk,{on:true,t:0,x0:p.x,success:Math.random()<0.5,resolved:false,hang:0,wind:false,w0:0});",
     "  Object.assign(dunk,{on:true,t:0,x0:p.x,success:Math.random()<pDunkChance(),resolved:false,hang:0,wind:false,w0:0});")
once('  lastShot="Dunk attempt · 50% chance";', '  lastShot="Dunk attempt · "+Math.round(pDunkChance()*100)+"% chance";')
once('    dunk.wind=true; dunk.w0=dunk.t; dunk.success=Math.random()<WIND_MAKE; lastShot="WINDMILL! · 40% chance";',
     '    dunk.wind=true; dunk.w0=dunk.t; dunk.success=Math.random()<pWindChance(); lastShot="WINDMILL! · "+Math.round(pWindChance()*100)+"% chance";')
once('''    text("Tap DUNK (50%) · push joystick UP in the air for a WINDMILL",cx,42,BODY(12,900),C.ink,"center");''',
     '''    text("Tap DUNK ("+Math.round(pDunkChance()*100)+"%) · push joystick UP in the air for a WINDMILL",cx,42,BODY(12,900),C.ink,"center");''')

# steals: Pickpocket steals more often, Long Arms from further away
once("  if(Math.abs(d.x-p.x)>STEAL_REACH){stealMsg={text:\"Too far away!\",t:1}; return;}",
     "  if(Math.abs(d.x-p.x)>STEAL_REACH*(PS?PS.arm:1)){stealMsg={text:\"Too far away!\",t:1}; return;}")
once("  const chance = (cpu.charging||!d.ground) ? 0 : SKILL.stealChance;",
     "  const chance = (cpu.charging||!d.ground) ? 0 : Math.min(0.9,SKILL.stealChance*(PS&&PS.pick?1+PS.pick*1.6:1));")
once("    const near=Math.abs(d.x-p.x)<=STEAL_REACH && owner===d,", "    const near=Math.abs(d.x-p.x)<=STEAL_REACH*(PS?PS.arm:1) && owner===d,")

# Glue Defender slows the computer down when he's right up against you; Ankle Breaker freezes him
once("      const step=SKILL.atkSpeed*dt*(cpuBurst>0?1.7:1);",
     "      const glued=PS&&PS.glue&&p.x<d.x&&d.x-p.x<50;\n"
     "      const step=SKILL.atkSpeed*dt*(cpuBurst>0?1.7:1)*(glued?Math.max(0.3,1-PS.glue*2):1);")
once("  if(cdunk.on){ runDunk(cdunk,d,-1,RL,CPU_DUNK_X,dt); return; }",
     "  if(cdunk.on){ runDunk(cdunk,d,-1,RL,CPU_DUNK_X,dt); return; }\n"
     "  if(dStunCool>0) dStunCool-=dt;\n"
     "  if(dStun>0){ dStun-=dt; if(cpuDefending()){ d.lean=Math.sin(performance.now()/45)*0.14; body(d,dt); return; } }")
once("  // computer\n", """  // Ankle Breaker: change direction sharply right in front of him and he can fall for it
  if(PS && PS.ankle && cpuOn && owner===p && ball.state==="held" && !charge.on && !dunk.on && d.x>p.x && d.x-p.x<90 && Math.abs(joy)>0.5){
    if(pJoyLast*joy<0 && dStunCool<=0 && Math.random()<PS.ankle*2.2){
      dStun=0.6+PS.ankle; dStunCool=3; say("ANKLES BROKEN!",NAME.p+" crossed "+NAME.d+" over!",C.info); play("squeak"); play("gasp"); setMood(d,"shock"); setMood(p,"happy");
    }
  }
  if(Math.abs(joy)>0.5) pJoyLast=joy;
  // computer
""")

# drawing: a giant boss skin is taller, long arms reach further
once("""  const hang=dunk.on && dunk.resolved && dunk.t-RISE-SLAM<dunk.hang;
  const F=p.face||1;
  drawAthlete(p,F===LOOK.p.dir?LOOK.p:Object.assign({},LOOK.p,{dir:F}),{x:hx*F,y:hy},{x:ox*F,y:oy},!p.ground,hang);""",
"""  const hang=dunk.on && dunk.resolved && dunk.t-RISE-SLAM<dunk.hang;
  const F=p.face||1, S=PS?PS.size:1;
  if(owner===p && ball.state==="held" && !charge.on && p.ground && !dunk.on) hy=Math.min(-24,(ball.y-p.y-9)/S);
  if(dunk.on && dunk.wind && !dunk.resolved){hx=(ball.x-p.x)/S; hy=(ball.y-p.y)/S;}
  if(playerArmUp() && !(owner===p) && !(tip.on) && !(stealSwipe>0 && owner!==p) && !dunk.on){const h=playerHand(); hx=Math.abs(h.x-p.x)/S; hy=(h.y-p.y)/S;}
  const lkp=Object.assign({},LOOK.p,{dir:F,armL:PS?(PS.has("arms")?1.25:1):1});
  ctx.save(); ctx.translate(p.x,p.y); ctx.scale(S,S); ctx.translate(-p.x,-p.y);
  drawAthlete(p,lkp,{x:hx*F,y:hy},{x:ox*F,y:oy},!p.ground,hang);
  ctx.restore();
  if(PS && PS.speed>1 && Math.abs(p.spd||0)>150){   // Speedster streaks
    const dir=Math.sign(p.spd); ctx.strokeStyle="rgba(255,255,255,0.55)"; ctx.lineWidth=2.5; ctx.lineCap="round";
    for(let i=0;i<3;i++){const y=p.y-30-i*18*S; ctx.beginPath(); ctx.moveTo(p.x-dir*(20+i*4),y); ctx.lineTo(p.x-dir*(46+i*8),y); ctx.stroke();}
  }""")

# show the abilities where the boss is picked
once('''      else if(open){skinOf[human]=id; saveGame(); playersMsg={text:BOYS[human].name+" plays as "+name,t:1.8};}''',
     '''      else if(open){skinOf[human]=id; saveGame(); playersMsg={text:BOYS[human].name+" plays as "+name+": "+BOSSES[i].ab.map(a=>ABIL[a]).join(", "),t:2.6};}''')
once('''  text(bb.name.toUpperCase(),tx,y+30,DISP(nfs),C.ink); text("#"+bb.num,x+w-16,y+30,DISP(20),C.muted,"right");''',
     '''  text(bb.name.toUpperCase(),tx,y+30,DISP(nfs),C.ink); text("#"+bb.num,x+w-16,y+30,DISP(20),C.muted,"right");
  if(skinOf[boy]){const ab=BOSSES[+skinOf[boy].slice(4)].ab.map(a=>ABIL[a]).join(" · "); let af=10; ctx.font=BODY(af,900); while(af>7 && ctx.measureText(ab).width>w-176){af--; ctx.font=BODY(af,900);} text(ab,tx,y+48,BODY(af,900),C.warn);}''')
once('''      text(it.kind==="player"?"Pick him on the Players screen"''', '''      text(it.kind==="player"?"Pick him on the Players screen to play with his abilities"''')

open(f, "w").write(s)
print("patched")
