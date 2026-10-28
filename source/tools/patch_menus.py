import re, sys
game, block = sys.argv[1], sys.argv[2]
s = open(game).read()

def once(a, b):
    global s
    assert s.count(a) == 1, ("expected once", a[:80], s.count(a))
    s = s.replace(a, b)

# --- name ---
once("<title>Hoop Duel Demo</title>", "<title>Hoops 4 Life</title>")
once("<p>Hoop Duel is played in landscape so both hoops fit on screen.</p>",
     "<p>Hoops 4 Life is played in landscape so both hoops fit on screen.</p>")
once('aria-label="Hoop Duel one versus one court.', 'aria-label="Hoops 4 Life basketball game.')

# --- fixed message colours (team colours can now be anything, even black or white) ---
s = s.replace("C.p2", "C.warn").replace("C.p1", "C.info")
once('panel:"#2E3866",', 'panel:"#2E3866",warn:"#FFC93C",info:"#7DB0FF",')
# put team colours back where they really mean the team
once("ctx.fillStyle=C.warn; ctx.fillRect(40,314,120,10);", "ctx.fillStyle=C.p2; ctx.fillRect(40,314,120,10);")
once("ctx.fillStyle=C.info; ctx.fillRect(684,314,120,10);", "ctx.fillStyle=C.p1; ctx.fillRect(684,314,120,10);")
once("if(hot){ctx.fillStyle=C.info;", "if(hot){ctx.fillStyle=C.p1;")
once('hot?C.info:C.wood', 'hot?C.p1:C.wood')
once('col=who==="p"?C.info:C.warn', 'col=who==="p"?C.p1:C.p2')

# --- manga portraits become per-boy images recoloured to each kit ---
m = re.search(r'const MANGA=\{p:new Image\(\), d:new Image\(\)\};\nMANGA\.p\.src="data:image/svg\+xml;charset=utf-8,"\+encodeURIComponent\((".*?")\);\nMANGA\.d\.src="data:image/svg\+xml;charset=utf-8,"\+encodeURIComponent\((".*?")\);', s)
assert m
s = s[:m.start()] + ("const MANGA_SVG_Z=" + m.group(1) + ";\nconst MANGA_SVG_K=" + m.group(2) + ";\n"
    "const MIMG={zackie:new Image(), keelan:new Image()};\n"
    "const MANGA={get p(){return MIMG[human];}, get d(){return MIMG[other()];}};") + s[m.end():]

# --- names in messages ---
for a, b in [
    ('"Opponent\'s ball!"', 'NAME.d+"\'s ball!"'),
    ('"Opponent shot from "', 'NAME.d+" shot from "'),
    ('"Opponent is going for the dunk!"', 'NAME.d+" is going for the dunk!"'),
    ('"You stuffed the opponent\'s dunk!"', '"You stuffed "+NAME.d+"\'s dunk!"'),
    ('"You blocked the opponent\'s dunk"', '"You blocked "+NAME.d+"\'s dunk"'),
    ('"Opponent missed the dunk! Grab it!"', 'NAME.d+" missed the dunk! Grab it!"'),
    ('"Opponent missed the dunk"', 'NAME.d+" missed the dunk"'),
    ('"You blocked the opponent"', '"You blocked "+NAME.d'),
    ('"Opponent +"', 'NAME.d+" +"'),
    ('youWin?"YOU WIN!":"OPPONENT WINS!", stats.score+" – "+stats.cpu+" · new game starting"',
     '(youWin?NAME.p:NAME.d).toUpperCase()+" WINS!", stats.score+" – "+stats.cpu'),
    ('"Opponent missed! Grab the rebound!"', 'NAME.d+" missed! Grab the rebound!"'),
]:
    once(a, b)

# --- stats for the game-over screen ---
once("stats.score+=ball.pts; stats.made++;",
     "stats.score+=ball.pts; stats.made++; if(ball.pts===3) stats.threes++; if(ball.dunk) stats.dunks++;")
once("const stats={score:0,cpu:0,made:0,att:0,streak:0,best:0};",
     "const stats={score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0};")
once('    lastShot="You blocked "+NAME.d;', '    lastShot="You blocked "+NAME.d; stats.blk++;')
once('lastShot = byP ? "Your dunk was blocked" : "You blocked "+NAME.d+"\'s dunk";',
     'lastShot = byP ? "Your dunk was blocked" : "You blocked "+NAME.d+"\'s dunk"; if(!byP) stats.blk++;')
# only a real game against the computer ends; practice never does
once("if(stats.score>=WIN||stats.cpu>=WIN){", "if(cpuOn && (stats.score>=WIN||stats.cpu>=WIN)){")
once("if(gameOverT>0){gameOverT-=dt; if(gameOverT<=0){stats.score=0;stats.cpu=0;stats.streak=0;inbound(\"p\");}}",
     "if(screen!==\"play\"){updateNets(dt); return;}\n  if(gameOverT>0){gameOverT-=dt; if(gameOverT<=0){endGame(); return;}}")

# --- menus, kits and saving go just before the athlete drawing code ---
once("// two-segment limb from a joint to an end point", open(block).read() + "\n// two-segment limb from a joint to an end point")

# --- HUD: pause button and name pills replace the old opponent chip ---
a = s.index("function drawHUD(){"); b = s.index("function drawControls(){")
s = s[:a] + '''function drawHUD(){
  ctx.fillStyle=C.panel; rr(PAUSE_BTN.x,PAUSE_BTN.y,PAUSE_BTN.w,PAUSE_BTN.h,12); ctx.fill();
  ctx.fillStyle=C.ink; ctx.fillRect(29,25,5,18); ctx.fillRect(38,25,5,18);
  const pill=(x,w,lk,bg,name,score)=>{
    const ink=inkOn(bg);
    ctx.fillStyle=bg; rr(x,14,w,40,20); ctx.fill();
    ctx.strokeStyle="rgba(255,255,255,0.35)"; ctx.lineWidth=1.5; ctx.stroke();
    faceBadge(lk,x+20,34,17,mix(bg,"#FFFFFF",0.3));
    text(name.toUpperCase(),x+43,34,BODY(13,900),ink); text(String(score),x+w-10,35,DISP(24),ink,"right");
  };
  pill(64,166,LOOK.p,C.p1,NAME.p,stats.score);
  if(cpuOn) pill(238,166,LOOK.d,C.p2,NAME.d,stats.cpu);
  const px=cpuOn?412:238, pw=W-16-px, cx=px+pw/2;
  ctx.fillStyle="rgba(46,56,102,0.95)"; rr(px,14,pw,40,12); ctx.fill();
  if(cpuOn && playerDefending()){
    text("DEFENSE · FIRST TO "+WIN,cx,26,BODY(11,900),C.warn,"center");
    text("Stay in front, JUMP to block, tap again at the top for a double jump",cx,42,BODY(12,900),C.ink,"center");
  } else if(cpuOn && owner!==p && ball.state==="free"){
    text("LOOSE BALL!",cx,26,BODY(11,900),C.warn,"center");
    text("Run to the ball to grab it",cx,42,BODY(13,900),C.ink,"center");
  } else if(owner===p && inKey(p.x)){
    text((cpuOn?"YOUR BALL · ":"PRACTICE · ")+"DUNK ZONE",cx,26,BODY(11,900),C.muted,"center");
    text("Tap DUNK · 50% chance to slam it in",cx,42,BODY(13,900),C.ink,"center");
  } else {
    const z=zoneFor(p.x,RR);
    text((cpuOn?"YOUR BALL · ":"PRACTICE · ")+z.name.toUpperCase(),cx,26,BODY(11,900),C.muted,"center");
    text("sweet spot "+z.n[0]+"–"+z.n[1]+" · fade "+z.f[0]+"–"+z.f[1],cx,42,BODY(13,900),C.ink,"center");
  }
  ctx.font=BODY(13,800); const tw=ctx.measureText(lastShot).width+28;
  ctx.fillStyle="rgba(27,35,64,0.92)"; rr(W/2-tw/2-20,352,tw,28,10); ctx.fill();
  text(lastShot,W/2-20,366,BODY(13,800),C.ink,"center");
}
''' + s[b:]
once("const CPU_CHIP={x:722,y:14,w:106,h:40};", "const PAUSE_BTN={x:16,y:14,w:40,h:40};")
once('faceBadge(LOOK.p,36,34,17,"#5C8EEA");', '')  if 'faceBadge(LOOK.p,36,34,17,"#5C8EEA");' in s else None

# --- screens in the draw loop ---
once("function draw(){\n  ctx.save();", "function drawGame(){\n  ctx.save();")
once("// ---------- input ----------", '''function draw(){
  ctx.save();
  if(screen==="title") drawTitle();
  else if(screen==="setup") drawSetup();
  else {
    drawGame();
    if(screen==="pause") drawPause();
    else if(screen==="over") drawOver();
  }
  ctx.restore();
}

// ---------- input ----------''')

# --- input: menus get taps, play gets the pause button instead of the old chip ---
a = s.index('  else if(q.x>=CPU_CHIP.x'); b = s.index('  else if(q.x<HALF && q.y>200)')
s = s[:a] + s[b:]
once('''cv.addEventListener("pointerdown",e=>{
  const q=toLocal(e); let role=null;
  if(''', '''cv.addEventListener("pointerdown",e=>{
  const q=toLocal(e); let role=null;
  if(screen!=="play"){
    for(let i=ui.length-1;i>=0;i--){const u=ui[i];
      if(q.x>=u.x&&q.x<=u.x+u.w&&q.y>=u.y&&q.y<=u.y+u.h){u.fn();break;}}
    e.preventDefault(); return;
  }
  if(q.x>=PAUSE_BTN.x-6&&q.x<=PAUSE_BTN.x+PAUSE_BTN.w+6&&q.y>=PAUSE_BTN.y-6&&q.y<=PAUSE_BTN.y+PAUSE_BTN.h+6){
    screen="pause"; touchJoy=0; shootTouch=false; roles.clear(); e.preventDefault(); return;
  }
  if(''')
once('''  if(e.repeat) return;
  keys.add(k); keyJoyUpdate();''', '''  if(e.repeat) return;
  if(k==="Escape"||k==="p"){ if(screen==="play") screen="pause"; else if(screen==="pause") screen="play"; return; }
  if(k==="Enter"){
    if(screen==="title") openSetup("vs"); else if(screen==="setup") tryStart();
    else if(screen==="over") startGame(); else if(screen==="pause") screen="play";
    return;
  }
  keys.add(k); keyJoyUpdate();''')

# --- start on the title screen with saved kits ---
once('fit(); inbound("p");', 'loadSave(); applyLooks(); fit(); inbound("p"); screen="title";')

open(game, "w").write(s)
print("patched")
