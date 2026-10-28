import sys
f = sys.argv[1]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)

# --- the physics helpers go just before the update loop ---
once("// ---------- update ----------", r'''// ---------- ball physics: rims, backboards and floor ----------
// How much speed the ball keeps when it bounces (coefficient of restitution), based on real basketball
// measurements: a steel rim gives back about 55%, the glass backboard about 75%, a hardwood floor about 78%.
const BOUNCE={rim:0.55, board:0.75, floor:0.78}, RIM_GRIP=0.88, BALL_R=8, RIM_Y=186;
const HOOPS=[   // each hoop: the front and back edge of the rim, and the face of the backboard
  {rim:RR, net:1, edges:[[737,RIM_Y],[775,RIM_Y]], face:777, faceDir:-1, top:140, bot:202},
  {rim:RL, net:0, edges:[[107,RIM_Y],[69,RIM_Y]],  face:67,  faceDir:1,  top:140, bot:202}
];
// bounce the ball off a small round point (a rim edge or a backboard corner)
function hitPoint(px,py,r,e){
  const dx=ball.x-px, dy=ball.y-py, dd=Math.hypot(dx,dy), min=BALL_R+r;
  if(dd>=min||dd<0.001) return false;
  const nx=dx/dd, ny=dy/dd; ball.x=px+nx*min; ball.y=py+ny*min;
  const vn=ball.vx*nx+ball.vy*ny; if(vn>=0) return false;
  // reverse the part of the speed going into the rim (losing some), keep most of the part along it
  const tx=ball.vx-vn*nx, ty=ball.vy-vn*ny;
  ball.vx=-e*vn*nx+tx*RIM_GRIP; ball.vy=-e*vn*ny+ty*RIM_GRIP;
  if(Math.hypot(ball.vx,ball.vy)<70) ball.vx+=(ball.x<px?-1:1)*45;   // a ball never balances on the rim
  return true;
}
function collideHoops(){
  let hit=null;
  for(const h of HOOPS){
    for(const [px,py] of h.edges) if(hitPoint(px,py,2.5,BOUNCE.rim)){hit="rim"; netKick(h.net,1.5,0);}
    if(ball.y>h.top && ball.y<h.bot){   // the glass
      if(h.faceDir<0 && ball.x+BALL_R>h.face && ball.x<h.face+7 && ball.vx>0){ball.x=h.face-BALL_R; ball.vx=-ball.vx*BOUNCE.board; ball.vy*=0.92; hit=hit||"board";}
      if(h.faceDir>0 && ball.x-BALL_R<h.face && ball.x>h.face-7 && ball.vx<0){ball.x=h.face+BALL_R; ball.vx=-ball.vx*BOUNCE.board; ball.vy*=0.92; hit=hit||"board";}
    }
    for(const cy of [h.top,h.bot]) if(hitPoint(h.face-h.faceDir*3.5,cy,3.5,BOUNCE.board)) hit=hit||"board";
  }
  return hit;
}
function floorAndWalls(){
  if(ball.y>FLOOR-BALL_R){
    ball.y=FLOOR-BALL_R;
    if(ball.vy>0){ball.vy=-ball.vy*BOUNCE.floor; ball.vx*=0.9;}
    if(Math.abs(ball.vy)<35) ball.vy=0;
  }
  if(ball.x<8){ball.x=8; ball.vx=Math.abs(ball.vx)*0.6;}
  if(ball.x>836){ball.x=836; ball.vx=-Math.abs(ball.vx)*0.6;}
}
// after a miss, a ball that bounces around and drops through its own hoop still counts
function checkRollIn(prevY){
  const h=ball.shooter===p?HOOPS[0]:HOOPS[1], a=Math.min(h.edges[0][0],h.edges[1][0]), b=Math.max(h.edges[0][0],h.edges[1][0]);
  if(ball.vy>0 && prevY<RIM_Y && ball.y>=RIM_Y && ball.x>a+5 && ball.x<b-5){
    ball.make=true; ball.lucky=true; ball.live=false; arrive(0);
  }
}

// ---------- update ----------''')

# --- flight: made shots follow their arc into the hoop; missed shots are simulated and bounce off what they hit ---
once('''  } else if(ball.state==="flight"){
    ball.t+=dt; const t=ball.t;
    ball.x=ball.x0+ball.vx*t; ball.y=ball.y0+ball.vy*t+0.5*GB*t*t;
    const early=t<ball.T*0.55;''',
'''  } else if(ball.state==="flight"){
    ball.t+=dt; const t=ball.t;
    let hit=null;
    if(ball.make){ ball.x=ball.x0+ball.vx*t; ball.y=ball.y0+ball.vy*t+0.5*GB*t*t; }
    else {   // small steps so the ball can't skip through the rim
      const n=4, h=dt/n;
      for(let k=0;k<n && !hit;k++){ ball.vy+=GB*h; ball.x+=ball.vx*h; ball.y+=ball.vy*h; hit=collideHoops(); }
    }
    const early=t<ball.T*0.55;''')
once('''    if(t>=ball.T) arrive(t);
  } else if(ball.state==="free"){
    ball.timer+=dt;
    ball.vy+=GB*dt; ball.x+=ball.vx*dt; ball.y+=ball.vy*dt;
    if(ball.vx>0 && ball.x>RR.board-8 && ball.y>140 && ball.y<202){ball.x=RR.board-8;ball.vx*=-0.5;}
    if(ball.vx<0 && ball.x<RL.board+15 && ball.y>140 && ball.y<202){ball.x=RL.board+15;ball.vx*=-0.5;}
    for(const fx of [RR.front,RL.front]){
      if(Math.hypot(ball.x-fx,ball.y-RR.y)<10){const away=fx===RR.front?-1:1;ball.vx=away*(Math.abs(ball.vx)*0.5+30);ball.vy=-Math.abs(ball.vy)*0.4;netKick(fx===RR.front?1:0,2.5,away*1.5);}
    }
    if(ball.x<8){ball.x=8;ball.vx=Math.abs(ball.vx)*0.6;}
    if(ball.x>836){ball.x=836;ball.vx=-Math.abs(ball.vx)*0.6;}
    if(ball.y>FLOOR-8){ball.y=FLOOR-8;ball.vy*=-0.6;ball.vx*=0.85;if(Math.abs(ball.vy)<40)ball.vy=0;}''',
'''    if(ball.make){ if(t>=ball.T) arrive(t); }
    else if(hit || t>=ball.T+0.25 || ball.y>FLOOR-BALL_R) missNow();
  } else if(ball.state==="free"){
    ball.timer+=dt;
    const n=4, h=dt/n;
    for(let k=0;k<n;k++){
      const prevY=ball.y;
      ball.vy+=GB*h; ball.x+=ball.vx*h; ball.y+=ball.vy*h;
      collideHoops(); floorAndWalls();
      if(ball.live && ball.timer<4) checkRollIn(prevY);
      if(ball.state!=="free") break;
    }
    if(ball.state!=="free") return;
    if(ball.y>=FLOOR-BALL_R-0.5 && ball.vy===0) ball.vx*=Math.max(0,1-1.3*dt);   // rolling slows down on the floor''')

# --- misses: commentary when the ball first hits something (or falls short), then it's a live rebound ---
once('''  } else {
    ball.state="free"; ball.vy=ball.vy+GB*t; ball.timer=0;
    if(byP){''', '''  } else {
    ball.vy=ball.vy+GB*t; missNow();
  }
}
function missNow(){
  const byP=ball.shooter===p;
  ball.state="free"; ball.timer=0; ball.live=true;
  {
    if(byP){''')
once('''    say(pick(ball.missType), tip+(cpuOn?" · grab the rebound!":""), C.warn);''',
     '''    say(pick(ball.missType), tip+(cpuOn?" · grab the rebound!":""), C.warn);''')

# --- rolled-in shots get their own commentary ---
once('''      const cat=ball.dunk?"dunk":(ball.far?"half":(ball.fade?"fade":(stats.streak>=3?"fire":(ball.pts===3?"three":"two"))));
      say(pick(cat), "+"+ball.pts''',
     '''      const cat=ball.lucky?"lucky":(ball.dunk?"dunk":(ball.far?"half":(ball.fade?"fade":(stats.streak>=3?"fire":(ball.pts===3?"three":"two")))));
      say(pick(cat), "+"+ball.pts''')
once('''      const cat=ball.dunk?"dunk":(ball.far?"half":(ball.fade?"fade":(ball.pts===3?"three":"two")));
      say(pick(cat),NAME.d+" +"+ball.pts,C.warn);''',
     '''      const cat=ball.lucky?"lucky":(ball.dunk?"dunk":(ball.far?"half":(ball.fade?"fade":(ball.pts===3?"three":"two"))));
      say(pick(cat),NAME.d+" +"+ball.pts,C.warn);''')
once('''  dunkMiss:["Rim says NO!",''', '''  lucky:["Shooter's roll!","It rolls in!","Lucky bounce!","Friendly rim!","Kissed it in!"],
  dunkMiss:["Rim says NO!",''')

# --- a rebound is only "live" until someone touches it ---
once('''    shooter:p,missType,dunk:false,fade:charge.fade,''', '''    shooter:p,missType,dunk:false,lucky:false,live:false,fade:charge.fade,''')
once('''    shooter:d,missType:over?"long":"short",dunk:false,''', '''    shooter:d,missType:over?"long":"short",dunk:false,lucky:false,live:false,''')
once('''function takeBall(e){
  owner=e; ball.state="held";''', '''function takeBall(e){
  owner=e; ball.state="held"; ball.live=false;''')
once('''  ball.state="held"; charge.on=false; cpu.charging=false; d.jumped=false; d.react=null;''',
     '''  ball.state="held"; ball.live=false; charge.on=false; cpu.charging=false; d.jumped=false; d.react=null;''')
once('''  ball.state="free"; ball.vx=shooterDir*60; ball.vy=60; ball.timer=0;''',
     '''  ball.state="free"; ball.vx=shooterDir*60; ball.vy=60; ball.timer=0; ball.live=false;''')
once('''vx:-dir*(120+Math.random()*60),vy:-120,timer:0,dunk:true});''', '''vx:-dir*(120+Math.random()*60),vy:-120,timer:0,dunk:true,live:false});''')
once('''vx:-dir*(150+Math.random()*90),vy:-280,timer:0});''', '''vx:-dir*(150+Math.random()*90),vy:-280,timer:0,live:false});''')

open(f, "w").write(s)
print("patched")
