import sys
f, blk = sys.argv[1], sys.argv[2]
s = open(f).read()

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:100])
    s = s.replace(a, b)

# the trophy code goes just before the title screen
once("function drawTitle(){", open(blk).read() + "function drawTitle(){")
once('''  else if(screen==="players") drawPlayers();''', '''  else if(screen==="players") drawPlayers();
  else if(screen==="trophies") drawTrophies();''')

# players each boy has unlocked (his own), and which one he's playing as
once('let owned=["zackie","keelan"];   // players that can be picked; bosses join this list later from Trophies, Rewards and Chests',
     'let owned={zackie:["zackie","keelan"],keelan:["zackie","keelan"]};   // players each boy can pick; bosses come from Trophies\n'
     'let skinOf={zackie:null,keelan:null};   // a boss the boy has chosen to play as ("boss3"), or null for himself')
once('    if(Array.isArray(s.owned)) owned=Array.from(new Set(["zackie","keelan",...s.owned]));',
     '''    for(const b of ["zackie","keelan"]){
      if(s.owned&&Array.isArray(s.owned[b])) owned[b]=Array.from(new Set(["zackie","keelan",...s.owned[b]]));
      if(s.skinOf&&typeof s.skinOf[b]==="string"&&owned[b].includes(s.skinOf[b])) skinOf[b]=s.skinOf[b];
      if(s.bonus&&s.bonus[b]) bonus[b]={m:+s.bonus[b].m||0,c:+s.bonus[b].c||0};
      if(s.spent&&s.spent[b]) spent[b]={m:+s.spent[b].m||0,c:+s.spent[b].c||0};
      if(s.extraBalls&&Array.isArray(s.extraBalls[b])) extraBalls[b]=s.extraBalls[b];
      if(s.shoesOwned&&Array.isArray(s.shoesOwned[b])) shoesOwned[b]=s.shoesOwned[b];
      if(!(kits[b].shoe>=0 && shoesOwned[b].includes(kits[b].shoe))) kits[b].shoe=-1;
    }''')
once("JSON.stringify({kits,human,wins,progress,medals,crowns,owned,sound:SND.on})",
     "JSON.stringify({kits,human,wins,progress,medals,crowns,owned,skinOf,bonus,spent,extraBalls,shoesOwned,sound:SND.on})")

# menu: Players at the top, Trophies under it, then Prizes
once('''  button(324,92,176,40,"PLAYERS",{fill:"#7B4FD6",sub:owned.length+" of "+(2+BOSSES.length)+" unlocked"},()=>{screen="players";});
  drawPrizes(human,412,140);''', '''  button(324,16,176,44,"PLAYERS",{fill:"#7B4FD6",sub:owned[human].length+" of "+(2+BOSSES.length)+" unlocked"},()=>{screen="players";});
  button(324,66,176,44,"TROPHIES",{fill:"#14A3B8",sub:"Spend medals & crowns"},()=>{screen="trophies"; tro.stage="shop"; tro.msg.t=0;});
  drawPrizes(human,412,118);''')
# prizes show what the boy can spend
once('''  const nMed=medals[boy].length, nCrown=crowns[boy].length, maxMed=LEVELS-ROADS.length, maxCrown=ROADS.length;''',
     '''  const wl=wallet(boy), nMed=wl.m, nCrown=wl.c, maxMed=LEVELS-ROADS.length, maxCrown=ROADS.length;''')
once('''text("MEDALS · of "+maxMed,x+77,y+92,BODY(10,900),C.muted);''', '''text("MEDALS · "+medals[boy].length+"/"+maxMed+" won",x+77,y+92,BODY(10,900),C.muted);''')
once('''text("CROWNS · of "+maxCrown,x+77,y+168,BODY(10,900),C.muted);''', '''text("CROWNS · "+crowns[boy].length+"/"+maxCrown+" won",x+77,y+168,BODY(10,900),C.muted);''')
once('''  text(nCrown?"Last boss: "+BOSSES[Math.floor(Math.max(...crowns[boy])/STOPS)].name''', '''  text(crowns[boy].length?"Last boss: "+BOSSES[Math.floor(Math.max(...crowns[boy])/STOPS)].name''')

# Players screen: the boy's own unlocked players; tapping an unlocked boss plays as him
once('''    const isBoy=!id.startsWith("boss"), i=isBoy?-1:+id.slice(4), open=owned.includes(id), sel=isBoy&&id===human;''',
     '''    const isBoy=!id.startsWith("boss"), i=isBoy?-1:+id.slice(4), open=owned[human].includes(id), sel=isBoy?(id===human&&!skinOf[human]):skinOf[human]===id;''')
once('''      if(isBoy){human=id; mapScroll=null; saveGame(); playersMsg={text:"Playing as "+name,t:1.5};}
      else if(open) playersMsg={text:name+" is unlocked",t:1.5};
      else playersMsg={text:name+" unlocks later from Trophies, Rewards and Chests",t:2};''',
     '''      if(isBoy){human=id; skinOf[id]=null; mapScroll=null; saveGame(); playersMsg={text:"Playing as "+name,t:1.5};}
      else if(open){skinOf[human]=id; saveGame(); playersMsg={text:BOYS[human].name+" plays as "+name,t:1.8};}
      else playersMsg={text:name+" is locked: win him from a Trophy",t:2};''')
once('''  text("Tap Zackie or Keelan to play as him. Bosses unlock later from Trophies, Rewards and Chests.",W/2,56,BODY(12,800),C.muted,"center");''',
     '''  text(BOYS[human].name+"'s players · tap one to play as him · win locked bosses from Trophies",W/2,56,BODY(12,800),C.muted,"center");''')

# looks: a boss "skin" keeps the boy's kit colours but has the boss's face, hair, name and number
once('''function applyLooks(){
  const o=other();
  LOOK.p=kitLook(BOYS[human],kits[human],1); LOOK.p.who="p";''', '''function boyBase(boy){
  const id=skinOf[boy]; if(!id) return BOYS[boy];
  const i=+id.slice(4), bl=bossLook(i);
  return Object.assign({},BOYS[boy],{name:BOSSES[i].name,num:bl.num,skin:bl.skin,skinDark:bl.skinDark,hair:bl.hair,hairHi:bl.hairHi,
    brow:bl.brow,eye:bl.eye,style:bl.style,gapTeeth:bl.gapTeeth,bigEars:bl.bigEars,band:bl.band});
}
function applyLooks(){
  const o=other();
  LOOK.p=kitLook(boyBase(human),kits[human],1); LOOK.p.who="p";''')
once('''  NAME.p=BOYS[human].name; NAME.d=BOYS[o].name;''', '''  NAME.p=boyBase(human).name; NAME.d=BOYS[o].name;''')
once('''  return Object.assign({},b,{dir,jersey:main,trim,shorts:mix(main,"#000000",0.18),numCol:trim,shoe:"#FFFFFF",sole:"#1B2340",sock:"#FFFFFF"});''',
     '''  const sh=k.shoe>=0?ARENAS[k.shoe]:null;   // arena shoes won from trophies
  return Object.assign({},b,{dir,jersey:main,trim,shorts:mix(main,"#000000",0.18),numCol:trim,shoe:sh?sh.p:"#FFFFFF",sole:sh?sh.s:"#1B2340",sock:"#FFFFFF"});''')
once('''  drawAthlete({x:0,y:0,lean:0,spd:0,run:0},kitLook(b,k,1),{x:14,y:-34},{x:-12,y:-26},false,false);''',
     '''  drawAthlete({x:0,y:0,lean:0,spd:0,run:0},kitLook(boyBase(boy),k,1),{x:14,y:-34},{x:-12,y:-26},false,false);''')
once('''  text(b.name.toUpperCase(),tx,y+30,DISP(24),C.ink); text("#"+b.num,x+w-16,y+30,DISP(20),C.muted,"right");''',
     '''  const bb=boyBase(boy); let nfs=24; ctx.font=DISP(nfs); while(nfs>14 && ctx.measureText(bb.name.toUpperCase()).width>w-210){nfs-=2; ctx.font=DISP(nfs);}
  text(bb.name.toUpperCase(),tx,y+30,DISP(nfs),C.ink); text("#"+bb.num,x+w-16,y+30,DISP(20),C.muted,"right");''')
# shoes row replaces the hint line at the bottom of the card
once('''  const hint=sel?"Ready to play":((mode==="level"&&!pickByPlayer)?"Plays as the computer":"Tap the card to "+(mode==="practice"?"pick ":"play as ")+b.name);
  text(hint,tx,y+h-22,BODY(12,800),sel?C.warn:C.muted);''', '''  const shoes=[-1,...shoesOwned[boy]], si=Math.max(0,shoes.indexOf(k.shoe>=0?k.shoe:-1)), sy=y+h-24;
  text("SHOES",tx,sy,BODY(12,900),C.muted);
  if(shoes.length>1) button(tx+46,sy-13,26,26,"‹",{size:16},()=>{k.shoe=shoes[(si-1+shoes.length)%shoes.length]; saveGame();});
  if(k.shoe>=0) drawShoeIcon(tx+92,sy+1,1,ARENAS[k.shoe]); else drawShoeIcon(tx+92,sy+1,1,{p:"#FFFFFF",s:"#1B2340"});
  text(k.shoe>=0?ARENAS[k.shoe].name:(shoes.length>1?"Classic":"Classic · win more from Trophies"),tx+112,sy,BODY(11,900),C.ink);
  if(shoes.length>1) button(x+w-42,sy-13,26,26,"›",{size:16},()=>{k.shoe=shoes[(si+1)%shoes.length]; saveGame();});''')
once('''  text("BALL",tx,y+176,BODY(12,900),C.muted);''', '''  text("BALL",tx,y+170,BODY(12,900),C.muted);''')
once('''  if(nextBall>0) text("next: "+bl[nextBall].name+" at Level "+nextBall,x+w-16,y+176,BODY(10,800),C.muted,"right");
  const by=y+202,''', '''  if(nextBall>0) text("next: "+bl[nextBall].name+" at Level "+nextBall,x+w-16,y+170,BODY(10,800),C.muted,"right");
  const by=y+194,''')
# balls won from trophies
once("function ballUnlocked(boy,i){return i===0 || Math.floor(progress[boy]/STOPS)>=i-1;}",
     "function ballUnlocked(boy,i){return i===0 || Math.floor(progress[boy]/STOPS)>=i-1 || extraBalls[boy].includes(i);}")

# a boy playing as a boss shows the boss's face in pop-ups and on the end screen
once('''  if(BOSS && who==="d"){ctx.restore(); faceBadge(LOOK.d,cx,cy,r,col);}''',
     '''  if((BOSS && who==="d")||(who==="p" && skinOf[human])){ctx.restore(); faceBadge(LOOK[who],cx,cy,r,col);}''')
once('''  if(!youWin && BOSS){faceBadge(LOOK.d,180,186,112,C.p2); drawCrown(180,72,22);} else portraitBadge(boy,180,186,112);''',
     '''  if(!youWin && BOSS){faceBadge(LOOK.d,180,186,112,C.p2); drawCrown(180,72,22);}
  else if(youWin && skinOf[human]) faceBadge(LOOK.p,180,186,112,C.p1);
  else portraitBadge(boy,180,186,112);''')

open(f, "w").write(s)
print("patched")
