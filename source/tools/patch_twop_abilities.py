# second step of the 2 Player patch: boss abilities for both players, and the lobby's abilities switch
import sys
f = sys.argv[1]
s = open(f, encoding="utf-8").read()
def once(a, b):
    global s
    n = s.count(a); assert n == 1, (n, a[:110]); s = s.replace(a, b)

# the right player's abilities come from dAb(): a computer boss's (BS) or a 2 Player boss look's (DS)
once("function handPos(e,dir,charging){const k=(e===d&&BOSS)?BS.size:", "function handPos(e,dir,charging){const k=(e===d&&dAb())?dAb().size:")
once('function cpuHand(){const S=BOSS?BS.size:1, A=BOSS?BS.arm*(sig.on==="block"&&BOSS.sv.reach?1.3:1):1;',
     'function cpuHand(){const DA=dAb(), S=DA?DA.size:1, A=DA?DA.arm*(BOSS&&sig.on==="block"&&BOSS.sv.reach?1.3:1):1;')
once("      const k=BOSS?BS.size:1, a={x:d.x-10*k,y:d.y-96*k};", "      const k=dAb()?dAb().size:1, a={x:d.x-10*k,y:d.y-96*k};")
once('<(BOSS?BS.blockR+(sig.on==="block"?12:0):18)*fadeK)', '<(dAb()?dAb().blockR+(BOSS&&sig.on==="block"?12:0):18)*fadeK)')
once("(ball.fade&&BOSS&&BS.fade?Math.max(0.35,1-BS.fade*1.3):1)", "(ball.fade&&dAb()&&dAb().fade?Math.max(0.35,1-dAb().fade*1.3):1)")
once('const R=(e===d&&BOSS)?24+BS.reb*40+(sig.on==="reb"?30:0):', 'const R=(e===d&&dAb())?24+dAb().reb*40+(BOSS&&sig.on==="reb"?30:0):')
once("const Hh=(e===d&&BOSS)?92*BS.size+(BS.arm-1)*30:", "const Hh=(e===d&&dAb())?92*dAb().size+(dAb().arm-1)*30:")
once("  const S=BOSS?BS.size:1, A=BOSS?BS.arm:1;\n  let hx=-16", "  const S=dAb()?dAb().size:1, A=dAb()?dAb().arm:1;\n  let hx=-16")
once("  if(BOSS && BS.speed>1 && Math.abs(d.spd||0)>150){", "  if(dAb() && dAb().speed>1 && Math.abs(d.spd||0)>150){")
once("  if(BOSS && pStun>0) p.lean=", "  if((BOSS||TWO.on) && pStun>0) p.lean=")
once("  if(!BOSS) return 1;\n  if(pStun>0) return 0;", "  if(!dAb() && !TWO.on) return 1;\n  if(pStun>0) return 0;\n  if(!dAb()) return 1;")
once('  if(inWay && sig.on==="guard") return 0.12;\n  if(inWay && BS.glue) return Math.max(0.25,1-BS.glue*2);',
     '  if(inWay && BOSS && sig.on==="guard") return 0.12;\n  if(inWay && dAb().glue) return Math.max(0.25,1-dAb().glue*2);')
# the sweet spot and dunk chances work for either player's abilities
once('function pRange(z,fade){\n  const r=(fade?z.f:z.n).slice(); if(!PS || z.behind) return r;\n'
     '  let w=0; if(PS.has("sharp")) w+=Math.round(PS.s*12); if(PS.deep && z!==ZONES.inside) w+=Math.round(PS.deep*14); if(fade && PS.fade) w+=3;',
     'function pRange(z,fade){return abRange(PS,z,fade);}\nfunction abRange(S,z,fade){\n  const r=(fade?z.f:z.n).slice(); if(!S || z.behind) return r;\n'
     '  let w=0; if(S.has("sharp")) w+=Math.round(S.s*12); if(S.deep && z!==ZONES.inside) w+=Math.round(S.deep*14); if(fade && S.fade) w+=3;')
once('function pDunkChance(){return PS&&PS.has("dunk")?Math.min(0.92,0.5+PS.s*1.0):0.5;}\n'
     'function pWindChance(){return PS&&PS.has("dunk")?Math.min(0.85,WIND_MAKE+PS.s*0.8):WIND_MAKE;}',
     'function pDunkChance(){return dunkChanceOf(PS);}\nfunction pWindChance(){return windChanceOf(PS);}\n'
     'function dunkChanceOf(S){return S&&S.has("dunk")?Math.min(0.92,0.5+S.s*1.0):0.5;}\n'
     'function windChanceOf(S){return S&&S.has("dunk")?Math.min(0.85,WIND_MAKE+S.s*0.8):WIND_MAKE;}')

# the lobby: boss looks, the head-to-head record, and a boss-abilities switch
once('skin:skinOf[human]||null}); }', 'skin:skinOf[human]||null,ab:twoAb?1:0}); }')
once('    LINK.other={boy:m.boy,main,trim,skin:okSkin(m.skin)};', '    LINK.other={boy:m.boy,main,trim,skin:okSkin(m.skin),ab:m.ab!==0};')
once('      const me=kitLook(BOYS[human],kits[human],1), them=kitLook(BOYS[LINK.other.boy],{main:LINK.other.main,trim:LINK.other.trim},-1);',
     '      const me=lookOf(human,skinOf[human]||null,kits[human],1), them=lookOf(LINK.other.boy,LINK.other.skin,{main:LINK.other.main,trim:LINK.other.trim},-1);')
once('      text(BOYS[human].name+" (this phone)",W/2-110,280,BODY(12,900),C.ink,"center");\n'
     '      text(BOYS[LINK.other.boy].name+" (other phone)",W/2+110,280,BODY(12,900),C.ink,"center");',
     '      const abLine=(skin,on)=>skin?(on?"Boss abilities ON":"Boss look only"):"";\n'
     '      text(me.name+" (this phone)",W/2-110,276,BODY(12,900),C.ink,"center");\n'
     '      text(them.name+" (other phone)",W/2+110,276,BODY(12,900),C.ink,"center");\n'
     '      text(abLine(skinOf[human],twoAb),W/2-110,292,BODY(10,900),C.warn,"center");\n'
     '      text(abLine(LINK.other.skin,LINK.other.ab),W/2+110,292,BODY(10,900),C.warn,"center");\n'
     '      const hm=h2h[human];\n'
     '      if(LINK.other.boy!==human && hm.w+hm.l>0) text("HEAD-TO-HEAD: "+BOYS[human].name+" "+hm.w+" · "+BOYS[LINK.other.boy].name+" "+hm.l,W/2,LINK.role==="host"?186:170,BODY(12,900),C.muted,"center");\n'
     '      if(skinOf[human]) button(W/2-130,326,260,44,twoAb?"BOSS ABILITIES: ON":"BOSS ABILITIES: OFF",{outline:"rgba(255,255,255,0.3)",size:14,sub:"tap to switch"},toggleTwoAb);')
once("shoesOwned,h2h,sound:SND.on", "shoesOwned,h2h,twoAb,sound:SND.on")
once("    if(s.crowd===false) SND.crowd=false;\n", "    if(s.crowd===false) SND.crowd=false;\n    if(s.twoAb===false) twoAb=false;\n")
open(f, "w", encoding="utf-8").write(s)
print("abilities patched")
