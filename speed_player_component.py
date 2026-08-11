"""Browser-side live player for the Speed Changer."""

import base64
from typing import Any, Callable

import streamlit as st


SPEED_PLAYER_HTML = """
<section class="speed-unit">
    <div class="unit-label"><span>VS TRANSFORM / LIVE DECK</span><span class="lamp-label"><i></i> SIGNAL READY</span></div>
    <canvas aria-label="Audio waveform and playhead"></canvas>
    <audio preload="auto"></audio>
    <div class="transport">
        <button type="button" data-action="play">▶ PLAY</button>
        <button type="button" data-action="stop">■ STOP</button>
        <span class="time-readout">0:00 / 0:00</span>
        <span class="live-status">LIVE AUDITION</span>
        <div class="monitor-level">
            <div class="monitor-knob" role="slider" tabindex="0" aria-label="Speed deck listening volume only" aria-valuemin="-60" aria-valuemax="0" aria-valuenow="0"></div>
            <div><span>MONITOR LEVEL</span><strong class="monitor-value">0 dB</strong><small>LISTENING ONLY · EXPORT UNAFFECTED</small></div>
            <button type="button" class="mute" data-action="mute" aria-pressed="false">MUTE</button>
        </div>
    </div>
    <div class="control-grid">
        <div class="control-block bpm-source">
            <div class="source-heading"><label for="source-bpm">ORIGINAL BPM</label><button type="button" class="bpm-lock" data-action="bpm-lock" aria-pressed="true">▣ LOCKED</button></div>
            <input id="source-bpm" type="number" min="40" max="250" step="0.1" />
            <button type="button" class="bpm-reset" data-action="bpm-reset">↺ RESET TO DETECTED BPM</button>
        </div>
        <div class="control-block bpm-target">
            <label for="target-bpm">TARGET BPM <strong class="target-readout"></strong></label>
            <input id="target-bpm" type="range" step="0.1" />
            <div class="range-scale"><span class="range-min"></span><span class="range-max"></span></div>
        </div>
    </div>
    <div class="pitch-panel">
        <div class="pitch-modes" role="group" aria-label="Pitch mode">
            <button type="button" data-mode="Follow speed">FOLLOW SPEED</button>
            <button type="button" data-mode="Keep original">KEEP ORIGINAL</button>
            <button type="button" data-mode="Custom">CUSTOM</button>
        </div>
        <div class="custom-pitch" hidden>
            <button type="button" class="nudge" data-pitch="down" aria-label="Lower pitch">−</button>
            <div class="knob-wrap">
                <div class="knob" role="slider" tabindex="0" aria-label="Pitch shift" aria-valuemin="-12" aria-valuemax="12" aria-valuenow="0"><span></span></div>
                <div class="pitch-readout">+0.0 ST</div>
            </div>
            <button type="button" class="nudge" data-pitch="up" aria-label="Raise pitch">+</button>
            <p>DRAG UP / DOWN · WHEEL · ARROW KEYS</p>
        </div>
    </div>
    <div class="settings-strip"><span class="speed-readout"></span><span class="pitch-summary"></span></div>
    <div class="unit-actions">
        <button type="button" class="preview" data-action="preview" hidden>CREATE CUSTOM PITCH PREVIEW</button>
        <button type="button" class="process" data-action="process">CHANGE SPEED</button>
    </div>
</section>
"""


SPEED_PLAYER_CSS = """
.speed-unit { padding:13px; border:1px solid rgba(216,201,167,.28); border-radius:3px; background:linear-gradient(180deg,rgba(119,118,107,.08),transparent 28%),rgba(23,24,21,.95); box-shadow:inset 0 0 0 3px rgba(0,0,0,.16); color:#eee3c7; font-family:"Avenir Next",Arial,sans-serif; user-select:none; }
.unit-label,.settings-strip { display:flex; justify-content:space-between; align-items:center; gap:12px; color:#d8c9a7; font:600 10px SFMono-Regular,Menlo,monospace; letter-spacing:.12em; }
.unit-label { padding:3px 3px 10px; }
.lamp-label { display:flex; align-items:center; gap:7px; color:rgba(216,201,167,.64); }
.lamp-label i { width:7px; height:7px; border-radius:50%; background:#87966c; box-shadow:0 0 7px rgba(135,150,108,.45); }
canvas { display:block; width:100%; height:165px; border:1px solid rgba(216,201,167,.16); background:#101a14; cursor:pointer; touch-action:none; }
audio { display:none; }
button,input { font:inherit; }
.transport { display:flex; align-items:center; gap:7px; padding:9px 0 13px; }
.transport button,.pitch-modes button,.unit-actions button,.nudge { min-height:33px; border:1px solid rgba(216,201,167,.28); border-radius:2px; background:linear-gradient(#273229,#19221b); color:#d8c9a7; font-size:10px; font-weight:700; letter-spacing:.07em; cursor:pointer; box-shadow:0 2px 0 #090d0a; }
.transport button { padding:0 12px; }
.transport button:hover,.pitch-modes button:hover,.nudge:hover { border-color:#d99a45; color:#eee3c7; }
.time-readout { margin-left:4px; color:#d99a45; font:600 11px SFMono-Regular,Menlo,monospace; }
.live-status { margin-left:auto; color:#87966c; font:600 9px SFMono-Regular,Menlo,monospace; letter-spacing:.10em; text-align:right; }
.monitor-level { display:grid; grid-template-columns:44px auto 48px; align-items:center; gap:8px; padding:5px 6px; border:1px solid rgba(216,201,167,.18); background:rgba(48,37,27,.34); }
.monitor-knob { --angle:135deg; position:relative; width:38px; height:38px; border:2px solid #77766b; border-radius:50%; background:radial-gradient(circle at 36% 30%,#69685f 0 6%,transparent 7%),radial-gradient(circle,#343631 0 50%,#20221e 51% 68%,#77766b 69% 72%,#171815 73%); box-shadow:inset 0 0 0 2px rgba(0,0,0,.3),0 3px 5px rgba(0,0,0,.42); cursor:ns-resize; transform:rotate(var(--angle)); }
.monitor-knob::after { content:""; position:absolute; top:4px; left:50%; width:2px; height:12px; background:#eee3c7; transform:translateX(-50%); }
.monitor-knob:focus { outline:2px solid rgba(217,154,69,.6); outline-offset:2px; }
.monitor-level div:nth-child(2)>span,.monitor-level small { display:block; color:rgba(216,201,167,.58); font:600 7px SFMono-Regular,Menlo,monospace; letter-spacing:.08em; white-space:nowrap; }
.monitor-level strong { display:block; margin:2px 0; color:#d99a45; font:600 10px SFMono-Regular,Menlo,monospace; }
.monitor-level small { color:rgba(216,201,167,.35); font-size:6px; }
.transport .monitor-level .mute { min-height:27px; padding:0 7px; font-size:7px; }
.transport .monitor-level .mute.active { border-color:#b85f3d; color:#d77961; background:rgba(184,95,61,.12); }
.control-grid { display:grid; grid-template-columns:145px 1fr; gap:10px; }
.control-block { padding:11px; border:1px solid rgba(216,201,167,.17); background:rgba(28,40,30,.82); box-shadow:inset 0 0 0 2px rgba(0,0,0,.12); }
.control-block label { display:flex; justify-content:space-between; margin-bottom:8px; color:#d8c9a7; font:600 10px SFMono-Regular,Menlo,monospace; letter-spacing:.10em; }
.source-heading{display:flex;align-items:center;justify-content:space-between;gap:8px}.source-heading label{margin:0}.source-heading .bpm-lock{min-height:25px;padding:0 7px;border:1px solid rgba(216,201,167,.24);border-radius:2px;background:#182019;color:#87966c;font:700 7px SFMono-Regular,Menlo,monospace;letter-spacing:.06em;cursor:pointer}.source-heading .bpm-lock.unlocked{border-color:#d99a45;color:#d99a45}.bpm-reset{width:100%;min-height:27px;margin-top:7px;border:1px solid rgba(216,201,167,.18);border-radius:2px;background:rgba(48,37,27,.45);color:rgba(216,201,167,.68);font:700 7px SFMono-Regular,Menlo,monospace;letter-spacing:.06em;cursor:pointer}.bpm-reset:hover{border-color:#d99a45;color:#eee3c7}
#source-bpm { box-sizing:border-box; width:100%; height:37px; border:1px solid rgba(216,201,167,.26); border-radius:2px; background:#171815; color:#d99a45; font:600 16px SFMono-Regular,Menlo,monospace; padding:0 9px; }
#source-bpm:disabled{cursor:not-allowed;color:rgba(217,154,69,.65);border-color:rgba(216,201,167,.13);background:#111510;opacity:1}
#target-bpm { width:100%; accent-color:#d99a45; cursor:pointer; }
.target-readout { color:#d99a45; font-family:SFMono-Regular,Menlo,monospace; }
.range-scale { display:flex; justify-content:space-between; color:rgba(216,201,167,.48); font:500 9px SFMono-Regular,Menlo,monospace; }
.pitch-panel { margin-top:10px; padding:10px; border:1px solid rgba(216,201,167,.17); background:rgba(48,37,27,.35); }
.pitch-modes { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; }
.pitch-modes button.active { border-color:#d99a45; color:#eee3c7; background:linear-gradient(rgba(217,154,69,.15),rgba(48,37,27,.72)); box-shadow:inset 3px 0 0 #d99a45,0 2px 0 #0b0d0b; }
.custom-pitch { display:grid; grid-template-columns:36px 112px 36px 1fr; align-items:center; gap:10px; margin-top:12px; padding-top:12px; border-top:1px solid rgba(216,201,167,.14); }
.custom-pitch[hidden] { display:none; }
.custom-pitch p { margin:0; color:rgba(216,201,167,.48); font:500 9px SFMono-Regular,Menlo,monospace; letter-spacing:.08em; }
.nudge { width:36px; padding:0; font-size:17px; }
.knob-wrap { display:grid; grid-template-columns:54px 1fr; align-items:center; gap:9px; }
.knob { --angle:0deg; position:relative; width:50px; height:50px; border:2px solid #77766b; border-radius:50%; background:radial-gradient(circle at 36% 30%,#69685f 0 6%,transparent 7%),radial-gradient(circle,#343631 0 50%,#20221e 51% 68%,#77766b 69% 72%,#171815 73%); box-shadow:inset 0 0 0 2px rgba(0,0,0,.30),0 3px 5px rgba(0,0,0,.42); cursor:ns-resize; transform:rotate(var(--angle)); }
.knob::after { content:""; position:absolute; top:5px; left:50%; width:2px; height:15px; background:#eee3c7; box-shadow:0 0 2px rgba(238,227,199,.30); transform:translateX(-50%); }
.knob:focus { outline:2px solid rgba(217,154,69,.60); outline-offset:3px; }
.pitch-readout { color:#d99a45; font:600 12px SFMono-Regular,Menlo,monospace; white-space:nowrap; }
.settings-strip { margin-top:10px; padding:9px 10px; border:1px solid rgba(216,201,167,.12); background:#171815; }
.settings-strip span { color:#d99a45; }
.unit-actions { display:flex; justify-content:flex-end; gap:9px; margin-top:10px; }
.unit-actions button { min-height:42px; padding:0 18px; }
.unit-actions .preview { color:#eee3c7; border-color:rgba(217,154,69,.44); }
.unit-actions .process { border-color:#d8c9a7; background:linear-gradient(#e4d5b3,#cdbc94); color:#101a14; box-shadow:0 3px 0 #6f6149; }
.unit-actions button:active { transform:translateY(2px); box-shadow:0 1px 0 #5d513d; }
@media(max-width:850px){ .transport{flex-wrap:wrap}.monitor-level{margin-left:auto} }
@media(max-width:620px){ .control-grid{grid-template-columns:1fr}.pitch-modes{grid-template-columns:1fr}.custom-pitch{grid-template-columns:36px 112px 36px}.custom-pitch p{display:none}.unit-actions{flex-direction:column}.unit-actions button{width:100%}.live-status{width:100%;max-width:none;margin-left:0;text-align:left}.monitor-level{width:100%;margin-left:0;grid-template-columns:44px 1fr 48px} }
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""


SPEED_PLAYER_JS = """
export default function(component) {
    const { data, parentElement, setTriggerValue } = component;
    const q = selector => parentElement.querySelector(selector);
    const canvas = q('canvas');
    const context = canvas.getContext('2d');
    const audio = q('audio');
    const sourceInput = q('#source-bpm');
    const targetInput = q('#target-bpm');
    const targetReadout = q('.target-readout');
    const minReadout = q('.range-min');
    const maxReadout = q('.range-max');
    const timeReadout = q('.time-readout');
    const liveStatus = q('.live-status');
    const speedReadout = q('.speed-readout');
    const pitchSummary = q('.pitch-summary');
    const customPanel = q('.custom-pitch');
    const knob = q('.knob');
    const monitorKnob = q('.monitor-knob');
    const pitchReadout = q('.pitch-readout');
    const previewButton = q('[data-action="preview"]');
    const processButton = q('[data-action="process"]');
    const modeButtons = [...parentElement.querySelectorAll('[data-mode]')];
    const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));

    let state = parentElement.__vsSpeedPlayer;
    if (!state || state.audioId !== data.audio_id) {
        state = {
            audioId: data.audio_id,
            sourceBpm: Number(data.settings.source_bpm),
            detectedBpm: Number(data.settings.detected_bpm ?? data.settings.source_bpm),
            targetBpm: Number(data.settings.target_bpm),
            mode: data.settings.pitch_mode,
            pitch: Number(data.settings.pitch_semitones || 0),
            monitorDb: 0,
            muted: false,
            sourceLocked: true,
            peaks: null,
            animationFrame: null,
        };
        parentElement.__vsSpeedPlayer = state;
        audio.src = data.audio_url;
        fetch(data.audio_url).then(response => response.arrayBuffer()).then(buffer => {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            return audioContext.decodeAudioData(buffer).finally(() => audioContext.close());
        }).then(decoded => {
            const channel = decoded.getChannelData(0);
            const points = 1800;
            const block = Math.max(1, Math.floor(channel.length / points));
            state.peaks = Array.from({length:points}, (_, index) => {
                let peak = 0;
                const end = Math.min(channel.length, (index + 1) * block);
                for (let offset = index * block; offset < end; offset++) peak = Math.max(peak, Math.abs(channel[offset]));
                return peak;
            });
            draw();
        }).catch(() => { state.peaks = []; draw(); });
    }

    function formatTime(seconds) {
        if (!Number.isFinite(seconds)) return '0:00';
        const minutes = Math.floor(seconds / 60);
        return `${minutes}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
    }

    function monitorGain() { return state.monitorDb <= -60 ? 0 : Math.pow(10, state.monitorDb / 20); }
    function updateMonitorLevel() {
        state.monitorDb = clamp(Math.round(state.monitorDb), -60, 0);
        monitorKnob.style.setProperty('--angle', `${-135 + (state.monitorDb + 60) / 60 * 270}deg`);
        monitorKnob.setAttribute('aria-valuenow', String(state.monitorDb));
        q('.monitor-value').textContent = state.monitorDb <= -60 ? '−∞ dB' : `${state.monitorDb} dB`;
        const mute = q('[data-action="mute"]');
        mute.classList.toggle('active', state.muted);
        mute.setAttribute('aria-pressed', String(state.muted));
        mute.textContent = state.muted ? 'UNMUTE' : 'MUTE';
        audio.volume = monitorGain();
        audio.muted = state.muted;
    }
    function setMonitorLevel(value) { state.monitorDb = value; updateMonitorLevel(); }

    function currentSpeed() { return state.targetBpm / state.sourceBpm; }
    function displayedPitch() {
        if (state.mode === 'Follow speed') return 12 * Math.log2(currentSpeed());
        if (state.mode === 'Keep original') return 0;
        return state.pitch;
    }
    function payload() {
        return {source_bpm:state.sourceBpm,detected_bpm:state.detectedBpm,target_bpm:state.targetBpm,pitch_mode:state.mode,pitch_semitones:state.pitch};
    }

    function updateControls() {
        state.sourceBpm = clamp(Number(state.sourceBpm) || 120, 40, 250);
        const minimum = Math.ceil(state.sourceBpm * .5 * 10) / 10;
        const maximum = Math.floor(Math.min(state.sourceBpm * 2, 300) * 10) / 10;
        state.targetBpm = clamp(Number(state.targetBpm) || state.sourceBpm, minimum, maximum);
        state.pitch = Math.round(clamp(Number(state.pitch) || 0, -12, 12) * 2) / 2;
        sourceInput.value = state.sourceBpm.toFixed(1);
        sourceInput.disabled = state.sourceLocked;
        const lockButton=q('[data-action="bpm-lock"]');lockButton.classList.toggle('unlocked',!state.sourceLocked);lockButton.setAttribute('aria-pressed',String(state.sourceLocked));lockButton.textContent=state.sourceLocked?'▣ LOCKED':'□ UNLOCKED';
        targetInput.min = minimum; targetInput.max = maximum; targetInput.value = state.targetBpm;
        targetReadout.textContent = `${state.targetBpm.toFixed(1)} BPM`;
        minReadout.textContent = minimum.toFixed(1); maxReadout.textContent = maximum.toFixed(1);
        const speed = currentSpeed();
        audio.playbackRate = speed;
        audio.preservesPitch = state.mode !== 'Follow speed';
        audio.mozPreservesPitch = state.mode !== 'Follow speed';
        audio.webkitPreservesPitch = state.mode !== 'Follow speed';
        modeButtons.forEach(button => button.classList.toggle('active', button.dataset.mode === state.mode));
        const custom = state.mode === 'Custom';
        customPanel.hidden = !custom; previewButton.hidden = !custom;
        knob.style.setProperty('--angle', `${state.pitch / 12 * 135}deg`);
        knob.setAttribute('aria-valuenow', state.pitch.toFixed(1));
        pitchReadout.textContent = `${state.pitch >= 0 ? '+' : ''}${state.pitch.toFixed(1)} ST`;
        speedReadout.textContent = `SPEED ${speed.toFixed(3)}×`;
        const pitch = displayedPitch();
        pitchSummary.textContent = `PITCH ${pitch >= 0 ? '+' : ''}${pitch.toFixed(1)} ST`;
        liveStatus.textContent = custom ? 'LIVE TEMPO · PREVIEW PITCH' : 'LIVE AUDITION';
    }

    function draw() {
        const ratio = window.devicePixelRatio || 1;
        const bounds = canvas.getBoundingClientRect();
        const width = Math.max(1, Math.round(bounds.width * ratio));
        const height = Math.max(1, Math.round(bounds.height * ratio));
        if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
        context.clearRect(0,0,width,height); context.fillStyle='#101a14'; context.fillRect(0,0,width,height);
        context.strokeStyle='rgba(216,201,167,.12)'; context.beginPath(); context.moveTo(0,height/2); context.lineTo(width,height/2); context.stroke();
        if (state.peaks && state.peaks.length) {
            context.strokeStyle='#d8c9a7'; context.lineWidth=Math.max(1,ratio); context.beginPath();
            state.peaks.forEach((peak,index)=>{ const x=index/(state.peaks.length-1)*width; context.moveTo(x,height/2-peak*height*.39); context.lineTo(x,height/2+peak*height*.39); }); context.stroke();
        }
        if (audio.duration) {
            const x=audio.currentTime/audio.duration*width; context.strokeStyle='#d99a45'; context.lineWidth=2*ratio; context.beginPath(); context.moveTo(x,0); context.lineTo(x,height); context.stroke();
        }
        timeReadout.textContent=`${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
    }

    function animate() { draw(); if (!audio.paused) state.animationFrame=requestAnimationFrame(animate); }
    q('[data-action="play"]').onclick=()=>{ audio.play(); if(state.animationFrame)cancelAnimationFrame(state.animationFrame); animate(); };
    q('[data-action="stop"]').onclick=()=>{ audio.pause(); if(state.animationFrame)cancelAnimationFrame(state.animationFrame); state.animationFrame=null; draw(); };
    audio.onended=()=>{ state.animationFrame=null; draw(); };
    canvas.onclick=event=>{ if(!audio.duration)return; const box=canvas.getBoundingClientRect(); audio.currentTime=clamp((event.clientX-box.left)/box.width,0,1)*audio.duration; draw(); };
    q('[data-action="bpm-lock"]').onclick=()=>{state.sourceLocked=!state.sourceLocked;updateControls();if(!state.sourceLocked)sourceInput.focus()};
    q('[data-action="bpm-reset"]').onclick=()=>{state.sourceBpm=state.detectedBpm;state.targetBpm=state.detectedBpm;state.mode='Follow speed';state.pitch=0;updateControls();setTriggerValue('reset',payload())};
    sourceInput.onchange=()=>{ if(state.sourceLocked)return;state.sourceBpm=Number(sourceInput.value); state.targetBpm=state.sourceBpm; updateControls(); };
    targetInput.oninput=()=>{ state.targetBpm=Number(targetInput.value); updateControls(); };
    modeButtons.forEach(button=>button.onclick=()=>{ state.mode=button.dataset.mode; updateControls(); });

    function setPitch(value){ state.pitch=value; updateControls(); }
    q('[data-pitch="down"]').onclick=()=>setPitch(state.pitch-.5);
    q('[data-pitch="up"]').onclick=()=>setPitch(state.pitch+.5);
    knob.onwheel=event=>{ event.preventDefault(); setPitch(state.pitch+(event.deltaY<0?.5:-.5)); };
    knob.onkeydown=event=>{ if(['ArrowUp','ArrowRight'].includes(event.key)){event.preventDefault();setPitch(state.pitch+.5);} if(['ArrowDown','ArrowLeft'].includes(event.key)){event.preventDefault();setPitch(state.pitch-.5);} };
    knob.onpointerdown=event=>{ knob.setPointerCapture(event.pointerId); const startY=event.clientY; const startPitch=state.pitch; knob.onpointermove=move=>setPitch(startPitch+(startY-move.clientY)/8); knob.onpointerup=up=>{knob.releasePointerCapture(up.pointerId);knob.onpointermove=null;}; };
    monitorKnob.onwheel=event=>{ event.preventDefault(); setMonitorLevel(state.monitorDb+(event.deltaY<0?2:-2)); };
    monitorKnob.onkeydown=event=>{ if(['ArrowUp','ArrowRight'].includes(event.key)){event.preventDefault();setMonitorLevel(state.monitorDb+1);} if(['ArrowDown','ArrowLeft'].includes(event.key)){event.preventDefault();setMonitorLevel(state.monitorDb-1);} if(event.key==='Home'){event.preventDefault();setMonitorLevel(-60);} if(event.key==='End'){event.preventDefault();setMonitorLevel(0);} };
    monitorKnob.onpointerdown=event=>{ monitorKnob.setPointerCapture(event.pointerId); const startY=event.clientY; const startDb=state.monitorDb; monitorKnob.onpointermove=move=>setMonitorLevel(startDb+(startY-move.clientY)/2); monitorKnob.onpointerup=up=>{monitorKnob.releasePointerCapture(up.pointerId);monitorKnob.onpointermove=null;}; };
    q('[data-action="mute"]').onclick=()=>{ state.muted=!state.muted; updateMonitorLevel(); };
    previewButton.onclick=()=>setTriggerValue('preview',payload());
    processButton.onclick=()=>setTriggerValue('process',payload());
    new ResizeObserver(draw).observe(canvas);
    updateControls(); updateMonitorLevel(); draw();
}
"""


_speed_player = st.components.v2.component(
    "vibes_supplier_speed_player_v3",
    html=SPEED_PLAYER_HTML,
    css=SPEED_PLAYER_CSS,
    js=SPEED_PLAYER_JS,
)


def initial_speed_deck_settings(detected_bpm: float) -> dict[str, Any]:
    """Start live audition at the detected tempo without changing the audio."""
    source_bpm = round(float(detected_bpm), 1)
    return {
        "detected_bpm": source_bpm,
        "source_bpm": source_bpm,
        "target_bpm": source_bpm,
        "pitch_mode": "Follow speed",
        "pitch_semitones": 0.0,
    }


def live_speed_player(
    browser_audio: bytes,
    audio_id: str,
    settings: dict[str, Any],
    *,
    key: str,
    on_preview_change: Callable[[], None],
    on_process_change: Callable[[], None],
    on_reset_change: Callable[[], None],
) -> Any:
    """Render the live Speed Changer deck and return its trigger state."""
    return _speed_player(
        key=key,
        data={
            "audio_url": "data:audio/mpeg;base64,"
            + base64.b64encode(browser_audio).decode("ascii"),
            "audio_id": audio_id,
            "settings": settings,
        },
        height=665,
        on_preview_change=on_preview_change,
        on_process_change=on_process_change,
        on_reset_change=on_reset_change,
    )
