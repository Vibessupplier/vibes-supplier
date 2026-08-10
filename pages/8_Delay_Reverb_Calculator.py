import streamlit as st

from analytics import track_page_view
from sync_generator_component import sync_generator
from timing_calculator import delay_timings, reverb_timings
from ui import show_header, show_tool_header


SYNC_KEY = "delay_reverb_sync_generator_v3"
PENDING_BPM_KEY = "delay_reverb_pending_bpm"


def capture_tap_tempo() -> None:
    state = st.session_state.get(SYNC_KEY, {})
    payload = state.get("bpm") if isinstance(state, dict) else getattr(state, "bpm", None)
    if isinstance(payload, dict) and "value" in payload:
        st.session_state[PENDING_BPM_KEY] = float(payload["value"])


track_page_view("delay_reverb_calculator")
show_header()
show_tool_header(
    "Tools / 07",
    "Delay & Reverb Calculator",
    "Lock delay repeats and useful reverb starting points to the tempo of your session.",
)

if PENDING_BPM_KEY in st.session_state:
    st.session_state["timing_bpm"] = st.session_state.pop(PENDING_BPM_KEY)

st.markdown(
    """
    <style>
    .timing-intro{display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:end;margin:0 0 1rem;padding:1rem;border:1px solid var(--line);background:rgba(23,34,25,.88)}
    .timing-intro span{color:var(--muted);font:700 .6rem var(--font-technical);letter-spacing:.13em}.timing-intro b{display:block;margin-top:.28rem;color:var(--bone);font:700 1rem var(--font-technical)}
    .timing-bank{margin:1.3rem 0 .6rem;border:1px solid var(--line-strong);background:linear-gradient(145deg,rgba(48,37,27,.7),rgba(23,24,21,.95));box-shadow:inset 0 0 0 3px rgba(0,0,0,.18)}
    .bank-label{display:flex;justify-content:space-between;padding:.75rem .85rem;border-bottom:1px solid var(--line);color:var(--sand);font:800 .62rem var(--font-technical);letter-spacing:.15em}.bank-label i{color:var(--lamp-green);font-style:normal}
    .timing-row{display:grid;grid-template-columns:90px repeat(3,1fr);gap:1px;border-bottom:1px solid rgba(216,201,167,.1)}.timing-row:last-child{border-bottom:0}.timing-row>*{padding:.72rem .8rem;background:rgba(16,26,20,.72)}
    .timing-row.header>*{color:var(--muted);font:700 .52rem var(--font-technical);letter-spacing:.1em}.timing-row b{color:var(--bone);font:800 .72rem var(--font-technical)}.timing-row code{display:block;color:var(--amber);font:700 .78rem var(--font-technical);background:none;padding:0}
    .reverb-row{display:grid;grid-template-columns:1.15fr .8fr .8fr 1.5fr;gap:1px;border-bottom:1px solid rgba(216,201,167,.1)}.reverb-row>*{padding:.75rem;background:rgba(16,26,20,.72)}.reverb-row b{color:var(--bone);font:800 .65rem var(--font-technical)}.reverb-row code{color:var(--amber);font:700 .76rem var(--font-technical);background:none}.reverb-row span{color:var(--muted);font-size:.72rem}
    @media(max-width:650px){.timing-row{grid-template-columns:70px repeat(3,1fr)}.timing-row>*{padding:.6rem .35rem}.timing-row code{font-size:.65rem}.reverb-row{grid-template-columns:1fr 1fr}.reverb-row span{grid-column:1/-1}.reverb-row.header{display:none}}
    </style>
    """,
    unsafe_allow_html=True,
)

bpm = float(st.session_state.setdefault("timing_bpm", 120.0))

sync_generator(bpm, key=SYNC_KEY, on_bpm_change=capture_tap_tempo)

reverb_rows = reverb_timings(bpm)
reverb_html = "".join(
    f'<div class="reverb-row"><b>{row.name}</b><code>{row.predelay_ms:.2f} ms</code><code>{row.decay_seconds:.2f} s</code><span>{row.character}</span></div>'
    for row in reverb_rows
)
st.markdown(
    f"""
    <div class="timing-bank">
      <div class="bank-label"><span>REVERB CHAMBER / STARTING POINTS</span><i>● BPM DERIVED</i></div>
      <div class="reverb-row header"><span>SPACE</span><span>PRE-DELAY</span><span>DECAY</span><span>CHARACTER</span></div>
      {reverb_html}
    </div>
    """,
    unsafe_allow_html=True,
)
st.info("Reverb values are musical starting points, not mastering rules. Adjust decay for arrangement density, source material, genre, and the behavior of your reverb plugin.")

delay_rows = delay_timings(bpm)
delay_html = "".join(
    f'<div class="timing-row"><b>{row.label}</b><code>{row.straight_ms:.2f} ms</code><code>{row.dotted_ms:.2f} ms</code><code>{row.triplet_ms:.2f} ms</code></div>'
    for row in delay_rows
)
st.markdown(
    f"""
    <div class="timing-bank">
      <div class="bank-label"><span>DELAY BANK / MILLISECONDS</span><i>● TEMPO LOCKED</i></div>
      <div class="timing-row header"><span>NOTE</span><span>STRAIGHT</span><span>DOTTED</span><span>TRIPLET</span></div>
      {delay_html}
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Use these values in a delay plugin's time control. Dotted and triplet values create different rhythmic movement at the same BPM.")
