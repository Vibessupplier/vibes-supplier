from pathlib import Path
import tempfile

import streamlit as st

from analytics import track_event, track_page_view
from audio_chopper import (
    AudioChopperError,
    CHOPPER_PREVIEW_SECONDS,
    SAMPLE_TRAY_LIMIT,
    WaveformData,
    build_sample_archive,
    create_audio_clip,
    extract_waveform,
)
from ui import show_header, show_panel_label, show_tool_header
from waveform_component import interactive_waveform


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
        st.session_state.pop("chopper_preview", None)
        st.session_state["chopper_samples"] = []
        st.session_state["chopper_next_sample_id"] = 1
        st.session_state["chopper_view_window"] = (
            0.0,
            float(waveform.duration_seconds),
        )
        st.session_state.pop("chopper_selection", None)
        st.session_state.pop("chopper_selection_signature", None)
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
    )
    start_seconds = float(component_selection["start"])
    end_seconds = float(component_selection["end"])
    view_start_seconds = float(component_selection["view_start"])
    view_end_seconds = float(component_selection["view_end"])
    st.session_state["chopper_selection"] = (start_seconds, end_seconds)
    st.session_state["chopper_view_window"] = (
        view_start_seconds,
        view_end_seconds,
    )
    selection_signature = (*upload_signature, start_seconds, end_seconds)
    if st.session_state.get("chopper_selection_signature") != selection_signature:
        st.session_state.pop("chopper_preview", None)
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
        "Play, selection and zoom stay in the browser. Press Use Selection "
        "only when the range is ready for preview or export."
    )

    saved_samples = st.session_state.setdefault("chopper_samples", [])
    tray_is_full = len(saved_samples) >= SAMPLE_TRAY_LIMIT

    preview_column, save_column = st.columns(2)
    with preview_column:
        create_preview = st.button("PREVIEW SELECTION", type="secondary")
    with save_column:
        save_sample = st.button(
            "SAVE SAMPLE",
            type="primary",
            disabled=tray_is_full,
            help=(
                f"The sample tray holds {SAMPLE_TRAY_LIMIT} samples. "
                "Remove one to save another."
                if tray_is_full
                else "Cut this selection and add it to the sample tray."
            ),
        )

    if create_preview:
        with st.spinner("Preparing the selected preview..."):
            try:
                with tempfile.TemporaryDirectory() as temp_directory:
                    input_path = Path(temp_directory) / f"source{suffix}"
                    output_path = Path(temp_directory) / "sample-preview.mp3"
                    input_path.write_bytes(audio_data)
                    create_audio_clip(
                        input_path,
                        output_path,
                        start_seconds,
                        end_seconds,
                        waveform.duration_seconds,
                        maximum_duration_seconds=CHOPPER_PREVIEW_SECONDS,
                    )
                    st.session_state["chopper_preview"] = output_path.read_bytes()
                    track_event("audio_preview_created", {"tool": "audio_chopper"})
            except (AudioChopperError, OSError) as error:
                st.error("The selected preview could not be created.")
                st.code(str(error))

    if save_sample:
        with st.spinner("Saving the selection to your sample tray..."):
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
                    )
                    sample_id = st.session_state.get("chopper_next_sample_id", 1)
                    saved_samples.append(
                        {
                            "id": sample_id,
                            "name": f"sample_{sample_id:02d}",
                            "audio": output_path.read_bytes(),
                            "start": start_seconds,
                            "end": end_seconds,
                        }
                    )
                    st.session_state["chopper_next_sample_id"] = sample_id + 1
                    st.session_state.pop("chopper_preview", None)
                    track_event(
                        "audio_processing_completed",
                        {"tool": "audio_chopper", "destination": "sample_tray"},
                    )
            except (AudioChopperError, OSError) as error:
                st.error("The sample could not be saved.")
                st.code(str(error))

    preview = st.session_state.get("chopper_preview")
    if preview is not None:
        st.write("**Selected preview (up to 30 seconds)**")
        st.audio(preview, format="audio/mpeg")

    if saved_samples:
        show_panel_label("TRAY 02", "SAVED SAMPLES", "LOADED")
        st.markdown(
            f'<div class="sample-tray-count">{len(saved_samples)} / '
            f'{SAMPLE_TRAY_LIMIT} sample slots loaded</div>',
            unsafe_allow_html=True,
        )

        for position, sample in enumerate(list(saved_samples), start=1):
            with st.container(border=True):
                name_column, delete_column = st.columns([4, 1])
                with name_column:
                    updated_name = st.text_input(
                        f"Sample {position} name",
                        value=sample["name"],
                        key=f"chopper_sample_name_{sample['id']}",
                    )
                    sample["name"] = updated_name
                with delete_column:
                    st.write("")
                    if st.button(
                        "REMOVE",
                        key=f"chopper_remove_sample_{sample['id']}",
                        type="secondary",
                    ):
                        saved_samples.remove(sample)
                        st.rerun()
                st.caption(
                    f"{format_time(sample['start'])} — "
                    f"{format_time(sample['end'])} · "
                    f"{sample['end'] - sample['start']:.1f} seconds"
                )
                st.audio(sample["audio"], format="audio/mpeg")

        try:
            archive_data = build_sample_archive(
                [(sample["name"], sample["audio"]) for sample in saved_samples]
            )
        except AudioChopperError as error:
            st.error(str(error))
        else:
            st.download_button(
                "DOWNLOAD ALL SAMPLES",
                data=archive_data,
                file_name=f"{Path(audio_file.name).stem}_samples.zip",
                mime="application/zip",
                on_click=track_event,
                args=(
                    "audio_downloaded",
                    {"tool": "audio_chopper", "format": "zip"},
                ),
            )

        if tray_is_full:
            st.info(
                "Your sample tray is full. Remove a sample to cut another."
            )

    st.caption(
        "The highlighted waveform is the selected range. Preview is limited "
        "to 30 seconds; Save Sample adds the complete selection to your tray."
    )
