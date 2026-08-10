from pathlib import Path
import tempfile

import streamlit as st

from analytics import track_event, track_page_view
from audio_chopper import (
    AudioChopperError,
    SAMPLE_TRAY_LIMIT,
    WaveformData,
    build_sample_archive,
    create_audio_clip,
    extract_waveform,
)
from sample_tray_component import sample_memory
from ui import show_header, show_tool_header
from waveform_component import interactive_waveform


TRAY_COMPONENT_KEY = "audio_chopper_sample_memory_v1"
PENDING_TRAY_ACTION_KEY = "audio_chopper_pending_tray_action"


def capture_tray_action() -> None:
    """Copy a tray action into session state before Streamlit reruns."""
    component_state = st.session_state.get(TRAY_COMPONENT_KEY, {})
    if isinstance(component_state, dict):
        action = component_state.get("action")
    else:
        action = getattr(component_state, "action", None)
    if action:
        st.session_state[PENDING_TRAY_ACTION_KEY] = dict(action)


@st.cache_data(show_spinner=False)
def analyze_uploaded_waveform(audio_data: bytes, suffix: str) -> WaveformData:
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        input_path.write_bytes(audio_data)
        return extract_waveform(input_path)


@st.cache_data(show_spinner=False)
def create_browser_audio(
    audio_data: bytes,
    suffix: str,
    source_duration_seconds: float,
) -> bytes:
    """Create one browser-friendly copy for fluid JavaScript playback."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"source{suffix}"
        output_path = Path(temp_directory) / "browser-player.mp3"
        input_path.write_bytes(audio_data)
        create_audio_clip(
            input_path,
            output_path,
            0.0,
            source_duration_seconds,
            source_duration_seconds,
        )
        return output_path.read_bytes()


def format_time(seconds: float) -> str:
    minutes, remaining_seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{remaining_seconds:04.1f}"


track_page_view("audio_chopper")
show_header()
show_tool_header(
    "Transform / 05",
    "Audio Chopper",
    "Find the moment, cut the sample and take it into your next production.",
)

st.markdown(
    """
    <style>
    .sample-readout { display:grid; grid-template-columns:repeat(3,1fr); gap:.6rem; margin:.4rem 0 1rem; }
    .sample-readout div { padding:.75rem; border:1px solid var(--line); border-radius:2px; background:rgba(23,24,21,.88); color:var(--sand); font-size:.68rem; letter-spacing:.08em; box-shadow:inset 0 0 0 2px rgba(0,0,0,.12); }
    .sample-readout b { display:block; margin-top:.3rem; color:var(--amber); font-family:var(--font-technical); font-size:.95rem; letter-spacing:0; }
    .sample-tray-count { margin:-.15rem 0 1rem; color:var(--muted); font-family:var(--font-technical); font-size:.66rem; letter-spacing:.09em; text-transform:uppercase; }
    </style>
    """,
    unsafe_allow_html=True,
)

audio_file = st.file_uploader(
    "Upload audio to sample",
    type=["wav", "mp3", "m4a", "flac"],
    key="audio_chopper_upload",
)

if audio_file is not None:
    audio_data = audio_file.getvalue()
    suffix = Path(audio_file.name).suffix.lower()
    upload_signature = ("waveform-v3", audio_file.name, audio_file.size)

    if st.session_state.get("chopper_upload_signature") != upload_signature:
        with st.spinner("Drawing the waveform..."):
            try:
                waveform = analyze_uploaded_waveform(audio_data, suffix)
            except (AudioChopperError, OSError) as error:
                st.error("The waveform could not be created.")
                st.code(str(error))
                st.stop()
        st.session_state["chopper_waveform"] = waveform
        st.session_state["chopper_samples"] = []
        st.session_state["chopper_next_sample_id"] = 1
        st.session_state["chopper_view_window"] = (
            0.0,
            float(waveform.duration_seconds),
        )
        st.session_state.pop("chopper_selection", None)
        st.session_state.pop("chopper_selection_signature", None)
        st.session_state["chopper_last_commit_id"] = 0
        st.session_state.pop(PENDING_TRAY_ACTION_KEY, None)
        st.session_state.pop(TRAY_COMPONENT_KEY, None)
        st.session_state["chopper_upload_signature"] = upload_signature

    waveform = st.session_state["chopper_waveform"]
    default_end = min(30.0, waveform.duration_seconds)
    view_start_seconds, view_end_seconds = st.session_state.get(
        "chopper_view_window",
        (0.0, float(waveform.duration_seconds)),
    )

    current_selection = st.session_state.get(
        "chopper_selection",
        (0.0, float(default_end)),
    )
    saved_samples = st.session_state.setdefault("chopper_samples", [])
    pending_tray_action = st.session_state.pop(PENDING_TRAY_ACTION_KEY, None)
    if pending_tray_action is not None:
        action_type = pending_tray_action.get("type")
        sample_id = pending_tray_action.get("id")
        sample = next(
            (item for item in saved_samples if item["id"] == sample_id),
            None,
        )
        if sample is not None and action_type == "remove":
            saved_samples.remove(sample)
        elif sample is not None and action_type == "rename":
            updated_name = str(pending_tray_action.get("name", "")).strip()
            if updated_name:
                sample["name"] = updated_name[:64]

    with st.spinner("Preparing the interactive player..."):
        try:
            browser_audio = create_browser_audio(
                audio_data,
                suffix,
                waveform.duration_seconds,
            )
        except (AudioChopperError, OSError) as error:
            st.error("The interactive player could not be prepared.")
            st.code(str(error))
            st.stop()
    component_selection = interactive_waveform(
        waveform,
        current_selection,
        (view_start_seconds, view_end_seconds),
        browser_audio,
        tray_count=len(saved_samples),
    )
    start_seconds = float(component_selection["start"])
    end_seconds = float(component_selection["end"])
    requested_fade_ms = int(component_selection.get("fade_ms", 10))
    fade_ms = requested_fade_ms if requested_fade_ms in {0, 5, 10, 25, 50} else 10
    view_start_seconds = float(component_selection["view_start"])
    view_end_seconds = float(component_selection["view_end"])
    st.session_state["chopper_selection"] = (start_seconds, end_seconds)
    st.session_state["chopper_view_window"] = (
        view_start_seconds,
        view_end_seconds,
    )
    selection_signature = (*upload_signature, start_seconds, end_seconds)
    st.session_state["chopper_selection_signature"] = selection_signature

    st.markdown(
        f"""
        <div class="sample-readout">
            <div>START<b>{format_time(start_seconds)}</b></div>
            <div>END<b>{format_time(end_seconds)}</b></div>
            <div>LENGTH<b>{end_seconds - start_seconds:.1f} s</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Select, play or loop the range in the browser. Use Selection cuts the "
        "complete range with FFmpeg and loads it directly into Sample Memory."
    )

    commit_id = int(component_selection.get("commit_id", 0))
    last_commit_id = int(st.session_state.get("chopper_last_commit_id", 0))
    if commit_id > last_commit_id:
        st.session_state["chopper_last_commit_id"] = commit_id
        if len(saved_samples) >= SAMPLE_TRAY_LIMIT:
            st.warning("Sample Memory is full. Remove a slot before adding another.")
        else:
            with st.spinner("Cutting the selection into Sample Memory..."):
                try:
                    with tempfile.TemporaryDirectory() as temp_directory:
                        input_path = Path(temp_directory) / f"source{suffix}"
                        output_path = Path(temp_directory) / "sample.mp3"
                        input_path.write_bytes(audio_data)
                        create_audio_clip(
                            input_path,
                            output_path,
                            start_seconds,
                            end_seconds,
                            waveform.duration_seconds,
                            edge_fade_seconds=fade_ms / 1000.0,
                        )
                        sample_id = st.session_state.get(
                            "chopper_next_sample_id", 1
                        )
                        saved_samples.append(
                            {
                                "id": sample_id,
                                "name": f"SAMPLE_{sample_id:02d}",
                                "audio": output_path.read_bytes(),
                                "start": start_seconds,
                                "end": end_seconds,
                            }
                        )
                        st.session_state["chopper_next_sample_id"] = sample_id + 1
                        track_event(
                            "audio_processing_completed",
                            {"tool": "audio_chopper", "destination": "sample_tray"},
                        )
                except (AudioChopperError, OSError) as error:
                    st.error("The sample could not be added to Sample Memory.")
                    st.code(str(error))

    sample_memory(
        saved_samples,
        key=TRAY_COMPONENT_KEY,
        on_action_change=capture_tray_action,
    )

    if saved_samples:
        try:
            archive_data = build_sample_archive(
                [(sample["name"], sample["audio"]) for sample in saved_samples]
            )
        except AudioChopperError as error:
            st.error(str(error))
        else:
            st.download_button(
                "DOWNLOAD ALL / ZIP",
                data=archive_data,
                file_name="vibes_supplier_samples.zip",
                mime="application/zip",
                on_click=track_event,
                args=(
                    "audio_downloaded",
                    {"tool": "audio_chopper", "format": "zip"},
                ),
            )

    if len(saved_samples) >= SAMPLE_TRAY_LIMIT:
        st.info("Sample Memory is full: 4 of 4 slots loaded.")

    st.caption(
        "The highlighted waveform is the active range. Use Selection adds the "
        "complete FFmpeg cut directly to the first free memory slot."
    )
