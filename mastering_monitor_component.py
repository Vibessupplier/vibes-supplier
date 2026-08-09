"""Browser-side live monitoring deck for the Mastering Analyzer."""

import base64

import streamlit as st


MONITOR_HTML = """
<section class="monitor-unit">
  <div class="unit-label"><span>VS MASTERING MONITOR / 01</span><span class="signal"><i></i> LIVE SIGNAL</span></div>
  <canvas class="waveform" aria-label="Master waveform and playhead"></canvas>
  <div class="transport">
    <button type="button" data-action="play">▶ PLAY</button>
    <button type="button" data-action="stop">■ STOP</button>
    <span class="time">0:00 / 0:00</span>
    <button type="button" class="mono" data-action="mono" aria-pressed="false">MONO CHECK / OFF</button>
  </div>
  <audio preload="auto"></audio>
  <div class="monitor-grid">
    <div class="spectrum-module">
      <div class="module-label">REAL-TIME SPECTRUM <span>20 Hz — 20 kHz</span></div>
      <canvas class="spectrum" aria-label="Live frequency spectrum"></canvas>
      <div class="frequency-scale"><span>20</span><span>100</span><span>1K</span><span>10K</span><span>20K</span></div>
    </div>
    <div class="meter-module">
      <div class="module-label">LEVEL MONITOR <span>APPROX. dBFS</span></div>
      <div class="meters">
        <div class="vu"><div class="vu-face"><span class="scale-arc"></span><span class="needle"></span><span class="pivot"></span><span class="glass-shine"></span><small>VS / LEVEL UNIT</small><b>PEAK</b></div><strong class="peak-value">−∞</strong></div>
        <div class="vu"><div class="vu-face"><span class="scale-arc"></span><span class="needle rms-needle"></span><span class="pivot"></span><span class="glass-shine"></span><small>VS / LEVEL UNIT</small><b>RMS</b></div><strong class="rms-value">−∞</strong></div>
      </div>
    </div>
  </div>
  <div class="response-control">
    <span>METER RESPONSE</span>
    <div role="group" aria-label="Meter response speed">
      <button type="button" data-response="steady">STEADY</button>
      <button type="button" data-response="balanced" class="active">BALANCED</button>
      <button type="button" data-response="fast">FAST</button>
    </div>
  </div>
  <div class="stereo-strip">
    <div><span>L / R BALANCE</span><strong class="balance-value">CENTER</strong></div>
    <div><span>STEREO WIDTH</span><strong class="width-value">0%</strong></div>
    <div><span>PHASE CORRELATION</span><strong class="phase-value">+1.00</strong><i class="phase-lamp"></i></div>
  </div>
  <p class="monitor-note">LIVE VALUES FOLLOW THE CURRENT PLAYHEAD. RUN ANALYZE MASTER FOR AUTHORITATIVE FULL-TRACK LUFS, TRUE PEAK AND DYNAMICS.</p>
</section>
"""


MONITOR_CSS = """
.monitor-unit{padding:13px;border:1px solid rgba(216,201,167,.28);border-radius:3px;background:linear-gradient(180deg,rgba(119,118,107,.08),transparent 26%),rgba(23,24,21,.95);box-shadow:inset 0 0 0 3px rgba(0,0,0,.16);color:#eee3c7;font-family:"Avenir Next",Arial,sans-serif;user-select:none}
.unit-label,.module-label{display:flex;justify-content:space-between;align-items:center;color:#d8c9a7;font:600 10px SFMono-Regular,Menlo,monospace;letter-spacing:.12em}.unit-label{padding:3px 3px 10px}.module-label{padding:0 0 8px}.module-label span{color:rgba(216,201,167,.48);font-size:8px}.signal{display:flex;align-items:center;gap:7px;color:rgba(216,201,167,.62)}.signal i{width:7px;height:7px;border-radius:50%;background:#87966c;box-shadow:0 0 7px rgba(135,150,108,.45)}
canvas{display:block;box-sizing:border-box;width:100%;border:1px solid rgba(216,201,167,.15);background:#101a14}.waveform{height:145px;cursor:pointer;touch-action:none}.spectrum{height:185px}audio{display:none}
.transport{display:flex;align-items:center;gap:7px;padding:9px 0 13px}.transport button{min-height:33px;padding:0 12px;border:1px solid rgba(216,201,167,.28);border-radius:2px;background:linear-gradient(#273229,#19221b);color:#d8c9a7;font-size:10px;font-weight:700;letter-spacing:.07em;cursor:pointer;box-shadow:0 2px 0 #090d0a}.transport button:hover{border-color:#d99a45;color:#eee3c7}.transport button:active{transform:translateY(2px);box-shadow:none}.time{color:#d99a45;font:600 11px SFMono-Regular,Menlo,monospace}.transport .mono{margin-left:auto}.transport .mono.active{border-color:#d99a45;color:#d99a45;background:linear-gradient(rgba(217,154,69,.14),rgba(48,37,27,.72));box-shadow:inset 3px 0 0 #d99a45,0 2px 0 #090d0a}
.monitor-grid{display:grid;grid-template-columns:minmax(0,1.12fr) minmax(350px,1fr);gap:10px}.spectrum-module,.meter-module{padding:11px;border:1px solid rgba(216,201,167,.17);background:rgba(28,40,30,.78);box-shadow:inset 0 0 0 2px rgba(0,0,0,.12)}.frequency-scale{display:flex;justify-content:space-between;padding-top:4px;color:rgba(216,201,167,.42);font:500 8px SFMono-Regular,Menlo,monospace}
.meters{display:grid;grid-template-columns:1fr 1fr;gap:10px}.vu{position:relative;padding:7px 7px 8px;border:1px solid #595950;border-radius:5px;background:radial-gradient(circle at 14% 18%,rgba(111,62,39,.48) 0 2px,transparent 3px),radial-gradient(circle at 82% 72%,rgba(91,49,32,.40) 0 3px,transparent 5px),radial-gradient(ellipse at 40% 90%,rgba(126,72,43,.24) 0 5px,transparent 9px),repeating-linear-gradient(108deg,transparent 0 8px,rgba(126,72,43,.055) 9px 10px),linear-gradient(145deg,#343630,#10120f 56%,#282a25);box-shadow:inset 0 1px rgba(238,227,199,.08),inset 0 0 0 3px rgba(0,0,0,.26),inset 4px -4px 9px rgba(111,62,39,.13),0 6px 12px rgba(0,0,0,.24);text-align:center}.vu::before,.vu::after{content:"";position:absolute;z-index:8;width:5px;height:5px;border:1px solid #68685e;border-radius:50%;background:radial-gradient(circle at 38% 32%,#8b897b,#292b26 58%);box-shadow:inset 0 1px rgba(238,227,199,.16),0 1px 2px rgba(0,0,0,.46)}.vu::before{top:5px;left:5px}.vu::after{top:5px;right:5px}.vu-face{position:relative;overflow:hidden;width:100%;height:auto;aspect-ratio:1.58/1;border:1px solid rgba(48,37,27,.72);border-radius:42% 42% 5px 5px/32% 32% 5px 5px;background:radial-gradient(ellipse at 50% 113%,rgba(217,154,69,.18) 0 20%,transparent 49%),radial-gradient(circle at 18% 28%,rgba(89,68,49,.07) 0 1px,transparent 2px),radial-gradient(circle at 74% 62%,rgba(89,68,49,.08) 0 1px,transparent 2px),linear-gradient(180deg,#ded2b5 0%,#cbbb97 65%,#b39d73 100%);box-shadow:inset 0 5px 11px rgba(48,37,27,.27),inset 0 -9px 17px rgba(217,154,69,.08),0 0 0 3px rgba(0,0,0,.40);transition:box-shadow 220ms ease,filter 220ms ease}.monitor-unit.powered .vu-face{filter:brightness(1.06) saturate(1.07);box-shadow:inset 0 5px 10px rgba(48,37,27,.20),inset 0 -24px 31px rgba(217,154,69,.25),0 0 0 3px rgba(0,0,0,.40),0 0 13px rgba(217,154,69,.15)}.vu-face::before{content:"−30       −18       −12        −6       −3        0";position:absolute;z-index:2;top:13%;left:4%;right:4%;color:#30251b;font:700 clamp(5px,.56vw,7px) SFMono-Regular,Menlo,monospace;letter-spacing:-.04em;white-space:nowrap}.scale-arc{position:absolute;z-index:1;inset:4% 3% 15%;background:repeating-conic-gradient(from 311deg at 50% 108%,rgba(48,37,27,.66) 0deg .62deg,transparent .70deg 5.9deg);mask-image:radial-gradient(circle at 50% 108%,transparent 0 61%,#000 62% 70%,transparent 71%);-webkit-mask-image:radial-gradient(circle at 50% 108%,transparent 0 61%,#000 62% 70%,transparent 71%)}.vu-face b{position:absolute;z-index:4;bottom:7%;left:0;right:0;color:#30251b;font:800 clamp(8px,.78vw,10px) SFMono-Regular,Menlo,monospace;letter-spacing:.18em}.vu-face small{position:absolute;z-index:2;top:34%;left:0;right:0;color:rgba(48,37,27,.57);font:700 clamp(5px,.48vw,6px) SFMono-Regular,Menlo,monospace;letter-spacing:.12em}.needle{position:absolute;z-index:4;bottom:-3%;left:50%;width:1.5px;height:78%;background:linear-gradient(#8c392d,#b85f3d 72%,#30251b);box-shadow:1px 0 1px rgba(48,37,27,.28);transform-origin:50% 100%;transform:translateX(-50%) rotate(-48deg);transition:transform 70ms linear}.pivot{position:absolute;z-index:5;bottom:-6%;left:50%;width:12%;aspect-ratio:1;border:2px solid #77766b;border-radius:50%;background:radial-gradient(circle at 38% 32%,#aaa899 0 9%,#4b4c45 32%,#20221e 70%);box-shadow:0 2px 4px rgba(0,0,0,.45);transform:translateX(-50%)}.glass-shine{position:absolute;z-index:6;inset:-24% -25% 18% 18%;border-radius:48%;background:linear-gradient(128deg,rgba(255,255,255,.22),rgba(255,255,255,.06) 20%,transparent 21% 53%,rgba(255,255,255,.045) 54%,transparent 66%);transform:rotate(-5deg);pointer-events:none;mix-blend-mode:screen}.vu strong{display:block;padding-top:7px;color:#d99a45;font:600 11px SFMono-Regular,Menlo,monospace;text-shadow:0 0 5px rgba(217,154,69,.14)}
.response-control{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:10px;padding:8px 10px;border:1px solid rgba(216,201,167,.14);background:rgba(48,37,27,.34)}.response-control>span{color:rgba(216,201,167,.58);font:600 8px SFMono-Regular,Menlo,monospace;letter-spacing:.10em}.response-control>div{display:flex;gap:5px}.response-control button{min-height:27px;padding:0 9px;border:1px solid rgba(216,201,167,.22);border-radius:2px;background:#19221b;color:rgba(216,201,167,.62);font:600 8px SFMono-Regular,Menlo,monospace;letter-spacing:.07em;cursor:pointer}.response-control button:hover{border-color:#d99a45;color:#eee3c7}.response-control button.active{border-color:#d99a45;background:rgba(217,154,69,.13);color:#d99a45;box-shadow:inset 2px 0 0 #d99a45}
.stereo-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}.stereo-strip>div{position:relative;padding:10px;border:1px solid rgba(216,201,167,.16);background:#171815}.stereo-strip span{display:block;color:rgba(216,201,167,.58);font:600 8px SFMono-Regular,Menlo,monospace;letter-spacing:.09em}.stereo-strip strong{display:block;margin-top:5px;color:#d99a45;font:600 13px SFMono-Regular,Menlo,monospace}.phase-lamp{position:absolute;right:10px;bottom:12px;width:7px;height:7px;border-radius:50%;background:#87966c;box-shadow:0 0 6px rgba(135,150,108,.36)}.phase-lamp.warn{background:#b85f3d;box-shadow:0 0 7px rgba(184,95,61,.48)}
.monitor-note{margin:10px 2px 0;color:rgba(216,201,167,.48);font:500 8px/1.5 SFMono-Regular,Menlo,monospace;letter-spacing:.07em}
@media(max-width:680px){.monitor-grid{grid-template-columns:1fr}.stereo-strip{grid-template-columns:1fr}.transport{flex-wrap:wrap}.transport .mono{margin-left:0}.waveform{height:125px}.response-control{align-items:flex-start;flex-direction:column}.response-control>div{width:100%}.response-control button{flex:1}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""


MONITOR_JS = """
export default function(component){
 const{data,parentElement}=component,q=s=>parentElement.querySelector(s),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const audio=q('audio'),wave=q('.waveform'),wc=wave.getContext('2d'),spectrum=q('.spectrum'),sc=spectrum.getContext('2d');
 let state=parentElement.__vsMasterMonitor;
 if(!state||state.audioId!==data.audio_id){state={audioId:data.audio_id,peaks:null,raf:null,mono:false,graph:null,response:'balanced',lastReadout:0,peakDb:-60,rmsDb:-60,balance:0,width:0,correlation:1,peakHoldUntil:0,peakAngle:-48,rmsAngle:-48};parentElement.__vsMasterMonitor=state;audio.src=data.audio_url;
  fetch(data.audio_url).then(r=>r.arrayBuffer()).then(b=>{const c=new(window.AudioContext||window.webkitAudioContext)();return c.decodeAudioData(b).finally(()=>c.close())}).then(decoded=>{const ch=decoded.getChannelData(0),points=1800,block=Math.max(1,Math.floor(ch.length/points));state.peaks=Array.from({length:points},(_,i)=>{let p=0,e=Math.min(ch.length,(i+1)*block);for(let x=i*block;x<e;x++)p=Math.max(p,Math.abs(ch[x]));return p});drawWave()}).catch(()=>{state.peaks=[];drawWave()});
 }
 const fit=(canvas,ctx)=>{const r=window.devicePixelRatio||1,b=canvas.getBoundingClientRect(),w=Math.max(1,Math.round(b.width*r)),h=Math.max(1,Math.round(b.height*r));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}return[w,h,r]};
 const fmt=s=>!Number.isFinite(s)?'0:00':`${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`;
 function drawWave(){const[w,h,r]=fit(wave,wc);wc.clearRect(0,0,w,h);wc.fillStyle='#101a14';wc.fillRect(0,0,w,h);wc.strokeStyle='rgba(216,201,167,.12)';wc.beginPath();wc.moveTo(0,h/2);wc.lineTo(w,h/2);wc.stroke();if(state.peaks?.length){wc.strokeStyle='#d8c9a7';wc.lineWidth=Math.max(1,r);wc.beginPath();state.peaks.forEach((p,i)=>{const x=i/(state.peaks.length-1)*w;wc.moveTo(x,h/2-p*h*.39);wc.lineTo(x,h/2+p*h*.39)});wc.stroke()}if(audio.duration){const x=audio.currentTime/audio.duration*w;wc.strokeStyle='#d99a45';wc.lineWidth=2*r;wc.beginPath();wc.moveTo(x,0);wc.lineTo(x,h);wc.stroke()}q('.time').textContent=`${fmt(audio.currentTime)} / ${fmt(audio.duration)}`}
 function setupGraph(){if(state.graph)return state.graph;const C=window.AudioContext||window.webkitAudioContext,ctx=new C(),source=ctx.createMediaElementSource(audio),split=ctx.createChannelSplitter(2),left=ctx.createAnalyser(),right=ctx.createAnalyser(),spec=ctx.createAnalyser(),normal=ctx.createGain(),lm=ctx.createGain(),rm=ctx.createGain(),merger=ctx.createChannelMerger(1),mono=ctx.createGain();left.fftSize=2048;right.fftSize=2048;spec.fftSize=2048;spec.smoothingTimeConstant=.76;source.connect(spec);spec.connect(normal);normal.connect(ctx.destination);source.connect(split);split.connect(left,0);split.connect(right,1);left.connect(lm);right.connect(rm);lm.gain.value=.5;rm.gain.value=.5;lm.connect(merger,0,0);rm.connect(merger,0,0);merger.connect(mono);mono.connect(ctx.destination);mono.gain.value=0;state.graph={ctx,left,right,spec,normal,mono};return state.graph}
 function db(v){return v>1e-7?20*Math.log10(v):-Infinity}function dbText(v){return Number.isFinite(v)?`${v.toFixed(1)} dB`:'−∞'}function needle(v){return -48+clamp((v+30)/30,0,1)*96}
 function responseConfig(){return state.response==='steady'?{interval:250,smooth:.14,attack:.38,release:.10,hold:700,decay:.24}:state.response==='fast'?{interval:60,smooth:.35,attack:.65,release:.28,hold:300,decay:.48}:{interval:125,smooth:.23,attack:.50,release:.17,hold:500,decay:.34}}
 function meters(now,updateReadout){if(!state.graph)return;const cfg=responseConfig(),{left,right,spec}=state.graph,n=left.fftSize,l=new Float32Array(n),r=new Float32Array(n);left.getFloatTimeDomainData(l);right.getFloatTimeDomainData(r);let ls=0,rs=0,cross=0,peak=0;for(let i=0;i<n;i++){ls+=l[i]*l[i];rs+=r[i]*r[i];cross+=l[i]*r[i];peak=Math.max(peak,Math.abs(l[i]),Math.abs(r[i]))}const lr=Math.sqrt(ls/n),rr=Math.sqrt(rs/n),rms=Math.sqrt((ls+rs)/(2*n)),corr=(ls>1e-12&&rs>1e-12)?cross/Math.sqrt(ls*rs):1,mid=Math.sqrt(Math.max((ls+2*cross+rs)/(4*n),0)),side=Math.sqrt(Math.max((ls-2*cross+rs)/(4*n),0)),width=(mid+side)>1e-9?100*side/(mid+side):0,balance=rr>1e-8&&lr>1e-8?20*Math.log10(rr/lr):0,pdb=db(peak),rdb=db(rms),safePeak=Number.isFinite(pdb)?pdb:-60,safeRms=Number.isFinite(rdb)?rdb:-60;if(safePeak>=state.peakDb){state.peakDb=safePeak;state.peakHoldUntil=now+cfg.hold}else if(now>state.peakHoldUntil){state.peakDb=Math.max(safePeak,state.peakDb-cfg.decay)}state.rmsDb=state.rmsDb*(1-cfg.smooth)+safeRms*cfg.smooth;state.balance=state.balance*(1-cfg.smooth)+balance*cfg.smooth;state.width=state.width*(1-cfg.smooth)+width*cfg.smooth;state.correlation=state.correlation*(1-cfg.smooth)+corr*cfg.smooth;const peakTarget=needle(state.peakDb),rmsTarget=needle(state.rmsDb);state.peakAngle+=(peakTarget-state.peakAngle)*(peakTarget>state.peakAngle?cfg.attack:cfg.release);state.rmsAngle+=(rmsTarget-state.rmsAngle)*cfg.smooth;q('.needle').style.transform=`translateX(-50%) rotate(${state.peakAngle}deg)`;q('.rms-needle').style.transform=`translateX(-50%) rotate(${state.rmsAngle}deg)`;if(updateReadout){q('.peak-value').textContent=dbText(state.peakDb);q('.rms-value').textContent=dbText(state.rmsDb);q('.balance-value').textContent=Math.abs(state.balance)<.15?'CENTER':`${state.balance>0?'R':'L'} +${Math.abs(state.balance).toFixed(1)} dB`;q('.width-value').textContent=`${state.width.toFixed(0)}% SIDE`;q('.phase-value').textContent=`${state.correlation>=0?'+':''}${state.correlation.toFixed(2)}`;q('.phase-lamp').classList.toggle('warn',state.correlation<.2)}drawSpectrum(spec)}
 function drawSpectrum(analyser){const[w,h,r]=fit(spectrum,sc),bins=new Uint8Array(analyser.frequencyBinCount);analyser.getByteFrequencyData(bins);sc.clearRect(0,0,w,h);sc.fillStyle='#101a14';sc.fillRect(0,0,w,h);sc.strokeStyle='rgba(216,201,167,.08)';for(let i=1;i<5;i++){sc.beginPath();sc.moveTo(0,h*i/5);sc.lineTo(w,h*i/5);sc.stroke()}const sr=state.graph.ctx.sampleRate,lo=Math.log10(20),hi=Math.log10(20000);sc.beginPath();for(let x=0;x<w;x+=Math.max(2,r)){const freq=Math.pow(10,lo+(x/w)*(hi-lo)),bin=Math.min(bins.length-1,Math.round(freq/(sr/2)*bins.length)),v=bins[bin]/255,y=h-v*h*.92;x===0?sc.moveTo(x,y):sc.lineTo(x,y)}sc.lineTo(w,h);sc.lineTo(0,h);sc.closePath();const g=sc.createLinearGradient(0,0,0,h);g.addColorStop(0,'rgba(217,154,69,.82)');g.addColorStop(1,'rgba(61,84,60,.15)');sc.fillStyle=g;sc.fill();sc.strokeStyle='#d99a45';sc.stroke()}
 function frame(now=performance.now()){drawWave();const updateReadout=now-state.lastReadout>=responseConfig().interval;meters(now,updateReadout);if(updateReadout)state.lastReadout=now;if(!audio.paused)state.raf=requestAnimationFrame(frame)}
 q('[data-action="play"]').onclick=()=>{const g=setupGraph();g.ctx.resume();audio.play();q('.monitor-unit').classList.add('powered');if(state.raf)cancelAnimationFrame(state.raf);frame()};q('[data-action="stop"]').onclick=()=>{audio.pause();q('.monitor-unit').classList.remove('powered');if(state.raf)cancelAnimationFrame(state.raf);state.raf=null;drawWave()};q('[data-action="mono"]').onclick=()=>{const g=setupGraph();state.mono=!state.mono;g.normal.gain.setTargetAtTime(state.mono?0:1,g.ctx.currentTime,.01);g.mono.gain.setTargetAtTime(state.mono?1:0,g.ctx.currentTime,.01);const b=q('[data-action="mono"]');b.classList.toggle('active',state.mono);b.setAttribute('aria-pressed',String(state.mono));b.textContent=`MONO CHECK / ${state.mono?'ON':'OFF'}`};parentElement.querySelectorAll('[data-response]').forEach(button=>{button.classList.toggle('active',button.dataset.response===state.response);button.onclick=()=>{state.response=button.dataset.response;state.lastReadout=0;parentElement.querySelectorAll('[data-response]').forEach(item=>item.classList.toggle('active',item===button))}});wave.onclick=e=>{if(!audio.duration)return;const b=wave.getBoundingClientRect();audio.currentTime=clamp((e.clientX-b.left)/b.width,0,1)*audio.duration;drawWave()};audio.onended=()=>{q('.monitor-unit').classList.remove('powered');state.raf=null;drawWave()};if(!state.observer){state.observer=new ResizeObserver(()=>{drawWave();if(state.graph)drawSpectrum(state.graph.spec)});state.observer.observe(q('.monitor-unit'))}drawWave();
}
"""


_mastering_monitor = st.components.v2.component(
    "vibes_supplier_mastering_monitor_v6",
    html=MONITOR_HTML,
    css=MONITOR_CSS,
    js=MONITOR_JS,
)


def live_mastering_monitor(
    audio_data: bytes,
    mime_type: str,
    audio_id: str,
    *,
    key: str,
) -> None:
    """Render a live browser monitor without returning uploaded audio data."""
    encoded = base64.b64encode(audio_data).decode("ascii")
    _mastering_monitor(
        key=key,
        data={
            "audio_url": f"data:{mime_type};base64,{encoded}",
            "audio_id": audio_id,
        },
        height=680,
    )
