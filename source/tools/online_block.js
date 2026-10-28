// ---------- TWO PHONES: host a game or join one, through the room server ----------
// One phone hosts and gets a 5-character code; the other types the code in. The room server only passes
// messages between the two phones. Everything that arrives is checked before it's used.
const NET_URL="https://hoops-4-life-2p.keith-hearne-ai.workers.dev";
const CODE_CHARS="ABCDEFGHJKMNPQRSTUVWXYZ23456789";
const LINK={ws:null,role:null,code:"",key:"",peer:false,other:null,stage:"menu",note:"",typed:"",busy:false,gen:0};
function netReset(stage){
  LINK.gen++;   // any messages still on their way from an old connection are ignored
  if(LINK.ws){try{LINK.ws.onclose=null; LINK.ws.close(1000,"bye");}catch(_){}}
  Object.assign(LINK,{ws:null,role:null,code:"",key:"",peer:false,other:null,stage:stage||"menu",busy:false});
}
function openOnline(){ netReset("menu"); LINK.note=""; LINK.typed=""; screen="online"; }
function leaveOnline(){ netReset("menu"); screen="title"; }
function saveKey(code,role,key){ try{sessionStorage.setItem("h4l2p:"+code+":"+role,key);}catch(_){} }
function loadKey(code,role){ try{return sessionStorage.getItem("h4l2p:"+code+":"+role)||"";}catch(_){return "";} }
function netSend(obj){ try{ if(LINK.ws && LINK.ws.readyState===1) LINK.ws.send(JSON.stringify(obj)); }catch(_){} }
// tell the other phone who's playing on this phone (the boy and his kit colours: nothing personal)
function sendIntro(){ const k=kits[human]; netSend({t:"intro",boy:human,main:k.main,trim:k.trim}); }

async function hostGame(){
  if(LINK.busy) return; netReset("creating"); LINK.busy=true; LINK.note="";
  try{
    const res=await fetch(NET_URL+"/new",{method:"POST"});
    if(!res.ok) throw new Error("status "+res.status);
    const d=await res.json();
    if(!/^[A-Z2-9]{5}$/.test(d.code||"") || typeof d.hostKey!=="string") throw new Error("bad reply");
    LINK.code=d.code; LINK.key=d.hostKey; saveKey(d.code,"host",d.hostKey);
    connect("host");
  }catch(_){ netReset("menu"); LINK.note="Couldn't reach the game server. Check the internet connection and try again."; }
}
function joinGame(){
  const code=LINK.typed.toUpperCase();
  if(code.length!==5){ LINK.note="Type all 5 characters of the code"; return; }
  netReset("connecting"); LINK.code=code; LINK.key=loadKey(code,"guest"); LINK.note="";
  connect("guest");
}
function connect(role){
  const gen=LINK.gen, code=LINK.code; LINK.role=role; LINK.stage=role==="host"?"hosting":"connecting";
  let url=NET_URL.replace(/^http/,"ws")+"/room/"+LINK.code+"?role="+role; if(LINK.key) url+="&key="+encodeURIComponent(LINK.key);
  let ws; try{ ws=new WebSocket(url); }catch(_){ LINK.stage="menu"; LINK.note="Couldn't connect."; return; }
  LINK.ws=ws; let opened=false;
  ws.onopen=()=>{ if(gen!==LINK.gen) return; opened=true; };
  ws.onmessage=e=>{ if(gen!==LINK.gen) return; onNetMessage(e.data); };
  ws.onclose=e=>{
    if(gen!==LINK.gen) return; LINK.ws=null;
    if(!opened){ netReset(role==="guest"?"join":"menu");
      LINK.note=role==="guest"?"Couldn't join "+code+": check the code. The game may be full or finished.":"Couldn't open the game. Try again.";
      LINK.typed=role==="guest"?LINK.typed:""; return; }
    if(e.code===4002){ netReset("menu"); LINK.note="That game has finished."; return; }
    LINK.peer=false; LINK.stage="lost"; LINK.note="Connection lost. Reconnecting…";
    setTimeout(()=>{ if(gen===LINK.gen && LINK.stage==="lost") connect(role); },1500);   // try again with the same code and key
  };
}
// everything from the network is checked: it must be a small JSON object of a type we know
function onNetMessage(raw){
  if(typeof raw!=="string" || raw.length>4096) return;
  let m; try{ m=JSON.parse(raw); }catch(_){ return; }
  if(!m || typeof m!=="object" || typeof m.t!=="string") return;
  if(m.t==="hello"){
    if(typeof m.key==="string" && m.key.length<=64){ LINK.key=m.key; saveKey(LINK.code,LINK.role,m.key); }
    LINK.peer=!!m.peer; LINK.stage=LINK.peer?"meeting":(LINK.role==="host"?"hosting":"waiting");
    if(LINK.peer) sendIntro();
  } else if(m.t==="peer"){
    if(m.s==="joined"){ LINK.peer=true; LINK.stage="meeting"; sendIntro(); play("tick"); }
    else if(m.s==="left"){ LINK.peer=false; LINK.other=null; LINK.stage=LINK.role==="host"?"hosting":"waiting"; LINK.note="The other phone left. Waiting for it to come back…"; }
  } else if(m.t==="intro"){
    if(!BOYS[m.boy]) return;
    const main=MAINS[m.main]?m.main:"blue", trim=TRIMS[m.trim]?m.trim:"white";
    LINK.other={boy:m.boy,main,trim}; LINK.stage="connected"; LINK.note=""; play("cheer",0.8);
  }
}

// --- the screen ---
let codeKeys=[];
function drawOnline(){
  ui=[]; drawCourt(); shade(0.84);
  bigTitle("TWO PHONES",W/2,30,28);
  const box=(x,y,w,h)=>{ctx.fillStyle="rgba(16,21,43,0.95)"; rr(x,y,w,h,18); ctx.fill(); ctx.strokeStyle="rgba(255,255,255,0.15)"; ctx.lineWidth=2; ctx.stroke();};
  const st=LINK.stage;
  if(st==="menu"){
    text("Play each other on two phones: one hosts, the other joins with the code",W/2,58,BODY(13,800),C.muted,"center");
    box(W/2-330,80,310,210); box(W/2+20,80,310,210);
    text("HOST A GAME",W/2-175,112,DISP(20),C.warn,"center");
    text("Get a code to share with",W/2-175,146,BODY(13,800),C.ink,"center");
    text("the other player",W/2-175,164,BODY(13,800),C.ink,"center");
    button(W/2-300,200,250,60,"HOST",{fill:"#2F6FE4",sub:"You play as "+BOYS[human].name},hostGame);
    text("JOIN A GAME",W/2+175,112,DISP(20),C.warn,"center");
    text("Type in the code from",W/2+175,146,BODY(13,800),C.ink,"center");
    text("the other phone",W/2+175,164,BODY(13,800),C.ink,"center");
    button(W/2+50,200,250,60,"JOIN",{fill:"#F26B1D",ink:C.navy,sub:"You play as "+BOYS[human].name},()=>{LINK.stage="join"; LINK.note="";});
  } else if(st==="join"){
    text("Type the code shown on the other phone",W/2,58,BODY(13,800),C.muted,"center");
    for(let i=0;i<5;i++){const x=W/2-150+i*62;   // the five code boxes
      ctx.fillStyle="rgba(46,56,102,0.95)"; rr(x,74,52,58,10); ctx.fill();
      ctx.strokeStyle=i===LINK.typed.length?C.warn:"rgba(255,255,255,0.25)"; ctx.lineWidth=i===LINK.typed.length?3:2; ctx.stroke();
      if(LINK.typed[i]) text(LINK.typed[i],x+26,104,DISP(30),C.ink,"center");}
    // an on-screen keyboard with just the characters codes use
    codeKeys=CODE_CHARS.split(""); const kw=44, kh=38, cols=11, kx0=W/2-(cols*kw+(cols-1)*6)/2;
    codeKeys.forEach((ch,i)=>{const c=i%cols, r=Math.floor(i/cols);
      button(kx0+c*(kw+6),146+r*(kh+6),kw,kh,ch,{size:17,outline:"rgba(255,255,255,0.25)"},()=>{ if(LINK.typed.length<5){LINK.typed+=ch; LINK.note="";} });});
    button(kx0+9*(kw+6),146+2*(kh+6),2*kw+6,kh,"⌫",{size:18,outline:"rgba(255,255,255,0.25)"},()=>{LINK.typed=LINK.typed.slice(0,-1);});
    button(W/2+60,290,180,46,"JOIN",{fill:"#F26B1D",ink:C.navy,disabled:LINK.typed.length!==5},joinGame);
    button(W/2-240,290,180,46,"BACK",{},()=>{LINK.stage="menu"; LINK.note="";});
  } else {
    // waiting, meeting or connected
    box(W/2-300,64,600,250);
    if(LINK.role==="host"){
      text("YOUR GAME CODE",W/2,90,BODY(13,900),C.muted,"center");
      text(LINK.code?LINK.code.split("").join(" "):"…",W/2,132,DISP(48),C.warn,"center");
      text("Read it out, or show this screen to the other player",W/2,170,BODY(13,800),C.ink,"center");
    } else {
      text("GAME CODE",W/2,90,BODY(13,900),C.muted,"center");
      text(LINK.code.split("").join(" "),W/2,132,DISP(40),C.ink,"center");
    }
    const dots=".".repeat(1+Math.floor(performance.now()/400)%3);
    let line, col=C.ink;
    if(st==="creating"||st==="connecting") line="Connecting"+dots;
    else if(st==="hosting") line="Waiting for the other phone to join"+dots;
    else if(st==="waiting") line="Waiting for the host"+dots;
    else if(st==="meeting") line="Found them! Saying hello"+dots;
    else if(st==="lost") {line="Connection lost. Reconnecting"+dots; col=C.warn;}
    if(st==="connected" && LINK.other){
      const me=kitLook(BOYS[human],kits[human],1), them=kitLook(BOYS[LINK.other.boy],{main:LINK.other.main,trim:LINK.other.trim},-1);
      faceBadge(me,W/2-110,232,30,MAINS[kits[human].main]); faceBadge(them,W/2+110,232,30,MAINS[LINK.other.main]);
      text("CONNECTED!",W/2,198,DISP(22),C.green,"center");
      text(BOYS[human].name+" (this phone)",W/2-110,280,BODY(12,900),C.ink,"center");
      text(BOYS[LINK.other.boy].name+" (other phone)",W/2+110,280,BODY(12,900),C.ink,"center");
      text("vs",W/2,236,DISP(18),C.muted,"center");
      if(LINK.other.boy===human) text("You're both "+BOYS[human].name+"! One of you can switch on the map",W/2,300,BODY(11,900),C.warn,"center");
      button(W/2+150,326,150,44,"PLAY",{fill:"#2F6FE4",disabled:true,sub:"matches coming next"});
    } else text(line||"",W/2,226,BODY(16,900),col,"center");
    button(W/2-300,326,150,44,LINK.stage==="connected"?"LEAVE":"CANCEL",{},()=>{ netReset("menu"); LINK.note=""; });
  }
  if(st==="menu"||st==="join") button(16,344,110,36,"MENU",{},leaveOnline);
  if(LINK.note){ctx.font=BODY(12,900); const w=Math.min(W-40,ctx.measureText(LINK.note).width+28);
    ctx.fillStyle="rgba(10,14,30,0.95)"; rr(W/2-w/2,st==="join"?340:300,w,28,10); ctx.fill();
    text(LINK.note,W/2,st==="join"?354:314,BODY(12,900),C.warn,"center");}
}
// typing the code on a keyboard
function onlineKey(k){
  if(screen!=="online" || LINK.stage!=="join") return false;
  if(k==="Backspace"){ LINK.typed=LINK.typed.slice(0,-1); return true; }
  if(k==="Enter"){ joinGame(); return true; }
  const ch=(k||"").toUpperCase();
  if(ch.length===1 && CODE_CHARS.includes(ch)){ if(LINK.typed.length<5) LINK.typed+=ch; LINK.note=""; return true; }
  return false;
}
