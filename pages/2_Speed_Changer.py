from pathlib import Path
import tempfile

import streamlit as st

from analytics import track_event, track_page_view
from audio_analysis import detect_bpm_from_file
from audio_effects import (
    MAX_SPEED_FACTOR,
    create_speed_player_audio,
    create_speed_preview,
    change_speed,
    resolve_speed_settings,
)
from audio_engine import AudioProcessingError
from speed_player_component import live_speed_player
from ui import show_header, show_tool_header


SPEED_PLAYER_KEY = "speed_live_player_v1"
PENDING_ACTION_KEY = "speed_pending_action"


@st.cache_data(show_spinner=False)
def detect_uploaded_bpm(audio_data: bytes, suffix: str) -> float:
    """Cache BPM detection so UI reruns do not analyze the same file again."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"input{suffix}"
        input_path.write_bytes(audio_data)
        return detect_bpm_from_file(input_path)


@st.cache_data(show_spinner=False)
def prepare_speed_player_audio(audio_data: bytes, suffix: str) -> bytes:
    """Cache one browser-compatible copy for uninterrupted live audition."""
    with tempfile.TemporaryDirectory() as temp_directory:
        input_path = Path(temp_directory) / f"input{suffix}"
        output_path = Path(temp_directory) / "speed-player.mp3"
        input_path.write_bytes(audio_data)
        create_speed_player_audio(input_path, output_path)
        return output_path.read_bytes()


def capture_speed_action(action: str) -> None:
    """Copy a component trigger into regular session state before rerunning."""
    component_state = st.session_state.get(SPEED_PLAYER_KEY, {})
    if isinstance(component_state, dict):
        payload = component_state.get(action)
    else:
        payload = getattr(component_state, action, None)
    if payload:
        st.session_state[PENDING_ACTION_KEY] = {
            "action": action,
            "settings": dict(payload),
        }


track_page_view("speed_changer")
show_header()
show_tool_header(
    "Transform / 02",
    "Speed Changer",
    "Play the track, reshape its motion live and export the final result.",
)

audio_file = st.file_uploader(
    "Upload your audio",
    type=["wav", "mp3", "m4a"],
    key="speed_upload",
)

if audio_file is not None:
    audio_data = audio_file.getvalue()
    suffix = Path(audio_file.name).suffix.lower()
    upload_signature = (audio_file.name, audio_file.size)

    if st.session_state.get("speed_upload_signature") != upload_signature:
        with st.spinner("Powering the live speed deck..."):
            try:
                detected_bpm = detect_uploaded_bpm(audio_data, suffix)
                browser_audio = prepare_speed_player_audio(audio_data, suffix)
            except (AudioProcessingError, OSError, ValueError) as error:
                st.error("The live speed deck could not prepare this audio.")
                st.code(str(error))
                st.stop()

        source_bpm = round(detected_bpm, 1)
        target_bpm = round(min(source_bpm * 1.20, source_bpm * MAX_SPEED_FACTOR), 1)
        st.session_state["speed_browser_audio"] = browser_audio
        st.session_state["speed_live_settings"] = {
            "source_bpm": source_bpm,
            "target_bpm": target_bpm,
            "pitch_mode": "Follow speed",
            "pitch_semitones": 0.0,
        }
        st.session_state.pop("speed_preview", None)
        st.session_state.pop("speed_result", None)
        st.session_state.pop(PENDING_ACTION_KEY, None)
        st.session_state.pop(SPEED_PLAYER_KEY, None)
        st.session_state["speed_upload_signature"] = upload_signature

    pending_action = st.session_state.pop(PENDING_ACTION_KEY, None)
    settings_error = None
    resolved_settings = None
    if pending_action is not None:
        submitted = pending_action["settings"]
        try:
            resolved_settings = resolve_speed_settings(
                float(submitted["source_bpm"]),
                float(submitted["target_bpm"]),
                str(submitted["pitch_mode"]),
                float(submitted.get("pitch_semitones", 0.0)),
            )
        except (AudioProcessingError, KeyError, TypeError, ValueError) as error:
            settings_error = str(error)
            pending_action = None
        else:
            st.session_state["speed_live_settings"] = {
                "source_bpm": resolved_settings.source_bpm,
                "target_bpm": resolved_settings.target_bpm,
                "pitch_mode": resolved_settings.pitch_mode,
                "pitch_semitones": resolved_settings.pitch_semitones,
            }

    if settings_error:
        st.error(f"The live deck returned invalid settings: {settings_error}")

    live_speed_player(
        st.session_state["speed_browser_audio"],
        audio_id=f"{audio_file.name}:{audio_file.size}",
        settings=st.session_state["speed_live_settings"],
        key=SPEED_PLAYER_KEY,
        on_preview_change=lambda: capture_speed_action("preview"),
        on_process_change=lambda: capture_speed_action("process"),
    )

    if pending_action is not None and resolved_settings is not None:
        st.session_state.pop("speed_result", None)

        if pending_action["action"] == "preview":
            if resolved_settings.pitch_mode != "Custom":
                st.error("A rendered preview is only needed for Custom Pitch.")
            else:
                with st.spinner("Rendering the custom pitch preview..."):
                    try:
                        with tempfile.TemporaryDirectory() as temp_directory:
                            input_path = Path(temp_directory) / f"input{suffix}"
                            output_path = Path(temp_directory) / "speed-preview.mp3"
                            input_path.write_bytes(audio_data)
                            create_speed_preview(
                                input_path,
                                output_path,
                                speed=resolved_settings.speed,
                                pitch_semitones=(
                                    resolved_settings.processing_pitch_semitones
                                ),
                            )
                            st.session_state["speed_preview"] = output_path.read_bytes()
                            track_event(
                                "audio_preview_created",
                                {"tool": "speed_changer", "pitch_mode": "Custom"},
                            )
                    except (AudioProcessingError, OSError) as error:
                        st.error("The custom pitch preview could not be created.")
                        st.code(str(error))

        elif pending_action["action"] == "process":
            st.session_state.pop("speed_preview", None)
            with st.spinner("Changing speed with the selected settings..."):
                try:
                    with tempfile.TemporaryDirectory() as temp_directory:
                        input_path = Path(temp_directory) / f"input{suffix}"
                        output_path = Path(temp_directory) / "speed-changed.mp3"
                        input_path.write_bytes(audio_data)
                        change_speed(
                            input_path,
                            output_path,
                            speed=resolved_settings.speed,
                            pitch_semitones=(
                                resolved_settings.processing_pitch_semitones
                            ),
                        )
                        st.session_state["speed_result"] = {
                            "audio": output_path.read_bytes(),
                            "filename": (
                                f"{Path(audio_file.name).stem}_speed-changed.mp3"
                            ),
                            "source_bpm": resolved_settings.source_bpm,
                            "target_bpm": resolved_settings.target_bpm,
                            "pitch_semitones": resolved_settings.pitch_semitones,
                        }
                        track_event(
                            "audio_processing_completed",
                            {
                                "tool": "speed_changer",
                                "pitch_mode": resolved_settings.pitch_mode,
                            },
                        )
                except (AudioProcessingError, OSError) as error:
                    st.error("The speed-changed version could not be created.")
                    st.code(str(error))

    preview = st.session_state.get("speed_preview")
    if preview is not None:
        st.write("**Rendered Custom Pitch preview (up to 20 seconds)**")
        st.audio(preview, format="audio/mpeg")

    result = st.session_state.get("speed_result")
    if result is not None:
        st.success("Your speed-changed version is ready.")
        st.write(
            f"**{result['source_bpm']:.1f} BPM → "
            f"{result['target_bpm']:.1f} BPM**"
        )
        st.write(f"**Pitch: {result['pitch_semitones']:+.1f} semitones**")
        st.audio(result["audio"], format="audio/mpeg")
        st.download_button(
            "DOWNLOAD MP3",
            data=result["audio"],
            file_name=result["filename"],
            mime="audio/mpeg",
        )
