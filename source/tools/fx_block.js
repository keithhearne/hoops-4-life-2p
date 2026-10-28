// ---------- dunk effects: thunder, breaking glass, and a cracked screen for a windmill ----------
const WIND_MAKE=0.4;   // a windmill is harder to finish than a normal dunk (0.5)
let boardFx={t:0,T:1,side:"R",shatter:false,shards:[],bolts:[],flash:0,boltT:0};
let crackFx={t:0,T:2.8,lines:[],rings:[],cx:0,cy:0};
function jagged(x0,y0,x1,y1,n,amp){
  const pts=[[x0,y0]];
  for(let i=1;i<n;i++){const u=i/n; pts.push([x0+(x1-x0)*u+(Math.random()-0.5)*amp, y0+(y1-y0)*u+(Math.random()-0.5)*amp*0.4]);}
  pts.push([x1,y1]); return pts;
}
function makeBolts(side){const bx=side==="R"?780:63; return [0,1].map(k=>jagged(bx+(Math.random()-0.5)*170,0,bx,148+k*34,9,46));}
// a made dunk: lightning hits the backboard and glass flies; a windmill shatters the whole board
function startBoardFx(side,wind){
  const bx=side==="R"?780:63, inward=side==="R"?-1:1, n=wind?48:16, shards=[];
  for(let i=0;i<n;i++) shards.push({x:bx+(Math.random()-0.5)*6, y:142+Math.random()*58,
    vx:inward*(40+Math.random()*(wind?280:150))+(Math.random()-0.5)*60, vy:-60-Math.random()*(wind?230:120),
    rot:Math.random()*6.28, vr:(Math.random()-0.5)*14, s:2+Math.random()*(wind?6:3.5)});
  const T=wind?2.6:1.6;
  boardFx={t:T,T,side,shatter:wind,shards,bolts:makeBolts(side),flash:0.32,boltT:wind?0.7:0.5};
  shakeT=Math.max(shakeT,wind?0.6:0.4);
}
// the phone screen "cracks" from a point near the middle, spreading out in jagged lines with rings between them
function startCrackFx(){
  const cx=W/2+(Math.random()-0.5)*80, cy=150+(Math.random()-0.5)*30, n=14, lines=[], rings=[];
  for(let i=0;i<n;i++){const a=i/n*Math.PI*2+(Math.random()-0.5)*0.35, len=360+Math.random()*320;
    lines.push(jagged(cx,cy,cx+Math.cos(a)*len,cy+Math.sin(a)*len,10,22));}
  for(const r of [28,70,130]){const ring=[];
    for(let i=0;i<n;i++){const a=i/n*Math.PI*2+(Math.random()-0.5)*0.2, rr2=r*(0.8+Math.random()*0.4); ring.push([cx+Math.cos(a)*rr2,cy+Math.sin(a)*rr2]);}
    rings.push(ring);}
  crackFx={t:2.8,T:2.8,lines,rings,cx,cy};
}
function updateFx(dt){
  if(boardFx.t>0){
    boardFx.t-=dt; if(boardFx.flash>0) boardFx.flash-=dt;
    if(boardFx.boltT>0){boardFx.boltT-=dt; if(Math.random()<0.35) boardFx.bolts=makeBolts(boardFx.side);}   // the bolt flickers
    for(const s of boardFx.shards){
      s.vy+=GB*dt; s.x+=s.vx*dt; s.y+=s.vy*dt; s.rot+=s.vr*dt;
      if(s.y>FLOOR-2){s.y=FLOOR-2; s.vy*=-0.25; s.vx*=0.6; s.vr*=0.5;}
    }
  }
  if(crackFx.t>0) crackFx.t-=dt;
}
function boardGone(side){return boardFx.t>0.5 && boardFx.shatter && boardFx.side===side;}
function drawBoardFx(){
  if(boardFx.t<=0) return;
  if(boardFx.boltT>0){
    for(const b of boardFx.bolts) for(const [w,col] of [[10,"rgba(140,180,255,0.35)"],[3.5,"rgba(220,235,255,0.95)"],[1.5,"#FFFFFF"]]){
      ctx.strokeStyle=col; ctx.lineWidth=w; ctx.lineJoin="round"; ctx.lineCap="round";
      ctx.beginPath(); b.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y)); ctx.stroke();
    }
    const bx=boardFx.side==="R"?780:63, g=ctx.createRadialGradient(bx,170,2,bx,170,80);
    g.addColorStop(0,"rgba(255,255,255,0.85)"); g.addColorStop(1,"rgba(160,200,255,0)");
    ctx.fillStyle=g; ctx.fillRect(bx-80,90,160,160);
  }
  ctx.globalAlpha=Math.min(1,boardFx.t/0.5);
  for(const s of boardFx.shards){
    ctx.save(); ctx.translate(s.x,s.y); ctx.rotate(s.rot);
    ctx.fillStyle="rgba(205,235,255,0.85)"; ctx.beginPath(); ctx.moveTo(-s.s,-s.s*0.6); ctx.lineTo(s.s,-s.s*0.2); ctx.lineTo(-s.s*0.2,s.s); ctx.closePath(); ctx.fill();
    ctx.strokeStyle="rgba(255,255,255,0.9)"; ctx.lineWidth=0.8; ctx.stroke(); ctx.restore();
  }
  ctx.globalAlpha=1;
}
function drawScreenFx(){
  if(boardFx.t>0 && boardFx.flash>0){ctx.fillStyle="rgba(255,255,255,"+(Math.min(1,boardFx.flash/0.32)*0.7).toFixed(3)+")"; ctx.fillRect(0,0,W,H);}
  if(crackFx.t<=0) return;
  const grow=Math.min(1,(crackFx.T-crackFx.t)/0.12);
  ctx.save(); ctx.globalAlpha=Math.min(1,crackFx.t/0.6); ctx.lineJoin="round"; ctx.lineCap="round";
  for(const [w,col] of [[3,"rgba(0,0,0,0.35)"],[1.4,"rgba(255,255,255,0.92)"]]){
    ctx.strokeStyle=col; ctx.lineWidth=w;
    for(const l of crackFx.lines){const n=Math.max(2,Math.ceil(l.length*grow)); ctx.beginPath(); for(let i=0;i<n;i++){const [x,y]=l[i]; i?ctx.lineTo(x,y):ctx.moveTo(x,y);} ctx.stroke();}
    if(grow>=1) for(const r of crackFx.rings){ctx.beginPath(); r.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y)); ctx.closePath(); ctx.stroke();}
  }
  const g=ctx.createRadialGradient(crackFx.cx,crackFx.cy,0,crackFx.cx,crackFx.cy,40);
  g.addColorStop(0,"rgba(255,255,255,0.7)"); g.addColorStop(1,"rgba(255,255,255,0)");
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(crackFx.cx,crackFx.cy,40,0,Math.PI*2); ctx.fill();
  ctx.restore();
}
// where the hand (and ball) is during a windmill: from overhead, 180 degrees round behind the back to down low,
// then forward and up over the top into the rim
function windmillHand(dk,e,dir,rim){
  const sx=e.x+dir*6, sy=e.y-47, L=34;
  if(dk.t<RISE){
    const u=Math.min(1,Math.max(0,(dk.t-dk.w0)/Math.max(0.08,RISE-dk.w0))), th=-Math.PI/2-Math.PI*u;
    return {x:sx+dir*Math.cos(th)*L, y:sy+Math.sin(th)*L};
  }
  const u=Math.min(1,(dk.t-RISE)/SLAM), th=Math.PI/2-Math.PI*0.9*u, k=u*u;
  const arm={x:sx+dir*Math.cos(th)*L, y:sy+Math.sin(th)*L};
  return {x:arm.x+(rim.x-arm.x)*k, y:arm.y+(rim.y-6-arm.y)*k};
}
