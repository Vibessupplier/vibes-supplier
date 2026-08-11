from pathlib import Path
import tempfile

import streamlit as st

from analytics import track_event, track_page_view
from format_converter import (
    BITRATES,
    OUTPUT_FORMATS,
    SAMPLE_RATES,
    WAV_DEPTHS,
    FormatConverterError,
    convert_audio,
    inspect_source,
    matched_bitrate,
    resolve_conversion_settings,
)
from ui import show_header, show_tool_header


@st.cache_data(show_spinner=False)
def inspect_uploaded_audio(audio_data: bytes, suffix: str):
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / f"source{suffix}"
        source.write_bytes(audio_data)
        return inspect_source(source)


def source_format(codec_name: str) -> str:
    return {
        "mp3": "MP3",
        "aac": "M4A / AAC",
        "alac": "M4A / ALAC",
        "flac": "FLAC",
        "pcm_s16le": "WAV PCM",
        "pcm_s24le": "WAV PCM",
        "pcm_s32le": "WAV PCM",
        "pcm_f32le": "WAV FLOAT",
    }.get(codec_name, codec_name.upper())


def rate_label(rate: int) -> str:
    return f"{rate / 1000:g} kHz"


track_page_view("audio_format_converter")
show_header()
show_tool_header(
    "Transform / 08",
    "Audio Format Converter",
    "Move audio cleanly between everyday studio formats with explicit quality controls.",
)

st.markdown(
    """
    <style>
    .format-machine{display:grid;grid-template-columns:1fr 1.15fr 1fr;align-items:center;gap:.7rem;margin:.2rem 0 1.3rem;padding:1rem;border:1px solid var(--line-strong);background:repeating-linear-gradient(100deg,transparent 0 9px,rgba(255,255,255,.018) 10px),linear-gradient(145deg,rgba(48,37,27,.88),rgba(23,24,21,.97));box-shadow:inset 0 0 0 3px rgba(0,0,0,.25),0 10px 24px rgba(0,0,0,.24)}
    .reel-stage{text-align:center;color:var(--sand);font:800 .58rem var(--font-technical);letter-spacing:.13em}.reel{position:relative;width:74px;height:74px;margin:0 auto .55rem;border:4px solid #77766b;border-radius:50%;background:radial-gradient(circle,#171815 0 10%,#77766b 11% 14%,#30251b 15% 30%,#171815 31% 39%,#595950 40% 43%,#20221e 44%);box-shadow:inset 0 0 10px #000,0 4px 8px rgba(0,0,0,.5)}
    .reel::before,.reel::after{content:"";position:absolute;top:13px;left:31px;width:8px;height:20px;border-radius:8px;background:#171815;transform-origin:4px 24px}.reel::after{transform:rotate(120deg)}.reel-output{border-color:#d99a45}
    .matrix-display{padding:.9rem;border:3px solid #0c0f0c;background:linear-gradient(rgba(238,227,199,.06),transparent),#172219;box-shadow:0 0 0 2px #53544d,inset 0 6px 12px rgba(0,0,0,.4);text-align:center}.matrix-display small{display:block;color:#87966c;font:700 .52rem var(--font-technical);letter-spacing:.16em}.matrix-display b{display:block;margin:.45rem 0;color:var(--amber);font:800 1.05rem var(--font-technical)}.matrix-display span{color:var(--muted);font:600 .5rem var(--font-technical);letter-spacing:.08em}
    .source-readout{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;margin:.8rem 0 1.25rem;border:1px solid var(--line)}.source-readout div{padding:.75rem;background:rgba(23,24,21,.9);color:var(--muted);font:700 .52rem var(--font-technical);letter-spacing:.09em}.source-readout b{display:block;margin-top:.35rem;color:var(--bone);font-size:.72rem;letter-spacing:0}
    .stage-label{display:flex;align-items:center;gap:.65rem;margin:1.2rem 0 .55rem;color:var(--amber);font:800 .61rem var(--font-technical);letter-spacing:.17em}.stage-label::after{content:"";height:1px;flex:1;background:var(--line)}
    @media(max-width:650px){.format-machine{grid-template-columns:1fr}.reel{width:58px;height:58px}.source-readout{grid-template-columns:repeat(2,1fr)}.source-readout div:last-child{grid-column:1/-1}}
    </style>
    <div class="format-machine">
      <div class="reel-stage"><div class="reel"></div>SOURCE REEL</div>
      <div class="matrix-display"><small>VS FORMAT MATRIX / 08</small><b>CODEC ROUTING</b><span>AUDIO STREAM 01 · OUTPUT ARMED</span></div>
      <div class="reel-stage"><div class="reel reel-output"></div>OUTPUT REEL</div>
    </div>
    """,
    unsafe_allow_html=True,
)

upload = st.file_uploader(
    "Upload audio to convert",
    type=["mp3", "wav", "flac", "m4a"],
    key="format_converter_upload",
)

if upload is not None:
    audio_data = upload.getvalue()
    suffix = Path(upload.name).suffix.lower()
    try:
        source_info = inspect_uploaded_audio(audio_data, suffix)
    except (FormatConverterError, OSError) as error:
        st.error("The audio stream could not be inspected.")
        st.code(str(error))
        st.stop()

    bitrate_text = f"{source_info.bit_rate / 1000:.0f} kbps" if source_info.bit_rate else "LOSSLESS"
    depth_text = f"{source_info.bits_per_sample}-bit" if source_info.bits_per_sample else "—"
    st.markdown(
        f"""
        <div class="source-readout">
          <div>FORMAT<b>{source_format(source_info.codec_name)}</b></div>
          <div>CHANNELS<b>{source_info.channels}</b></div>
          <div>SAMPLE RATE<b>{rate_label(source_info.sample_rate)}</b></div>
          <div>BIT DEPTH<b>{depth_text}</b></div>
          <div>BITRATE<b>{bitrate_text}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="stage-label">OUTPUT STAGE / FORMAT</div>', unsafe_allow_html=True)
    output_format = st.radio("Output format", OUTPUT_FORMATS, horizontal=True)

    rate_options = [None, *SAMPLE_RATES]
    selected_rate = st.selectbox(
        "Sample rate",
        rate_options,
        format_func=lambda value: f"MATCH SOURCE · {rate_label(source_info.sample_rate)}" if value is None else rate_label(value),
    )

    selected_bitrate = None
    selected_depth = None
    if output_format in {"MP3", "M4A / AAC"}:
        source_match = matched_bitrate(source_info)
        bitrate_options = [None, *BITRATES]
        selected_bitrate = st.selectbox(
            f"{output_format} bitrate",
            bitrate_options,
            format_func=lambda value: f"MATCH SOURCE · {source_match} kbps" if value is None else f"{value} kbps",
        )
        resolved_bitrate = source_match if selected_bitrate is None else selected_bitrate
        if source_info.bit_rate and resolved_bitrate > source_info.bit_rate / 1000 + 8:
            st.info("Increasing bitrate creates a larger file but cannot restore detail missing from the source.")
        st.caption("MP3 and AAC are lossy formats. Exporting requires a new encode, even when matching the source bitrate.")
    elif output_format == "WAV":
        matched_depth = source_info.bits_per_sample if source_info.bits_per_sample in WAV_DEPTHS else 24
        depth_options = [None, *WAV_DEPTHS]
        selected_depth = st.selectbox(
            "PCM bit depth",
            depth_options,
            format_func=lambda value: f"MATCH SOURCE · {matched_depth}-bit" if value is None else f"{value}-bit PCM",
        )
        if source_info.codec_name in {"mp3", "aac"}:
            st.info("WAV avoids further lossy compression, but it cannot recover detail already removed from an MP3 or AAC source.")
    elif output_format == "FLAC":
        st.caption("FLAC is lossless. It reduces file size without discarding decoded audio samples.")
        if source_info.codec_name in {"mp3", "aac"}:
            st.info("FLAC prevents another lossy encode, but it cannot restore information already removed from the source.")
    else:
        st.caption("ALAC is Apple Lossless audio inside an M4A container, compatible with the Apple ecosystem.")
        if source_info.codec_name in {"mp3", "aac"}:
            st.info("ALAC prevents another lossy encode, but it cannot restore information already removed from the source.")

    resolved_rate = source_info.sample_rate if selected_rate is None else selected_rate
    if resolved_rate > source_info.sample_rate:
        st.warning("Upsampling increases the sample count but does not add new high-frequency detail.")

    signature = (
        upload.name, upload.size, output_format,
        selected_rate, selected_bitrate, selected_depth,
    )
    if st.button("CONVERT AUDIO", type="primary"):
        with st.spinner("Routing audio through the format matrix..."):
            try:
                settings = resolve_conversion_settings(
                    output_format,
                    source_info,
                    bitrate_kbps=selected_bitrate,
                    sample_rate=selected_rate,
                    wav_bit_depth=selected_depth,
                )
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    source = root / f"source{suffix}"
                    output = root / f"converted{settings.extension}"
                    source.write_bytes(audio_data)
                    convert_audio(source, output, settings)
                    result_info = inspect_source(output)
                    st.session_state["format_converter_result"] = {
                        "signature": signature,
                        "audio": output.read_bytes(),
                        "settings": settings,
                        "info": result_info,
                    }
                track_event(
                    "audio_processing_completed",
                    {"tool": "audio_format_converter", "format": output_format.lower()},
                )
            except (FormatConverterError, OSError) as error:
                st.error("The audio could not be converted.")
                st.code(str(error))

    result = st.session_state.get("format_converter_result")
    if result and result["signature"] == signature:
        settings = result["settings"]
        result_info = result["info"]
        filename = f"{Path(upload.name).stem}_converted{settings.extension}"
        st.success("Output reel ready. Listen before downloading.")
        st.caption(
            f"{settings.format_name} · {result_info.channels} ch · "
            f"{rate_label(result_info.sample_rate)}"
            + (f" · {settings.bitrate_kbps} kbps" if settings.bitrate_kbps else "")
            + (f" · {settings.bit_depth}-bit" if settings.bit_depth else "")
        )
        st.audio(result["audio"], format=settings.mime_type)
        st.download_button(
            f"DOWNLOAD {settings.format_name}",
            result["audio"],
            filename,
            settings.mime_type,
            on_click=track_event,
            args=("audio_downloaded", {"tool": "audio_format_converter", "format": settings.format_name.lower()}),
        )

st.caption("Conversion changes the container and encoding settings; it does not improve information absent from the source recording.")
