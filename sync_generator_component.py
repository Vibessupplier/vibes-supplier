"""Browser-side tempo clock and metronome for timing calculators."""

from typing import Any, Callable

import streamlit as st


SYNC_HTML = """
<section class="sync-unit">
  <div class="plate"><span>VS SYNC GENERATOR / 07</span><span><i></i> CLOCK READY</span></div>
  <div class="display">
    <div class="tempo-control"><small>TEMPO</small><div class="tempo-entry"><button data-action="down">−</button><input class="bpm-readout" type="number" min="20" max="300" step="0.1" value="120.0" aria-label="Tempo in BPM"/><button data-action="up">+</button></div><em>BPM · DRAG / WHEEL / TYPE</em></div>
    <div class="beats"></div>
  </div>
  <div class="controls">
    <button data-action="play">▶ PLAY</button><button data-action="stop">■ STOP</button>
    <button class="tap" data-action="tap">TAP TEMPO</button>
    <label class="cycle-label">CYCLE<select class="cycle"><option>4</option><option selected>8</option><option>16</option><option>32</option></select></label>
    <label>CLICK / ECHO DIVISION<select>
      <option value="2">1/2 · STRAIGHT</option><option value="3">1/2 · DOTTED</option><option value="1.3333333333">1/2 · TRIPLET</option>
      <option value="1" selected>1/4 · STRAIGHT</option><option value="1.5">1/4 · DOTTED</option><option value="0.6666666667">1/4 · TRIPLET</option>
      <option value="0.5">1/8 · STRAIGHT</option><option value="0.75">1/8 · DOTTED</option><option value="0.3333333333">1/8 · TRIPLET</option>
      <option value="0.25">1/16 · STRAIGHT</option><option value="0.375">1/16 · DOTTED</option><option value="0.1666666667">1/16 · TRIPLET</option>
      <option value="0.125">1/32 · STRAIGHT</option><option value="0.1875">1/32 · DOTTED</option><option value="0.0833333333">1/32 · TRIPLET</option>
    </select></label>
  </div>
  <p>FIRST BEAT ACCENT · BROWSER-GENERATED CLICK · NO AUDIO UPLOAD</p>
</section>
"""

SYNC_CSS = """
.sync-unit{padding:13px;border:1px solid #68685f;border-radius:3px;background:repeating-linear-gradient(98deg,transparent 0 8px,rgba(255,255,255,.018) 9px),linear-gradient(145deg,#30312c,#151814 65%,#30251b);box-shadow:inset 0 0 0 3px rgba(0,0,0,.28),0 9px 18px rgba(0,0,0,.28);color:#eee3c7;font-family:"Avenir Next",Arial,sans-serif}.plate{display:flex;justify-content:space-between;padding:1px 3px 10px;color:#d8c9a7;font:700 9px SFMono-Regular,Menlo,monospace;letter-spacing:.13em}.plate span:last-child{color:rgba(216,201,167,.55)}.plate i{display:inline-block;width:7px;height:7px;margin-right:6px;border-radius:50%;background:#87966c;box-shadow:0 0 7px rgba(135,150,108,.6)}.display{display:grid;grid-template-columns:210px 1fr;gap:12px;padding:12px;border:3px solid #0b0e0b;background:linear-gradient(rgba(238,227,199,.07),transparent),#172219;box-shadow:inset 0 7px 16px rgba(0,0,0,.45),0 0 0 2px #53544d}.tempo-control{display:grid;gap:5px;align-content:center}.display small,.display em{color:#899174;font:700 7px SFMono-Regular,Menlo,monospace;letter-spacing:.1em}.tempo-entry{display:grid;grid-template-columns:32px 1fr 32px;gap:5px}.tempo-entry button{border:1px solid rgba(216,201,167,.28);border-radius:2px;background:#202a22;color:#d8c9a7;font:700 18px SFMono-Regular,Menlo,monospace;cursor:pointer}.bpm-readout{box-sizing:border-box;width:100%;border:1px solid rgba(217,154,69,.4);outline:0;background:#101a14;color:#d99a45;font:700 28px SFMono-Regular,Menlo,monospace;text-align:center;text-shadow:0 0 8px rgba(217,154,69,.18);cursor:ns-resize;-moz-appearance:textfield}.bpm-readout::-webkit-inner-spin-button{display:none}.bpm-readout:focus{border-color:#d99a45}.beats{display:grid;grid-template-columns:repeat(var(--steps,8),minmax(5px,1fr));gap:4px;align-content:center}.beats b{display:grid;place-items:center;min-height:45px;border:1px solid rgba(137,145,116,.32);color:rgba(216,201,167,.35);font:700 9px SFMono-Regular,Menlo,monospace}.beats b.active{color:#171815;background:#d99a45;box-shadow:inset 0 0 9px rgba(255,244,196,.4),0 0 8px rgba(217,154,69,.25)}.beats b.accent.active{background:#eee3c7}.controls{display:flex;align-items:stretch;gap:7px;padding-top:12px}.controls button,.controls select{min-height:38px;border:1px solid rgba(216,201,167,.3);border-radius:2px;background:linear-gradient(#29332b,#182019);color:#eee3c7;font:700 9px SFMono-Regular,Menlo,monospace;letter-spacing:.07em;cursor:pointer;box-shadow:0 2px 0 #080b08}.controls button:active{transform:translateY(2px);box-shadow:none}.controls .tap{border-color:#d99a45;color:#d99a45}.controls label{display:grid;grid-template-columns:auto 155px;align-items:center;gap:8px;margin-left:auto;color:rgba(216,201,167,.58);font:700 7px SFMono-Regular,Menlo,monospace;letter-spacing:.08em}.controls .cycle-label{grid-template-columns:auto 58px;margin-left:0}.controls select{padding:0 7px}.sync-unit p{margin:10px 2px 0;color:rgba(216,201,167,.38);font:600 7px SFMono-Regular,Menlo,monospace;letter-spacing:.09em}@media(max-width:760px){.controls{flex-wrap:wrap}.controls label{margin-left:0}}@media(max-width:620px){.display{grid-template-columns:1fr}.controls label{width:100%;grid-template-columns:1fr 155px}.controls .cycle-label{width:auto;grid-template-columns:auto 65px}.beats b{min-height:28px;font-size:7px}}
"""

SYNC_JS = """
export default function(component){
 const{data,parentElement,setTriggerValue}=component,q=s=>parentElement.querySelector(s),readout=q('.bpm-readout'),beats=q('.beats'),division=parentElement.querySelector('.controls label:last-of-type select'),cycleSelect=q('.cycle'),clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
 let state=parentElement.__vsSync;if(!state){state={playing:false,timer:null,nextTime:0,tick:0,taps:[],ctx:null,bpm:Number(data.bpm)||120,cycle:8,drag:null};parentElement.__vsSync=state}
 const incomingBpm=Number(data.bpm)||120;if(Math.abs(incomingBpm-state.bpm)>.001&&!state.drag){state.bpm=incomingBpm;if(state.playing&&state.ctx){state.nextTime=state.ctx.currentTime+.04;state.tick=0}}readout.value=state.bpm.toFixed(1);cycleSelect.value=String(state.cycle);
 function renderBeats(){beats.style.setProperty('--steps',state.cycle);beats.innerHTML=Array.from({length:state.cycle},(_,i)=>`<b>${i+1}</b>`).join('')}renderBeats();
 function updateDivisionLabel(){const option=division.options[division.selectedIndex],milliseconds=60000/state.bpm*Number(division.value);option.dataset.baseLabel=option.dataset.baseLabel||option.textContent.split(' · ')[0]+' · '+option.textContent.split(' · ')[1];[...division.options].forEach(item=>{const base=item.dataset.baseLabel||(item.dataset.baseLabel=item.textContent);item.textContent=`${base} · ${(60000/state.bpm*Number(item.value)).toFixed(2)} ms`})}updateDivisionLabel();
 function click(time,accent){const ctx=state.ctx,osc=ctx.createOscillator(),gain=ctx.createGain();osc.frequency.value=accent?1450:920;gain.gain.setValueAtTime(.0001,time);gain.gain.exponentialRampToValueAtTime(accent ? .32 : .20,time+.002);gain.gain.exponentialRampToValueAtTime(.0001,time+.045);osc.connect(gain).connect(ctx.destination);osc.start(time);osc.stop(time+.055)}
 function schedule(){if(!state.playing)return;const factor=Number(division.value),interval=60/state.bpm*factor;while(state.nextTime<state.ctx.currentTime+.1){const index=state.tick%state.cycle,accent=index===0;click(state.nextTime,accent);const delay=Math.max(0,(state.nextTime-state.ctx.currentTime)*1000);setTimeout(()=>{[...beats.children].forEach((el,i)=>el.classList.toggle('active',i===index));beats.firstElementChild?.classList.toggle('accent',index===0)},delay);state.nextTime+=interval;state.tick++}state.timer=setTimeout(schedule,25)}
 q('[data-action="play"]').onclick=()=>{if(state.playing)return;state.ctx=state.ctx||new(window.AudioContext||window.webkitAudioContext)();state.ctx.resume();state.playing=true;state.nextTime=state.ctx.currentTime+.05;state.tick=0;schedule()};
 q('[data-action="stop"]').onclick=()=>{state.playing=false;clearTimeout(state.timer);[...beats.children].forEach(el=>el.classList.remove('active','accent'))};
 function setBpm(value){state.bpm=Math.round(clamp(Number(value)||120,20,300)*10)/10;readout.value=state.bpm.toFixed(1);updateDivisionLabel();if(state.playing&&state.ctx){state.nextTime=state.ctx.currentTime+.04;state.tick=0}}
 function commitBpm(){setTriggerValue('bpm',{value:state.bpm,nonce:Date.now()})}
 q('[data-action="down"]').onclick=()=>{setBpm(state.bpm-1);commitBpm()};q('[data-action="up"]').onclick=()=>{setBpm(state.bpm+1);commitBpm()};
 readout.onchange=()=>{setBpm(readout.value);commitBpm()};readout.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();readout.blur()}};
 readout.onwheel=e=>{e.preventDefault();setBpm(state.bpm+(e.deltaY<0?1:-1));clearTimeout(state.wheelCommit);state.wheelCommit=setTimeout(commitBpm,180)};
 readout.onpointerdown=e=>{state.drag={y:e.clientY,bpm:state.bpm};readout.setPointerCapture(e.pointerId)};readout.onpointermove=e=>{if(state.drag)setBpm(state.drag.bpm+(state.drag.y-e.clientY)*.2)};readout.onpointerup=e=>{if(!state.drag)return;state.drag=null;readout.releasePointerCapture(e.pointerId);commitBpm()};
 q('[data-action="tap"]').onclick=()=>{const now=performance.now();state.taps=state.taps.filter(value=>now-value<2500);state.taps.push(now);if(state.taps.length>1){const gaps=state.taps.slice(1).map((value,index)=>value-state.taps[index]),bpm=60000/(gaps.reduce((a,b)=>a+b,0)/gaps.length);setBpm(bpm);commitBpm()}};
 cycleSelect.onchange=()=>{state.cycle=Number(cycleSelect.value);state.tick=0;renderBeats()};
 division.onchange=()=>{updateDivisionLabel();if(state.playing){state.nextTime=state.ctx.currentTime+.04;state.tick=0}};
}
"""

_sync_generator = st.components.v2.component(
    "vibes_supplier_sync_generator_v3", html=SYNC_HTML, css=SYNC_CSS, js=SYNC_JS
)


def sync_generator(bpm: float, *, key: str, on_bpm_change: Callable[[], None]) -> Any:
    return _sync_generator(key=key, data={"bpm": bpm}, height=285, on_bpm_change=on_bpm_change)
