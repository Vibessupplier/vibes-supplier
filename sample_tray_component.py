"""Compact browser-side four-slot sample memory for Audio Chopper."""

import base64
from typing import Any, Callable

import streamlit as st


TRAY_HTML = """
<section class="memory-unit">
  <div class="plate-label"><span>VS SAMPLE MEMORY / 4 SLOT</span><span class="memory-state"><i></i> OUTPUT READY</span></div>
  <div class="lcd-glass">
    <div class="lcd-header"><span>PROGRAM</span><span>NAME</span><span>TIME</span><span>TRANSPORT</span></div>
    <div class="slots"></div>
    <div class="lcd-footer"><span class="memory-count">MEMORY 00/04</span><span>44.1 / SAMPLE BANK</span></div>
    <div class="glass-reflection"></div>
  </div>
  <div class="memory-note">CLICK THE NAME TO RENAME · ONLY ONE SLOT PLAYS AT A TIME</div>
  <audio preload="auto"></audio>
</section>
"""


TRAY_CSS = """
.memory-unit{padding:12px;border:1px solid #595950;border-radius:4px;background:radial-gradient(circle at 8% 18%,rgba(111,62,39,.38) 0 2px,transparent 3px),repeating-linear-gradient(108deg,transparent 0 10px,rgba(126,72,43,.045) 11px 12px),linear-gradient(145deg,#343630,#10120f 58%,#282a25);box-shadow:inset 0 1px rgba(238,227,199,.08),inset 0 0 0 3px rgba(0,0,0,.26),0 7px 14px rgba(0,0,0,.25);color:#172219;font-family:SFMono-Regular,Menlo,monospace;user-select:none}
.plate-label{display:flex;justify-content:space-between;padding:0 3px 9px;color:#d8c9a7;font-size:9px;font-weight:700;letter-spacing:.11em}.memory-state{display:flex;align-items:center;gap:7px;color:rgba(216,201,167,.54)}.memory-state i{width:7px;height:7px;border-radius:50%;background:#d99a45;box-shadow:0 0 6px rgba(217,154,69,.35)}
.lcd-glass{position:relative;overflow:hidden;padding:10px;border:2px solid #11130f;border-radius:3px;background:radial-gradient(circle at 20% 20%,rgba(238,227,199,.12),transparent 34%),linear-gradient(180deg,#949d83,#7e8973 58%,#727d69);box-shadow:inset 0 7px 14px rgba(23,34,25,.22),inset 0 -6px 11px rgba(238,227,199,.08),0 0 0 3px #4b4c45,0 0 0 5px rgba(0,0,0,.36)}
.lcd-header,.slot-row{display:grid;grid-template-columns:58px minmax(130px,1fr) 72px 122px;align-items:center;gap:8px}.lcd-header{padding:0 7px 6px;border-bottom:1px solid rgba(23,34,25,.34);color:rgba(23,34,25,.62);font-size:7px;font-weight:700;letter-spacing:.12em}.slot-row{position:relative;min-height:40px;padding:3px 7px;border-bottom:1px solid rgba(23,34,25,.22)}.slot-row:last-child{border-bottom:0}.slot-number{font-size:13px;font-weight:800}.slot-number i{display:inline-block;width:6px;height:6px;margin-right:7px;border-radius:50%;background:rgba(23,34,25,.18)}.slot-row.playing .slot-number i{background:#8b4d24;box-shadow:0 0 4px rgba(139,77,36,.42)}.slot-name{overflow:hidden;border:0;background:transparent;color:#172219;font:800 12px SFMono-Regular,Menlo,monospace;text-align:left;text-overflow:ellipsis;white-space:nowrap;cursor:text}.slot-name:hover{text-decoration:underline;text-decoration-style:dotted}.slot-name-input{box-sizing:border-box;width:100%;border:0;border-bottom:1px solid #172219;outline:0;background:rgba(238,227,199,.12);color:#172219;font:800 12px SFMono-Regular,Menlo,monospace}.slot-time{font-size:10px;font-weight:700}.slot-actions{display:flex;justify-content:flex-end;gap:4px}.slot-actions button{width:34px;height:27px;padding:0;border:1px solid rgba(23,34,25,.38);border-radius:2px;background:rgba(238,227,199,.10);color:#172219;font:800 10px SFMono-Regular,Menlo,monospace;cursor:pointer;box-shadow:0 1px rgba(238,227,199,.2)}.slot-actions button:hover{background:rgba(238,227,199,.26)}.slot-actions .remove{color:#703d2f}.slot-row.empty{color:rgba(23,34,25,.34)}.slot-row.empty .slot-name{cursor:default;color:rgba(23,34,25,.34);text-decoration:none}.progress-track{position:absolute;right:7px;bottom:2px;left:73px;height:3px;background:repeating-linear-gradient(90deg,rgba(23,34,25,.18) 0 7%,transparent 7% 9%)}.progress-fill{display:block;width:0;height:100%;background:#354b38}.lcd-footer{display:flex;justify-content:space-between;padding:8px 7px 0;border-top:1px solid rgba(23,34,25,.28);color:rgba(23,34,25,.64);font-size:8px;font-weight:800;letter-spacing:.08em}.glass-reflection{position:absolute;inset:-35% -20% 55% 18%;border-radius:50%;background:linear-gradient(128deg,rgba(255,255,255,.16),transparent 45%);pointer-events:none;transform:rotate(-4deg)}.memory-note{padding:10px 2px 0;color:rgba(216,201,167,.42);font-size:7px;font-weight:600;letter-spacing:.07em}audio{display:none}
@media(max-width:620px){.lcd-header{display:none}.slot-row{grid-template-columns:45px 1fr 58px;gap:5px}.slot-actions{grid-column:1/-1;justify-content:flex-start;padding-left:50px}.progress-track{left:57px}.lcd-footer{font-size:6px}}
"""


TRAY_JS = """
export default function(component){
 const{data,parentElement,setTriggerValue}=component,q=s=>parentElement.querySelector(s),slots=q('.slots'),audio=q('audio');
 const esc=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
 let state=parentElement.__vsSampleMemory;if(!state){state={activeId:null};parentElement.__vsSampleMemory=state}
 function time(seconds){const value=Number(seconds)||0;return `${Math.floor(value/60)}:${String(Math.floor(value%60)).padStart(2,'0')}.${Math.floor(value%1*10)}`}
 function render(){const samples=data.samples||[],rows=[];for(let index=0;index<4;index++){const sample=samples[index],number=String(index+1).padStart(2,'0');if(sample){const playing=state.activeId===sample.id&&!audio.paused;rows.push(`<div class="slot-row${playing?' playing':''}" data-id="${sample.id}"><span class="slot-number"><i></i>${number}</span><button class="slot-name" type="button" title="Rename sample">${esc(sample.name)}</button><span class="slot-time">${time(sample.duration)}</span><span class="slot-actions"><button type="button" class="play" aria-label="Play ${esc(sample.name)}">▶</button><button type="button" class="stop" aria-label="Stop sample">■</button><button type="button" class="remove" aria-label="Remove ${esc(sample.name)}">×</button></span><span class="progress-track"><i class="progress-fill"></i></span></div>`)}else rows.push(`<div class="slot-row empty"><span class="slot-number"><i></i>${number}</span><span class="slot-name">— EMPTY —</span><span class="slot-time">—:—</span><span></span></div>`)}slots.innerHTML=rows.join('');q('.memory-count').textContent=`MEMORY ${String(samples.length).padStart(2,'0')}/04`;slots.querySelectorAll('.slot-row[data-id]').forEach(row=>{const id=Number(row.dataset.id),sample=samples.find(item=>item.id===id);row.querySelector('.play').onclick=()=>{if(state.activeId!==id){audio.src=sample.audio_url;state.activeId=id}audio.play();render()};row.querySelector('.stop').onclick=()=>{audio.pause();audio.currentTime=0;state.activeId=null;render()};row.querySelector('.remove').onclick=()=>{if(state.activeId===id){audio.pause();state.activeId=null}setTriggerValue('action',{type:'remove',id,nonce:Date.now()})};row.querySelector('.slot-name').onclick=()=>editName(row,sample)})}
 function editName(row,sample){const button=row.querySelector('.slot-name'),input=document.createElement('input');input.className='slot-name-input';input.value=sample.name;button.replaceWith(input);input.focus();input.select();const save=()=>{const name=input.value.trim();if(name&&name!==sample.name)setTriggerValue('action',{type:'rename',id:sample.id,name,nonce:Date.now()});else render()};input.onblur=save;input.onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();input.blur()}if(event.key==='Escape'){event.preventDefault();render()}}}
 audio.ontimeupdate=()=>{if(state.activeId===null||!audio.duration)return;const row=slots.querySelector(`[data-id="${state.activeId}"]`),fill=row?.querySelector('.progress-fill');if(fill)fill.style.width=`${Math.min(100,audio.currentTime/audio.duration*100)}%`};audio.onended=()=>{state.activeId=null;render()};render();
}
"""


_sample_tray = st.components.v2.component(
    "vibes_supplier_sample_memory_v1",
    html=TRAY_HTML,
    css=TRAY_CSS,
    js=TRAY_JS,
)


def sample_memory(
    samples: list[dict[str, Any]],
    *,
    key: str,
    on_action_change: Callable[[], None],
) -> Any:
    """Render compact sample playback and editing without native audio widgets."""
    component_samples = [
        {
            "id": sample["id"],
            "name": sample["name"],
            "duration": sample["end"] - sample["start"],
            "audio_url": "data:audio/mpeg;base64,"
            + base64.b64encode(sample["audio"]).decode("ascii"),
        }
        for sample in samples
    ]
    return _sample_tray(
        key=key,
        data={"samples": component_samples},
        height=310,
        on_action_change=on_action_change,
    )
