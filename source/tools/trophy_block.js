// ---------- Trophies: buy one with medals and crowns, tap it open, spin the prize wheel ----------
// Prices: about one level of medals for a Rare; each step up costs roughly twice as much and adds crowns.
const TROPHY_TYPES=[
  {id:"rare",name:"RARE",col:"#3D9BFF",dark:"#1B4F99",price:{m:5,c:0},player:0.025,med:[2,3,4,6],cr:[1]},
  {id:"epic",name:"EPIC",col:"#A86BFF",dark:"#5A2DA8",price:{m:12,c:0},player:0.05,med:[4,6,8,12],cr:[1,2]},
  {id:"legendary",name:"LEGENDARY",col:"#FFB020",dark:"#A86400",price:{m:20,c:1},player:0.10,med:[8,12,16,24],cr:[1,2]},
  {id:"diamond",name:"DIAMOND",col:"#7FE3FF",dark:"#2A8DB0",price:{m:35,c:2},player:0.15,med:[12,20,30,40],cr:[1,2,3]}
];
// what each boy has won from trophies, and what he has spent
let bonus={zackie:{m:0,c:0},keelan:{m:0,c:0}}, spent={zackie:{m:0,c:0},keelan:{m:0,c:0}};
let extraBalls={zackie:[],keelan:[]}, shoesOwned={zackie:[],keelan:[]};
function wallet(b){return {m:medals[b].length+bonus[b].m-spent[b].m, c:crowns[b].length+bonus[b].c-spent[b].c};}
function canBuy(b,t){const w=wallet(b); return w.m>=t.price.m && w.c>=t.price.c;}
let tro={stage:"shop",type:null,taps:0,shake:0,t:0,last:0,wheel:null,msg:{text:"",t:0},parts:[]};
const pickOne=a=>a[Math.floor(Math.random()*a.length)];
function buildWheel(t,boy){
  const items=[], used={ball:new Set(),shoe:new Set()};
  const lockedBosses=BOSSES.map((_,i)=>i).filter(i=>!owned[boy].includes("boss"+i));
  const ballsLeft=ballList().map((_,i)=>i).filter(i=>i>0 && !ballUnlocked(boy,i));
  const shoesLeft=ARENAS.map((_,i)=>i).filter(i=>!shoesOwned[boy].includes(i));
  const medalsItem=()=>({kind:"medals",n:pickOne(t.med)});
  for(let k=0;k<9;k++){
    const r=Math.random();
    let it;
    if(r<0.25){const c=ballsLeft.filter(i=>!used.ball.has(i)); it=c.length?{kind:"ball",i:pickOne(c)}:medalsItem(); if(it.kind==="ball") used.ball.add(it.i);}
    else if(r<0.5){const c=shoesLeft.filter(i=>!used.shoe.has(i)); it=c.length?{kind:"shoes",i:pickOne(c)}:medalsItem(); if(it.kind==="shoes") used.shoe.add(it.i);}
    else if(r<0.7) it={kind:"crowns",n:pickOne(t.cr)};
    else it=medalsItem();
    it.w=0.6+Math.random()*0.8;   // each prize gets its own random chance
    items.push(it);
  }
  const playerIt=lockedBosses.length?{kind:"player",i:pickOne(lockedBosses)}:Object.assign(medalsItem(),{w:1});
  items.splice(Math.floor(Math.random()*10),0,playerIt);
  // pick the prize first: the player slot has the trophy's fixed chance, the rest share what's left
  let win;
  if(playerIt.kind==="player" && Math.random()<t.player) win=items.indexOf(playerIt);
  else {
    const others=items.map((it,k)=>k).filter(k=>items[k]!==playerIt || playerIt.kind!=="player");
    const tot=others.reduce((s,k)=>s+items[k].w,0); let r=Math.random()*tot; win=others[others.length-1];
    for(const k of others){r-=items[k].w; if(r<=0){win=k; break;}}
  }
  // a real spin: random start, random number of turns, slowing down like a wheel with friction, landing anywhere inside the slot
  const A=Math.PI*2/10, rot0=Math.random()*Math.PI*2, jitter=(Math.random()*2-1)*0.38*A;
  let end=-(win+0.5)*A+jitter; const turns=5+Math.floor(Math.random()*3);
  let total=((end-rot0)%(Math.PI*2)+Math.PI*2)%(Math.PI*2)+turns*Math.PI*2;
  return {items,win,rot0,total,ease:1.9+Math.random()*0.9,T:7,t:0,lastSlot:-1};
}
function wheelAngle(w){const u=Math.min(1,w.t/w.T); return w.rot0+w.total*(1-Math.pow(1-u,w.ease));}
function grant(it,boy){
  if(it.kind==="player") owned[boy].push("boss"+it.i);
  else if(it.kind==="ball") extraBalls[boy].push(it.i);
  else if(it.kind==="shoes") shoesOwned[boy].push(it.i);
  else if(it.kind==="crowns") bonus[boy].c+=it.n;
  else bonus[boy].m+=it.n;
  saveGame();
}
function itemName(it){
  return it.kind==="player"?BOSSES[it.i].name:it.kind==="ball"?ballList()[it.i].name+" ball":it.kind==="shoes"?ARENAS[it.i].name+" shoes"
    :("+"+it.n+(it.kind==="crowns"?(it.n>1?" crowns":" crown"):" medals"));
}
function buyTrophy(t){
  if(!canBuy(human,t)){tro.msg={text:"Not enough medals or crowns yet: win more games!",t:2}; return;}
  spent[human].m+=t.price.m; spent[human].c+=t.price.c; saveGame();
  tro={stage:"box",type:t,taps:0,shake:0,t:0,last:performance.now(),wheel:null,msg:{text:"",t:0},parts:[]};
  play("cheer",0.75);
}
function tapTrophy(){
  if(tro.stage!=="box") return;
  tro.taps++; tro.shake=0.35; play("crack");
  if(tro.taps>=3){
    tro.stage="burst"; tro.t=0; play("glass",true); play("thunder");
    tro.parts=Array.from({length:46},()=>{const a=Math.random()*Math.PI*2, v=120+Math.random()*320; return {x:W/2,y:200,vx:Math.cos(a)*v,vy:Math.sin(a)*v-120,r:2+Math.random()*5,c:Math.random()<0.5?tro.type.col:"#FFFFFF"};});
    tro.wheel=buildWheel(tro.type,human);
    grant(tro.wheel.items[tro.wheel.win],human);   // saved straight away, so closing the app mid-spin loses nothing
  }
}
function drawTrophyIcon(x,y,s,t,cracks){   // a cup on a stand; diamonds get a gem
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s); ctx.lineJoin="round";
  ctx.fillStyle=t.dark; rr(-26,40,52,10,3); ctx.fill(); rr(-18,32,36,10,3); ctx.fill();
  ctx.fillStyle=t.col; ctx.fillRect(-5,12,10,22);
  ctx.strokeStyle=t.dark; ctx.lineWidth=6; ctx.beginPath(); ctx.arc(-30,-14,12,Math.PI*0.5,Math.PI*1.5); ctx.stroke(); ctx.beginPath(); ctx.arc(30,-14,12,-Math.PI*0.5,Math.PI*0.5); ctx.stroke();
  ctx.fillStyle=t.col; ctx.beginPath(); ctx.moveTo(-32,-34); ctx.lineTo(32,-34); ctx.quadraticCurveTo(30,14,0,16); ctx.quadraticCurveTo(-30,14,-32,-34); ctx.closePath(); ctx.fill();
  ctx.strokeStyle=t.dark; ctx.lineWidth=3; ctx.stroke();
  ctx.fillStyle="rgba(255,255,255,0.35)"; ctx.beginPath(); ctx.ellipse(-16,-16,5,14,0.2,0,Math.PI*2); ctx.fill();
  if(t.id==="diamond"){ctx.fillStyle="#FFFFFF"; ctx.strokeStyle=t.dark; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(0,-26); ctx.lineTo(11,-14); ctx.lineTo(0,2); ctx.lineTo(-11,-14); ctx.closePath(); ctx.fill(); ctx.stroke();}
  else {ctx.fillStyle="#FFFFFF"; ctx.beginPath(); for(let k=0;k<10;k++){const a=-Math.PI/2+k*Math.PI/5, r=k%2?4.5:10.5; ctx[k?"lineTo":"moveTo"](Math.cos(a)*r,-12+Math.sin(a)*r);} ctx.closePath(); ctx.fill();}
  if(cracks){ctx.strokeStyle="#1B2340"; ctx.lineWidth=2.2; ctx.lineCap="round";
    const C1=[[-4,-34,2,-20,-6,-8,4,6],[18,-34,12,-18,22,-6]], C2=[[-30,-20,-14,-12,-24,0],[8,-6,22,-2,14,12],[-6,2,-14,12]];
    for(const L of (cracks>=2?C1.concat(C2):C1)){ctx.beginPath(); ctx.moveTo(L[0],L[1]); for(let k=2;k<L.length;k+=2) ctx.lineTo(L[k],L[k+1]); ctx.stroke();}}
  ctx.restore();
}
function drawShoeIcon(x,y,s,a){
  ctx.save(); ctx.translate(x,y); ctx.scale(s,s);
  ctx.fillStyle=a.s; ctx.beginPath(); ctx.ellipse(1,6,14,4,0,0,Math.PI*2); ctx.fill();
  ctx.fillStyle=a.p; ctx.beginPath(); ctx.moveTo(-12,4); ctx.lineTo(-12,-6); ctx.quadraticCurveTo(-6,-10,-2,-6); ctx.lineTo(8,-1); ctx.quadraticCurveTo(15,1,14,4); ctx.closePath(); ctx.fill();
  ctx.strokeStyle=a.s; ctx.lineWidth=1.6; ctx.beginPath(); ctx.moveTo(-6,-5); ctx.lineTo(-2,-1); ctx.moveTo(-3,-6); ctx.lineTo(1,-2); ctx.stroke();
  ctx.restore();
}
function drawItemIcon(it,x,y,s){
  if(it.kind==="player") faceBadge(Object.assign(bossLook(it.i),{dir:1}),x,y,15*s,ARENAS[it.i].p);
  else if(it.kind==="ball") drawBallAt(x,y,11*s,ballList()[it.i],0.4);
  else if(it.kind==="shoes") drawShoeIcon(x,y,1.05*s,ARENAS[it.i]);
  else if(it.kind==="crowns") drawCrown(x,y+7*s,11*s);
  else drawMedal(x,y+5*s,9*s);
}
function drawWallet(cx,y){
  const w=wallet(human);
  ctx.fillStyle="rgba(46,56,102,0.95)"; rr(cx-170,y-17,340,34,17); ctx.fill();
  text(BOYS[human].name.toUpperCase(),cx-152,y,BODY(13,900),C.muted);
  drawMedal(cx-20,y+3,10); text(String(w.m),cx-4,y+1,DISP(18),C.ink);
  drawCrown(cx+80,y+8,12); text(String(w.c),cx+98,y+1,DISP(18),C.ink);
}
function drawTrophies(){
  ui=[]; drawCourt(); shade(0.86);
  const now=performance.now(), dt=Math.min(0.05,(now-(tro.last||now))/1000); tro.last=now;
  if(tro.shake>0) tro.shake-=dt;
  if(tro.msg.t>0) tro.msg.t-=dt;
  if(tro.stage==="shop"){
    bigTitle("TROPHIES",W/2,30,28);
    drawWallet(W/2,66);
    const cw=192, gap=10, x0=(W-4*cw-3*gap)/2;
    TROPHY_TYPES.forEach((t,k)=>{
      const x=x0+k*(cw+gap), y=92, h=242, ok=canBuy(human,t);
      ctx.fillStyle="rgba(27,35,64,0.96)"; rr(x,y,cw,h,16); ctx.fill();
      ctx.strokeStyle=t.col; ctx.lineWidth=3; ctx.stroke();
      ctx.fillStyle="#BFE9FF"; ctx.globalAlpha=0.16; rr(x+10,y+10,cw-20,96,12); ctx.fill(); ctx.globalAlpha=1;
      drawTrophyIcon(x+cw/2,y+58,0.82,t,0);
      text(t.name,x+cw/2,y+124,DISP(18),t.col,"center");
      // price
      const px=x+cw/2; let parts=[];
      if(t.price.m) parts.push(["m",t.price.m]); if(t.price.c) parts.push(["c",t.price.c]);
      const pw=parts.length*62, sx=px-pw/2+12;
      parts.forEach(([kind,n],j)=>{const ix=sx+j*62; if(kind==="m") drawMedal(ix,y+156,9); else drawCrown(ix,y+163,11); text(String(n),ix+16,y+154,DISP(17),C.ink);});
      text(String(+(t.player*100).toFixed(1))+"% chance of a player",x+cw/2,y+184,BODY(11,900),C.muted,"center");
      button(x+16,y+196,cw-32,36,"BUY",{fill:ok?t.col:"rgba(60,68,100,0.9)",ink:ok?C.navy:"rgba(255,255,255,0.45)"},()=>buyTrophy(t));
    });
    button(16,344,130,36,"BACK",{},()=>{screen="title";});
    text("Win games for medals and beat bosses for crowns",W/2,362,BODY(12,800),C.muted,"center");
  } else if(tro.stage==="box"){
    text(tro.type.name+" TROPHY",W/2,30,DISP(24),tro.type.col,"center");
    const sx=tro.shake>0?Math.sin(now/22)*8*tro.shake/0.35:0;
    ctx.fillStyle="#BFE9FF"; rr(W/2-130,58,260,252,30); ctx.fill();
    ctx.strokeStyle=tro.type.col; ctx.lineWidth=5; ctx.stroke();
    const pulse=1+0.04*Math.sin(now/180);
    drawTrophyIcon(W/2+sx,170,2.1*pulse,tro.type,tro.taps);
    text(tro.taps===0?"TAP IT 3 TIMES TO OPEN!":(tro.taps===1?"2 MORE TAPS!":"1 MORE TAP!"),W/2,340,DISP(18),C.warn,"center");
    ui.push({x:W/2-130,y:58,w:260,h:252,fn:tapTrophy});
  } else {
    const w=tro.wheel;
    if(tro.stage==="burst"){tro.t+=dt; if(tro.t>0.7){tro.stage="spin";}}
    else if(tro.stage==="spin"){
      w.t+=dt;
      const A=Math.PI*2/10, slot=Math.floor(((-wheelAngle(w))%(Math.PI*2)+Math.PI*2)%(Math.PI*2)/A);
      if(slot!==w.lastSlot){w.lastSlot=slot; SND.last.tick=0; play("tick");}
      if(w.t>=w.T){tro.stage="won"; tro.t=0; const it=w.items[w.win]; play("cheer",it.kind==="player"?1.8:1.1);}
    } else tro.t+=dt;
    // the wheel
    const cx=W/2, cy=206, R=150, A=Math.PI*2/10, ang=tro.stage==="burst"?w.rot0:wheelAngle(w);
    const pop=tro.stage==="burst"?Math.min(1,tro.t/0.7):1;
    ctx.save(); ctx.translate(cx,cy); ctx.scale(pop,pop);
    ctx.fillStyle="#1B2340"; ctx.beginPath(); ctx.arc(0,0,R+8,0,Math.PI*2); ctx.fill();
    w.items.forEach((it,k)=>{
      const a0=ang+k*A-Math.PI/2, a1=a0+A, mid=a0+A/2;
      ctx.fillStyle=it.kind==="player"?"#FFC93C":(k%2?tro.type.col:mix(tro.type.col,"#FFFFFF",0.55));
      ctx.beginPath(); ctx.moveTo(0,0); ctx.arc(0,0,R,a0,a1); ctx.closePath(); ctx.fill();
      ctx.strokeStyle="#1B2340"; ctx.lineWidth=2; ctx.stroke();
      const ix=Math.cos(mid)*R*0.66, iy=Math.sin(mid)*R*0.66;
      ctx.save(); ctx.translate(ix,iy); ctx.rotate(mid+Math.PI/2);
      drawItemIcon(it,0,-8,1);
      let lab=it.kind==="player"?"PLAYER":it.kind==="ball"?"BALL":it.kind==="shoes"?"SHOES":"+"+it.n;
      text(lab,0,16,BODY(10,900),"#1B2340","center");
      ctx.restore();
    });
    ctx.fillStyle="#FFFFFF"; ctx.beginPath(); ctx.arc(0,0,16,0,Math.PI*2); ctx.fill(); ctx.strokeStyle="#1B2340"; ctx.lineWidth=3; ctx.stroke();
    ctx.restore();
    // the pointer at the top
    ctx.fillStyle=C.warn; ctx.strokeStyle="#1B2340"; ctx.lineWidth=3; ctx.beginPath(); ctx.moveTo(cx-14,cy-R-22); ctx.lineTo(cx+14,cy-R-22); ctx.lineTo(cx,cy-R+4); ctx.closePath(); ctx.fill(); ctx.stroke();
    // bits of trophy flying out when it bursts
    if(tro.stage==="burst") for(const p2 of tro.parts){p2.vy+=500*dt; p2.x+=p2.vx*dt; p2.y+=p2.vy*dt; ctx.fillStyle=p2.c; ctx.beginPath(); ctx.arc(p2.x,p2.y,p2.r,0,Math.PI*2); ctx.fill();}
    if(tro.stage==="won"){
      const it=w.items[w.win], k=Math.min(1,tro.t*4);
      ctx.save(); ctx.globalAlpha=k; ctx.fillStyle="rgba(10,14,30,0.7)"; ctx.fillRect(0,0,W,H);
      ctx.fillStyle="rgba(16,21,43,0.97)"; rr(W/2-200,96,400,200,22); ctx.fill(); ctx.strokeStyle=it.kind==="player"?"#FFC93C":tro.type.col; ctx.lineWidth=5; ctx.stroke();
      text(it.kind==="player"?"NEW PLAYER!":"YOU WON",W/2,124,DISP(22),C.warn,"center");
      drawItemIcon(it,W/2,178,2.2);
      text(itemName(it),W/2,232,DISP(18),C.ink,"center");
      text(it.kind==="player"?"Pick him on the Players screen":it.kind==="ball"?"Pick it as your ball before a game":it.kind==="shoes"?"Pick them as your shoes before a game":"Added to "+BOYS[human].name+"'s prizes",W/2,256,BODY(12,800),C.muted,"center");
      ctx.restore();
      if(tro.t>0.5) button(W/2-90,306,180,44,"COLLECT",{fill:"#F26B1D",ink:C.navy},()=>{tro.stage="shop";});
    } else text(tro.stage==="spin"?"SPINNING...":"",W/2,374,DISP(16),C.warn,"center");
  }
  if(tro.msg.t>0){ctx.globalAlpha=Math.min(1,tro.msg.t*3); ctx.font=BODY(13,900); const w2=ctx.measureText(tro.msg.text).width+28;
    ctx.fillStyle="rgba(10,14,30,0.95)"; rr(W/2-w2/2,300,w2,30,12); ctx.fill(); text(tro.msg.text,W/2,315,BODY(13,900),C.warn,"center"); ctx.globalAlpha=1;}
}
