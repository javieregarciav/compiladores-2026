<?php
/**
 * index.php — Mini-Compilador v2.0
 * Analizador Léxico + Árbol Sintáctico + Analizador Semántico
 * Ingeniería en Sistemas · Universidad Mariano Gálvez de Guatemala
 */
$integrantes = [
    'Javier Emanuel García Vásquez',
    'José Luis Curup Aquino',
    'Deyvis Abisai Silva Enríquez',
    'Erica Patricia Hidalgo Castro',
];
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MiniCompiler v2.0 · Proyecto Final Compiladores</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
/* ================================================================ RESET */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;background:#020408;color:#e0f4ff;font-family:'Share Tech Mono','Courier New',monospace;font-size:13px;overflow:hidden}

/* ================================================================ VARIABLES */
:root{
  --bg0:#020408;--bg1:#040810;--bg2:#060d18;--bg3:#0a1628;--bg4:#0d1e35;
  --cyan:#00f5ff;--green:#00ff88;--amber:#ffb700;--red:#ff2d55;--purple:#bf5af2;--blue:#0a84ff;
  --cglow:0 0 8px rgba(0,245,255,.6),0 0 20px rgba(0,245,255,.2);
  --gglow:0 0 8px rgba(0,255,136,.6),0 0 20px rgba(0,255,136,.2);
  --aglow:0 0 8px rgba(255,183,0,.6),0 0 20px rgba(255,183,0,.2);
  --rglow:0 0 8px rgba(255,45,85,.7),0 0 24px rgba(255,45,85,.3);
  --t1:#e0f4ff;--t2:#7ab3cc;--t3:#2a4a60;--t4:#152030;
  --bd1:rgba(0,245,255,.08);--bd2:rgba(0,245,255,.18);--bd3:rgba(0,245,255,.45);
  --font:'Share Tech Mono',monospace;--disp:'Orbitron',monospace;
}

/* ================================================================ SCANLINES */
body::before{content:'';position:fixed;inset:0;z-index:9999;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.07) 2px,rgba(0,0,0,.07) 4px);
  pointer-events:none;animation:scan 8s linear infinite}
@keyframes scan{from{background-position:0 0}to{background-position:0 100px}}
body::after{content:'';position:fixed;inset:0;z-index:9998;
  background:radial-gradient(ellipse at 50% 0%,rgba(0,245,255,.04) 0%,transparent 70%);pointer-events:none}

/* ================================================================ CIRCUIT BG */
.cbg{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.04}

/* ================================================================ APP SHELL */
#app{position:relative;z-index:1;display:grid;grid-template-rows:auto auto 1fr auto;height:100vh;overflow:hidden}

/* ================================================================ BANNER */
#banner{
  position:relative;z-index:2;
  background:linear-gradient(90deg,rgba(0,10,22,.98),rgba(0,20,40,.98),rgba(0,10,22,.98));
  border-bottom:1px solid var(--bd2);
  padding:9px 20px;
  display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;
  overflow:visible;
}
#banner::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan) 30%,var(--green) 70%,transparent);opacity:.5}
#banner::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.25}
.bn-left{display:flex;flex-direction:column;gap:2px}
.bn-label{font-family:var(--disp);font-size:7px;letter-spacing:2.5px;color:var(--t3);text-transform:uppercase}
.bn-title{font-family:var(--disp);font-size:13px;font-weight:900;letter-spacing:3px;text-transform:uppercase;
  color:var(--cyan);text-shadow:0 0 12px rgba(0,245,255,.5),0 0 30px rgba(0,245,255,.15)}
.bn-center{display:flex;flex-wrap:wrap;justify-content:center;gap:3px 14px}
.bn-author{font-size:10px;color:var(--green);text-shadow:0 0 8px rgba(0,255,136,.3);white-space:nowrap}
.bn-author::before{content:'▸ ';color:var(--t3);font-size:9px}
.bn-right{display:flex;flex-direction:column;gap:2px;text-align:right}
.bn-uni{font-size:9px;color:var(--amber);text-shadow:0 0 8px rgba(255,183,0,.3);line-height:1.5}
.bn-course{font-family:var(--disp);font-size:7.5px;letter-spacing:1.5px;color:var(--t2);text-transform:uppercase}
.bn-teacher{font-size:9px;color:var(--purple);text-shadow:0 0 8px rgba(191,90,242,.3)}

/* ================================================================ HEADER */
header{display:flex;align-items:center;gap:16px;padding:0 20px;height:48px;
  background:linear-gradient(90deg,var(--bg2),rgba(0,245,255,.03));
  border-bottom:1px solid var(--bd2);position:relative;overflow:hidden}
header::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  animation:hglow 3s ease-in-out infinite;opacity:.5}
@keyframes hglow{0%,100%{opacity:.4}50%{opacity:1}}
.logo{display:flex;align-items:center;gap:10px}
.logo-icon{width:30px;height:30px;border:1.5px solid var(--cyan);border-radius:6px;
  display:flex;align-items:center;justify-content:center;
  box-shadow:var(--cglow),inset 0 0 12px rgba(0,245,255,.08)}
.logo-icon::before{content:'⬡';color:var(--cyan);font-size:14px;animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{text-shadow:0 0 6px var(--cyan)}50%{text-shadow:0 0 18px var(--cyan),0 0 30px rgba(0,245,255,.4)}}
.logo-text{font-family:var(--disp);font-size:13px;font-weight:700;letter-spacing:3px;
  color:var(--cyan);text-shadow:var(--cglow);text-transform:uppercase}
.logo-sub{font-family:var(--font);font-size:9px;color:var(--t2);letter-spacing:1px;display:block;margin-top:-2px}
.hdiv{width:1px;height:26px;background:linear-gradient(180deg,transparent,var(--cyan),transparent);opacity:.3;margin:0 4px}
.htags{display:flex;gap:8px}
.tag{font-size:8px;font-family:var(--disp);letter-spacing:1.5px;padding:3px 8px;
  border-radius:2px;border:1px solid;text-transform:uppercase}
.tag-c{border-color:var(--cyan);color:var(--cyan)}
.tag-g{border-color:var(--green);color:var(--green)}
.tag-p{border-color:var(--purple);color:var(--purple)}
.hstatus{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:10px;color:var(--t2)}
.sdot{width:7px;height:7px;border-radius:50%;background:var(--green);
  box-shadow:var(--gglow);animation:blink 2.5s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* ================================================================ MAIN TABS */
.tab-bar{display:flex;gap:0;border-bottom:1px solid var(--bd2);background:var(--bg2);flex-shrink:0}
.tab-btn{font-family:var(--disp);font-size:8px;letter-spacing:1.5px;text-transform:uppercase;
  padding:0 18px;height:34px;background:none;border:none;border-right:1px solid var(--bd1);
  color:var(--t3);cursor:pointer;transition:all .15s;position:relative;white-space:nowrap}
.tab-btn:hover{color:var(--t1);background:rgba(0,245,255,.04)}
.tab-btn.active{color:var(--cyan);background:var(--bg3)}
.tab-btn.active::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:var(--cyan);box-shadow:0 0 8px var(--cyan)}
.tab-btn .tab-badge{font-size:8px;background:var(--red);color:#fff;border-radius:10px;
  padding:1px 5px;margin-left:6px;display:none}
.tab-btn .tab-badge.show{display:inline}

/* ================================================================ MAIN LAYOUT */
main{display:grid;grid-template-columns:1fr 340px;overflow:hidden}
.tab-content{display:none;flex:1;overflow:hidden;flex-direction:column}
.tab-content.active{display:flex}

/* ================================================================ PANEL BASE */
.panel{border-right:1px solid var(--bd1);border-bottom:1px solid var(--bd1);
  display:flex;flex-direction:column;overflow:hidden;position:relative}
.ph{display:flex;align-items:center;gap:10px;padding:0 14px;height:34px;
  background:var(--bg2);border-bottom:1px solid var(--bd2);flex-shrink:0;position:relative}
.ph::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--cyan);box-shadow:0 0 8px var(--cyan)}
.ph.green::before{background:var(--green);box-shadow:0 0 8px var(--green)}
.ph.amber::before{background:var(--amber);box-shadow:0 0 8px var(--amber)}
.ph.red::before{background:var(--red);box-shadow:0 0 8px var(--red)}
.ph.purple::before{background:var(--purple);box-shadow:0 0 8px var(--purple)}
.ph-title{font-family:var(--disp);font-size:8px;font-weight:700;letter-spacing:2px;
  text-transform:uppercase;color:var(--cyan)}
.ph-title.green{color:var(--green)}.ph-title.amber{color:var(--amber)}
.ph-title.red{color:var(--red)}.ph-title.purple{color:var(--purple)}
.ph-count{margin-left:auto;font-size:10px;color:var(--t3)}

/* ================================================================ EDITOR */
#panel-editor{grid-column:1;grid-row:1;display:flex;flex-direction:column}
.ed-wrap{flex:1;display:flex;overflow:hidden;position:relative}
#lnum{width:48px;background:var(--bg1);border-right:1px solid var(--bd1);overflow:hidden;flex-shrink:0}
#lnum-inner{padding:12px 10px 12px 0;font-family:var(--font);font-size:12px;line-height:20px;
  color:var(--t3);text-align:right;user-select:none;white-space:pre}
.ed-core{flex:1;position:relative;overflow:hidden}
#code-hl{position:absolute;inset:0;padding:12px 16px;font-family:var(--font);font-size:13px;
  line-height:20px;white-space:pre;overflow:hidden;pointer-events:none;z-index:1;color:var(--t1);word-break:normal}
#code-ed{position:absolute;inset:0;background:var(--bg1);color:transparent;caret-color:var(--cyan);
  border:none;outline:none;resize:none;font-family:var(--font);font-size:13px;line-height:20px;
  padding:12px 16px;tab-size:4;overflow:auto;z-index:2;white-space:pre;word-break:normal}
.ed-status{height:22px;background:var(--bg2);border-top:1px solid var(--bd1);
  display:flex;align-items:center;padding:0 16px;gap:20px;font-size:10px;color:var(--t3);flex-shrink:0}
.ed-status b{color:var(--cyan)}

/* ================================================================ SIDE PANEL */
#side{grid-column:2;grid-row:1/3;border-left:1px solid var(--bd2);display:flex;flex-direction:column;overflow:hidden}

/* ================================================================ TABLES */
.tscroll{flex:1;overflow-y:auto;overflow-x:hidden}
.tscroll::-webkit-scrollbar{width:3px}
.tscroll::-webkit-scrollbar-thumb{background:var(--cyan);border-radius:2px;opacity:.4}
table.dt{width:100%;border-collapse:collapse;font-size:11px}
table.dt thead tr{background:var(--bg1);position:sticky;top:0;z-index:5}
table.dt thead th{padding:5px 10px;text-align:left;font-family:var(--disp);font-size:7.5px;
  letter-spacing:1.5px;text-transform:uppercase;color:var(--t3);border-bottom:1px solid var(--bd2)}
table.dt tbody tr{border-bottom:1px solid var(--bd1);transition:background .1s;
  animation:rapp .2s ease forwards;opacity:0}
@keyframes rapp{from{opacity:0;transform:translateX(-4px)}to{opacity:1;transform:none}}
table.dt tbody tr:nth-child(even){background:rgba(0,245,255,.012)}
table.dt tbody tr:hover{background:rgba(0,245,255,.06);cursor:default}
table.dt tbody td{padding:4px 10px;color:var(--t2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:120px}
table.dt tbody td:first-child{font-family:var(--disp);font-size:8.5px;letter-spacing:.8px}

/* token type colors */
.tok-INT,.tok-FLOAT,.tok-STRING,.tok-BOOLEAN{color:#5ac8fa}
.tok-IF,.tok-ELSE,.tok-WHILE,.tok-FOR,.tok-RETURN,.tok-AND,.tok-OR,.tok-NOT{color:#bf5af2}
.tok-TRUE,.tok-FALSE,.tok-NULL{color:#ff9f0a}
.tok-PRINT,.tok-INPUT{color:#ff6b6b}
.tok-ENTERO,.tok-DECIMAL{color:#ff9f0a}
.tok-CADENA{color:#30d158}
.tok-ID{color:#e0f4ff}
.tok-IGUAL,.tok-DIFERENTE,.tok-MENOR,.tok-MAYOR,.tok-MENOR_IGUAL,.tok-MAYOR_IGUAL,
.tok-MAS,.tok-MENOS,.tok-MULT,.tok-DIV,.tok-MOD,.tok-ASIGNACION,
.tok-Y_LOGICO,.tok-O_LOGICO,.tok-NO_LOGICO{color:#0a84ff}

/* ================================================================ CONSOLE */
#console{flex:1;overflow-y:auto;overflow-x:hidden;padding:10px 16px;
  background:var(--bg1);font-family:var(--font);font-size:12px;line-height:1.7}
#console::-webkit-scrollbar{width:3px}
#console::-webkit-scrollbar-thumb{background:var(--red);border-radius:2px}
.cline{display:flex;gap:10px;align-items:baseline;padding:1px 0}
.cline.error .ci{color:var(--red)}.cline.ok .ci{color:var(--green)}
.cline.info .ci{color:var(--cyan)}.cline.warn .ci{color:var(--amber)}
.ci{font-size:10px;width:14px;flex-shrink:0}
.ct{color:var(--t2)}.ct b{color:var(--red);font-weight:normal}
.cline.ok .ct{color:var(--green);opacity:.85}

/* ================================================================ SYNTAX TREE — VISUAL */
#tree-panel{flex:1;overflow:auto;background:var(--bg1);position:relative}
#tree-panel::-webkit-scrollbar{width:6px;height:6px}
#tree-panel::-webkit-scrollbar-thumb{background:rgba(191,90,242,.4);border-radius:3px}
#tree-canvas-wrap{padding:20px;display:inline-block;min-width:100%}
#tree-svg{display:block;overflow:visible}
.tree-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:100%;gap:8px;color:var(--t4);font-family:var(--disp);font-size:9px;letter-spacing:2px;text-transform:uppercase}
.tnode{cursor:pointer}.tnode:hover .tnbox{filter:brightness(1.3)}
.tnlabel{font-family:'Share Tech Mono',monospace;font-size:10px;fill:#e0f4ff;
  dominant-baseline:central;text-anchor:middle;pointer-events:none;user-select:none}
.tnsub{font-family:'Share Tech Mono',monospace;font-size:9px;
  dominant-baseline:central;text-anchor:middle;pointer-events:none;user-select:none;opacity:.7}
.tedge{fill:none;stroke-width:1.5;stroke-linecap:round;opacity:.45}
#tree-toolbar{display:flex;align-items:center;gap:8px;padding:6px 16px;
  border-bottom:1px solid var(--bd1);flex-shrink:0;background:var(--bg2)}
.ttbtn{font-family:var(--disp);font-size:7.5px;letter-spacing:1px;text-transform:uppercase;
  padding:4px 10px;background:none;border:1px solid var(--bd2);border-radius:2px;
  color:var(--t2);cursor:pointer;transition:all .15s}
.ttbtn:hover{border-color:var(--purple);color:var(--purple)}
#tree-legend{display:flex;flex-wrap:wrap;gap:6px 14px;padding:8px 16px;
  border-top:1px solid var(--bd1);flex-shrink:0;background:var(--bg2)}
.tlegitem{display:flex;align-items:center;gap:5px;font-size:10px;color:var(--t2);font-family:var(--font)}
.tlegdot{width:10px;height:10px;border-radius:2px;flex-shrink:0}

/* ================================================================ SEMANTIC */
#sem-panel{flex:1;overflow-y:auto;padding:12px 16px;background:var(--bg1)}
#sem-panel::-webkit-scrollbar{width:3px}
#sem-panel::-webkit-scrollbar-thumb{background:var(--amber);border-radius:2px}
.sem-section{margin-bottom:16px}
.sem-section-title{font-family:var(--disp);font-size:8px;letter-spacing:2px;text-transform:uppercase;
  color:var(--amber);border-bottom:1px solid rgba(255,183,0,.2);padding-bottom:4px;margin-bottom:8px}
.sem-item{display:flex;align-items:center;gap:8px;padding:4px 0;font-size:11px;
  border-bottom:1px solid var(--bd1)}
.sem-icon{width:16px;text-align:center;flex-shrink:0}
.sem-icon.ok{color:var(--green)}.sem-icon.err{color:var(--red)}.sem-icon.warn{color:var(--amber)}
.sem-text{color:var(--t2);flex:1}
.sem-loc{color:var(--t3);font-size:10px;white-space:nowrap}
.sem-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px}
.sem-stat-box{background:var(--bg3);border:1px solid var(--bd2);border-radius:4px;
  padding:10px 14px;text-align:center}
.sem-stat-num{font-family:var(--disp);font-size:22px;font-weight:900;display:block}
.sem-stat-num.cyan{color:var(--cyan);text-shadow:var(--cglow)}
.sem-stat-num.green{color:var(--green);text-shadow:var(--gglow)}
.sem-stat-num.amber{color:var(--amber);text-shadow:var(--aglow)}
.sem-stat-num.red{color:var(--red);text-shadow:var(--rglow)}
.sem-stat-label{font-family:var(--disp);font-size:7px;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--t3);margin-top:2px;display:block}

/* ================================================================ INTERMEDIATE (TAC) */
.ir-toolbar{display:flex;align-items:center;gap:6px;padding:6px 10px;background:var(--bg2);
  border-bottom:1px solid var(--bd1);flex-shrink:0;flex-wrap:wrap}
.ir-sub{font-family:var(--disp);font-size:8px;letter-spacing:1.5px;text-transform:uppercase;
  padding:5px 12px;background:transparent;border:1px solid var(--bd2);border-radius:3px;
  color:var(--t3);cursor:pointer;transition:all .15s}
.ir-sub:hover{color:var(--t1);border-color:var(--bd3);background:rgba(0,245,255,.04)}
.ir-sub.active{color:var(--cyan);border-color:var(--cyan);background:rgba(0,245,255,.08);
  box-shadow:0 0 8px rgba(0,245,255,.2)}
.ir-stats{margin-left:auto;font-family:var(--disp);font-size:8.5px;letter-spacing:1px;
  color:var(--t2);padding-right:6px}
.ir-stats b.cyan{color:var(--cyan)}.ir-stats b.green{color:var(--green)}
.ir-stats b.amber{color:var(--amber)}
.ir-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;
  flex:1;gap:8px;color:var(--t4);font-family:var(--disp);font-size:9px;
  letter-spacing:2px;text-transform:uppercase;background:var(--bg1)}
.ir-view{flex:1;background:var(--bg1);overflow:auto}
.ir-view table.dt tbody td{font-size:11px;color:var(--t1);max-width:none}
.ir-view table.dt tbody td.ir-n{color:var(--t3);text-align:right;font-family:var(--disp);font-size:9px}
.ir-view table.dt tbody td.ir-lbl{color:var(--purple);font-family:var(--disp);font-size:9.5px}
.ir-view table.dt tbody td.ir-instr{color:var(--cyan);text-shadow:0 0 6px rgba(0,245,255,.15)}
.ir-view table.dt tbody td.ir-op{color:var(--amber);text-align:center;font-family:var(--disp);font-size:10px}
.ir-view table.dt tbody td.ir-arg{color:var(--t2)}
.ir-view table.dt tbody td.ir-dest{color:var(--green)}
.ir-cmp-grid{display:grid;grid-template-columns:1fr 1fr;flex:1;overflow:hidden;border-bottom:1px solid var(--bd2)}
.ir-cmp-col{display:flex;flex-direction:column;overflow:hidden;border-right:1px solid var(--bd1)}
.ir-cmp-col:last-child{border-right:none}
.ir-cmp-hdr{display:flex;align-items:center;justify-content:space-between;
  padding:6px 12px;font-family:var(--disp);font-size:9px;letter-spacing:2px;
  text-transform:uppercase;background:var(--bg2);border-bottom:1px solid var(--bd1);flex-shrink:0}
.ir-cmp-tag{font-size:8px;color:var(--t3);background:var(--bg3);
  padding:2px 8px;border-radius:8px;border:1px solid var(--bd2)}
.ir-pre{padding:10px 14px;margin:0;font-family:var(--font);font-size:11.5px;line-height:1.55;
  color:var(--t1);white-space:pre;overflow:visible}
.ir-traza{flex-shrink:0;border-top:1px solid var(--bd2);background:var(--bg2)}
.ir-traza-hdr{padding:5px 12px;font-family:var(--disp);font-size:8px;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--purple);border-bottom:1px solid var(--bd1)}
.ir-info{padding:14px 22px;color:var(--t2);font-size:12px;line-height:1.65;max-width:880px}
.ir-info h3{font-family:var(--disp);font-size:11px;letter-spacing:2px;text-transform:uppercase;
  color:var(--cyan);text-shadow:var(--cglow);margin:18px 0 8px;
  border-bottom:1px solid rgba(0,245,255,.18);padding-bottom:5px}
.ir-info h3:first-child{margin-top:4px}
.ir-info p{margin:6px 0}
.ir-info b{color:var(--t1)}
.ir-info code{font-family:var(--font);font-size:11.5px;color:var(--amber);
  background:rgba(255,183,0,.06);padding:1px 5px;border-radius:2px}
.ir-info ul,.ir-info ol{margin:6px 0 10px 22px}
.ir-info li{margin:3px 0}
.ir-info-pre{font-family:var(--font);font-size:11px;line-height:1.55;color:var(--t1);
  background:var(--bg2);border:1px solid var(--bd1);border-radius:3px;
  padding:10px 14px;margin:6px 0 10px;white-space:pre;overflow-x:auto}

/* ================================================================ EMPTY STATE */
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:100%;gap:8px;color:var(--t4);font-family:var(--disp);font-size:9px;
  letter-spacing:2px;text-transform:uppercase}
.empty .ei{font-size:28px;opacity:.3}

/* ================================================================ BOTTOM PANEL */
#panel-bottom{grid-column:1;grid-row:2;display:flex;flex-direction:column;
  border-top:1px solid var(--bd2);overflow:hidden}

/* ================================================================ FOOTER */
footer{height:46px;background:var(--bg2);border-top:1px solid var(--bd2);
  display:flex;align-items:center;gap:8px;padding:0 16px;flex-shrink:0;
  position:relative;z-index:100;overflow:visible}
footer::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.3}
.btn{display:inline-flex;align-items:center;gap:7px;padding:6px 14px;border:1px solid;
  border-radius:3px;font-family:var(--disp);font-size:8px;font-weight:700;letter-spacing:2px;
  text-transform:uppercase;cursor:pointer;transition:all .15s;position:relative;overflow:hidden;white-space:nowrap}
.btn:active{transform:scale(.97)}
.btn-run{color:var(--cyan);border-color:var(--cyan);background:rgba(0,245,255,.05);
  box-shadow:0 0 12px rgba(0,245,255,.15),inset 0 0 12px rgba(0,245,255,.03)}
.btn-run:hover{background:rgba(0,245,255,.1);box-shadow:0 0 20px rgba(0,245,255,.3);text-shadow:0 0 8px var(--cyan)}
.btn-run.running{animation:bpulse .6s ease-in-out infinite}
@keyframes bpulse{0%,100%{box-shadow:0 0 12px rgba(0,245,255,.15)}50%{box-shadow:0 0 28px rgba(0,245,255,.5)}}
.btn-clear{color:var(--t2);border-color:var(--bd2);background:transparent}
.btn-clear:hover{color:var(--t1);border-color:var(--bd3)}
.sep{width:1px;height:20px;background:var(--bd1);margin:0 2px}

/* ================================================================ EXAMPLE PICKER — FIXED */
.ex-picker{position:relative;z-index:200}
.btn-ex{color:var(--amber);border-color:rgba(255,183,0,.3);background:rgba(255,183,0,.04)}
.btn-ex:hover{background:rgba(255,183,0,.1);box-shadow:0 0 12px rgba(255,183,0,.2)}
.ex-menu{
  display:none;
  position:fixed;            /* fixed so it escapes any overflow:hidden parent */
  width:320px;
  background:var(--bg4);
  border:1px solid var(--bd3);
  border-radius:6px;
  box-shadow:0 0 24px rgba(0,245,255,.15),0 -8px 32px rgba(0,0,0,.8);
  z-index:9000;
  overflow:hidden;
  animation:mapp .15s ease;
}
.ex-menu.open{display:block}
@keyframes mapp{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.ex-menu-hdr{padding:8px 14px 6px;font-family:var(--disp);font-size:7.5px;letter-spacing:2px;
  text-transform:uppercase;color:var(--cyan);border-bottom:1px solid var(--bd1);opacity:.8}
.ex-item{display:flex;align-items:center;gap:12px;width:100%;padding:9px 14px;
  background:none;border:none;border-bottom:1px solid var(--bd1);cursor:pointer;
  text-align:left;transition:background .1s;color:var(--t1)}
.ex-item:last-child{border-bottom:none}
.ex-item:hover{background:rgba(0,245,255,.08)}
.ex-item:hover .ex-n{color:var(--cyan);text-shadow:0 0 8px var(--cyan)}
.ex-n{font-family:var(--disp);font-size:11px;font-weight:700;color:var(--t3);min-width:22px;transition:all .1s}
.ex-inf{display:flex;flex-direction:column;gap:1px}
.ex-inf b{font-family:var(--font);font-size:11px;font-weight:normal;color:var(--t1)}
.ex-inf small{font-size:9px;color:var(--t3)}

/* ================================================================ FOOTER INFO */
.ft-info{margin-left:auto;display:flex;gap:16px;font-size:10px;color:var(--t3)}
.ft-info span b{color:var(--t2)}

/* ================================================================ PROGRESS */
#prog{position:fixed;top:0;left:0;height:2px;width:0%;
  background:linear-gradient(90deg,var(--cyan),var(--green));
  box-shadow:0 0 8px var(--cyan);z-index:10000;transition:width .3s ease}

/* ================================================================ HIGHLIGHT COLORS */
.hk{color:#bf5af2}.ht{color:#5ac8fa}.hn{color:#ff9f0a}.hs{color:#30d158}
.hc{color:#3a5a6a;font-style:italic}.hb{color:#ff6b6b}.ho{color:#0a84ff}

/* ================================================================ SCROLL */
::-webkit-scrollbar{width:4px;height:4px}
::-webkit-scrollbar-track{background:var(--bg1)}
::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:2px}

/* ================================================================ ANIMATIONS */
header{animation:fdown .4s ease .1s both}
main{animation:fin .4s ease .2s both}
footer{animation:fup .4s ease .3s both}
@keyframes fdown{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
@keyframes fup{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@keyframes fin{from{opacity:0}to{opacity:1}}
</style>
</head>
<body>

<div id="prog"></div>

<!-- Circuit bg -->
<svg class="cbg" viewBox="0 0 1400 900" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
  <g stroke="#00f5ff" stroke-width=".5" fill="none">
    <line x1="0" y1="80" x2="200" y2="80"/><circle cx="200" cy="80" r="3" fill="#00f5ff"/>
    <line x1="200" y1="80" x2="200" y2="160"/><line x1="200" y1="160" x2="500" y2="160"/>
    <circle cx="500" cy="160" r="3" fill="#00f5ff"/>
    <line x1="500" y1="160" x2="500" y2="80"/><line x1="500" y1="80" x2="900" y2="80"/>
    <circle cx="900" cy="80" r="3" fill="#00f5ff"/>
    <line x1="900" y1="80" x2="900" y2="220"/><line x1="900" y1="220" x2="1400" y2="220"/>
    <line x1="0" y1="320" x2="300" y2="320"/><circle cx="300" cy="320" r="3" fill="#00f5ff"/>
    <line x1="300" y1="320" x2="300" y2="420"/><line x1="300" y1="420" x2="700" y2="420"/>
    <circle cx="700" cy="420" r="5" fill="none" stroke="#00f5ff" stroke-width="1"/>
    <circle cx="700" cy="420" r="2" fill="#00f5ff"/>
    <line x1="700" y1="420" x2="1100" y2="420"/><line x1="1100" y1="420" x2="1100" y2="320"/>
    <line x1="1100" y1="320" x2="1400" y2="320"/>
    <line x1="0" y1="560" x2="400" y2="560"/><circle cx="400" cy="560" r="3" fill="#00f5ff"/>
    <line x1="400" y1="560" x2="400" y2="640"/><line x1="400" y1="640" x2="800" y2="640"/>
    <line x1="800" y1="640" x2="800" y2="560"/><line x1="800" y1="560" x2="1400" y2="560"/>
    <line x1="150" y1="0" x2="150" y2="900"/><line x1="1050" y1="0" x2="1050" y2="900"/>
    <rect x="320" y="180" width="60" height="40" rx="2"/>
    <rect x="730" y="460" width="80" height="50" rx="2"/>
    <circle cx="150" cy="160" r="4" fill="none"/><circle cx="150" cy="160" r="1.5" fill="#00f5ff"/>
    <circle cx="1050" cy="320" r="4" fill="none"/><circle cx="1050" cy="320" r="1.5" fill="#00f5ff"/>
  </g>
</svg>

<div id="app">

  <!-- BANNER -->
  <div id="banner">
    <div class="bn-left">
      <span class="bn-label">Proyecto Final</span>
      <span class="bn-title">Compiladores</span>
    </div>
    <div class="bn-center">
      <?php foreach($integrantes as $i): ?>
      <span class="bn-author"><?php echo htmlspecialchars($i); ?></span>
      <?php endforeach; ?>
    </div>
    <div class="bn-right">
      <span class="bn-uni">Facultad de Ingeniería en Sistemas<br>Universidad Mariano Gálvez de Guatemala · Jocotenango</span>
      <span class="bn-course">Compiladores · 120262294035A</span>
      <span class="bn-teacher">Ing. Manuel Alberto Herrera Estrada</span>
    </div>
  </div>

  <!-- HEADER -->
  <header>
    <div class="logo">
      <div class="logo-icon"></div>
      <div>
        <span class="logo-text">MiniCompiler</span>
        <span class="logo-sub">Lexer · Parser · Semantic Analyzer v2.0</span>
      </div>
    </div>
    <div class="hdiv"></div>
    <div class="htags">
      <span class="tag tag-c">Léxico</span>
      <span class="tag tag-g">Sintáctico</span>
      <span class="tag tag-p">Semántico</span>
    </div>
    <div class="hstatus">
      <div class="sdot"></div>
      <span id="hdr-status">Sistema listo</span>
    </div>
  </header>

  <!-- MAIN -->
  <main>

    <!-- LEFT COLUMN -->
    <div style="display:flex;flex-direction:column;overflow:hidden;grid-column:1;grid-row:1/3;">

      <!-- TAB BAR -->
      <div class="tab-bar">
        <button class="tab-btn active" onclick="switchTab('editor')" id="tab-editor">✎ Editor</button>
        <button class="tab-btn" onclick="switchTab('tokens')" id="tab-tokens">◆ Tokens <span class="tab-badge" id="badge-tokens">0</span></button>
        <button class="tab-btn" onclick="switchTab('tree')" id="tab-tree">⬡ Árbol Sint. <span class="tab-badge" id="badge-tree">!</span></button>
        <button class="tab-btn" onclick="switchTab('semantic')" id="tab-semantic">⚑ Semántico <span class="tab-badge" id="badge-sem">!</span></button>
        <button class="tab-btn" onclick="switchTab('intermediate')" id="tab-intermediate">▦ Intermedio <span class="tab-badge" id="badge-ir">0</span></button>
        <button class="tab-btn" onclick="switchTab('errors')" id="tab-errors">⚠ Errores <span class="tab-badge" id="badge-errors">0</span></button>
      </div>

      <!-- TAB: EDITOR -->
      <div class="tab-content active" id="view-editor" style="flex:1;overflow:hidden;">
        <div class="panel" id="panel-editor" style="flex:1;border-right:none;border-bottom:none;">
          <div class="ph">
            <span class="ph-title">● Código Fuente</span>
            <span class="ph-count" id="editor-info">0 líneas · 0 chars</span>
          </div>
          <div class="ed-wrap">
            <div id="lnum"><div id="lnum-inner">1</div></div>
            <div class="ed-core">
              <div id="code-hl" aria-hidden="true"></div>
              <textarea id="code-ed" spellcheck="false" autocomplete="off" autocorrect="off" autocapitalize="off"
                placeholder="// Escribe tu código MiniLang aquí&#10;// Presiona F5 o el botón ANALIZAR&#10;&#10;int x = 10;"></textarea>
            </div>
          </div>
          <div class="ed-status">
            <span>Línea <b id="cur-ln">1</b>, Col <b id="cur-col">1</b></span>
            <span>Tokens: <b id="sb-tok">—</b></span>
            <span>Símbolos: <b id="sb-sym">—</b></span>
            <span style="margin-left:auto">MiniLang 1.0 · UTF-8</span>
          </div>
        </div>
      </div>

      <!-- TAB: TOKENS -->
      <div class="tab-content" id="view-tokens" style="flex:1;overflow:hidden;">
        <div class="panel" style="flex:1;border-right:none;border-bottom:none;">
          <div class="ph">
            <span class="ph-title">◆ Tabla de Tokens</span>
            <span class="ph-count" id="tok-count">0 tokens</span>
          </div>
          <div class="tscroll">
            <div class="empty" id="tok-empty"><span class="ei">◆</span><span>Sin análisis</span></div>
            <table class="dt" id="tok-table" style="display:none">
              <thead><tr><th style="width:120px">Tipo</th><th style="width:130px">Valor</th><th style="width:50px">Ln</th><th>Col</th></tr></thead>
              <tbody id="tok-body"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB: ÁRBOL SINTÁCTICO -->
      <div class="tab-content" id="view-tree" style="flex:1;overflow:hidden;">
        <div class="panel" style="flex:1;border-right:none;border-bottom:none;display:flex;flex-direction:column;">
          <div class="ph purple">
            <span class="ph-title purple">⬡ Árbol Sintáctico Visual</span>
            <span class="ph-count" id="tree-count">—</span>
          </div>
          <div id="tree-toolbar">
            <button class="ttbtn" onclick="treeExpandAll()">Expandir todo</button>
            <button class="ttbtn" onclick="treeCollapseAll()">Colapsar todo</button>
            <button class="ttbtn" onclick="treeZoomReset()">Zoom reset</button>
            <span style="margin-left:auto;font-size:10px;color:var(--t3);font-family:var(--font)">Clic en nodo para expandir/colapsar</span>
          </div>
          <div id="tree-panel" style="flex:1">
            <div class="tree-empty" id="tree-empty" style="height:100%"><span style="font-size:32px;opacity:.2">⬡</span><span>Sin análisis — presiona F5</span></div>
            <div id="tree-canvas-wrap" style="display:none">
              <svg id="tree-svg"></svg>
            </div>
          </div>
          <div id="tree-legend" style="display:none">
            <div class="tlegitem"><div class="tlegdot" style="background:#7b2ff7"></div>Programa / Bloque</div>
            <div class="tlegitem"><div class="tlegdot" style="background:#0e7dd6"></div>Declaración</div>
            <div class="tlegitem"><div class="tlegdot" style="background:#0a7d6b"></div>Asignación</div>
            <div class="tlegitem"><div class="tlegdot" style="background:#8b5e00"></div>Control (if/while/for)</div>
            <div class="tlegitem"><div class="tlegdot" style="background:#8b1a1a"></div>Función / Llamada</div>
            <div class="tlegitem"><div class="tlegdot" style="background:#1a5c1a"></div>Expresión / Op</div>
            <div class="tlegitem"><div class="tlegdot" style="background:#2a2a5a"></div>Literal / ID</div>
          </div>
        </div>
      </div>

      <!-- TAB: SEMÁNTICO -->
      <div class="tab-content" id="view-semantic" style="flex:1;overflow:hidden;">
        <div class="panel" style="flex:1;border-right:none;border-bottom:none;">
          <div class="ph amber">
            <span class="ph-title amber">⚑ Análisis Semántico</span>
            <span class="ph-count" id="sem-count">—</span>
          </div>
          <div id="sem-panel">
            <div class="tree-empty" id="sem-empty"><span style="font-size:28px;opacity:.3">⚑</span><span>Sin análisis</span></div>
            <div id="sem-content" style="display:none"></div>
          </div>
        </div>
      </div>

      <!-- TAB: CÓDIGO INTERMEDIO (TAC) -->
      <div class="tab-content" id="view-intermediate" style="flex:1;overflow:hidden;">
        <div class="panel" style="flex:1;border-right:none;border-bottom:none;display:flex;flex-direction:column;">
          <div class="ph">
            <span class="ph-title">▦ Código Intermedio · TAC (3 direcciones)</span>
            <span class="ph-count" id="ir-count">—</span>
          </div>

          <!-- Sub-toolbar -->
          <div class="ir-toolbar">
            <button class="ir-sub active" data-sub="orig" onclick="switchIRSub('orig')">Sin optimizar</button>
            <button class="ir-sub" data-sub="opt"  onclick="switchIRSub('opt')">Optimizado</button>
            <button class="ir-sub" data-sub="cmp"  onclick="switchIRSub('cmp')">Comparación</button>
            <button class="ir-sub" data-sub="info" onclick="switchIRSub('info')">Info</button>
            <span class="ir-stats" id="ir-stats"></span>
          </div>

          <!-- Empty state -->
          <div class="ir-empty" id="ir-empty">
            <span style="font-size:32px;opacity:.2">▦</span>
            <span>Sin análisis — presiona F5</span>
            <span style="font-size:9px;color:var(--t3);margin-top:4px">El TAC requiere el backend Python (PHP + bridge.py)</span>
          </div>

          <!-- Sub-vista: ORIGINAL -->
          <div class="ir-view tscroll" id="ir-view-orig" style="display:none">
            <table class="dt" id="ir-table-orig">
              <thead><tr><th style="width:36px">#</th><th style="width:72px">Etiqueta</th><th>Instrucción</th><th style="width:64px">Op</th><th style="width:80px">Arg1</th><th style="width:80px">Arg2</th><th style="width:80px">Dest</th></tr></thead>
              <tbody id="ir-body-orig"></tbody>
            </table>
          </div>

          <!-- Sub-vista: OPTIMIZADO -->
          <div class="ir-view tscroll" id="ir-view-opt" style="display:none">
            <table class="dt" id="ir-table-opt">
              <thead><tr><th style="width:36px">#</th><th style="width:72px">Etiqueta</th><th>Instrucción</th><th style="width:64px">Op</th><th style="width:80px">Arg1</th><th style="width:80px">Arg2</th><th style="width:80px">Dest</th></tr></thead>
              <tbody id="ir-body-opt"></tbody>
            </table>
          </div>

          <!-- Sub-vista: COMPARACIÓN -->
          <div class="ir-view" id="ir-view-cmp" style="display:none;flex-direction:column;overflow:hidden;flex:1;">
            <div class="ir-cmp-grid">
              <div class="ir-cmp-col">
                <div class="ir-cmp-hdr"><span style="color:var(--cyan)">Sin optimizar</span> <span id="ir-cmp-orig-n" class="ir-cmp-tag">0</span></div>
                <div class="tscroll" style="flex:1">
                  <pre class="ir-pre" id="ir-pre-orig"></pre>
                </div>
              </div>
              <div class="ir-cmp-col">
                <div class="ir-cmp-hdr"><span style="color:var(--green)">Optimizado</span> <span id="ir-cmp-opt-n" class="ir-cmp-tag">0</span></div>
                <div class="tscroll" style="flex:1">
                  <pre class="ir-pre" id="ir-pre-opt"></pre>
                </div>
              </div>
            </div>
            <div class="ir-traza">
              <div class="ir-traza-hdr">Traza del optimizador (pasadas hasta punto fijo)</div>
              <div class="tscroll" style="max-height:120px">
                <table class="dt" style="font-size:10px">
                  <thead><tr><th style="width:50px">Iter</th><th>Pasada</th><th style="width:60px">Antes</th><th style="width:60px">Después</th><th style="width:60px">Δ</th></tr></thead>
                  <tbody id="ir-traza-body"></tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Sub-vista: INFO -->
          <div class="ir-view tscroll" id="ir-view-info" style="display:none">
            <div class="ir-info">
<h3>CÓDIGO INTERMEDIO  =  FRONTERA FRONT-END / BACK-END</h3>
<p>El código intermedio es la <b>frontera</b> entre el FRONT-END y el BACK-END
de un compilador. <b>No es solo "una etapa más"</b>: es el <b>contrato</b> que
permite separar el lenguaje fuente de la máquina destino.</p>
<pre class="ir-info-pre">
  FRONT-END  ───►  CÓDIGO INTERMEDIO  ───►  BACK-END
  (lenguaje              (TAC)              (máquina
   fuente)                                   objetivo)
</pre>
<p>Si cambia el lenguaje fuente solo se rehace el front-end.<br>
Si cambia la arquitectura objetivo solo se rehace el back-end.<br>
El IR (representación intermedia) es el único punto que ambos lados conocen.</p>

<h3>Estructura de este proyecto</h3>
<pre class="ir-info-pre">
  frontend/                   ← depende del lenguaje fuente
     lexer.py                  análisis léxico
     tabla_simbolos.py         tabla de símbolos
     parser.py                 AST (análisis sintáctico)
     generador_intermedio.py   emite el TAC

  intermedio.py               ← contrato compartido
     Quad                      cuádruplo (op, arg1, arg2, dest)
     formatear_tac             pretty-printer

  backend/                    ← depende de la máquina objetivo
     optimizador.py            optimiza el TAC
     (futuro) generador_objeto.py  emite ensamblador
</pre>

<h3>Tipos de código intermedio</h3>
<ul>
  <li>Notación postfija &nbsp;&nbsp;&nbsp; <code>a b +</code></li>
  <li><b>Three-Address Code (TAC)</b> &nbsp;&nbsp;&nbsp; <code>t1 = a + b</code> &nbsp;&nbsp;◄── usamos este</li>
  <li>Cuádruplos / Triples</li>
  <li>SSA (Static Single Assignment)</li>
  <li>DAG (detecta subexpresiones comunes)</li>
</ul>

<h3>Cuál usa este compilador</h3>
<p><b>Three-Address Code (TAC)</b> en formato de <b>cuádruplos</b>:
<code>( op , arg1 , arg2 , dest )</code></p>
<pre class="ir-info-pre">
  a = 5             →  ( = , 5  , _ , a   )
  $t1 = b + c       →  ( + , b  , c , $t1 )
  if $t1 goto $L2   →  ( if_false , $t1 , _ , $L2 )
  goto $L3          →  ( goto , _ , _ , $L3 )
  $L2:              →  ( label , _ , _ , $L2 )
  print x           →  ( print , x , _ , _  )
</pre>
<p>Los temporales y etiquetas usan prefijo <code>$</code> que el lexer no acepta
como identificador, así nunca chocan con variables del usuario llamadas
<code>t1</code> o <code>L1</code>.</p>

<h3>Optimizaciones (back-end)</h3>
<p>El optimizador ejecuta varias pasadas hasta <b>punto fijo</b>:</p>
<ol>
  <li><b>Constant Folding</b> &nbsp; <code>3 + 4 → 7</code></li>
  <li><b>Algebraic Simplification</b> &nbsp; <code>x * 1 → x</code> · <code>x + 0 → x</code></li>
  <li><b>Constant Propagation</b> &nbsp; <code>x = 5; t = x + 1 → t = 5 + 1</code></li>
  <li><b>Copy Propagation</b> &nbsp; <code>a = b; c = a + 1 → c = b + 1</code></li>
  <li><b>Dead-Code Elimination</b> &nbsp; elimina temporales nunca leídos</li>
  <li><b>Branch Pruning</b> &nbsp; <code>ifFalse true → elimina el salto</code></li>
  <li><b>Jump Threading</b> &nbsp; <code>goto L; L: → elimina el goto</code></li>
</ol>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: ERRORS -->
      <div class="tab-content" id="view-errors" style="flex:1;overflow:hidden;">
        <div class="panel" style="flex:1;border-right:none;border-bottom:none;">
          <div class="ph red">
            <span class="ph-title red">⚠ Consola de Errores</span>
            <span class="ph-count" id="err-count">—</span>
          </div>
          <div id="console"></div>
        </div>
      </div>

    </div><!-- /left column -->

    <!-- RIGHT SIDE: Symbols -->
    <div id="side">
      <div class="ph green" style="flex-shrink:0">
        <span class="ph-title green">◆ Tabla de Símbolos</span>
        <span class="ph-count" id="sym-count">0 símbolos</span>
      </div>
      <div class="tscroll" style="flex:1">
        <div class="empty" id="sym-empty"><span class="ei">◆</span><span>Sin análisis</span></div>
        <table class="dt" id="sym-table" style="display:none">
          <thead><tr><th style="width:100px">Nombre</th><th style="width:68px">Tipo</th><th style="width:38px">Ln</th><th>Valor</th></tr></thead>
          <tbody id="sym-body"></tbody>
        </table>
      </div>

      <!-- Mini stats in side panel -->
      <div style="border-top:1px solid var(--bd2);padding:10px 14px;flex-shrink:0;background:var(--bg2)">
        <div style="font-family:var(--disp);font-size:7px;letter-spacing:2px;text-transform:uppercase;color:var(--t3);margin-bottom:8px">Resumen</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
          <div style="background:var(--bg3);border:1px solid var(--bd2);border-radius:3px;padding:8px;text-align:center">
            <span id="stat-tokens" style="font-family:var(--disp);font-size:20px;font-weight:900;color:var(--cyan);text-shadow:var(--cglow);display:block">0</span>
            <span style="font-family:var(--disp);font-size:7px;letter-spacing:1px;text-transform:uppercase;color:var(--t3)">Tokens</span>
          </div>
          <div style="background:var(--bg3);border:1px solid var(--bd2);border-radius:3px;padding:8px;text-align:center">
            <span id="stat-syms" style="font-family:var(--disp);font-size:20px;font-weight:900;color:var(--green);text-shadow:var(--gglow);display:block">0</span>
            <span style="font-family:var(--disp);font-size:7px;letter-spacing:1px;text-transform:uppercase;color:var(--t3)">Símbolos</span>
          </div>
          <div style="background:var(--bg3);border:1px solid var(--bd2);border-radius:3px;padding:8px;text-align:center">
            <span id="stat-lines" style="font-family:var(--disp);font-size:20px;font-weight:900;color:var(--amber);text-shadow:var(--aglow);display:block">0</span>
            <span style="font-family:var(--disp);font-size:7px;letter-spacing:1px;text-transform:uppercase;color:var(--t3)">Líneas</span>
          </div>
          <div style="background:var(--bg3);border:1px solid var(--bd2);border-radius:3px;padding:8px;text-align:center">
            <span id="stat-errs" style="font-family:var(--disp);font-size:20px;font-weight:900;color:var(--red);text-shadow:var(--rglow);display:block">0</span>
            <span style="font-family:var(--disp);font-size:7px;letter-spacing:1px;text-transform:uppercase;color:var(--t3)">Errores</span>
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- FOOTER -->
  <footer>
    <button class="btn btn-run" id="btn-run" onclick="runAnalysis()">
      <span>▶</span> Analizar <span style="opacity:.5;font-size:7px">[F5]</span>
    </button>
    <div class="sep"></div>
    <button class="btn btn-clear" onclick="clearAll()"><span>⌫</span> Limpiar</button>

    <!-- EXAMPLE PICKER — uses position:fixed for the menu -->
    <div class="ex-picker" id="ex-picker">
      <button class="btn btn-ex" id="btn-ex" onclick="toggleExMenu(event)">
        <span>📄</span> Ejemplos <span id="ex-arrow" style="font-size:9px;margin-left:2px;transition:transform .2s;display:inline-block">▾</span>
      </button>
      <div class="ex-menu" id="ex-menu">
        <div class="ex-menu-hdr">Seleccionar ejemplo</div>
        <button class="ex-item" onclick="loadEx(0)"><span class="ex-n">01</span><span class="ex-inf"><b>Variables y Tipos</b><small>Declaraciones, asignaciones, operadores</small></span></button>
        <button class="ex-item" onclick="loadEx(1)"><span class="ex-n">02</span><span class="ex-inf"><b>Control de Flujo</b><small>if / else anidados, lógica booleana</small></span></button>
        <button class="ex-item" onclick="loadEx(2)"><span class="ex-n">03</span><span class="ex-inf"><b>Bucles while y for</b><small>Iteraciones y acumuladores</small></span></button>
        <button class="ex-item" onclick="loadEx(3)"><span class="ex-n">04</span><span class="ex-inf"><b>Expresiones Complejas</b><small>Todos los operadores mezclados</small></span></button>
        <button class="ex-item" onclick="loadEx(4)"><span class="ex-n">05</span><span class="ex-inf"><b>Errores Léxicos</b><small>Caracteres ilegales y duplicados</small></span></button>
        <button class="ex-item" onclick="loadEx(5)"><span class="ex-n">06</span><span class="ex-inf"><b>Strings y Booleanos</b><small>Cadenas con escapes, tablas de verdad</small></span></button>
        <button class="ex-item" onclick="loadEx(6)"><span class="ex-n">07</span><span class="ex-inf"><b>Programa Completo</b><small>Integración de todas las estructuras</small></span></button>
      </div>
    </div>

    <div class="ft-info">
      <span>Tokens: <b id="ft-tok">0</b></span>
      <span>Símbolos: <b id="ft-sym">0</b></span>
      <span>Errores: <b id="ft-err">0</b></span>
    </div>
  </footer>

</div><!-- /#app -->

<script>
/* ================================================================
   LEXER ENGINE
================================================================ */
const RESERVED = {int:'INT',float:'FLOAT',string:'STRING',boolean:'BOOLEAN',
  if:'IF',else:'ELSE',while:'WHILE',for:'FOR',return:'RETURN',
  true:'TRUE',false:'FALSE',print:'PRINT',input:'INPUT',
  and:'AND',or:'OR',not:'NOT',null:'NULL'};
const RESERVED_INV = Object.fromEntries(Object.entries(RESERVED).map(([k,v])=>[v,k]));
const TIPOS_DATO = new Set(['INT','FLOAT','STRING','BOOLEAN']);

const SPEC = [
  ['COMENTARIO', /\/\/[^\n]*/y],
  ['DECIMAL',    /\d+\.\d+/y,  v=>parseFloat(v)],
  ['ENTERO',     /\d+/y,       v=>parseInt(v)],
  ['CADENA',     /"(?:[^"\\]|\\.)*"/y],
  ['ID',         /[a-zA-Z_][a-zA-Z_0-9]*/y],
  ['IGUAL',      /==/y], ['DIFERENTE', /!=/y],
  ['MENOR_IGUAL',/<=/y], ['MAYOR_IGUAL',/>=/y],
  ['Y_LOGICO',   /&&/y], ['O_LOGICO',  /\|\|/y],
  ['MAS',/\+/y],['MENOS',/-/y],['MULT',/\*/y],['DIV',/\//y],['MOD',/%/y],
  ['NO_LOGICO',/!/y],['MENOR',/</y],['MAYOR',/>/y],['ASIGNACION',/=/y],
  ['PUNTO_COMA',/;/y],['COMA',/,/y],
  ['PAREN_IZQ',/\(/y],['PAREN_DER',/\)/y],
  ['LLAVE_IZQ',/\{/y],['LLAVE_DER',/\}/y],
  ['NUEVA_LINEA',/\n/y],['ESPACIO',/[ \t\r]+/y],
];
const IGNORE = new Set(['NUEVA_LINEA','ESPACIO','COMENTARIO']);

function runLexer(code) {
  const tokens=[], errores=[], simbolos={};
  let linea=1, inicioLinea=0, ultimoTipo=null, proximoEsId=false;
  const consumed = new Uint8Array(code.length);
  for(const [,re] of SPEC) re.lastIndex=0;
  let pos=0;
  while(pos<code.length){
    let matched=false;
    for(const [nombre,re,conv] of SPEC){
      re.lastIndex=pos;
      const m=re.exec(code);
      if(m && m.index===pos){
        const val=m[0];
        for(let i=pos;i<pos+val.length;i++) consumed[i]=1;
        if(nombre==='NUEVA_LINEA'){linea++;inicioLinea=pos+val.length;pos+=val.length;matched=true;break;}
        if(IGNORE.has(nombre)){pos+=val.length;matched=true;break;}
        const col=pos-inicioLinea+1;
        let tipo=nombre, valReal=val;
        if(tipo==='ID') tipo=RESERVED[val]||'ID';
        if(tipo==='CADENA') valReal=val.slice(1,-1).replace(/\\"/g,'"').replace(/\\n/g,'\n').replace(/\\t/g,'\t').replace(/\\\\/g,'\\');
        else if(conv) valReal=conv(val);
        tokens.push({tipo,valor:String(valReal),linea,columna:col});
        if(TIPOS_DATO.has(tipo)){ultimoTipo=RESERVED_INV[tipo]||tipo.toLowerCase();proximoEsId=true;}
        else if(tipo==='ID'&&proximoEsId&&ultimoTipo){
          if(simbolos[val]) errores.push(`[Línea ${linea}] Error semántico: '${val}' ya fue declarado (línea ${simbolos[val].linea}).`);
          else simbolos[val]={nombre:val,tipo:ultimoTipo,linea,valor:'—'};
          proximoEsId=false;ultimoTipo=null;
        } else {proximoEsId=false;}
        pos+=val.length;matched=true;break;
      }
    }
    if(!matched){
      const ch=code[pos];
      if(ch!=='\n'&&ch!==' '&&ch!=='\t'&&ch!=='\r'){
        const col=pos-inicioLinea+1;
        errores.push(`[Línea ${linea}, Col ${col}] Carácter ilegal: '${ch}'`);
      }
      consumed[pos]=1;pos++;
    }
  }
  return {tokens, simbolos:Object.values(simbolos), errores};
}

/* ================================================================
   SYNTAX TREE BUILDER
================================================================ */
function buildTree(tokens) {
  // Recursive descent parser — builds a display tree
  let pos = 0;
  const toks = tokens.filter(t =>
    !['NUEVA_LINEA','ESPACIO','COMENTARIO'].includes(t.tipo));

  function peek(offset=0){ return toks[pos+offset]||null; }
  function consume(){ return toks[pos++]||null; }
  function expect(tipo){ const t=peek(); if(t&&t.tipo===tipo){pos++;return t;} return null; }

  function parseProgram(){
    const stmts=[];
    while(pos<toks.length){ const s=parseStatement(); if(s) stmts.push(s); else pos++; }
    return {type:'Program', children:stmts};
  }

  function parseStatement(){
    const t=peek();
    if(!t) return null;
    if(TIPOS_DATO.has(t.tipo)) return parseDeclaration();
    if(t.tipo==='IF') return parseIf();
    if(t.tipo==='WHILE') return parseWhile();
    if(t.tipo==='FOR') return parseFor();
    if(t.tipo==='PRINT'||t.tipo==='INPUT') return parsePrint();
    if(t.tipo==='ID'){
      const next=peek(1);
      if(next&&next.tipo==='ASIGNACION') return parseAssignment();
    }
    if(t.tipo==='LLAVE_IZQ') return parseBlock();
    if(t.tipo==='PUNTO_COMA'){consume();return null;}
    // unknown token — skip
    const tok=consume();
    return {type:'Unknown', token:tok};
  }

  function parseDeclaration(){
    const typeT=consume();
    const idT=peek()&&peek().tipo==='ID'?consume():null;
    let expr=null;
    if(peek()&&peek().tipo==='ASIGNACION'){consume();expr=parseExpr();}
    expect('PUNTO_COMA');
    return {type:'Declaration',dataType:typeT,id:idT,expr};
  }

  function parseAssignment(){
    const idT=consume();
    expect('ASIGNACION');
    const expr=parseExpr();
    expect('PUNTO_COMA');
    return {type:'Assignment',id:idT,expr};
  }

  function parseIf(){
    const kw=consume();
    expect('PAREN_IZQ');
    const cond=parseExpr();
    expect('PAREN_DER');
    const body=parseBlock();
    let elseBody=null;
    if(peek()&&peek().tipo==='ELSE'){consume();elseBody=parseBlock();}
    return {type:'If',kw,cond,body,elseBody};
  }

  function parseWhile(){
    const kw=consume();
    expect('PAREN_IZQ');
    const cond=parseExpr();
    expect('PAREN_DER');
    const body=parseBlock();
    return {type:'While',kw,cond,body};
  }

  function parseFor(){
    const kw=consume();
    expect('PAREN_IZQ');
    const init=parseStatement();
    const cond=parseExpr(); expect('PUNTO_COMA');
    // update: id = expr
    const updId=peek()&&peek().tipo==='ID'?consume():null;
    let updExpr=null;
    if(peek()&&peek().tipo==='ASIGNACION'){consume();updExpr=parseExpr();}
    expect('PAREN_DER');
    const body=parseBlock();
    return {type:'For',kw,init,cond,updId,updExpr,body};
  }

  function parsePrint(){
    const kw=consume();
    expect('PAREN_IZQ');
    const arg=parseExpr();
    expect('PAREN_DER');
    expect('PUNTO_COMA');
    return {type:'Print',kw,arg};
  }

  function parseBlock(){
    if(peek()&&peek().tipo==='LLAVE_IZQ'){
      consume();
      const stmts=[];
      while(pos<toks.length&&!(peek()&&peek().tipo==='LLAVE_DER')){
        const s=parseStatement();if(s) stmts.push(s);
      }
      expect('LLAVE_DER');
      return {type:'Block',stmts};
    }
    // single statement block
    const s=parseStatement();
    return {type:'Block',stmts:s?[s]:[]};
  }

  function parseExpr(){
    return parseLogicalOr();
  }
  function parseLogicalOr(){
    let left=parseLogicalAnd();
    while(peek()&&peek().tipo==='O_LOGICO'){
      const op=consume(); const right=parseLogicalAnd();
      left={type:'BinaryOp',op,left,right};
    }
    return left;
  }
  function parseLogicalAnd(){
    let left=parseEquality();
    while(peek()&&peek().tipo==='Y_LOGICO'){
      const op=consume(); const right=parseEquality();
      left={type:'BinaryOp',op,left,right};
    }
    return left;
  }
  function parseEquality(){
    let left=parseRelational();
    while(peek()&&(peek().tipo==='IGUAL'||peek().tipo==='DIFERENTE')){
      const op=consume(); const right=parseRelational();
      left={type:'BinaryOp',op,left,right};
    }
    return left;
  }
  function parseRelational(){
    let left=parseAddSub();
    while(peek()&&['MENOR','MAYOR','MENOR_IGUAL','MAYOR_IGUAL'].includes(peek().tipo)){
      const op=consume(); const right=parseAddSub();
      left={type:'BinaryOp',op,left,right};
    }
    return left;
  }
  function parseAddSub(){
    let left=parseMulDiv();
    while(peek()&&(peek().tipo==='MAS'||peek().tipo==='MENOS')){
      const op=consume(); const right=parseMulDiv();
      left={type:'BinaryOp',op,left,right};
    }
    return left;
  }
  function parseMulDiv(){
    let left=parseUnary();
    while(peek()&&['MULT','DIV','MOD'].includes(peek().tipo)){
      const op=consume(); const right=parseUnary();
      left={type:'BinaryOp',op,left,right};
    }
    return left;
  }
  function parseUnary(){
    if(peek()&&(peek().tipo==='NO_LOGICO'||peek().tipo==='MENOS')){
      const op=consume(); const operand=parseUnary();
      return {type:'UnaryOp',op,operand};
    }
    return parsePrimary();
  }
  function parsePrimary(){
    const t=peek();
    if(!t) return null;
    if(t.tipo==='PAREN_IZQ'){
      consume();const e=parseExpr();expect('PAREN_DER');
      return {type:'Group',expr:e};
    }
    if(t.tipo==='ENTERO'||t.tipo==='DECIMAL') return {type:'Literal',token:consume()};
    if(t.tipo==='CADENA') return {type:'StringLit',token:consume()};
    if(t.tipo==='TRUE'||t.tipo==='FALSE'||t.tipo==='NULL') return {type:'BoolLit',token:consume()};
    if(t.tipo==='ID'){
      const id=consume();
      if(peek()&&peek().tipo==='PAREN_IZQ'){
        consume();
        const args=[];
        while(peek()&&peek().tipo!=='PAREN_DER'){
          args.push(parseExpr());
          if(peek()&&peek().tipo==='COMA') consume();
        }
        expect('PAREN_DER');
        return {type:'Call',id,args};
      }
      return {type:'Identifier',token:id};
    }
    if(TIPOS_DATO.has(t.tipo)||['IF','ELSE','WHILE','FOR','RETURN','PRINT','INPUT','AND','OR','NOT'].includes(t.tipo)){
      return {type:'Keyword',token:consume()};
    }
    return {type:'Token',token:consume()};
  }

  return parseProgram();
}

/* ================================================================
   TREE RENDERER — VISUAL SVG CANVAS
================================================================ */

// ── Node palette ──────────────────────────────────────────────────
const NODE_STYLE = {
  Program:     {fill:'#3b1a7a',stroke:'#7b2ff7',icon:'⬡'},
  Block:       {fill:'#2a1060',stroke:'#6b1fe6',icon:'{ }'},
  Declaration: {fill:'#0a3d6b',stroke:'#0e7dd6',icon:'≡'},
  Assignment:  {fill:'#0a3d2a',stroke:'#0a7d6b',icon:'←'},
  If:          {fill:'#4a3000',stroke:'#c07a00',icon:'?'},
  While:       {fill:'#3d2800',stroke:'#a06000',icon:'↻'},
  For:         {fill:'#3a2200',stroke:'#8b5e00',icon:'⟳'},
  Print:       {fill:'#4a0a0a',stroke:'#cc2222',icon:'▶'},
  Call:        {fill:'#4a0a0a',stroke:'#cc2222',icon:'()'},
  BinaryOp:    {fill:'#0a2a0a',stroke:'#1a7a1a',icon:'±'},
  UnaryOp:     {fill:'#0a2a14',stroke:'#1a7a3a',icon:'!'},
  Group:       {fill:'#0a2a3a',stroke:'#1a6a8a',icon:'( )'},
  Literal:     {fill:'#1a1a3a',stroke:'#4a4aaa',icon:'#'},
  StringLit:   {fill:'#0a1a0a',stroke:'#2a6a2a',icon:'"'},
  BoolLit:     {fill:'#1a1a3a',stroke:'#6a4aaa',icon:'!'},
  Identifier:  {fill:'#1a2a2a',stroke:'#3a6a6a',icon:'$'},
  Token:       {fill:'#1a1a2a',stroke:'#3a3a6a',icon:'T'},
  Keyword:     {fill:'#2a1a0a',stroke:'#6a4a1a',icon:'KW'},
  Unknown:     {fill:'#2a0a0a',stroke:'#6a1a1a',icon:'?'},
};
const DEFAULT_STYLE = {fill:'#1a1a2a',stroke:'#3a3a6a',icon:'·'};

// ── Layout constants ───────────────────────────────────────────────
const NW = 130;  // node width
const NH = 40;   // node height
const HGAP = 24; // horizontal gap between siblings
const VGAP = 56; // vertical gap between levels

// ── Global tree state ─────────────────────────────────────────────
let _treeData = null;      // {node, layout} root
let _collapsed = new Set(); // set of node ids that are collapsed

// ── Assign unique IDs to all nodes ────────────────────────────────
let _nodeCounter = 0;
function assignIds(node) {
  if (!node) return;
  node._id = ++_nodeCounter;
  const kids = getKids(node);
  kids.forEach(assignIds);
}

function getKids(node) {
  if (!node) return [];
  switch(node.type) {
    case 'Program':    return (node.children||[]).filter(Boolean);
    case 'Block':      return (node.stmts||[]).filter(Boolean);
    case 'Declaration':{
      const c=[];
      if(node.dataType) c.push({type:'Token',token:node.dataType,label:'Tipo',_label:'Tipo'});
      if(node.id)       c.push({type:'Token',token:node.id,label:'ID',_label:'ID'});
      if(node.expr)     c.push({...node.expr,_label:'valor'});
      return c;}
    case 'Assignment': {
      const c=[];
      if(node.id)   c.push({type:'Identifier',token:node.id,_label:'var'});
      if(node.expr) c.push({...node.expr,_label:'expr'});
      return c;}
    case 'If': {
      const c=[];
      if(node.cond)     c.push({...node.cond,_label:'cond'});
      if(node.body)     c.push({...node.body,_label:'then'});
      if(node.elseBody) c.push({...node.elseBody,_label:'else'});
      return c;}
    case 'While': {
      const c=[];
      if(node.cond) c.push({...node.cond,_label:'cond'});
      if(node.body) c.push(node.body);
      return c;}
    case 'For': {
      const c=[];
      if(node.init)  c.push({...node.init,_label:'init'});
      if(node.cond)  c.push({...node.cond,_label:'cond'});
      if(node.updId) c.push({type:'Identifier',token:node.updId,_label:'upd'});
      if(node.body)  c.push(node.body);
      return c;}
    case 'Print':    return node.arg ? [{...node.arg,_label:'arg'}] : [];
    case 'Call':     return (node.args||[]).filter(Boolean);
    case 'BinaryOp': {
      const c=[];
      if(node.left)  c.push({...node.left,_label:'izq'});
      if(node.right) c.push({...node.right,_label:'der'});
      return c;}
    case 'UnaryOp':  return node.operand ? [node.operand] : [];
    case 'Group':    return node.expr ? [node.expr] : [];
    default: return [];
  }
}

// ── Node label ────────────────────────────────────────────────────
function nodeLabel(node) {
  switch(node.type) {
    case 'Program':    return 'PROGRAMA';
    case 'Block':      return 'BLOQUE';
    case 'Declaration':return `DECL ${node.dataType?node.dataType.valor:''} ${node.id?node.id.valor:''}`.trim();
    case 'Assignment': return `ASIG ${node.id?node.id.valor:''}`.trim();
    case 'If':         return 'IF';
    case 'While':      return 'WHILE';
    case 'For':        return 'FOR';
    case 'Print':      return `PRINT`;
    case 'Call':       return `${node.id?node.id.valor:'CALL'}()`;
    case 'BinaryOp':   return `OP  ${node.op?node.op.valor:'?'}`;
    case 'UnaryOp':    return `!`;
    case 'Group':      return '( expr )';
    case 'Literal':    return `${node.token?node.token.valor:''}`;
    case 'StringLit':  return `"${node.token?node.token.valor.slice(0,12):''}${node.token&&node.token.valor.length>12?'…':''}"`;
    case 'BoolLit':    return `${node.token?node.token.valor:''}`;
    case 'Identifier': return `${node.token?node.token.valor:'ID'}`;
    case 'Token':      return `${node.token?node.token.valor:''}`;
    case 'Keyword':    return `${node.token?node.token.valor:''}`;
    default:           return node.type||'?';
  }
}

function nodeSubLabel(node) {
  if (node._label) return node._label;
  return '';
}

// ── Recursive Reingold-Tilford layout ─────────────────────────────
function layoutTree(node, depth=0) {
  const collapsed = _collapsed.has(node._id);
  const kids = collapsed ? [] : getKids(node);
  kids.forEach(assignIds); // ensure IDs on dynamic sub-nodes

  if (kids.length === 0) {
    return { node, x: 0, y: depth*(NH+VGAP), w: NW, children: [], depth, collapsed };
  }

  const childLayouts = kids.map(k => layoutTree(k, depth+1));

  // Space children evenly
  let cx = 0;
  childLayouts.forEach((cl, i) => {
    const subtreeW = getSubtreeWidth(cl);
    shiftTree(cl, cx);
    cx += subtreeW + HGAP;
  });
  cx -= HGAP;

  // Center parent over children
  const firstX = childLayouts[0].x;
  const lastCL = childLayouts[childLayouts.length-1];
  const lastX = lastCL.x;
  const parentX = (firstX + lastX) / 2;

  return { node, x: parentX, y: depth*(NH+VGAP), w: NW, children: childLayouts, depth, collapsed };
}

function getSubtreeWidth(layout) {
  if (layout.children.length === 0) return NW;
  const leftmost = getLeftmost(layout);
  const rightmost = getRightmost(layout);
  return rightmost - leftmost + NW;
}

function getLeftmost(layout) {
  if (layout.children.length === 0) return layout.x;
  return Math.min(layout.x, ...layout.children.map(getLeftmost));
}

function getRightmost(layout) {
  if (layout.children.length === 0) return layout.x;
  return Math.max(layout.x, ...layout.children.map(getRightmost));
}

function shiftTree(layout, dx) {
  layout.x += dx;
  layout.children.forEach(c => shiftTree(c, dx));
}

// ── SVG rendering ─────────────────────────────────────────────────
const SVG_NS = 'http://www.w3.org/2000/svg';
function svgEl(tag, attrs={}) {
  const el = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v));
  return el;
}

function renderTreeSVG(rootLayout) {
  const svg = document.getElementById('tree-svg');
  svg.innerHTML = '';

  // Compute canvas size
  const allNodes = [];
  collectLayouts(rootLayout, allNodes);
  if (allNodes.length === 0) return;

  const minX = Math.min(...allNodes.map(l => l.x));
  const maxX = Math.max(...allNodes.map(l => l.x)) + NW;
  const maxY = Math.max(...allNodes.map(l => l.y)) + NH;

  const padX = 20, padY = 20;
  const W = maxX - minX + padX*2;
  const H = maxY + padY*2;

  svg.setAttribute('width', Math.max(W, 400));
  svg.setAttribute('height', H + 20);
  svg.setAttribute('viewBox', `${minX-padX} -${padY} ${W} ${H+padY}`);

  // Draw edges first (behind nodes)
  const edgeGroup = svgEl('g', {id:'tree-edges'});
  svg.appendChild(edgeGroup);

  // Draw nodes
  const nodeGroup = svgEl('g', {id:'tree-nodes'});
  svg.appendChild(nodeGroup);

  drawLayout(rootLayout, edgeGroup, nodeGroup);
}

function collectLayouts(layout, arr) {
  arr.push(layout);
  layout.children.forEach(c => collectLayouts(c, arr));
}

function drawLayout(layout, edgeG, nodeG) {
  const {node, x, y, children, collapsed} = layout;
  const st = NODE_STYLE[node.type] || DEFAULT_STYLE;
  const cx = x + NW/2;
  const cy = y + NH/2;

  // Draw edges to children
  children.forEach(child => {
    const childCx = child.x + NW/2;
    const childCy = child.y + NH/2;
    // Cubic bezier for smooth curves
    const mx = cx;
    const my = y + NH + VGAP/2;
    const path = svgEl('path', {
      class: 'tedge',
      d: `M ${cx} ${y+NH} C ${mx} ${my}, ${childCx} ${my}, ${childCx} ${child.y}`,
      stroke: st.stroke,
    });
    edgeG.appendChild(path);
  });

  // Node group
  const g = svgEl('g', {
    class: 'tnode',
    transform: `translate(${x}, ${y})`,
  });
  g.addEventListener('click', () => toggleNodeCollapse(node._id));

  // Shadow/glow rect
  const glow = svgEl('rect', {
    x:1, y:1, width:NW-2, height:NH-2, rx:8,
    fill: st.stroke, opacity:'0.15'
  });
  g.appendChild(glow);

  // Main box
  const rect = svgEl('rect', {
    class:'tnbox', x:0, y:0, width:NW, height:NH, rx:7,
    fill: st.fill, stroke: st.stroke, 'stroke-width':'1.5',
  });
  g.appendChild(rect);

  // Collapse indicator (dot at bottom-center if has children)
  const allKids = getKids(node);
  if (allKids.length > 0) {
    const indicator = svgEl('circle', {
      cx: NW/2, cy: NH-4, r: 3,
      fill: collapsed ? st.stroke : 'transparent',
      stroke: st.stroke, 'stroke-width': '1.2'
    });
    g.appendChild(indicator);
  }

  // Icon (left side)
  const icon = svgEl('text', {
    x: 14, y: NH/2,
    'dominant-baseline':'central', 'text-anchor':'middle',
    fill: st.stroke, 'font-size':'11', 'font-family':"'Share Tech Mono',monospace",
    'pointer-events':'none'
  });
  icon.textContent = st.icon;
  g.appendChild(icon);

  // Label text
  const lbl = nodeLabel(node);
  const labelEl = svgEl('text', {
    class:'tnlabel', x: NW/2 + 4, y: NH/2 - (nodeSubLabel(node)?4:0),
    fill: '#e0f4ff',
  });
  labelEl.textContent = truncate(lbl, 13);
  g.appendChild(labelEl);

  // Sub-label
  const sub = nodeSubLabel(node);
  if (sub) {
    const subEl = svgEl('text', {
      class:'tnsub', x: NW/2 + 4, y: NH/2 + 9,
      fill: st.stroke,
    });
    subEl.textContent = sub;
    g.appendChild(subEl);
  }

  nodeG.appendChild(g);

  // Recurse
  children.forEach(child => drawLayout(child, edgeG, nodeG));
}

function truncate(s, max) {
  return s.length > max ? s.slice(0, max-1)+'…' : s;
}

// ── Collapse / expand ─────────────────────────────────────────────
function toggleNodeCollapse(id) {
  if (_collapsed.has(id)) _collapsed.delete(id);
  else _collapsed.add(id);
  rebuildTree();
}

function rebuildTree() {
  if (!_treeData) return;
  _nodeCounter = 0;
  assignIds(_treeData);
  const layout = layoutTree(_treeData);
  renderTreeSVG(layout);
}

function treeExpandAll() {
  _collapsed.clear();
  rebuildTree();
}

function treeCollapseAll() {
  // Collapse everything except root
  const ids = [];
  function collect(node) {
    if (!node) return;
    ids.push(node._id);
    getKids(node).forEach(collect);
  }
  if (_treeData) getKids(_treeData).forEach(n => { if(n) { collect(n); }});
  ids.forEach(id => _collapsed.add(id));
  rebuildTree();
}

function treeZoomReset() {
  const panel = document.getElementById('tree-panel');
  panel.scrollTop = 0;
  panel.scrollLeft = 0;
}

// ── Main entry: draw from AST ─────────────────────────────────────
function drawVisualTree(astRoot) {
  _treeData = astRoot;
  _collapsed = new Set();
  _nodeCounter = 0;
  assignIds(astRoot);
  const layout = layoutTree(astRoot);
  document.getElementById('tree-empty').style.display = 'none';
  document.getElementById('tree-canvas-wrap').style.display = 'block';
  document.getElementById('tree-legend').style.display = 'flex';
  renderTreeSVG(layout);

  const allNodes = [];
  collectLayouts(layout, allNodes);
  return allNodes.length;
}

/* ================================================================
   SEMANTIC ANALYZER
================================================================ */
function runSemantic(tokens, simbolos, errores) {
  const issues = [];
  const symMap = {};
  simbolos.forEach(s => symMap[s.nombre] = s);

  // 1. Variables usadas sin declarar
  const declaredNames = new Set(simbolos.map(s=>s.nombre));
  tokens.forEach(tok => {
    if(tok.tipo==='ID' && !declaredNames.has(tok.valor) &&
       !['print','input'].includes(tok.valor)){
      // Check if it's a reference (not declaration context)
      // We'll flag it as warning only
    }
  });

  // 2. Collect all IDs used vs declared
  const usedIds = new Set();
  tokens.forEach(t => { if(t.tipo==='ID') usedIds.add(t.valor); });
  const unusedVars = simbolos.filter(s => {
    const count = tokens.filter(t=>t.tipo==='ID'&&t.valor===s.nombre).length;
    return count <= 1; // declared but never used again
  });

  // 3. Type analysis for assignments
  const ARITH_OPS = new Set(['MAS','MENOS','MULT','DIV','MOD']);

  // 4. Count structures
  const ifs    = tokens.filter(t=>t.tipo==='IF').length;
  const whiles = tokens.filter(t=>t.tipo==='WHILE').length;
  const fors   = tokens.filter(t=>t.tipo==='FOR').length;
  const prints = tokens.filter(t=>t.tipo==='PRINT').length;
  const decls  = tokens.filter(t=>TIPOS_DATO.has(t.tipo)).length;
  const assigns= tokens.filter(t=>t.tipo==='ASIGNACION').length;

  return {
    issues,
    unusedVars,
    stats:{ifs,whiles,fors,prints,decls,assigns,
      totalTokens:tokens.length, totalSymbols:simbolos.length,
      lexErrors: errores.filter(e=>e.includes('ilegal')).length,
      semErrors: errores.filter(e=>e.includes('semántico')).length,
    }
  };
}

function renderSemantic(semResult, errores) {
  const {stats, unusedVars} = semResult;
  let html = '';

  // Stats grid
  html += `<div class="sem-stats">
    <div class="sem-stat-box"><span class="sem-stat-num cyan">${stats.totalTokens}</span><span class="sem-stat-label">Total Tokens</span></div>
    <div class="sem-stat-box"><span class="sem-stat-num green">${stats.totalSymbols}</span><span class="sem-stat-label">Símbolos</span></div>
    <div class="sem-stat-box"><span class="sem-stat-num amber">${stats.decls}</span><span class="sem-stat-label">Declaraciones</span></div>
    <div class="sem-stat-box"><span class="sem-stat-num" style="color:var(--purple);text-shadow:0 0 8px var(--purple)">${stats.assigns}</span><span class="sem-stat-label">Asignaciones</span></div>
  </div>`;

  // Estructuras de control
  html += `<div class="sem-section">
    <div class="sem-section-title">Estructuras de Control</div>`;
  const structs = [
    {label:'Condicionales (if)',  val:stats.ifs,   icon:'🔀'},
    {label:'Bucles while',         val:stats.whiles, icon:'🔁'},
    {label:'Bucles for',           val:stats.fors,   icon:'🔂'},
    {label:'Llamadas print()',     val:stats.prints,  icon:'📤'},
  ];
  structs.forEach(s=>{
    html+=`<div class="sem-item">
      <span class="sem-icon ok">${s.icon}</span>
      <span class="sem-text">${s.label}</span>
      <span class="sem-loc" style="color:var(--cyan);font-family:var(--disp);font-weight:700">${s.val}</span>
    </div>`;
  });
  html += '</div>';

  // Errores semánticos
  const semErrs = errores.filter(e=>e.includes('semántico'));
  const lexErrs = errores.filter(e=>e.includes('ilegal'));
  html += `<div class="sem-section">
    <div class="sem-section-title">Diagnóstico de Errores</div>`;
  if(errores.length===0){
    html+=`<div class="sem-item"><span class="sem-icon ok">✔</span><span class="sem-text">Sin errores léxicos ni semánticos</span></div>`;
  } else {
    if(lexErrs.length>0)
      html+=`<div class="sem-item"><span class="sem-icon err">✖</span><span class="sem-text">${lexErrs.length} error(es) léxico(s) — caracteres ilegales</span></div>`;
    if(semErrs.length>0)
      html+=`<div class="sem-item"><span class="sem-icon err">✖</span><span class="sem-text">${semErrs.length} error(es) semántico(s) — variables duplicadas</span></div>`;
    errores.forEach(e=>{
      const isErr=e.includes('ilegal')||e.includes('semántico');
      html+=`<div class="sem-item">
        <span class="sem-icon ${isErr?'err':'warn'}">${isErr?'✖':'⚠'}</span>
        <span class="sem-text" style="font-size:10px">${escH(e)}</span>
      </div>`;
    });
  }
  html+='</div>';

  // Variables declaradas con tipos
  html += `<div class="sem-section">
    <div class="sem-section-title">Variables Declaradas</div>`;
  if(unusedVars.length>0){
    html+=`<div class="sem-item"><span class="sem-icon warn">⚠</span>
      <span class="sem-text">${unusedVars.length} variable(s) declaradas pero no reutilizadas</span></div>`;
  }
  html+='</div>';

  return html;
}

/* ================================================================
   SYNTAX HIGHLIGHTING
================================================================ */
const HL = [
  [/\/\/[^\n]*/g,                     'hc'],
  [/"(?:[^"\\]|\\.)*"/g,              'hs'],
  [/\b(int|float|string|boolean)\b/g, 'ht'],
  [/\b(if|else|while|for|return|and|or|not)\b/g,'hk'],
  [/\b(true|false|null)\b/g,          'hn'],
  [/\b(print|input)\b/g,              'hb'],
  [/\b\d+(?:\.\d+)?\b/g,             'hn'],
  [/[+\-*/%]|==|!=|<=|>=|[<>]|&&|\|\||!/g,'ho'],
];
function escH(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function highlight(code){
  const len=code.length;
  const spans=new Array(len).fill(null);
  for(const [re,cls] of HL){
    re.lastIndex=0;let m;
    while((m=re.exec(code))!==null)
      for(let i=m.index;i<m.index+m[0].length;i++) if(spans[i]===null) spans[i]=cls;
  }
  let out='',i=0;
  while(i<len){
    const cls=spans[i];
    if(!cls){out+=escH(code[i]);i++;}
    else{
      let j=i;while(j<len&&spans[j]===cls)j++;
      out+=`<span class="${cls}">${escH(code.slice(i,j))}</span>`;i=j;
    }
  }
  return out;
}

/* ================================================================
   EDITOR SYNC
================================================================ */
const ed=document.getElementById('code-ed');
const hl=document.getElementById('code-hl');
const lni=document.getElementById('lnum-inner');

function syncEditor(){
  hl.innerHTML=highlight(ed.value);
  hl.scrollTop=ed.scrollTop;hl.scrollLeft=ed.scrollLeft;
  const lines=(ed.value.match(/\n/g)||[]).length+1;
  lni.textContent=Array.from({length:lines},(_,i)=>i+1).join('\n');
  lni.style.marginTop=-ed.scrollTop+'px';
  document.getElementById('editor-info').textContent=`${lines} líneas · ${ed.value.length} chars`;
}
ed.addEventListener('input',syncEditor);
ed.addEventListener('scroll',()=>{
  hl.scrollTop=ed.scrollTop;hl.scrollLeft=ed.scrollLeft;
  lni.style.marginTop=-ed.scrollTop+'px';
});
ed.addEventListener('keydown',e=>{
  if(e.key==='Tab'){
    e.preventDefault();
    const s=ed.selectionStart;
    ed.value=ed.value.slice(0,s)+'    '+ed.value.slice(ed.selectionEnd);
    ed.selectionStart=ed.selectionEnd=s+4;syncEditor();
  }
});
ed.addEventListener('keyup',updateCursor);
ed.addEventListener('click',updateCursor);
function updateCursor(){
  const txt=ed.value.slice(0,ed.selectionStart);
  const ln=(txt.match(/\n/g)||[]).length+1;
  const col=txt.length-txt.lastIndexOf('\n');
  document.getElementById('cur-ln').textContent=ln;
  document.getElementById('cur-col').textContent=col;
}

/* ================================================================
   TAB SWITCHER
================================================================ */
function switchTab(name){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  document.getElementById('view-'+name).classList.add('active');
}

/* ================================================================
   PROGRESS BAR
================================================================ */
function setProgress(p){
  document.getElementById('prog').style.width=p+'%';
  if(p>=100) setTimeout(()=>document.getElementById('prog').style.width='0',400);
}

/* ================================================================
   CONSOLE LOG
================================================================ */
function clog(type,text){
  const icons={error:'✖',ok:'✔',info:'›',warn:'⚠'};
  const div=document.createElement('div');
  div.className='cline '+type;
  div.innerHTML=`<span class="ci">${icons[type]||'›'}</span><span class="ct">${text}</span>`;
  document.getElementById('console').appendChild(div);
}

/* ================================================================
   MAIN ANALYSIS
================================================================ */
function runAnalysis(){
  const btn=document.getElementById('btn-run');
  btn.classList.add('running');
  setProgress(20);
  document.getElementById('hdr-status').textContent='Analizando...';
  const code=ed.value;

  // Clear all
  document.getElementById('console').innerHTML='';
  document.getElementById('tok-body').innerHTML='';
  document.getElementById('sym-body').innerHTML='';
  const _treeSvg=document.getElementById('tree-svg'); if(_treeSvg) _treeSvg.innerHTML='';

  const t0=performance.now();

  // Use fetch if analizar.php is available, else run JS lexer
  const useBackend = (window.location.protocol!=='file:');

  const analyze = useBackend
    ? fetch('analizar.php',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({codigo:code})})
        .then(r=>r.ok?r.json():Promise.reject('HTTP '+r.status))
    : Promise.resolve(runLexer(code));

  analyze.then(data=>{
    setProgress(60);
    const {tokens,simbolos,errores}=data;
    const tac           = data.tac           || [];
    const tacOpt        = data.tac_optimizado|| [];
    const metr          = data.metricas      || {};
    const traza         = data.traza_optimizacion || [];
    const ms=Math.round(performance.now()-t0);

    // ── TOKENS ──
    if(tokens&&tokens.length>0){
      document.getElementById('tok-empty').style.display='none';
      document.getElementById('tok-table').style.display='table';
      const frag=document.createDocumentFragment();
      tokens.forEach((tok,i)=>{
        const tr=document.createElement('tr');
        tr.style.animationDelay=Math.min(i*6,300)+'ms';
        const cls='tok-'+tok.tipo;
        tr.innerHTML=`<td class="${cls}">${escH(tok.tipo)}</td>
          <td style="color:var(--t1);max-width:130px;overflow:hidden;text-overflow:ellipsis" title="${escH(tok.valor)}">${escH(String(tok.valor).replace(/\n/g,'↵').replace(/\t/g,'→'))}</td>
          <td style="color:var(--t3);text-align:center">${tok.linea}</td>
          <td style="color:var(--t3);text-align:center">${tok.columna}</td>`;
        frag.appendChild(tr);
      });
      document.getElementById('tok-body').appendChild(frag);
      document.getElementById('tok-count').textContent=tokens.length+' tokens';
      document.getElementById('badge-tokens').textContent=tokens.length;
      document.getElementById('badge-tokens').classList.add('show');
    }

    // ── SYMBOLS ──
    const typeColors={int:'#5ac8fa',float:'#5ac8fa',string:'#30d158',boolean:'#ff9f0a'};
    if(simbolos&&simbolos.length>0){
      document.getElementById('sym-empty').style.display='none';
      document.getElementById('sym-table').style.display='table';
      const frag2=document.createDocumentFragment();
      simbolos.forEach((sim,i)=>{
        const tr=document.createElement('tr');
        tr.style.animationDelay=Math.min(i*12,300)+'ms';
        const tc=typeColors[sim.tipo]||'var(--t2)';
        tr.innerHTML=`<td style="color:var(--green)">${escH(sim.nombre)}</td>
          <td style="color:${tc}">${escH(sim.tipo)}</td>
          <td style="color:var(--t3);text-align:center">${sim.linea}</td>
          <td style="color:var(--t3)">${escH(String(sim.valor))}</td>`;
        frag2.appendChild(tr);
      });
      document.getElementById('sym-body').appendChild(frag2);
      document.getElementById('sym-count').textContent=simbolos.length+' símbolos';
    }

    // ── SYNTAX TREE ──
    setProgress(70);
    const tree=buildTree(tokens||[]);
    const nodeCount = drawVisualTree(tree);
    document.getElementById('tree-count').textContent=nodeCount+' nodos';
    document.getElementById('badge-tree').textContent=nodeCount;
    document.getElementById('badge-tree').classList.add('show');

    // ── SEMANTIC ──
    setProgress(85);
    const semResult=runSemantic(tokens||[],simbolos||[],errores||[]);
    document.getElementById('sem-empty').style.display='none';
    const semContent=document.getElementById('sem-content');
    semContent.style.display='block';
    semContent.innerHTML=renderSemantic(semResult,errores||[]);
    const totalIssues=(errores||[]).length;
    document.getElementById('sem-count').textContent=totalIssues===0?'OK':totalIssues+' aviso(s)';
    document.getElementById('badge-sem').textContent=totalIssues;
    document.getElementById('badge-sem').classList.add('show');

    // ── INTERMEDIATE CODE (TAC) ──
    renderIntermediate(tac, tacOpt, metr, traza);

    // ── CONSOLE ──
    const errs=errores||[];
    if(errs.length===0){
      clog('ok',`✔ Análisis completado en ${ms}ms — ${tokens.length} tokens · ${simbolos.length} símbolos · 0 errores`);
      document.getElementById('err-count').textContent='sin errores';
      document.getElementById('badge-errors').style.display='none';
      document.getElementById('hdr-status').textContent='Análisis OK';
    } else {
      clog('warn',`Se encontraron <b>${errs.length} error(es)</b>:`);
      errs.forEach(e=>clog('error',escH(e)));
      document.getElementById('err-count').textContent=errs.length+' error(es)';
      document.getElementById('badge-errors').textContent=errs.length;
      document.getElementById('badge-errors').classList.add('show');
      document.getElementById('hdr-status').textContent=errs.length+' error(es)';
    }
    clog('info',`Backend: ${useBackend?'PHP→Python lexer.py':'JS lexer (modo local)'} · ${ms}ms`);

    // ── STATUS ──
    const tl=tokens?tokens.length:0, sl=simbolos?simbolos.length:0;
    const lines=(code.match(/\n/g)||[]).length+1;
    document.getElementById('sb-tok').textContent=tl;
    document.getElementById('sb-sym').textContent=sl;
    document.getElementById('stat-tokens').textContent=tl;
    document.getElementById('stat-syms').textContent=sl;
    document.getElementById('stat-lines').textContent=lines;
    document.getElementById('stat-errs').textContent=errs.length;
    document.getElementById('ft-tok').textContent=tl;
    document.getElementById('ft-sym').textContent=sl;
    document.getElementById('ft-err').textContent=errs.length;

    setProgress(100);
    btn.classList.remove('running');

  }).catch(err=>{
    // Fallback to JS lexer if PHP not available
    if(useBackend){
      clog('warn','PHP no disponible, usando lexer JavaScript local...');
      const data=runLexer(code);
      analyze._done=true;
      // Re-run with local data
      setTimeout(()=>{
        const e2=new CustomEvent('localAnalysis',{detail:data});
        document.dispatchEvent(e2);
      },0);
    } else {
      clog('error','Error: '+err);
    }
    btn.classList.remove('running');
    setProgress(100);
  });
}

// Fallback handler
document.addEventListener('localAnalysis', e=>{
  // Just re-trigger with the JS result already computed
  // Quick patch: set window flag and rerun
  window._localData=e.detail;
  const origFetch=window.fetch;
  window.fetch=()=>Promise.resolve({ok:true,json:()=>Promise.resolve(e.detail)});
  runAnalysis();
  window.fetch=origFetch;
});

/* ================================================================
   INTERMEDIATE CODE (TAC) — render
================================================================ */
let _irCurrentSub = 'orig';

function _irRowHtml(r){
  const lbl = r.etiqueta ? `${escH(r.etiqueta)}:` : '';
  return `<tr>
    <td class="ir-n">${r.n}</td>
    <td class="ir-lbl">${lbl}</td>
    <td class="ir-instr">${escH(r.instruccion)}</td>
    <td class="ir-op">${escH(r.op)}</td>
    <td class="ir-arg">${escH(String(r.arg1))}</td>
    <td class="ir-arg">${escH(String(r.arg2))}</td>
    <td class="ir-dest">${escH(String(r.dest))}</td>
  </tr>`;
}

function _irPretty(rows){
  if(!rows||rows.length===0) return '(vacío)';
  return rows.map(r=>{
    const lbl = r.etiqueta ? `${r.etiqueta}:` : '';
    const n = String(r.n).padStart(3,' ');
    return `${n}: ${lbl?lbl.padEnd(8,' '):'        '}${r.instruccion}`;
  }).join('\n');
}

function renderIntermediate(tac, tacOpt, metr, traza){
  const hasTac = (tac && tac.length>0) || (tacOpt && tacOpt.length>0);

  // Empty state
  const empty = document.getElementById('ir-empty');
  if(!hasTac){
    empty.style.display='flex';
    document.querySelectorAll('.ir-view').forEach(v=>v.style.display='none');
    document.getElementById('ir-count').textContent='—';
    document.getElementById('ir-stats').innerHTML='';
    document.getElementById('badge-ir').textContent='0';
    document.getElementById('badge-ir').classList.remove('show');
    return;
  }
  empty.style.display='none';

  // Tablas
  document.getElementById('ir-body-orig').innerHTML = tac.map(_irRowHtml).join('');
  document.getElementById('ir-body-opt').innerHTML  = tacOpt.map(_irRowHtml).join('');

  // Comparación: pre + tags + traza
  document.getElementById('ir-pre-orig').textContent = _irPretty(tac);
  document.getElementById('ir-pre-opt').textContent  = _irPretty(tacOpt);
  document.getElementById('ir-cmp-orig-n').textContent = `${tac.length} cuádruplos`;
  document.getElementById('ir-cmp-opt-n').textContent  = `${tacOpt.length} cuádruplos`;

  document.getElementById('ir-traza-body').innerHTML = (traza||[]).map(t=>{
    const delta = t.delta;
    const dColor = delta<0 ? 'var(--green)' : (delta>0 ? 'var(--red)' : 'var(--t3)');
    const dStr = delta>0 ? `+${delta}` : String(delta);
    return `<tr>
      <td style="color:var(--cyan);text-align:center">${t.iter}</td>
      <td style="color:var(--t1)">${escH(t.pasada)}</td>
      <td style="color:var(--t2);text-align:center">${t.antes}</td>
      <td style="color:var(--t2);text-align:center">${t.despues}</td>
      <td style="color:${dColor};text-align:center">${dStr}</td>
    </tr>`;
  }).join('') || `<tr><td colspan="5" style="text-align:center;color:var(--t3);padding:8px">El optimizador no realizó ningún cambio</td></tr>`;

  // Métricas y badges
  const co = metr.cuad_orig ?? tac.length;
  const cp = metr.cuad_opt  ?? tacOpt.length;
  const to = metr.temps_orig ?? 0;
  const tp = metr.temps_opt  ?? 0;
  const red = metr.reduccion_pct ?? 0;
  document.getElementById('ir-count').textContent = `${co} → ${cp} cuádruplos`;
  document.getElementById('ir-stats').innerHTML =
    `Cuádruplos: <b class="cyan">${co}</b> → <b class="green">${cp}</b> &nbsp;·&nbsp; ` +
    `Reducción: <b class="amber">${red}%</b> &nbsp;·&nbsp; ` +
    `Temporales: <b class="cyan">${to}</b> → <b class="green">${tp}</b>`;
  document.getElementById('badge-ir').textContent = co;
  document.getElementById('badge-ir').classList.add('show');

  // Mostrar la sub-vista activa
  switchIRSub(_irCurrentSub);
}

function switchIRSub(sub){
  _irCurrentSub = sub;
  document.querySelectorAll('.ir-sub').forEach(b=>{
    b.classList.toggle('active', b.dataset.sub===sub);
  });
  // Si no hay datos cargados todavía, no mostramos nada (sigue el empty state)
  if(document.getElementById('ir-empty').style.display==='flex') return;
  document.querySelectorAll('.ir-view').forEach(v=>v.style.display='none');
  const map = {orig:'ir-view-orig', opt:'ir-view-opt', cmp:'ir-view-cmp', info:'ir-view-info'};
  const target = document.getElementById(map[sub] || map.orig);
  if(target){
    target.style.display = (sub==='cmp') ? 'flex' : 'block';
  }
}

// Info siempre disponible (incluso sin análisis). Mostrarla si el usuario hace click en Info sin haber analizado.
document.addEventListener('DOMContentLoaded', ()=>{
  document.querySelector('.ir-sub[data-sub="info"]').addEventListener('click', ()=>{
    document.getElementById('ir-empty').style.display='none';
    document.querySelectorAll('.ir-view').forEach(v=>v.style.display='none');
    document.getElementById('ir-view-info').style.display='block';
  });
});

/* ================================================================
   CLEAR ALL
================================================================ */
function clearAll(){
  ed.value='';syncEditor();
  ['tok-body','sym-body','console','ir-body-orig','ir-body-opt','ir-traza-body'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.innerHTML='';
  });
  document.getElementById('tree-svg').innerHTML='';
  document.getElementById('tree-canvas-wrap').style.display='none';
  document.getElementById('tree-legend').style.display='none';
  ['tok-empty','sym-empty','tree-empty','sem-empty','ir-empty'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.style.display='';
  });
  document.getElementById('tok-table').style.display='none';
  document.getElementById('sym-table').style.display='none';
  document.getElementById('sem-content').style.display='none';
  document.querySelectorAll('.ir-view').forEach(v=>v.style.display='none');
  ['ir-pre-orig','ir-pre-opt'].forEach(id=>{ const el=document.getElementById(id); if(el) el.textContent=''; });
  const irStats=document.getElementById('ir-stats'); if(irStats) irStats.innerHTML='';
  ['tok-count','sym-count','err-count','tree-count','sem-count','ir-count'].forEach(id=>{
    const el=document.getElementById(id); if(el) el.textContent='—';
  });
  ['sb-tok','sb-sym','ft-tok','ft-sym','ft-err','stat-tokens','stat-syms','stat-lines','stat-errs'].forEach(id=>document.getElementById(id).textContent='0');
  document.getElementById('hdr-status').textContent='Sistema listo';
  clog('info','Editor limpiado. Listo para nuevo análisis.');
}

/* ================================================================
   EXAMPLE PICKER — position:fixed menu, calculates coords dynamically
================================================================ */
let exOpen=false;

function toggleExMenu(e){
  e.stopPropagation();
  exOpen=!exOpen;
  const menu=document.getElementById('ex-menu');
  const arrow=document.getElementById('ex-arrow');
  if(exOpen){
    // Position the fixed menu above the button
    const btn=document.getElementById('btn-ex');
    const rect=btn.getBoundingClientRect();
    menu.style.left=rect.left+'px';
    menu.style.top=(rect.top-menu.offsetHeight-8)+'px';
    // Show first, then measure and reposition
    menu.classList.add('open');
    requestAnimationFrame(()=>{
      const mh=menu.offsetHeight;
      menu.style.top=(rect.top-mh-8)+'px';
    });
    arrow.style.transform='rotate(180deg)';
  } else {
    menu.classList.remove('open');
    arrow.style.transform='';
  }
}

document.addEventListener('click',e=>{
  if(!document.getElementById('ex-picker').contains(e.target)){
    document.getElementById('ex-menu').classList.remove('open');
    document.getElementById('ex-arrow').style.transform='';
    exOpen=false;
  }
});

/* ================================================================
   EXAMPLES
================================================================ */
const EXAMPLES=[
{titulo:'Variables y Tipos',codigo:`// Ejemplo 01 — Variables y Tipos de Dato
int edad = 25;
float salario = 15750.50;
string nombre = "Ana García";
boolean activo = true;

int anioNacimiento = 2025 - edad;
float bono = salario * 0.10;
float salarioTotal = salario + bono;
int residuo = edad % 7;

edad = edad + 1;
salario = salarioTotal;

print(nombre);
print(salarioTotal);
print(activo);
`},
{titulo:'Control de Flujo',codigo:`// Ejemplo 02 — Estructuras if / else
int nota = 78;
boolean aprobado = false;
string calificacion = "indefinida";

if (nota >= 90) {
    calificacion = "Excelente";
    aprobado = true;
} else {
    if (nota >= 70) {
        calificacion = "Aprobado";
        aprobado = true;
    } else {
        if (nota >= 60) {
            calificacion = "Regular";
            aprobado = false;
        } else {
            calificacion = "Reprobado";
            aprobado = false;
        }
    }
}

boolean conBecas = aprobado && (nota >= 75);
boolean requiereRecuperar = !aprobado || (nota < 60);

print(calificacion);
print(conBecas);
`},
{titulo:'Bucles while y for',codigo:`// Ejemplo 03 — Bucles while y for
int i = 1;
int suma = 0;
while (i <= 100) {
    suma = suma + i;
    i = i + 1;
}
print(suma);

int n = 10;
int factorial = 1;
int k = n;
while (k > 1) {
    factorial = factorial * k;
    k = k - 1;
}
print(factorial);

int base = 7;
for (int j = 1; j <= 12; j = j + 1) {
    int resultado = base * j;
    print(resultado);
}
`},
{titulo:'Expresiones Complejas',codigo:`// Ejemplo 04 — Expresiones y Operadores
float a = 10.5;
float b = 3.2;
float c = 0.0;

c = a + b * 2.0 - 1.5;
float d = a / b + b % 3.0;

boolean mayor = a > b;
boolean menor = a < b;
boolean igual = a == b;
boolean diferente = a != b;
boolean mayIgual = a >= 10.5;
boolean menIgual = b <= 3.2;

boolean r1 = (a > 5.0) && (b < 5.0);
boolean r2 = (a == 10.5) || (b == 0.0);
boolean r3 = !(a < b) && (c != 0.0);

int x = 100;
int y = 37;
int cociente = x / y;
int residuoMod = x % y;

print(c);
print(r1);
print(cociente);
`},
{titulo:'Errores Léxicos',codigo:`// Ejemplo 05 — Errores Léxicos Intencionales
int x = 10;
float y = 3.14;
string mensaje = "Hola";

// ERROR 1: carácter ilegal '@'
int z = 5@2;

// ERROR 2: carácter ilegal '#'
float pi = 3.14#15;

// ERROR 3: variable duplicada
int x = 99;

// ERROR 4: carácter ilegal '^'
int potencia = 2^8;

boolean activo = true;
int contador = 0;

while (contador < 5) {
    contador = contador + 1;
}

print(x);
print(mensaje);
`},
{titulo:'Strings y Booleanos',codigo:`// Ejemplo 06 — Cadenas y Lógica Booleana
string saludo = "Hola, Mundo!";
string ruta = "C:\\\\Users\\\\Compiladores";
string comillas = "Él dijo: \\"Hola\\"";
string vacia = "";

boolean verdadero = true;
boolean falso = false;
boolean nulo = null;

boolean tt = verdadero && verdadero;
boolean tf = verdadero && falso;
boolean ft = falso && verdadero;
boolean ff = falso && falso;

boolean tt2 = verdadero || verdadero;
boolean ff2 = falso || falso;

boolean noV = !verdadero;
boolean noF = !falso;

boolean complejo = (tt || tf) && (!ff) && (tt2 != ff2);

print(saludo);
print(complejo);
`},
{titulo:'Programa Completo',codigo:`// Ejemplo 07 — Programa Integrador
// Ingeniería en Sistemas · Compiladores 120262294035A

int totalAlumnos = 30;
float sumaNotas = 0.0;
float promedio = 0.0;
int aprobados = 0;
int reprobados = 0;
boolean cursoActivo = true;
string nombreCurso = "Compiladores 120262294035A";

float nota1 = 85.0;
float nota2 = 72.5;
float nota3 = 91.0;
float nota4 = 60.0;
float nota5 = 55.5;

sumaNotas = nota1 + nota2 + nota3 + nota4 + nota5;
int totalMuestras = 5;
promedio = sumaNotas / totalMuestras;

if (nota1 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }
if (nota2 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }
if (nota3 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }
if (nota4 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }
if (nota5 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }

string estadoCurso = "indefinido";
if (promedio >= 90) {
    estadoCurso = "Excelente";
} else {
    if (promedio >= 75) {
        estadoCurso = "Bueno";
    } else {
        if (promedio >= 60) {
            estadoCurso = "Regular";
        } else {
            estadoCurso = "Bajo";
        }
    }
}

boolean cursoExitoso = cursoActivo && (aprobados > reprobados);
boolean requiereApoyo = !cursoExitoso || (promedio < 70);

int intentos = 0;
while (intentos < 3) {
    intentos = intentos + 1;
    boolean valido = (promedio >= 0) && (promedio <= 100);
}

int porcentajeAprobados = (aprobados * 100) / totalMuestras;
float rango = 91.0 - 55.5;

print(nombreCurso);
print(promedio);
print(estadoCurso);
print(aprobados);
print(cursoExitoso);
print(porcentajeAprobados);
`},
];

function loadEx(idx){
  const ex=EXAMPLES[idx||0];
  ed.value=ex.codigo;syncEditor();
  document.getElementById('ex-menu').classList.remove('open');
  document.getElementById('ex-arrow').style.transform='';
  exOpen=false;
  document.getElementById('console').innerHTML='';
  switchTab('editor');
  clog('info',`Ejemplo cargado: <b>${ex.titulo}</b> · Presiona F5 para analizar.`);
}

/* ================================================================
   KEYBOARD & INIT
================================================================ */
document.addEventListener('keydown',e=>{if(e.key==='F5'){e.preventDefault();runAnalysis();}});

loadEx(0);
updateCursor();
clog('info','MiniCompiler v2.0 iniciado · Léxico + Árbol Sintáctico + Semántico · Presiona <b>F5</b> para analizar.');
</script>
</body>
</html>
