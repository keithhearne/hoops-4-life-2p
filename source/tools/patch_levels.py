import sys
f = sys.argv[1]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

# --- difficulty and game length can change per level ---
once("const W=844, H=390, FLOOR=310, G=1100, GB=900, FILL=1.75, WIN=21;",
     "const W=844, H=390, FLOOR=310, G=1100, GB=900, FILL=1.75;\nlet WIN=21;   // points needed to win; levels change it")
once("const SKILL={noReact:", "const SKILL_BASE={acc:1, noReact:")
once("dunkTry:0.3, dunkMake:0.5, blockDunk:0.25, dblChance:0.33};",
     "dunkTry:0.3, dunkMake:0.5, blockDunk:0.25, dblChance:0.33};\nlet SKILL=Object.assign({},SKILL_BASE);   // the quick 1 v 1 game uses SKILL_BASE; each level sets its own")
once("const chance=z.cpu*(cpu.fade?0.85:1), make=Math.random()<chance;",
     "const chance=Math.min(0.95,z.cpu*SKILL.acc*(cpu.fade?0.85:1)), make=Math.random()<chance;")

# --- saving each boy's progress ---
once("    if(s.wins) wins=Object.assign({zackie:0,keelan:0},s.wins);",
     "    if(s.wins) wins=Object.assign({zackie:0,keelan:0},s.wins);\n    if(s.progress) progress=Object.assign({zackie:0,keelan:0},s.progress);")
once("JSON.stringify({kits,human,wins})", "JSON.stringify({kits,human,wins,progress})")

# --- starting and ending games ---
once("""  cpuOn = mode==="vs";""",
     """  if(mode==="level"){SKILL=levelSkill(level); WIN=levelTarget(level);}
  else {SKILL=Object.assign({},SKILL_BASE); WIN=21;}
  cpuOn = mode!=="practice";""")
once("""  if(cpuOn) say(NAME.p+" vs "+NAME.d,"First to "+WIN+" wins",C.ink);""",
     """  if(mode==="level") say(levelName(level),NAME.p+" vs "+NAME.d+" · first to "+WIN,C.ink);
  else if(cpuOn) say(NAME.p+" vs "+NAME.d,"First to "+WIN+" wins",C.ink);""")
once("""  if(youWin) wins[human]=(wins[human]||0)+1;
  saveGame(); screen="over";""",
     """  if(youWin) wins[human]=(wins[human]||0)+1;
  newRoad=false;
  if(mode==="level" && youWin && level>=progress[human]){
    progress[human]=Math.min(LEVELS,level+1);
    newRoad = progress[human]<LEVELS && progress[human]%STOPS===0;
  }
  saveGame(); screen="over";""")
once("""function tryStart(){ if(mode==="vs" && kits.zackie.main===kits.keelan.main) return; saveGame(); startGame(); }""",
     """function tryStart(){ if(mode!=="practice" && kits.zackie.main===kits.keelan.main) return; saveGame(); startGame(); }
function toMap(){screen="title"; mapScroll=null;}""")

# --- the level map ---
a = s.index("let mapScroll=null, mapDrag=null;")
b = s.index("\n", a)
s = s[:a] + "let mapScroll=null, mapDrag=null, mapMsg={text:\"\",t:0};   // null = scroll to the current level next time the map is drawn" + s[b:]

once("function mapMaxScroll(){return Math.max(0,mapContentH()-MAP.h);}",
'''const VIEW={y:MAP.y+48,h:MAP.h-48};   // the scrolling part of the map, under the Zackie/Keelan tabs
function mapMaxScroll(){return Math.max(0,mapContentH()-VIEW.h);}
// ---------- levels: every stop is a 1 v 1 game, each one a bit harder than the last ----------
const LEVELS=ROADS.length*STOPS;
let progress={zackie:0,keelan:0}, level=0, newRoad=false;   // progress = how many levels that boy has beaten
function levelName(n){return "Road "+(Math.floor(n/STOPS)+1)+" · Level "+(n%STOPS+1);}
function levelTarget(n){return n<STOPS?11:(n<2*STOPS?15:21);}   // longer games on later roads
function levelSkill(n){
  const t=n/(LEVELS-1), L=(a,b)=>a+(b-a)*t;   // level 1 = easiest, last level = hardest
  return {acc:L(0.6,1.25), noReact:L(0.5,0.06), timingNoise:L(0.6,0.16), defSpeed:L(115,195), chaseSpeed:L(135,210),
    atkSpeed:L(100,165), fadeChance:L(0.25,0.85), dunkTry:L(0.08,0.45), dunkMake:L(0.38,0.62), blockDunk:L(0.08,0.42),
    dblChance:L(0.05,0.5)};
}
function openLevel(n){level=n; mode="level"; screen="setup";}
function tapMap(q){
  const cy=q.y-VIEW.y+mapScroll;
  for(let r=0;r<ROADS.length;r++) for(let i=0;i<STOPS;i++){
    const s=stopPos(r,i), n=r*STOPS+i;
    if(Math.hypot(q.x-s.x,cy-s.y)<STOP_R+10){
      if(n<=progress[human]) openLevel(n);
      else mapMsg={text:"Beat level "+((progress[human]%STOPS)+1)+(Math.floor(progress[human]/STOPS)!==r?" on road "+(Math.floor(progress[human]/STOPS)+1):"")+" first",t:1.8};
      return;
    }
  }
}
function padlock(x,y,col){
  ctx.strokeStyle=col; ctx.lineWidth=2; ctx.beginPath(); ctx.arc(x,y-3,3.6,Math.PI,0); ctx.stroke();
  ctx.fillStyle=col; rr(x-5.5,y-3,11,8,2); ctx.fill();
}''')

a = s.index("function drawRoadMap(){"); b = s.index("function inMap(q){")
s = s[:a] + '''function drawRoadMap(){
  const prog=progress[human];
  if(mapScroll===null){ // centre on the level this boy should play next
    const n=Math.min(prog,LEVELS-1), sp=stopPos(Math.floor(n/STOPS),n%STOPS);
    mapScroll=clamp(sp.y-VIEW.h*0.62,0,mapMaxScroll());
  }
  ctx.save();
  ctx.fillStyle="rgba(16,21,43,0.96)"; rr(MAP.x,MAP.y,MAP.w,MAP.h,18); ctx.fill();
  ctx.strokeStyle="rgba(255,255,255,0.14)"; ctx.lineWidth=2; ctx.stroke();
  // whose map: one tab per boy
  const tw=(MAP.w-30)/2;
  ["zackie","keelan"].forEach((boy,k)=>{
    const x=MAP.x+10+k*(tw+10), sel=boy===human, col=MAINS[kits[boy].main];
    ctx.fillStyle=sel?col:"rgba(46,56,102,0.9)"; rr(x,MAP.y+9,tw,32,12); ctx.fill();
    if(sel){ctx.strokeStyle=C.ink; ctx.lineWidth=2; ctx.stroke();}
    text(BOYS[boy].name.toUpperCase()+"  "+Math.min(progress[boy],LEVELS)+"/"+LEVELS,x+tw/2,MAP.y+26,BODY(13,900),sel?inkOn(col):C.muted,"center");
    ui.push({x,y:MAP.y+5,w:tw,h:40,fn:()=>{if(human!==boy){human=boy; mapScroll=null; saveGame();}}});
  });
  ctx.beginPath(); ctx.rect(MAP.x,VIEW.y,MAP.w,VIEW.h); ctx.clip();
  ctx.translate(0,VIEW.y-mapScroll);
  const locked="#39416A", pulse=1+0.12*Math.sin(performance.now()/180);
  ROADS.forEach((road,r)=>{
    const start=stopPos(r,0), open=r*STOPS<=prog;
    text(road.name+(open?"":" · LOCKED"),MAP.x+MAP.w/2,start.y+34,DISP(15),open?C.ink:C.muted,"center");
    // the road: straight lines between the stops; the part leading to locked levels is grey
    const pts=[];
    for(let i=0;i<STOPS;i++){const sp=stopPos(r,i);
      if(i===0){pts.push([sp.x,sp.y,0]); pts.push([sp.x,sp.y-LEAD,1]);}
      else if(i===STOPS-1){pts.push([sp.x,sp.y+LEAD,i]); pts.push([sp.x,sp.y,i]);}
      else pts.push([sp.x,sp.y,i]);}
    ctx.lineWidth=5; ctx.lineCap="round"; ctx.lineJoin="round";
    for(let k=0;k<pts.length-1;k++){
      ctx.strokeStyle=(r*STOPS+pts[k+1][2]<=prog)?road.col:locked;
      ctx.beginPath(); ctx.moveTo(pts[k][0],pts[k][1]); ctx.lineTo(pts[k+1][0],pts[k+1][1]); ctx.stroke();
    }
    // the levels
    for(let i=0;i<STOPS;i++){
      const sp=stopPos(r,i), n=r*STOPS+i, done=n<prog, cur=n===prog, R=cur?STOP_R*1.1:STOP_R;
      if(cur){ctx.strokeStyle=C.warn; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(sp.x,sp.y,(STOP_R+7)*pulse,0,Math.PI*2); ctx.stroke();}
      ctx.fillStyle=(done||cur)?road.col:locked; ctx.beginPath(); ctx.arc(sp.x,sp.y,R,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle=(done||cur)?C.ink:"rgba(255,255,255,0.35)"; ctx.lineWidth=3; ctx.stroke();
      text(String(i+1),sp.x,sp.y+1,DISP(18),(done||cur)?inkOn(road.col):"rgba(255,255,255,0.45)","center");
      if(done){ // gold tick badge for a beaten level
        ctx.fillStyle=C.warn; ctx.beginPath(); ctx.arc(sp.x+15,sp.y-14,8,0,Math.PI*2); ctx.fill();
        ctx.strokeStyle=C.navy; ctx.lineWidth=2.4; ctx.beginPath(); ctx.moveTo(sp.x+11,sp.y-14); ctx.lineTo(sp.x+14,sp.y-11); ctx.lineTo(sp.x+19,sp.y-17); ctx.stroke();
      } else if(!cur){
        ctx.fillStyle=C.navy; ctx.beginPath(); ctx.arc(sp.x+15,sp.y+14,8,0,Math.PI*2); ctx.fill();
        padlock(sp.x+15,sp.y+15,C.muted);
      }
      if(cur) text("PLAY",sp.x,sp.y+R+12,BODY(11,900),C.warn,"center");
    }
  });
  ctx.restore();
  // scroll bar
  const max=mapMaxScroll();
  if(max>0){
    const track=VIEW.h-20, bar=Math.max(36,track*VIEW.h/(VIEW.h+max)), by=VIEW.y+10+(track-bar)*(mapScroll/max);
    ctx.fillStyle="rgba(255,255,255,0.12)"; rr(MAP.x+MAP.w-10,VIEW.y+10,4,track,2); ctx.fill();
    ctx.fillStyle="rgba(255,255,255,0.55)"; rr(MAP.x+MAP.w-10,by,4,bar,2); ctx.fill();
  }
  if(mapMsg.t>0){
    mapMsg.t-=1/60;
    ctx.globalAlpha=Math.min(1,mapMsg.t*3);
    ctx.font=BODY(13,900); const w=ctx.measureText(mapMsg.text).width+24;
    ctx.fillStyle="rgba(10,14,30,0.95)"; rr(MAP.x+MAP.w/2-w/2,MAP.y+MAP.h-44,w,30,12); ctx.fill();
    text(mapMsg.text,MAP.x+MAP.w/2,MAP.y+MAP.h-29,BODY(13,900),C.warn,"center");
    ctx.globalAlpha=1;
  }
}
''' + s[b:]
once("function inMap(q){return q.x>=MAP.x&&q.x<=MAP.x+MAP.w&&q.y>=MAP.y&&q.y<=MAP.y+MAP.h;}",
     "function inMap(q){return q.x>=MAP.x&&q.x<=MAP.x+MAP.w&&q.y>=VIEW.y&&q.y<=VIEW.y+VIEW.h;}")
once('''{fill:"#2F6FE4",sub:"First to "+WIN},()=>openSetup("vs"));''',
     '''{fill:"#2F6FE4",sub:"Quick game · first to 21"},()=>openSetup("vs"));''')

# --- setup screen for a level ---
once("  ui.push({x,y,w,h,fn:()=>{human=boy;}});",
     "  if(mode!==\"level\") ui.push({x,y,w,h,fn:()=>{human=boy;}});   // on a level, the boy whose map it is plays")
once('''const tag=sel?"PLAYING":(mode==="vs"?"COMPUTER":"WATCHING");''',
     '''const tag=sel?"PLAYING":(mode==="practice"?"WATCHING":"COMPUTER");''')
once('''  text(sel?"Ready to play":"Tap the card to "+(mode==="vs"?"play as ":"pick ")+b.name,tx,y+h-22,BODY(12,800),sel?C.warn:C.muted);''',
     '''  const hint=sel?"Ready to play":(mode==="level"?"Plays as the computer":"Tap the card to "+(mode==="vs"?"play as ":"pick ")+b.name);
  text(hint,tx,y+h-22,BODY(12,800),sel?C.warn:C.muted);''')
once('''  text(mode==="vs"?"WHO'S PLAYING?":"WHO'S PRACTISING?",W/2,26,DISP(22),C.warn,"center");
  text(mode==="vs"?"Tap a card to play as him. The other one is the computer. Pick jersey and trim colours.":"Tap a card to pick who practises, and choose the kit.",W/2,47,BODY(13,800),C.muted,"center");''',
     '''  const heads={vs:["WHO'S PLAYING?","Tap a card to play as him. The other one is the computer. Pick jersey and trim colours."],
    practice:["WHO'S PRACTISING?","Tap a card to pick who practises, and choose the kit."],
    level:[levelName(level).toUpperCase(),BOYS[human].name+" vs the computer · first to "+levelTarget(level)+" · pick jersey and trim colours"]};
  text(heads[mode][0],W/2,26,DISP(22),C.warn,"center");
  text(heads[mode][1],W/2,47,BODY(13,800),C.muted,"center");''')
once('''  const clash=mode==="vs" && kits.zackie.main===kits.keelan.main;
  button(22,336,130,42,"BACK",{},()=>{screen="title";});''',
     '''  const clash=mode!=="practice" && kits.zackie.main===kits.keelan.main;
  button(22,336,130,42,"BACK",{},toMap);''')

# --- game over for a level ---
once('''  const head=(youWin?NAME.p:NAME.d).toUpperCase()+" WINS!";''',
     '''  const lv=mode==="level", allDone=lv && youWin && level===LEVELS-1;
  const head=allDone?"ALL LEVELS BEATEN!":(lv&&youWin?"LEVEL "+(level%STOPS+1)+" BEATEN!":(youWin?NAME.p:NAME.d).toUpperCase()+" WINS!");''')
once('''  text(NAME.p.toUpperCase()+"'S GAME",332,140,BODY(12,900),C.muted);''',
     '''  if(lv) text(levelName(level).toUpperCase()+(newRoad?"   ·   ROAD "+(Math.floor(progress[human]/STOPS)+1)+" IS OPEN!":""),332,140,BODY(12,900),newRoad?C.warn:C.muted);
  else text(NAME.p.toUpperCase()+"'S GAME",332,140,BODY(12,900),C.muted);''')
once('''  button(332,312,220,50,"REMATCH",{fill:"#F26B1D",ink:C.navy},()=>startGame());
  button(564,312,140,50,"MENU",{outline:"rgba(255,255,255,0.3)"},()=>{screen="title";});''',
     '''  if(lv){
    if(youWin && level<LEVELS-1) button(332,312,220,50,"NEXT LEVEL",{fill:"#F26B1D",ink:C.navy,sub:levelName(level+1)},()=>{level++; startGame();});
    else button(332,312,220,50,youWin?"PLAY AGAIN":"TRY AGAIN",{fill:"#F26B1D",ink:C.navy},()=>startGame());
    button(564,312,140,50,"MAP",{outline:"rgba(255,255,255,0.3)"},toMap);
  } else {
    button(332,312,220,50,"REMATCH",{fill:"#F26B1D",ink:C.navy},()=>startGame());
    button(564,312,140,50,"MENU",{outline:"rgba(255,255,255,0.3)"},toMap);
  }''')
once('''  button(bx,248,300,44,"MAIN MENU",{outline:"rgba(255,255,255,0.3)"},()=>{screen="title";});''',
     '''  button(bx,248,300,44,"MAIN MENU",{outline:"rgba(255,255,255,0.3)"},toMap);''')

# --- input: tabs and buttons first, then dragging or tapping the map ---
once('''    if(screen==="title" && inMap(q)){
      mapDrag={id:e.pointerId,y0:q.y,s0:mapScroll};
      try{cv.setPointerCapture(e.pointerId);}catch(_){}
      e.preventDefault(); return;
    }
    for(let i=ui.length-1;i>=0;i--){const u=ui[i];
      if(q.x>=u.x&&q.x<=u.x+u.w&&q.y>=u.y&&q.y<=u.y+u.h){u.fn();break;}}
    e.preventDefault(); return;''',
     '''    for(let i=ui.length-1;i>=0;i--){const u=ui[i];
      if(q.x>=u.x&&q.x<=u.x+u.w&&q.y>=u.y&&q.y<=u.y+u.h){u.fn(); e.preventDefault(); return;}}
    if(screen==="title" && inMap(q)){
      mapDrag={id:e.pointerId,y0:q.y,s0:mapScroll,moved:false};
      try{cv.setPointerCapture(e.pointerId);}catch(_){}
    }
    e.preventDefault(); return;''')
once("  if(mapDrag && mapDrag.id===e.pointerId){const q=toLocal(e); mapScroll=clamp(mapDrag.s0-(q.y-mapDrag.y0),0,mapMaxScroll()); return;}",
     "  if(mapDrag && mapDrag.id===e.pointerId){const q=toLocal(e); if(Math.abs(q.y-mapDrag.y0)>7) mapDrag.moved=true;\n    mapScroll=clamp(mapDrag.s0-(q.y-mapDrag.y0),0,mapMaxScroll()); return;}")
once("  if(mapDrag && mapDrag.id===e.pointerId) mapDrag=null;",
     "  if(mapDrag && mapDrag.id===e.pointerId){ if(!mapDrag.moved && e.type===\"pointerup\") tapMap(toLocal(e)); mapDrag=null; }")

open(f, "w").write(s)
print("patched")
