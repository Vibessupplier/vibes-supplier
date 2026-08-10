"""Lightweight synchronized browser-side A/B mastering player."""

import base64

import streamlit as st


AB_HTML = """
<section class="ab-unit">
  <div class="unit-label"><span>VS MASTERING / A-B DECK</span><span class="sync-lamp"><i></i> SYNC READY</span></div>
  <div class="transport">
    <button type="button" data-action="play">▶ PLAY BOTH</button>
    <button type="button" data-action="stop">■ STOP</button>
    <span class="time">0:00 / 0:00</span>
    <span class="listening-mode"></span>
    <div class="monitor-level">
      <div class="monitor-knob" role="slider" tabindex="0" aria-label="A/B listening volume only" aria-valuemin="-60" aria-valuemax="0" aria-valuenow="0"></div>
      <div><span>MONITOR LEVEL</span><strong class="monitor-value">0 dB</strong><small>LISTENING ONLY · METERS UNAFFECTED</small></div>
      <button type="button" class="mute" data-action="mute" aria-pressed="false">MUTE</button>
    </div>
  </div>
  <input class="timeline" type="range" min="0" max="1000" value="0" aria-label="Synchronized A/B playhead" />
  <div class="source-switch" role="group" aria-label="Choose the audible master">
    <button type="button" class="active" data-source="a"><small>A / REFERENCE</small><strong>LISTEN A</strong><i></i></button>
    <div class="switch-label"><span>INSTANT A / B</span><b>ONLY ONE SOURCE IS AUDIBLE</b></div>
    <button type="button" data-source="b"><small>B / YOUR MASTER</small><strong>LISTEN B</strong><i></i></button>
  </div>
  <div class="comparison-meters">
    <div class="module-label"><span>LOUDNESS COMPARISON</span><small>GLOBAL VALUES · LIVE RMS MARKERS</small></div>
    <div class="metric-row lufs-row">
      <div class="metric-label"><b>INTEGRATED LUFS</b><small>FULL-TRACK / FFmpeg</small></div>
      <div class="metric-source"><span>A / REFERENCE <strong class="a-lufs-value"></strong></span><div class="meter-track"><i class="a-lufs-fill"></i></div></div>
      <div class="metric-source"><span>B / YOUR MASTER <strong class="b-lufs-value"></strong></span><div class="meter-track"><i class="b-lufs-fill"></i></div></div>
    </div>
    <div class="metric-row rms-row">
      <div class="metric-label"><b>RMS LEVEL</b><small>GLOBAL BAR / LIVE MARKER</small></div>
      <div class="metric-source"><span>A / REFERENCE <strong class="a-rms-value"></strong></span><div class="meter-track"><i class="a-rms-fill"></i><em class="a-rms-live"></em></div></div>
      <div class="metric-source"><span>B / YOUR MASTER <strong class="b-rms-value"></strong></span><div class="meter-track"><i class="b-rms-fill"></i><em class="b-rms-live"></em></div></div>
    </div>
    <div class="meter-scale"><span>−36</span><span>−24</span><span>−18</span><span>−12</span><span>−6</span><span>0</span></div>
  </div>
  <p class="note">A AND B RUN AT THE SAME PLAYHEAD, BUT ONLY THE SELECTED SOURCE REACHES THE MONITOR OUTPUT. INTEGRATED LUFS AND GLOBAL RMS REMAIN THE AUTHORITATIVE ORIGINAL-FILE RESULTS.</p>
  <audio class="audio-a" preload="auto"></audio><audio class="audio-b" preload="auto"></audio>
</section>
"""


AB_CSS = """
.ab-unit{padding:13px;border:1px solid rgba(216,201,167,.28);border-radius:3px;background:linear-gradient(180deg,rgba(119,118,107,.08),transparent 28%),rgba(23,24,21,.95);box-shadow:inset 0 0 0 3px rgba(0,0,0,.16);color:#eee3c7;font-family:"Avenir Next",Arial,sans-serif;user-select:none}
.unit-label,.module-label{display:flex;justify-content:space-between;align-items:center;color:#d8c9a7;font:600 10px SFMono-Regular,Menlo,monospace;letter-spacing:.12em}.unit-label{padding:3px 3px 10px}.sync-lamp{display:flex;align-items:center;gap:7px;color:rgba(216,201,167,.62)}.sync-lamp i{width:7px;height:7px;border-radius:50%;background:#87966c;box-shadow:0 0 7px rgba(135,150,108,.45)}
.transport{display:flex;align-items:center;gap:7px}.transport button,.source-switch button{min-height:35px;padding:0 12px;border:1px solid rgba(216,201,167,.28);border-radius:2px;background:linear-gradient(#273229,#19221b);color:#d8c9a7;font-size:9px;font-weight:700;letter-spacing:.07em;cursor:pointer;box-shadow:0 2px 0 #090d0a}.transport button:hover,.source-switch button:hover{border-color:#d99a45;color:#eee3c7}.transport button:active,.source-switch button:active{transform:translateY(2px);box-shadow:none}.time{color:#d99a45;font:600 11px SFMono-Regular,Menlo,monospace}.listening-mode{margin-left:auto;color:#87966c;font:600 8px SFMono-Regular,Menlo,monospace;letter-spacing:.09em}.timeline{box-sizing:border-box;width:100%;margin:12px 0 10px;accent-color:#d99a45;cursor:pointer}.monitor-level{display:grid;grid-template-columns:44px auto 48px;align-items:center;gap:8px;padding:5px 6px;border:1px solid rgba(216,201,167,.18);background:rgba(48,37,27,.34)}.monitor-knob{--angle:135deg;position:relative;width:38px;height:38px;border:2px solid #77766b;border-radius:50%;background:radial-gradient(circle at 36% 30%,#69685f 0 6%,transparent 7%),radial-gradient(circle,#343631 0 50%,#20221e 51% 68%,#77766b 69% 72%,#171815 73%);box-shadow:inset 0 0 0 2px rgba(0,0,0,.3),0 3px 5px rgba(0,0,0,.42);cursor:ns-resize;transform:rotate(var(--angle))}.monitor-knob::after{content:"";position:absolute;top:4px;left:50%;width:2px;height:12px;background:#eee3c7;transform:translateX(-50%)}.monitor-knob:focus{outline:2px solid rgba(217,154,69,.6);outline-offset:2px}.monitor-level div:nth-child(2)>span,.monitor-level small{display:block;color:rgba(216,201,167,.58);font:600 7px SFMono-Regular,Menlo,monospace;letter-spacing:.08em;white-space:nowrap}.monitor-level strong{display:block;margin:2px 0;color:#d99a45;font:600 10px SFMono-Regular,Menlo,monospace}.monitor-level small{color:rgba(216,201,167,.35);font-size:6px}.transport .monitor-level .mute{min-height:27px;padding:0 7px;font-size:7px}.transport .monitor-level .mute.active{border-color:#b85f3d;color:#d77961;background:rgba(184,95,61,.12)}
.source-switch{display:grid;grid-template-columns:1fr 150px 1fr;gap:8px;align-items:stretch}.source-switch button{position:relative;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;min-height:60px}.source-switch button small{color:rgba(216,201,167,.52);font:600 7px SFMono-Regular,Menlo,monospace}.source-switch button strong{margin-top:5px;font:700 11px SFMono-Regular,Menlo,monospace}.source-switch button i{position:absolute;right:12px;width:8px;height:8px;border-radius:50%;background:#353931}.source-switch button.active{border-color:#d99a45;background:linear-gradient(rgba(217,154,69,.14),rgba(48,37,27,.72));color:#d99a45;box-shadow:inset 3px 0 0 #d99a45,0 2px 0 #090d0a}.source-switch button.active i{background:#d99a45;box-shadow:0 0 8px rgba(217,154,69,.6)}.switch-label{display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px solid rgba(216,201,167,.12);background:#101a14;text-align:center}.switch-label span{color:#d8c9a7;font:700 8px SFMono-Regular,Menlo,monospace;letter-spacing:.1em}.switch-label b{margin-top:5px;color:rgba(216,201,167,.36);font:600 6px SFMono-Regular,Menlo,monospace;letter-spacing:.06em}
.comparison-meters{margin-top:10px;padding:11px;border:1px solid rgba(216,201,167,.17);background:rgba(28,40,30,.78);box-shadow:inset 0 0 0 2px rgba(0,0,0,.12)}.module-label{padding-bottom:9px}.module-label small{color:rgba(216,201,167,.42);font-size:7px}.metric-row{display:grid;grid-template-columns:135px 1fr 1fr;gap:9px;padding:10px;border:1px solid rgba(216,201,167,.12);background:#171815}.metric-row+.metric-row{border-top:0}.metric-label{display:flex;flex-direction:column;justify-content:center}.metric-label b{color:#d8c9a7;font:700 8px SFMono-Regular,Menlo,monospace;letter-spacing:.08em}.metric-label small{margin-top:4px;color:rgba(216,201,167,.34);font:600 6px SFMono-Regular,Menlo,monospace}.metric-source span{display:flex;justify-content:space-between;color:rgba(216,201,167,.54);font:600 7px SFMono-Regular,Menlo,monospace;letter-spacing:.06em}.metric-source strong{color:#d99a45;font-size:10px}.meter-track{position:relative;overflow:hidden;height:13px;margin-top:7px;border:1px solid rgba(216,201,167,.14);background:repeating-linear-gradient(90deg,transparent 0 11%,rgba(216,201,167,.06) 11% 11.5%),#090c09;box-shadow:inset 0 1px 4px rgba(0,0,0,.72)}.meter-track i{position:absolute;inset:0 auto 0 0;width:0;background:linear-gradient(90deg,#3d543c,#87966c 72%,#d99a45);box-shadow:0 0 5px rgba(217,154,69,.22)}.meter-track em{position:absolute;z-index:2;top:-1px;bottom:-1px;left:0;width:3px;background:#eee3c7;box-shadow:0 0 6px rgba(238,227,199,.7);transform:translateX(-50%)}.meter-scale{display:flex;justify-content:space-between;margin:5px 4px 0 154px;color:rgba(216,201,167,.32);font:500 6px SFMono-Regular,Menlo,monospace}.note{margin:10px 2px 0;color:rgba(216,201,167,.42);font:500 7px/1.5 SFMono-Regular,Menlo,monospace;letter-spacing:.06em}audio{display:none}
@media(max-width:820px){.transport{flex-wrap:wrap}.listening-mode{margin-left:0}.monitor-level{margin-left:auto}}
@media(max-width:680px){.source-switch{grid-template-columns:1fr 1fr}.switch-label{display:none}.metric-row{grid-template-columns:1fr}.metric-label{padding-bottom:2px}.meter-scale{margin-left:4px}.listening-mode{width:100%}.monitor-level{width:100%;margin-left:0;grid-template-columns:44px 1fr 48px}.source-switch button{min-width:0}.note{font-size:6px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""


AB_JS = """
export default function(component){
 const{data,parentElement}=component,q=s=>parentElement.querySelector(s),clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 const a=q('.audio-a'),b=q('.audio-b'),timeline=q('.timeline');
 let state=parentElement.__vsAbDeck;
 if(!state||state.audioId!==data.audio_id){state={audioId:data.audio_id,active:'a',muted:false,monitorDb:0,graph:null,raf:null,duration:0};parentElement.__vsAbDeck=state;a.src=data.a_url;b.src=data.b_url}
 const fmt=s=>!Number.isFinite(s)?'0:00':`${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`;
 const meterPct=value=>clamp((Number(value)+36)/36,0,1)*100;
 function setGlobalMeters(){[['a','lufs'],['b','lufs'],['a','rms'],['b','rms']].forEach(([source,metric])=>{const value=Number(data[`${source}_${metric}`]);q(`.${source}-${metric}-value`).textContent=`${value.toFixed(1)} ${metric==='lufs'?'LUFS':'dBFS'}`;q(`.${source}-${metric}-fill`).style.width=`${meterPct(value)}%`});q('.listening-mode').textContent=data.volume_matched?'VOLUME MATCH / LISTENING COPIES':'ORIGINAL PLAYBACK LEVELS'}
 function monitorGain(){return state.monitorDb<=-60?0:Math.pow(10,state.monitorDb/20)}
 function updateMonitorLevel(){const knob=q('.monitor-knob'),mute=q('[data-action="mute"]');state.monitorDb=clamp(Math.round(state.monitorDb),-60,0);knob.style.setProperty('--angle',`${-135+(state.monitorDb+60)/60*270}deg`);knob.setAttribute('aria-valuenow',String(state.monitorDb));q('.monitor-value').textContent=state.monitorDb<=-60?'−∞ dB':`${state.monitorDb} dB`;mute.classList.toggle('active',state.muted);mute.setAttribute('aria-pressed',String(state.muted));mute.textContent=state.muted?'UNMUTE':'MUTE';if(state.graph)state.graph.output.gain.setTargetAtTime(state.muted?0:monitorGain(),state.graph.ctx.currentTime,.015)}
 function setMonitorLevel(value){state.monitorDb=value;updateMonitorLevel()}
 function setupGraph(){if(state.graph)return state.graph;const C=window.AudioContext||window.webkitAudioContext,ctx=new C(),sourceA=ctx.createMediaElementSource(a),sourceB=ctx.createMediaElementSource(b),analyserA=ctx.createAnalyser(),analyserB=ctx.createAnalyser(),gainA=ctx.createGain(),gainB=ctx.createGain(),output=ctx.createGain();analyserA.fftSize=1024;analyserB.fftSize=1024;sourceA.connect(analyserA);sourceB.connect(analyserB);analyserA.connect(gainA);analyserB.connect(gainB);gainA.connect(output);gainB.connect(output);output.connect(ctx.destination);output.gain.value=state.muted?0:monitorGain();state.graph={ctx,analyserA,analyserB,gainA,gainB,output};setActive(state.active,false);return state.graph}
 function setActive(source,ramp=true){state.active=source;parentElement.querySelectorAll('[data-source]').forEach(button=>button.classList.toggle('active',button.dataset.source===source));if(!state.graph)return;const{ctx,gainA,gainB}=state.graph,aValue=source==='a'?1:0,bValue=source==='b'?1:0;if(ramp){gainA.gain.setTargetAtTime(aValue,ctx.currentTime,.012);gainB.gain.setTargetAtTime(bValue,ctx.currentTime,.012)}else{gainA.gain.value=aValue;gainB.gain.value=bValue}}
 function updateDuration(){if(Number.isFinite(a.duration)&&Number.isFinite(b.duration)){state.duration=Math.min(a.duration,b.duration);timeline.max=String(Math.max(1,state.duration*1000));q('.time').textContent=`${fmt(a.currentTime)} / ${fmt(state.duration)}`}}
 function liveRms(analyser){const values=new Float32Array(analyser.fftSize);analyser.getFloatTimeDomainData(values);let sum=0;for(const value of values)sum+=value*value;const rms=Math.sqrt(sum/values.length);return rms>1e-7?20*Math.log10(rms):-60}
 function frame(){if(!state.graph)return;if(Math.abs(a.currentTime-b.currentTime)>.045)b.currentTime=a.currentTime;timeline.value=String(Math.min(state.duration,a.currentTime)*1000);q('.time').textContent=`${fmt(a.currentTime)} / ${fmt(state.duration)}`;q('.a-rms-live').style.left=`${meterPct(liveRms(state.graph.analyserA))}%`;q('.b-rms-live').style.left=`${meterPct(liveRms(state.graph.analyserB))}%`;if(!a.paused)state.raf=requestAnimationFrame(frame)}
 q('[data-action="play"]').onclick=async()=>{const graph=setupGraph();await graph.ctx.resume();updateDuration();if(a.currentTime>=state.duration-.05){a.currentTime=0;b.currentTime=0}else b.currentTime=a.currentTime;await Promise.all([a.play(),b.play()]);if(state.raf)cancelAnimationFrame(state.raf);frame()};
 q('[data-action="stop"]').onclick=()=>{a.pause();b.pause();if(state.raf)cancelAnimationFrame(state.raf);state.raf=null};
 const monitorKnob=q('.monitor-knob');monitorKnob.onwheel=event=>{event.preventDefault();setMonitorLevel(state.monitorDb+(event.deltaY<0?2:-2))};monitorKnob.onkeydown=event=>{if(['ArrowUp','ArrowRight'].includes(event.key)){event.preventDefault();setMonitorLevel(state.monitorDb+1)}if(['ArrowDown','ArrowLeft'].includes(event.key)){event.preventDefault();setMonitorLevel(state.monitorDb-1)}if(event.key==='Home'){event.preventDefault();setMonitorLevel(-60)}if(event.key==='End'){event.preventDefault();setMonitorLevel(0)}};monitorKnob.onpointerdown=event=>{monitorKnob.setPointerCapture(event.pointerId);const startY=event.clientY,startDb=state.monitorDb;monitorKnob.onpointermove=move=>setMonitorLevel(startDb+(startY-move.clientY)/2);monitorKnob.onpointerup=up=>{monitorKnob.releasePointerCapture(up.pointerId);monitorKnob.onpointermove=null}};q('[data-action="mute"]').onclick=()=>{state.muted=!state.muted;updateMonitorLevel()};updateMonitorLevel();
 parentElement.querySelectorAll('[data-source]').forEach(button=>button.onclick=()=>setActive(button.dataset.source));
 timeline.oninput=()=>{const time=Number(timeline.value)/1000;a.currentTime=time;b.currentTime=time;q('.time').textContent=`${fmt(time)} / ${fmt(state.duration)}`};
 a.onloadedmetadata=updateDuration;b.onloadedmetadata=updateDuration;a.onended=()=>{b.pause();state.raf=null};b.onended=()=>{a.pause();state.raf=null};setGlobalMeters();setActive(state.active,false);updateDuration();
}
"""


_mastering_ab = st.components.v2.component(
    "vibes_supplier_mastering_ab_v2",
    html=AB_HTML,
    css=AB_CSS,
    js=AB_JS,
)


def mastering_ab_player(
    reference_audio: bytes,
    reference_mime: str,
    track_audio: bytes,
    track_mime: str,
    *,
    reference_lufs: float,
    reference_rms: float,
    track_lufs: float,
    track_rms: float,
    volume_matched: bool,
    audio_id: str,
    key: str,
) -> None:
    """Render synchronized A/B listening with original global measurements."""
    reference_encoded = base64.b64encode(reference_audio).decode("ascii")
    track_encoded = base64.b64encode(track_audio).decode("ascii")
    _mastering_ab(
        key=key,
        data={
            "a_url": f"data:{reference_mime};base64,{reference_encoded}",
            "b_url": f"data:{track_mime};base64,{track_encoded}",
            "a_lufs": reference_lufs,
            "a_rms": reference_rms,
            "b_lufs": track_lufs,
            "b_rms": track_rms,
            "volume_matched": volume_matched,
            "audio_id": audio_id,
        },
        height=410,
    )
