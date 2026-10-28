// ---------- arenas: one original arena per level, each with its own colours and centre-court emblem ----------
// p = main colour, s = second colour, wood = floor, e = emblem shape
const ARENAS=[
  {name:"Northside Gym",     p:"#E8772E",s:"#1B2A4A",wood:"#E2B57A",e:"ball"},
  {name:"Harbor Hall",       p:"#0E7C86",s:"#F2E9D8",wood:"#D99A5B",e:"wave"},
  {name:"Ember Arena",       p:"#D9381E",s:"#FFB627",wood:"#C98A50",e:"flame"},
  {name:"Summit Center",     p:"#2D5DA8",s:"#FFFFFF",wood:"#DDB07A",e:"peak"},
  {name:"Volt Garden",       p:"#F2C200",s:"#1A1A1A",wood:"#D7A466",e:"bolt"},
  {name:"Royal Court",       p:"#5B3A8C",s:"#C9CED6",wood:"#C8915A",e:"crown"},
  {name:"Aurora Dome",       p:"#1FA37A",s:"#8E6CE0",wood:"#D9A86F",e:"star"},
  {name:"Comet Coliseum",    p:"#3A2E8C",s:"#FF6FA8",wood:"#CF9860",e:"comet"},
  {name:"Sunrise Fieldhouse",p:"#F08A24",s:"#FFE066",wood:"#E4B87F",e:"sun"},
  {name:"Glacier Bowl",      p:"#7FC8E8",s:"#1D3557",wood:"#E8C79A",e:"diamond"},
  {name:"Redwood Arena",     p:"#2F5D3A",s:"#A0522D",wood:"#B9774A",e:"leaf"},
  {name:"Iron Works",        p:"#5A6270",s:"#FF7A1A",wood:"#C68C55",e:"shield"},
  {name:"Galaxy Garden",     p:"#14161F",s:"#2EC4B6",wood:"#B98250",e:"planet"},
  {name:"Falcon Center",     p:"#7A4E2D",s:"#F4E3C1",wood:"#D7A064",e:"wings"},
  {name:"Lagoon Arena",      p:"#19B5B0",s:"#FF7F6B",wood:"#E0B582",e:"wave"},
  {name:"Canyon Center",     p:"#C0582F",s:"#F1D3A2",wood:"#CC925A",e:"peak"},
  {name:"Lantern Hall",      p:"#B3202A",s:"#F5C542",wood:"#C7894F",e:"ball"},
  {name:"Midnight Arena",    p:"#16224A",s:"#C4CCD8",wood:"#B67E4D",e:"star"},
  {name:"Storm Center",      p:"#3E4C59",s:"#FFD23F",wood:"#C99358",e:"bolt"},
  {name:"Prism Arena",       p:"#6C3FD1",s:"#3DDC97",wood:"#D8A872",e:"diamond"},
  {name:"Volcano Pit",       p:"#1E1A1A",s:"#FF3D2E",wood:"#A8693F",e:"flame"},
  {name:"Orbit Arena",       p:"#4A2A7A",s:"#2EC4B6",wood:"#C68D59",e:"planet"},
  {name:"Kingdom Center",    p:"#1F4FBF",s:"#F2C14E",wood:"#D29C61",e:"crown"},
  {name:"Tidal Dome",        p:"#0F5E9C",s:"#57CC99",wood:"#DCAE78",e:"wave"},
  {name:"Arrow Arena",       p:"#1B7F3B",s:"#FFFFFF",wood:"#D4A06A",e:"arrow"},
  {name:"Solar Arena",       p:"#FF8C1A",s:"#7A1F1F",wood:"#CB9257",e:"sun"},
  {name:"Fortress Arena",    p:"#2B2D33",s:"#D72638",wood:"#B27849",e:"shield"},
  {name:"Starlight Coliseum",p:"#1C1C1C",s:"#E8C547",wood:"#BF8650",e:"comet"},
  {name:"Titan Dome",        p:"#8C5A2B",s:"#1A1A1A",wood:"#C48B55",e:"wings"},
  {name:"Hoops 4 Life Arena",p:"#10152B",s:"#FFC93C",wood:"#D99A5B",e:"crest"}
];
function currentArena(){return mode==="level" && (screen==="play"||screen==="pause"||screen==="over") ? ARENAS[Math.floor(level/STOPS)%ARENAS.length] : null;}
// emblem shapes, drawn in a unit circle (radius 1) centred on 0,0
function emblemShape(kind){
  const P=pts=>{ctx.beginPath(); pts.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y)); ctx.closePath();};
  switch(kind){
    case "star": {const pts=[]; for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5, r=i%2?0.28:0.66; pts.push([Math.cos(a)*r,Math.sin(a)*r]);} P(pts); ctx.fill(); break;}
    case "bolt": P([[0.12,-0.7],[-0.38,0.08],[-0.04,0.08],[-0.14,0.7],[0.38,-0.12],[0.04,-0.12]]); ctx.fill(); break;
    case "flame": ctx.beginPath(); ctx.moveTo(0,0.66); ctx.bezierCurveTo(-0.55,0.6,-0.5,0,-0.12,-0.3); ctx.bezierCurveTo(-0.1,0,0.02,0.05,0.05,-0.12);
      ctx.bezierCurveTo(0.08,-0.4,0.02,-0.55,0.1,-0.7); ctx.bezierCurveTo(0.5,-0.35,0.62,0.55,0,0.66); ctx.fill(); break;
    case "peak": P([[-0.68,0.42],[-0.2,-0.3],[0.02,0.02],[0.22,-0.52],[0.68,0.42]]); ctx.fill(); break;
    case "crown": P([[-0.6,0.36],[-0.66,-0.36],[-0.3,-0.02],[0,-0.48],[0.3,-0.02],[0.66,-0.36],[0.6,0.36]]); ctx.fill(); break;
    case "wave": ctx.lineWidth=0.16; ctx.lineCap="round"; for(const dy of [-0.2,0.18]){ctx.beginPath(); ctx.moveTo(-0.62,dy);
      ctx.bezierCurveTo(-0.32,dy-0.32,-0.12,dy+0.3,0.1,dy); ctx.bezierCurveTo(0.3,dy-0.3,0.48,dy+0.26,0.62,dy); ctx.stroke();} break;
    case "ball": ctx.lineWidth=0.09; ctx.beginPath(); ctx.arc(0,0,0.58,0,Math.PI*2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-0.58,0); ctx.lineTo(0.58,0); ctx.moveTo(0,-0.58); ctx.lineTo(0,0.58);
      ctx.moveTo(-0.36,-0.46); ctx.quadraticCurveTo(-0.1,0,-0.36,0.46); ctx.moveTo(0.36,-0.46); ctx.quadraticCurveTo(0.1,0,0.36,0.46); ctx.stroke(); break;
    case "diamond": P([[0,-0.66],[0.5,-0.1],[0,0.66],[-0.5,-0.1]]); ctx.fill(); break;
    case "comet": ctx.beginPath(); ctx.arc(0.26,-0.2,0.26,0,Math.PI*2); ctx.fill();
      P([[0.08,-0.38],[-0.66,0.5],[0.44,-0.02]]); ctx.fill(); break;
    case "sun": ctx.beginPath(); ctx.arc(0,0,0.3,0,Math.PI*2); ctx.fill();
      for(let i=0;i<10;i++){const a=i*Math.PI/5; P([[Math.cos(a-0.12)*0.38,Math.sin(a-0.12)*0.38],[Math.cos(a)*0.66,Math.sin(a)*0.66],[Math.cos(a+0.12)*0.38,Math.sin(a+0.12)*0.38]]); ctx.fill();} break;
    case "leaf": ctx.beginPath(); ctx.moveTo(0,-0.66); ctx.quadraticCurveTo(0.6,-0.1,0,0.6); ctx.quadraticCurveTo(-0.6,-0.1,0,-0.66); ctx.fill(); break;
    case "shield": P([[-0.48,-0.56],[0.48,-0.56],[0.48,0.05],[0,0.64],[-0.48,0.05]]); ctx.fill(); break;
    case "planet": ctx.beginPath(); ctx.arc(0,0,0.34,0,Math.PI*2); ctx.fill(); ctx.lineWidth=0.09;
      ctx.beginPath(); ctx.ellipse(0,0,0.66,0.2,-0.4,0,Math.PI*2); ctx.stroke(); break;
    case "wings": for(const sx of [-1,1]){ctx.beginPath(); ctx.moveTo(0.06*sx,0.1);
      ctx.quadraticCurveTo(0.4*sx,-0.6,0.7*sx,-0.4); ctx.quadraticCurveTo(0.5*sx,-0.15,0.6*sx,-0.05); ctx.quadraticCurveTo(0.4*sx,0.05,0.48*sx,0.2);
      ctx.quadraticCurveTo(0.25*sx,0.25,0.06*sx,0.1); ctx.fill();} ctx.beginPath(); ctx.arc(0,0.12,0.12,0,Math.PI*2); ctx.fill(); break;
    case "arrow": P([[-0.62,0.12],[0.12,0.12],[0.12,0.36],[0.64,0],[0.12,-0.36],[0.12,-0.12],[-0.62,-0.12]]); ctx.fill(); break;
    case "crest": {const pts=[]; for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5, r=i%2?0.24:0.5; pts.push([Math.cos(a)*r,Math.sin(a)*r-0.08]);} P(pts); ctx.fill();
      ctx.font="900 0.36px Bungee, Arial Black, sans-serif"; ctx.textAlign="center"; ctx.textBaseline="middle"; ctx.fillText("H4L",0,0.48); break;}
  }
}
// a round emblem: filled disc, a ring, and the shape. sy squashes it flat, the way a floor logo looks from the side
function drawEmblem(a,cx,cy,r,sy){
  ctx.save(); ctx.translate(cx,cy); ctx.scale(r,r*(sy||1));
  ctx.fillStyle=a.p; ctx.beginPath(); ctx.arc(0,0,1,0,Math.PI*2); ctx.fill();
  ctx.strokeStyle=a.s; ctx.lineWidth=0.1; ctx.beginPath(); ctx.arc(0,0,0.88,0,Math.PI*2); ctx.stroke();
  ctx.strokeStyle="rgba(255,255,255,0.55)"; ctx.lineWidth=0.05; ctx.beginPath(); ctx.arc(0,0,1,0,Math.PI*2); ctx.stroke();
  ctx.fillStyle=a.s; ctx.strokeStyle=a.s; emblemShape(a.e);
  ctx.restore();
}
// a seeded crowd so every arena has the same fans every time
const crowdCache={};
function crowdFor(i){
  if(crowdCache[i]) return crowdCache[i];
  let seed=1234+i*977; const rnd=()=>{seed=(seed*16807)%2147483647; return seed/2147483647;};
  const a=ARENAS[i], cols=[a.p,a.s,"#FFFFFF",mix(a.p,"#000000",0.3),"#9AA3BF"], skins=["#F2C6A8","#D9A285","#8A5A3C","#E9B48A","#5A3825"];
  const fans=[];
  for(const [row,y] of [[0,196],[1,232],[2,268]]) for(let x=8+row*9;x<W;x+=17+rnd()*5)
    fans.push({x,y:y+rnd()*4,shirt:cols[Math.floor(rnd()*cols.length)],skin:skins[Math.floor(rnd()*skins.length)],ph:rnd()*6.28});
  return crowdCache[i]=fans;
}
function drawArenaCourt(a,ai){
  const roof=mix(a.p,"#05070F",0.78), stands=mix(a.p,"#0B1020",0.6);
  ctx.fillStyle=roof; ctx.fillRect(0,0,W,H);
  // spotlights from the roof
  ctx.fillStyle="rgba(255,255,255,0.05)";
  for(const x of [150,422,694]){ctx.beginPath(); ctx.moveTo(x-12,0); ctx.lineTo(x+12,0); ctx.lineTo(x+120,FLOOR); ctx.lineTo(x-120,FLOOR); ctx.closePath(); ctx.fill();}
  // arena banner
  const bw=300; ctx.fillStyle=mix(a.p,"#000000",0.15); rr(W/2-bw/2,62,bw,32,10); ctx.fill();
  ctx.strokeStyle=a.s; ctx.lineWidth=2; ctx.stroke();
  drawEmblem(a,W/2-bw/2+16,78,12); drawEmblem(a,W/2+bw/2-16,78,12);
  let fs=15; ctx.font=DISP(fs); while(fs>10 && ctx.measureText(a.name.toUpperCase()).width>bw-70){fs--; ctx.font=DISP(fs);}
  text(a.name.toUpperCase(),W/2,79,DISP(fs),isLight(mix(a.p,"#000000",0.15))?"#10152B":"#FFFFFF","center");
  // stands and the crowd
  ctx.fillStyle=stands; ctx.fillRect(0,170,W,140);
  ctx.fillStyle=mix(a.s,stands,0.75); for(const y of [206,242,278]) ctx.fillRect(0,y,W,2);
  const t=performance.now()/1000, cheer=celebrate.t>0?1:0.25;
  for(const f of crowdFor(ai)){
    const bob=Math.max(0,Math.sin(t*6+f.ph))*3*cheer;
    ctx.fillStyle=f.shirt; ctx.fillRect(f.x-6,f.y+2-bob,12,9);
    ctx.fillStyle=f.skin; ctx.beginPath(); ctx.arc(f.x,f.y-3-bob,4.5,0,Math.PI*2); ctx.fill();
  }
  ctx.fillStyle=a.p; ctx.fillRect(0,300,W,10);   // courtside board in arena colours
  ctx.fillStyle=a.s; ctx.fillRect(0,300,W,2);
  // floor
  ctx.fillStyle=a.wood; ctx.fillRect(0,FLOOR,W,H-FLOOR);
  ctx.fillStyle="rgba(0,0,0,0.08)"; for(let x=0;x<W;x+=34) ctx.fillRect(x,FLOOR,1,H-FLOOR);   // boards
  ctx.fillStyle=C.chalk; ctx.fillRect(0,FLOOR,W,4);
  ctx.fillStyle=mix(a.wood,"#000000",0.22); ctx.fillRect(0,342,W,2); ctx.fillRect(0,370,W,2);
  // centre-court emblem, flattened to lie on the floor
  ctx.fillStyle="rgba(255,255,255,0.35)"; ctx.beginPath(); ctx.ellipse(422,340,92,25,0,0,Math.PI*2); ctx.fill();
  drawEmblem(a,422,340,84,0.27);
}
