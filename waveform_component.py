"""Reusable browser-side interactive waveform component."""

import base64
from typing import Any

import streamlit as st

from audio_chopper import WaveformData


WAVEFORM_HTML = """
<div class="wave-editor">
    <canvas aria-label="Interactive audio waveform"></canvas>
    <audio preload="auto"></audio>
    <div class="wave-toolbar">
        <button type="button" data-action="play">▶ PLAY SELECTION</button>
        <button type="button" data-action="stop">■ STOP</button>
        <button type="button" data-action="loop" aria-pressed="false">↻ LOOP OFF</button>
        <span class="selection-time"></span>
        <button type="button" class="apply" data-action="apply">USE SELECTION</button>
    </div>
    <div class="edge-fade">
        <span>EDGE FADE / DE-CLICK</span>
        <div role="group" aria-label="Sample edge fade duration">
            <button type="button" data-fade="0">OFF</button>
            <button type="button" data-fade="5">5</button>
            <button type="button" data-fade="10" class="active">10</button>
            <button type="button" data-fade="25">25</button>
            <button type="button" data-fade="50">50 ms</button>
        </div>
        <small>HEARD IN PLAY / APPLIED ON USE SELECTION</small>
    </div>
    <div class="wave-footer">
        <div class="monitor-level">
            <div class="monitor-knob" role="slider" tabindex="0" aria-label="Chopper listening volume only" aria-valuemin="-60" aria-valuemax="0" aria-valuenow="0"></div>
            <div><span>MONITOR LEVEL</span><strong class="monitor-value">0 dB</strong><small>LISTENING ONLY · EXPORT UNAFFECTED</small></div>
            <button type="button" class="mute" data-action="mute" aria-pressed="false">MUTE</button>
        </div>
        <div class="wave-hint">DRAG TO SELECT · WHEEL TO ZOOM · SHIFT + WHEEL TO MOVE</div>
        <div class="view-controls" aria-label="Waveform view controls">
            <button type="button" data-action="pan-left" title="Move left">←</button>
            <button type="button" data-action="zoom-out" title="Zoom out">−</button>
            <button type="button" data-action="zoom-in" title="Zoom in">+</button>
            <button type="button" data-action="pan-right" title="Move right">→</button>
        </div>
    </div>
</div>
"""

WAVEFORM_CSS = """
.wave-editor {
    position: relative;
    overflow: hidden;
    padding: 12px 12px 8px;
    border: 1px solid rgba(216, 201, 167, 0.26);
    border-radius: 3px;
    background: linear-gradient(180deg, rgba(119,118,107,.08), transparent 35%), #171815;
    box-shadow: inset 0 0 0 3px rgba(0,0,0,.16);
    user-select: none;
}
canvas {
    display: block;
    width: 100%;
    height: 210px;
    cursor: crosshair;
    touch-action: none;
}
.wave-hint {
    color: rgba(216, 201, 167, 0.58);
    font: 600 10px "IBM Plex Mono", monospace;
    letter-spacing: 0.10em;
    text-align: right;
}
.wave-footer { display:flex; align-items:center; justify-content:flex-end; gap:12px; padding-top:7px; }
.monitor-level { display:grid; grid-template-columns:44px auto 48px; align-items:center; gap:8px; margin-right:auto; padding:5px 6px; border:1px solid rgba(216,201,167,.18); background:rgba(48,37,27,.34); }
.monitor-knob { --angle:135deg; position:relative; width:38px; height:38px; border:2px solid #77766b; border-radius:50%; background:radial-gradient(circle at 36% 30%,#69685f 0 6%,transparent 7%),radial-gradient(circle,#343631 0 50%,#20221e 51% 68%,#77766b 69% 72%,#171815 73%); box-shadow:inset 0 0 0 2px rgba(0,0,0,.3),0 3px 5px rgba(0,0,0,.42); cursor:ns-resize; transform:rotate(var(--angle)); }
.monitor-knob::after { content:""; position:absolute; top:4px; left:50%; width:2px; height:12px; background:#eee3c7; transform:translateX(-50%); }
.monitor-knob:focus { outline:2px solid rgba(217,154,69,.6); outline-offset:2px; }
.monitor-level div:nth-child(2)>span,.monitor-level small { display:block; color:rgba(216,201,167,.58); font:600 7px "IBM Plex Mono",monospace; letter-spacing:.08em; white-space:nowrap; }
.monitor-level strong { display:block; margin:2px 0; color:#d99a45; font:600 10px "IBM Plex Mono",monospace; }
.monitor-level small { color:rgba(216,201,167,.35); font-size:6px; }
.monitor-level .mute { min-height:27px; padding:0 7px; border:1px solid rgba(216,201,167,.24); border-radius:2px; background:#1c281e; color:#d8c9a7; font:700 7px "IBM Plex Sans",sans-serif; cursor:pointer; }
.monitor-level .mute.active { border-color:#b85f3d; color:#d77961; background:rgba(184,95,61,.12); }
.view-controls { display:flex; gap:5px; }
.view-controls button {
    width:30px;
    height:27px;
    padding:0;
    border:1px solid rgba(216,201,167,.24);
    border-radius:2px;
    background:#1c281e;
    color:#d8c9a7;
    font:600 14px "IBM Plex Mono",monospace;
    cursor:pointer;
}
.view-controls button:hover { border-color:#d99a45; color:#eee3c7; }
.wave-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-top: 9px;
}
.wave-toolbar button {
    min-height: 32px;
    padding: 0 11px;
    border: 1px solid rgba(216,201,167,.24);
    border-radius: 2px;
    background: #1c281e;
    color: #d8c9a7;
    font: 700 10px "IBM Plex Sans", sans-serif;
    letter-spacing: .06em;
    cursor: pointer;
}
.wave-toolbar button:hover { border-color: #d99a45; color: #eee3c7; }
.wave-toolbar button.loop-active { border-color:#d99a45; color:#d99a45; background:rgba(217,154,69,.10); }
.wave-toolbar button.apply {
    margin-left: auto;
    border-color: #d8c9a7;
    background: linear-gradient(#e4d5b3, #cdbc94);
    color: #101a14;
    box-shadow: 0 2px 0 #6f6149;
}
.wave-toolbar button.apply:active,
.wave-toolbar button.apply.selection-applied {
    border-color: #d99a45;
    background: #d99a45;
    color: #101a14;
    box-shadow: 0 0 0 2px rgba(217,154,69,.20), 0 2px 0 #765326;
    transform: translateY(1px);
}
.edge-fade { display:flex; align-items:center; gap:10px; margin-top:8px; padding:7px 9px; border:1px solid rgba(216,201,167,.14); background:rgba(48,37,27,.30); }
.edge-fade>span,.edge-fade small { color:rgba(216,201,167,.56); font:600 7px "IBM Plex Mono",monospace; letter-spacing:.09em; }
.edge-fade>div { display:flex; gap:4px; }
.edge-fade button { min-width:34px; height:25px; padding:0 6px; border:1px solid rgba(216,201,167,.20); border-radius:2px; background:#19221b; color:rgba(216,201,167,.58); font:700 7px "IBM Plex Mono",monospace; cursor:pointer; }
.edge-fade button:hover { border-color:#d99a45; color:#eee3c7; }
.edge-fade button.active { border-color:#d99a45; background:rgba(217,154,69,.13); color:#d99a45; box-shadow:inset 2px 0 0 #d99a45; }
.edge-fade small { margin-left:auto; color:rgba(216,201,167,.34); font-size:6px; }
.selection-time { color:#d99a45; font:600 11px "IBM Plex Mono",monospace; }
audio { display:none; }
@media(max-width:760px){.wave-toolbar{flex-wrap:wrap}.wave-toolbar button.apply{width:100%;margin-left:0}.edge-fade{flex-wrap:wrap}.edge-fade small{width:100%;margin-left:0}.wave-footer{flex-wrap:wrap;justify-content:flex-start}.monitor-level{width:100%;grid-template-columns:44px 1fr 48px}.wave-hint{text-align:left}.view-controls{margin-left:auto}}
"""

WAVEFORM_JS = """
export default function(component) {
    const { data, parentElement, setStateValue } = component;
    const canvas = parentElement.querySelector('canvas');
    const context = canvas.getContext('2d');
    const audio = parentElement.querySelector('audio');
    const timeLabel = parentElement.querySelector('.selection-time');
    const playButton = parentElement.querySelector('[data-action="play"]');
    const stopButton = parentElement.querySelector('[data-action="stop"]');
    const loopButton = parentElement.querySelector('[data-action="loop"]');
    const applyButton = parentElement.querySelector('[data-action="apply"]');
    const panLeftButton = parentElement.querySelector('[data-action="pan-left"]');
    const panRightButton = parentElement.querySelector('[data-action="pan-right"]');
    const zoomOutButton = parentElement.querySelector('[data-action="zoom-out"]');
    const zoomInButton = parentElement.querySelector('[data-action="zoom-in"]');
    const monitorKnob = parentElement.querySelector('.monitor-knob');
    const fadeButtons = [...parentElement.querySelectorAll('[data-fade]')];
    audio.src = data.audio_url;
    const peaks = data.peaks;
    const duration = data.duration;
    let start = data.selection.start;
    let end = data.selection.end;
    let viewStart = data.view.start;
    let viewEnd = data.view.end;
    let dragMode = null;
    let anchorTime = 0;
    let originalStart = start;
    let originalEnd = end;
    let pointerX = 0;
    let autoPanFrame = null;
    let lastAutoPanTime = 0;
    let monitorState = parentElement.__vsChopperMonitor;
    if (!monitorState) {
        monitorState = { db: 0, muted: false, fadeMs: 10 };
        parentElement.__vsChopperMonitor = monitorState;
    }
    if (!Number.isFinite(monitorState.fadeMs)) monitorState.fadeMs = 10;
    let playingSelection = false;
    let loopSelection = false;
    let playheadTime = null;
    let animationFrame = null;

    function clamp(value, minimum, maximum) {
        return Math.max(minimum, Math.min(maximum, value));
    }

    function timeAt(clientX) {
        const bounds = canvas.getBoundingClientRect();
        const ratio = clamp((clientX - bounds.left) / bounds.width, 0, 1);
        return viewStart + ratio * (viewEnd - viewStart);
    }

    function xAt(time, width) {
        return (time - viewStart) / (viewEnd - viewStart) * width;
    }

    function resize() {
        const ratio = window.devicePixelRatio || 1;
        const bounds = canvas.getBoundingClientRect();
        canvas.width = Math.max(1, Math.round(bounds.width * ratio));
        canvas.height = Math.max(1, Math.round(bounds.height * ratio));
        draw();
    }

    function drawWave(width, height, color, clipStart, clipEnd) {
        const first = Math.max(0, Math.floor(viewStart / duration * peaks.length));
        const last = Math.min(peaks.length, Math.ceil(viewEnd / duration * peaks.length));
        const visible = Math.max(1, last - first);
        const middle = height / 2;
        const amplitude = height * 0.43;
        context.save();
        if (clipStart !== undefined) {
            context.beginPath();
            context.rect(clipStart, 0, Math.max(0, clipEnd - clipStart), height);
            context.clip();
        }
        context.strokeStyle = color;
        context.lineWidth = Math.max(1, window.devicePixelRatio || 1);
        context.beginPath();
        for (let pixel = 0; pixel < width; pixel += 2) {
            const from = first + Math.floor(pixel / width * visible);
            const to = Math.min(last, first + Math.ceil((pixel + 2) / width * visible));
            let peak = 0;
            for (let index = from; index < to; index++) peak = Math.max(peak, peaks[index] || 0);
            context.moveTo(pixel, middle - peak * amplitude);
            context.lineTo(pixel, middle + peak * amplitude);
        }
        context.stroke();
        context.restore();
    }

    function draw() {
        const width = canvas.width;
        const height = canvas.height;
        context.clearRect(0, 0, width, height);
        context.fillStyle = '#171815';
        context.fillRect(0, 0, width, height);
        context.strokeStyle = 'rgba(216,201,167,.12)';
        context.beginPath();
        context.moveTo(0, height / 2);
        context.lineTo(width, height / 2);
        context.stroke();
        drawWave(width, height, 'rgba(216,201,167,.38)');

        const selectedX1 = xAt(start, width);
        const selectedX2 = xAt(end, width);
        context.fillStyle = 'rgba(89,68,49,.26)';
        context.fillRect(selectedX1, 0, selectedX2 - selectedX1, height);
        drawWave(width, height, '#d99a45', selectedX1, selectedX2);
        context.strokeStyle = '#eee3c7';
        context.lineWidth = 2 * (window.devicePixelRatio || 1);
        context.beginPath();
        context.moveTo(selectedX1, 0);
        context.lineTo(selectedX1, height);
        context.moveTo(selectedX2, 0);
        context.lineTo(selectedX2, height);
        context.stroke();

        if (playheadTime !== null && playheadTime >= viewStart && playheadTime <= viewEnd) {
            const playheadX = xAt(playheadTime, width);
            context.strokeStyle = '#87966c';
            context.lineWidth = 2 * (window.devicePixelRatio || 1);
            context.beginPath();
            context.moveTo(playheadX, 0);
            context.lineTo(playheadX, height);
            context.stroke();
            context.fillStyle = '#87966c';
            context.beginPath();
            context.moveTo(playheadX - 5, 0);
            context.lineTo(playheadX + 5, 0);
            context.lineTo(playheadX, 8 * (window.devicePixelRatio || 1));
            context.fill();
        }

        context.fillStyle = '#d8c9a7';
        context.font = `${11 * (window.devicePixelRatio || 1)}px IBM Plex Mono, monospace`;
        context.fillText(viewStart.toFixed(2) + ' s', 8, height - 10);
        const endLabel = viewEnd.toFixed(2) + ' s';
        const labelWidth = context.measureText(endLabel).width;
        context.fillText(endLabel, width - labelWidth - 8, height - 10);
        timeLabel.textContent = `${start.toFixed(2)} — ${end.toFixed(2)} s`;
    }

    function commitSelection() {
        if (end - start < 0.1) end = Math.min(duration, start + 0.1);
        const commitId = Date.now();
        setStateValue('selection', {
            start,
            end,
            view_start: viewStart,
            view_end: viewEnd,
            commit_id: commitId,
            fade_ms: monitorState.fadeMs,
        });
    }

    function markSelectionDirty() {
        applyButton.disabled = Boolean(data.tray_full);
        applyButton.classList.remove('selection-applied');
        applyButton.textContent = data.tray_full ? `TRAY FULL / ${data.tray_count} OF 4` : 'USE SELECTION';
    }

    function stopAutoPan() {
        if (autoPanFrame !== null) cancelAnimationFrame(autoPanFrame);
        autoPanFrame = null;
        lastAutoPanTime = 0;
    }

    function autoPanVelocity() {
        if (!dragMode) return 0;
        const box = canvas.getBoundingClientRect();
        const edgeZone = Math.min(64, box.width * 0.14);
        const localX = pointerX - box.left;
        let strength = 0;
        if (localX < edgeZone) strength = -(1 - clamp(localX / edgeZone, 0, 1));
        else if (localX > box.width - edgeZone) strength = 1 - clamp((box.width - localX) / edgeZone, 0, 1);
        const span = viewEnd - viewStart;
        const speed = dragMode === 'move' ? span * 0.48 : span * 0.24;
        return strength * speed;
    }

    function runAutoPan(timestamp) {
        if (!dragMode) { stopAutoPan(); return; }
        const velocity = autoPanVelocity();
        if (lastAutoPanTime && velocity) {
            const deltaSeconds = Math.min((timestamp - lastAutoPanTime) / 1000, 0.05);
            const span = viewEnd - viewStart;
            const requestedShift = velocity * deltaSeconds;
            const nextViewStart = clamp(viewStart + requestedShift, 0, duration - span);
            const actualShift = nextViewStart - viewStart;
            if (actualShift) {
                viewStart = nextViewStart;
                viewEnd = viewStart + span;
                if (dragMode === 'move') {
                    start = clamp(start + actualShift, 0, duration - (end - start));
                    end = start + (originalEnd - originalStart);
                    originalStart += actualShift;
                    originalEnd += actualShift;
                    anchorTime += actualShift;
                } else if (dragMode === 'start') {
                    start = clamp(start + actualShift, 0, end - 0.1);
                } else if (dragMode === 'end') {
                    end = clamp(end + actualShift, start + 0.1, duration);
                } else if (dragMode === 'new') {
                    const pointerTime = timeAt(pointerX);
                    start = Math.min(anchorTime, pointerTime);
                    end = Math.max(anchorTime, pointerTime);
                }
                draw();
            }
        }
        lastAutoPanTime = timestamp;
        autoPanFrame = requestAnimationFrame(runAutoPan);
    }

    canvas.onpointerdown = (event) => {
        markSelectionDirty();
        stopAutoPan();
        canvas.setPointerCapture(event.pointerId);
        pointerX = event.clientX;
        const time = timeAt(event.clientX);
        const tolerance = (viewEnd - viewStart) * 0.025;
        originalStart = start;
        originalEnd = end;
        anchorTime = time;
        if (Math.abs(time - start) <= tolerance) dragMode = 'start';
        else if (Math.abs(time - end) <= tolerance) dragMode = 'end';
        else if (time > start && time < end) dragMode = 'move';
        else {
            dragMode = 'new';
            start = time;
            end = Math.min(viewEnd, time + 0.1);
        }
        draw();
        autoPanFrame = requestAnimationFrame(runAutoPan);
    };

    canvas.onpointermove = (event) => {
        if (!dragMode) return;
        pointerX = event.clientX;
        const time = timeAt(event.clientX);
        if (dragMode === 'start') start = clamp(time, viewStart, end - 0.1);
        else if (dragMode === 'end') end = clamp(time, start + 0.1, viewEnd);
        else if (dragMode === 'move') {
            const length = originalEnd - originalStart;
            const nextStart = clamp(originalStart + time - anchorTime, viewStart, viewEnd - length);
            start = nextStart;
            end = nextStart + length;
        } else {
            start = Math.min(anchorTime, time);
            end = Math.max(anchorTime, time);
        }
        draw();
    };

    canvas.onpointerup = (event) => {
        if (!dragMode) return;
        canvas.releasePointerCapture(event.pointerId);
        dragMode = null;
        stopAutoPan();
        draw();
    };
    canvas.onpointercancel = () => { dragMode = null; stopAutoPan(); draw(); };

    canvas.onwheel = (event) => {
        event.preventDefault();
        const oldSpan = viewEnd - viewStart;
        if (event.shiftKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) {
            const direction = event.deltaX || event.deltaY;
            const shift = oldSpan * 0.16 * Math.sign(direction);
            viewStart = clamp(viewStart + shift, 0, duration - oldSpan);
            viewEnd = viewStart + oldSpan;
        } else {
            const anchor = timeAt(event.clientX);
            const newSpan = clamp(oldSpan * (event.deltaY < 0 ? 0.72 : 1.38), 0.25, duration);
            const ratio = (anchor - viewStart) / oldSpan;
            viewStart = clamp(anchor - newSpan * ratio, 0, duration - newSpan);
            viewEnd = viewStart + newSpan;
        }
        draw();
    };

    function zoomView(factor) {
        const oldSpan = viewEnd - viewStart;
        const newSpan = clamp(oldSpan * factor, 0.25, duration);
        const center = (start + end) / 2;
        viewStart = clamp(center - newSpan / 2, 0, duration - newSpan);
        viewEnd = viewStart + newSpan;
        draw();
    }

    function panView(direction) {
        const span = viewEnd - viewStart;
        viewStart = clamp(viewStart + direction * span * 0.22, 0, duration - span);
        viewEnd = viewStart + span;
        draw();
    }

    zoomInButton.onclick = () => zoomView(0.72);
    zoomOutButton.onclick = () => zoomView(1.38);
    panLeftButton.onclick = () => panView(-1);
    panRightButton.onclick = () => panView(1);

    function applyAuditionGain() {
        const fadeSeconds = Math.min(monitorState.fadeMs / 1000, (end - start) / 4);
        let fadeFactor = 1;
        if (playingSelection && fadeSeconds > 0) {
            const fadeIn = clamp((audio.currentTime - start) / fadeSeconds, 0, 1);
            const fadeOut = clamp((end - audio.currentTime) / fadeSeconds, 0, 1);
            fadeFactor = Math.min(fadeIn, fadeOut);
        }
        audio.volume = clamp(monitorGain() * fadeFactor, 0, 1);
        audio.muted = monitorState.muted;
    }
    playButton.onclick = () => {
        playingSelection = true;
        audio.currentTime = start;
        playheadTime = start;
        applyAuditionGain();
        audio.play();
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
        animatePlayhead();
    };
    stopButton.onclick = () => {
        playingSelection = false;
        audio.pause();
        playheadTime = start;
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
        animationFrame = null;
        draw();
    };
    loopButton.onclick = () => {
        loopSelection = !loopSelection;
        loopButton.classList.toggle('loop-active', loopSelection);
        loopButton.setAttribute('aria-pressed', String(loopSelection));
        loopButton.textContent = loopSelection ? '↻ LOOP ON' : '↻ LOOP OFF';
    };
    applyButton.onclick = () => {
        if (applyButton.disabled || data.tray_full) return;
        applyButton.disabled = true;
        applyButton.classList.add('selection-applied');
        applyButton.textContent = '✓ ADDING TO TRAY';
        window.setTimeout(commitSelection, 240);
    };
    function monitorGain(){return monitorState.db<=-60?0:Math.pow(10,monitorState.db/20)}
    function updateMonitorLevel(){monitorState.db=clamp(Math.round(monitorState.db),-60,0);monitorKnob.style.setProperty('--angle',`${-135+(monitorState.db+60)/60*270}deg`);monitorKnob.setAttribute('aria-valuenow',String(monitorState.db));parentElement.querySelector('.monitor-value').textContent=monitorState.db<=-60?'−∞ dB':`${monitorState.db} dB`;const muteButton=parentElement.querySelector('[data-action="mute"]');muteButton.classList.toggle('active',monitorState.muted);muteButton.setAttribute('aria-pressed',String(monitorState.muted));muteButton.textContent=monitorState.muted?'UNMUTE':'MUTE';applyAuditionGain()}
    function setMonitorLevel(value){monitorState.db=value;updateMonitorLevel()}
    monitorKnob.onwheel=event=>{event.preventDefault();setMonitorLevel(monitorState.db+(event.deltaY<0?2:-2))};
    monitorKnob.onkeydown=event=>{if(['ArrowUp','ArrowRight'].includes(event.key)){event.preventDefault();setMonitorLevel(monitorState.db+1)}if(['ArrowDown','ArrowLeft'].includes(event.key)){event.preventDefault();setMonitorLevel(monitorState.db-1)}if(event.key==='Home'){event.preventDefault();setMonitorLevel(-60)}if(event.key==='End'){event.preventDefault();setMonitorLevel(0)}};
    monitorKnob.onpointerdown=event=>{monitorKnob.setPointerCapture(event.pointerId);const startY=event.clientY,startDb=monitorState.db;monitorKnob.onpointermove=move=>setMonitorLevel(startDb+(startY-move.clientY)/2);monitorKnob.onpointerup=up=>{monitorKnob.releasePointerCapture(up.pointerId);monitorKnob.onpointermove=null}};
    parentElement.querySelector('[data-action="mute"]').onclick=()=>{monitorState.muted=!monitorState.muted;updateMonitorLevel()};
    fadeButtons.forEach(button=>{button.classList.toggle('active',Number(button.dataset.fade)===monitorState.fadeMs);button.onclick=()=>{monitorState.fadeMs=Number(button.dataset.fade);fadeButtons.forEach(item=>item.classList.toggle('active',item===button));applyAuditionGain()}});
    applyButton.disabled=Boolean(data.tray_full);applyButton.classList.remove('selection-applied');applyButton.textContent=data.tray_full?`TRAY FULL / ${data.tray_count} OF 4`:'USE SELECTION';
    updateMonitorLevel();
    audio.ontimeupdate = () => {
        if (playingSelection && audio.currentTime >= end) {
            if (loopSelection) {
                audio.currentTime = start;
                playheadTime = start;
                audio.play();
            } else {
                playingSelection = false;
                audio.pause();
                audio.currentTime = start;
                playheadTime = start;
                if (animationFrame !== null) cancelAnimationFrame(animationFrame);
                animationFrame = null;
                draw();
            }
        }
    };

    function animatePlayhead() {
        if (!playingSelection) return;
        if (audio.currentTime >= end && loopSelection) audio.currentTime = start;
        applyAuditionGain();
        playheadTime = audio.currentTime;
        draw();
        animationFrame = requestAnimationFrame(animatePlayhead);
    }

    const observer = new ResizeObserver(resize);
    observer.observe(canvas);
    resize();
    return () => {
        observer.disconnect();
        audio.pause();
        stopAutoPan();
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
    };
}
"""


_interactive_waveform = st.components.v2.component(
    "vibes_supplier_waveform_v10",
    html=WAVEFORM_HTML,
    css=WAVEFORM_CSS,
    js=WAVEFORM_JS,
)


def interactive_waveform(
    waveform: WaveformData,
    selection: tuple[float, float],
    view: tuple[float, float],
    browser_audio: bytes,
    *,
    tray_count: int,
) -> dict[str, float]:
    """Render the browser waveform and return committed selection state."""
    default = {
        "selection": {
            "start": selection[0],
            "end": selection[1],
            "view_start": view[0],
            "view_end": view[1],
            "commit_id": 0,
            "fade_ms": 10,
        }
    }
    result = _interactive_waveform(
        key="audio_chopper_interactive_waveform_v10",
        data={
            "peaks": waveform.peaks,
            "duration": waveform.duration_seconds,
            "selection": {"start": selection[0], "end": selection[1]},
            "view": {"start": view[0], "end": view[1]},
            "audio_url": (
                "data:audio/mpeg;base64,"
                + base64.b64encode(browser_audio).decode("ascii")
            ),
            "tray_count": tray_count,
            "tray_full": tray_count >= 4,
        },
        default=default,
        height=390,
        on_selection_change=lambda: None,
    )
    value: Any = getattr(result, "selection", None)
    return value or default["selection"]
