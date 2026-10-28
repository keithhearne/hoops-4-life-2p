// ---------- the two boys, their kits, and saved progress ----------
const BOYS={
  zackie:{name:"Zackie",num:"11",skin:"#F2C6A8",skinDark:"#D9A285",hair:"#C9A15A",hairHi:"#E6C784",brow:"#A88445",
    eye:"#6E8A9A",style:"crop",gapTeeth:true,bigEars:true},
  keelan:{name:"Keelan",num:"3",skin:"#F0C3A7",skinDark:"#D4A086",hair:"#6B4A32",hairHi:"#9A7556",brow:"#4A3020",
    eye:"#5A3A22",style:"quiff",gapTeeth:false,bigEars:false}
};
const MAINS={blue:"#2F6FE4",green:"#1FA35B",purple:"#7B4FD6",red:"#E03A3A",black:"#22232B",white:"#F4F4F1",yellow:"#FFC93C"};
const TRIMS={white:"#FFFFFF",green:"#1FA35B",red:"#E03A3A",yellow:"#FFC93C",blue:"#2F6FE4",purple:"#7B4FD6",black:"#22232B",navy:"#1B2340"};
const kits={zackie:{main:"blue",trim:"white"},keelan:{main:"yellow",trim:"navy"}};
let human="zackie", wins={zackie:0,keelan:0};
const NAME={p:"Zackie",d:"Keelan"};
function other(){return human==="zackie"?"keelan":"zackie";}
function hex2rgb(h){const n=parseInt(h.slice(1),16);return [n>>16&255,n>>8&255,n&255];}
function mix(a,b,t){const A=hex2rgb(a),B=hex2rgb(b);return "#"+A.map((v,i)=>Math.round(v+(B[i]-v)*t).toString(16).padStart(2,"0")).join("");}
function isLight(h){const [r,g,b]=hex2rgb(h);return (0.2126*r+0.7152*g+0.0722*b)/255>0.6;}
function inkOn(bg){return isLight(bg)?"#1B2340":"#FFFFFF";}
function kitLook(b,k,dir){
  const main=MAINS[k.main], trim=TRIMS[k.trim];
  return Object.assign({},b,{dir,jersey:main,trim,shorts:mix(main,"#000000",0.18),numCol:trim,shoe:"#FFFFFF",sole:"#1B2340",sock:"#FFFFFF"});
}
function niceKit(k){const c=s=>s[0].toUpperCase()+s.slice(1);return c(k.main)+" with "+k.trim+" trim";}
// recolour the manga portrait to match a boy's chosen kit
function mangaSrc(boy){
  const k=kits[boy], main=MAINS[k.main], trim=TRIMS[k.trim], light=mix(main,"#FFFFFF",0.28);
  const outline=isLight(trim)?"#1A1424":"#FFFFFF";
  const sw=(s,a,b)=>s.split(a).join(b);
  let s;
  if(boy==="zackie"){
    s=sw(sw(MANGA_SVG_Z,"#2F6FE4",main),"#5C8EEA",light);
    s=sw(s,'stroke="#FFFFFF" stroke-width="7"','stroke="'+trim+'" stroke-width="7"');
    s=sw(s,'stroke="#FFFFFF" stroke-width="6"','stroke="'+trim+'" stroke-width="6"');
    s=sw(s,'fill="#FFFFFF" stroke="#1A1424" stroke-width="5" paint-order="stroke">11','fill="'+trim+'" stroke="'+outline+'" stroke-width="5" paint-order="stroke">11');
  } else {
    s=sw(sw(MANGA_SVG_K,"#FFC93C",main),"#FFDB7A",light);
    s=sw(s,'stroke="#1B2340" stroke-width="7"','stroke="'+trim+'" stroke-width="7"');
    s=sw(s,'stroke="#1B2340" stroke-width="6"','stroke="'+trim+'" stroke-width="6"');
    s=sw(s,'fill="#1B2340" stroke="#FFFFFF" stroke-width="5" paint-order="stroke">3','fill="'+trim+'" stroke="'+outline+'" stroke-width="5" paint-order="stroke">3');
  }
  return "data:image/svg+xml;charset=utf-8,"+encodeURIComponent(s);
}
function refreshManga(boy){MIMG[boy].src=mangaSrc(boy);}
// sets up both players' looks, colours and names for the chosen kits and who is playing
function applyLooks(){
  const o=other();
  LOOK.p=kitLook(BOYS[human],kits[human],1);
  LOOK.d=kitLook(BOYS[o],kits[o],-1);
  C.p1=MAINS[kits[human].main]; C.p2=MAINS[kits[o].main];
  NAME.p=BOYS[human].name; NAME.d=BOYS[o].name;
  refreshManga("zackie"); refreshManga("keelan");
}
const SAVE_KEY="hoops4life";
function loadSave(){
  try{
    const s=JSON.parse(localStorage.getItem(SAVE_KEY)||"null");
    if(!s) return;
    for(const b of ["zackie","keelan"]) if(s.kits&&s.kits[b]&&MAINS[s.kits[b].main]&&TRIMS[s.kits[b].trim]) kits[b]=s.kits[b];
    if(BOYS[s.human]) human=s.human;
    if(s.wins) wins=Object.assign({zackie:0,keelan:0},s.wins);
  }catch(_){}
}
function saveGame(){try{localStorage.setItem(SAVE_KEY,JSON.stringify({kits,human,wins}));}catch(_){}}

// ---------- screens: title, setup, play, pause, game over ----------
let screen="title", mode="vs", overWinner="p", ui=[];
function startGame(){
  applyLooks();
  Object.assign(stats,{score:0,cpu:0,made:0,att:0,streak:0,best:0,threes:0,dunks:0,blk:0});
  cpuOn = mode==="vs";
  pendingInbound=null; gameOverT=0; celebrate.t=0; charge.shown=0; dblFx.t=0; cpuFx.t=0;
  moods.p.m=moods.d.m="happy"; moods.p.t=moods.d.t=0;
  touchJoy=0; shootTouch=false; shootKey=false; needRelease=true;
  lastShot="Hold SHOOT, let go in the green zone";
  inbound("p"); screen="play";
  if(cpuOn) say(NAME.p+" vs "+NAME.d,"First to "+WIN+" wins",C.ink);
  else say("Shooting practice",NAME.p+", shoot as much as you like",C.ink);
}
function endGame(){
  const youWin=stats.score>=WIN; overWinner=youWin?"p":"d";
  if(youWin) wins[human]=(wins[human]||0)+1;
  saveGame(); screen="over";
}
function openSetup(m){mode=m; screen="setup";}
function tryStart(){ if(mode==="vs" && kits.zackie.main===kits.keelan.main) return; saveGame(); startGame(); }
function button(x,y,w,h,label,o,fn){
  o=o||{};
  ctx.globalAlpha=o.disabled?0.45:1;
  ctx.fillStyle=o.fill||C.panel; rr(x,y,w,h,14); ctx.fill();
  if(o.outline){ctx.strokeStyle=o.outline; ctx.lineWidth=2; ctx.stroke();}
  const ink=o.ink||C.ink;
  text(label,x+w/2,y+h/2+(o.sub?-7:1),BODY(o.size||17,900),ink,"center");
  if(o.sub) text(o.sub,x+w/2,y+h/2+11,BODY(11,800),ink,"center");
  ctx.globalAlpha=1;
  if(!o.disabled && fn) ui.push({x,y,w,h,fn});
}
function shade(a){ctx.fillStyle="rgba(10,14,30,"+a+")"; ctx.fillRect(0,0,W,H);}
function portraitBadge(boy,cx,cy,r){
  const col=MAINS[kits[boy].main], img=MIMG[boy];
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fillStyle=col; ctx.fill(); ctx.clip();
  if(img.complete && img.naturalWidth) ctx.drawImage(img,70,8,260,260,cx-r,cy-r,r*2,r*2);
  ctx.restore();
  ctx.strokeStyle=C.ink; ctx.lineWidth=4; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.stroke();
}
function bigTitle(t,x,y,size,align){
  ctx.font=DISP(size); ctx.textAlign=align||"center"; ctx.textBaseline="middle";
  ctx.lineWidth=7; ctx.lineJoin="round"; ctx.strokeStyle=C.navy; ctx.strokeText(t,x,y);
  ctx.fillStyle=C.warn; ctx.fillText(t,x,y);
}
function drawTitle(){
  ui=[]; drawCourt(); drawNetLayer(false); drawNetLayer(true); shade(0.72);
  portraitBadge("zackie",140,196,92); text(BOYS.zackie.name.toUpperCase(),140,306,DISP(18),C.ink,"center");
  portraitBadge("keelan",W-140,196,92); text(BOYS.keelan.name.toUpperCase(),W-140,306,DISP(18),C.ink,"center");
  bigTitle("HOOPS 4 LIFE",W/2,58,48);
  text(BOYS.zackie.name+" vs "+BOYS.keelan.name,W/2,98,BODY(16,900),C.muted,"center");
  const bx=W/2-160, bw=320;
  button(bx,122,bw,50,"1 v 1 vs COMPUTER",{fill:"#2F6FE4",sub:"First to "+WIN},()=>openSetup("vs"));
  button(bx,180,bw,50,"SHOOTING PRACTICE",{fill:"#F26B1D",ink:C.navy,sub:"No defender"},()=>openSetup("practice"));
  button(bx,238,bw,42,"TABLE MODE",{disabled:true,sub:"2 players, 1 phone · coming soon"});
  button(bx,288,bw,42,"TWO PHONES",{disabled:true,sub:"2 players over Wi-Fi · coming soon"});
  text("Wins vs the computer:  "+BOYS.zackie.name+" "+(wins.zackie||0)+"  ·  "+BOYS.keelan.name+" "+(wins.keelan||0),W/2,358,BODY(14,900),C.muted,"center");
}
function swatch(cx,cy,r,col,sel,disabled,fn){
  ctx.globalAlpha=disabled?0.25:1;
  if(sel){ctx.strokeStyle=C.warn; ctx.lineWidth=3; ctx.beginPath(); ctx.arc(cx,cy,r+4,0,Math.PI*2); ctx.stroke();}
  ctx.fillStyle=col; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle="rgba(255,255,255,0.7)"; ctx.lineWidth=1.5; ctx.stroke();
  if(disabled){ctx.strokeStyle=C.ink; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(cx-r*0.7,cy+r*0.7); ctx.lineTo(cx+r*0.7,cy-r*0.7); ctx.stroke();}
  ctx.globalAlpha=1;
  if(!disabled) ui.push({x:cx-r-3,y:cy-r-3,w:2*r+6,h:2*r+6,fn});
}
function playerCard(boy,x,y,w,h){
  const sel=boy===human, k=kits[boy], b=BOYS[boy];
  ui.push({x,y,w,h,fn:()=>{human=boy;}});
  ctx.fillStyle=sel?"rgba(46,56,102,0.98)":"rgba(27,35,64,0.95)"; rr(x,y,w,h,18); ctx.fill();
  ctx.strokeStyle=sel?C.warn:"rgba(255,255,255,0.15)"; ctx.lineWidth=sel?4:2; ctx.stroke();
  // player preview in his kit
  ctx.save(); rr(x,y,w,h,18); ctx.clip();
  ctx.fillStyle=MAINS[k.main]; ctx.globalAlpha=0.18; ctx.beginPath(); ctx.arc(x+80,y+h-60,74,0,Math.PI*2); ctx.fill(); ctx.globalAlpha=1;
  ctx.translate(x+80,y+h-12); ctx.scale(1.95,1.95);
  drawAthlete({x:0,y:0,lean:0,spd:0,run:0},kitLook(b,k,1),{x:14,y:-34},{x:-12,y:-26},false,false);
  ctx.restore();
  const tag=sel?"PLAYING":(mode==="vs"?"COMPUTER":"WATCHING");
  ctx.fillStyle=sel?C.warn:C.panel; rr(x+12,y+12,100,24,12); ctx.fill();
  text(tag,x+62,y+24,BODY(12,900),sel?C.navy:C.muted,"center");
  const tx=x+160;
  text(b.name.toUpperCase(),tx,y+30,DISP(24),C.ink); text("#"+b.num,x+w-16,y+30,DISP(20),C.muted,"right");
  text("JERSEY",tx,y+62,BODY(12,900),C.muted);
  Object.keys(MAINS).forEach((m,i)=>swatch(tx+14+i*31,y+86,12,MAINS[m],k.main===m,false,()=>{
    k.main=m; if(TRIMS[k.trim]===MAINS[m]) k.trim=(m==="white"?"navy":"white"); refreshManga(boy);
  }));
  text("TRIM",tx,y+120,BODY(12,900),C.muted);
  Object.keys(TRIMS).forEach((t,i)=>{const same=TRIMS[t]===MAINS[k.main];
    swatch(tx+13+i*27,y+144,10,TRIMS[t],k.trim===t,same,()=>{k.trim=t; refreshManga(boy);});});
  text(niceKit(k),tx,y+180,BODY(14,900),C.ink);
  text(sel?"Ready to play":"Tap the card to "+(mode==="vs"?"play as ":"pick ")+b.name,tx,y+h-22,BODY(12,800),sel?C.warn:C.muted);
}
function drawSetup(){
  ui=[]; drawCourt(); shade(0.8);
  text(mode==="vs"?"WHO'S PLAYING?":"WHO'S PRACTISING?",W/2,26,DISP(22),C.warn,"center");
  text(mode==="vs"?"Tap a card to play as him. The other one is the computer. Pick jersey and trim colours.":"Tap a card to pick who practises, and choose the kit.",W/2,47,BODY(13,800),C.muted,"center");
  playerCard("zackie",22,62,390,262);
  playerCard("keelan",432,62,390,262);
  const clash=mode==="vs" && kits.zackie.main===kits.keelan.main;
  button(22,336,130,42,"BACK",{},()=>{screen="title";});
  if(clash) text("Pick different jersey colours",W/2,357,BODY(14,900),C.warn,"center");
  button(W-22-210,336,210,42,"START",{fill:"#F26B1D",ink:C.navy,disabled:clash},tryStart);
}
function drawPause(){
  ui=[]; shade(0.75);
  bigTitle("PAUSED",W/2,92,40);
  const bx=W/2-150;
  button(bx,134,300,50,"RESUME",{fill:"#2F6FE4"},()=>{screen="play"; needRelease=true;});
  button(bx,194,300,44,"RESTART",{outline:"rgba(255,255,255,0.3)"},()=>startGame());
  button(bx,248,300,44,"MAIN MENU",{outline:"rgba(255,255,255,0.3)"},()=>{screen="title";});
}
function drawOver(){
  ui=[]; shade(0.84);
  const youWin=overWinner==="p", boy=youWin?human:other();
  portraitBadge(boy,180,186,112);
  let size=40; ctx.font=DISP(size);
  const head=(youWin?NAME.p:NAME.d).toUpperCase()+" WINS!";
  while(size>24 && ctx.measureText(head).width>470){size-=2; ctx.font=DISP(size);}
  bigTitle(head,330,62,size,"left");
  text(NAME.p+"  "+stats.score+"  –  "+stats.cpu+"  "+NAME.d,332,104,BODY(20,900),C.ink);
  text(NAME.p.toUpperCase()+"'S GAME",332,140,BODY(12,900),C.muted);
  const rows=[["Shots made",stats.made+" / "+stats.att],["3-pointers",String(stats.threes)],["Dunks",String(stats.dunks)],
    ["Blocks",String(stats.blk)],["Best streak",String(stats.best)],["Wins vs computer",String(wins[human]||0)]];
  rows.forEach(([l,v],i)=>{const cx=332+(i%2)*236, cy=168+Math.floor(i/2)*38;
    ctx.fillStyle="rgba(46,56,102,0.9)"; rr(cx,cy-15,224,32,10); ctx.fill();
    text(l,cx+12,cy+1,BODY(14,800),C.muted); text(v,cx+212,cy+2,DISP(16),C.ink,"right");});
  button(332,312,220,50,"REMATCH",{fill:"#F26B1D",ink:C.navy},()=>startGame());
  button(564,312,140,50,"MENU",{outline:"rgba(255,255,255,0.3)"},()=>{screen="title";});
}
