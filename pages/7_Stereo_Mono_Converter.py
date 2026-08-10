from io import BytesIO
from pathlib import Path
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

import streamlit as st

from analytics import track_event, track_page_view
from stereo_converter import (
    SUPPORTED_MP3_BITRATES,
    StereoConverterError,
    inspect_audio,
    merge_mono,
    resolve_output_settings,
    source_bitrate_kbps,
    split_stereo,
)
from ui import show_header, show_tool_header


def info_line(info) -> str:
    bitrate = f" · {info.bit_rate / 1000:.0f} kbps" if info.bit_rate else ""
    depth = f" · {info.bits_per_sample}-bit" if info.bits_per_sample else ""
    return f"{info.channels} ch · {info.sample_rate / 1000:g} kHz{depth}{bitrate}"


def inspect_upload(upload):
    suffix = Path(upload.name).suffix.lower() or ".audio"
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / f"source{suffix}"
        path.write_bytes(upload.getvalue())
        return inspect_audio(path)


def bitrate_control(default_bitrate: int | None, key: str) -> int:
    options = list(SUPPORTED_MP3_BITRATES)
    default = default_bitrate if default_bitrate in options else 192
    return st.selectbox(
        "MP3 bitrate",
        options,
        index=options.index(default),
        format_func=lambda value: f"{value} kbps" + (" · MATCH SOURCE" if value == default_bitrate else ""),
        key=key,
    )


def patchbay(mode: str) -> str:
    """Return a lightweight analog routing diagram for the selected mode."""
    if mode == "split":
        left_label, right_label = "STEREO INPUT", "L MONO + R MONO"
        jacks = (
            '<div class="jack jack-input jack-center active"><i></i></div>'
            '<div class="jack jack-output jack-top"><i></i><b>L</b></div>'
            '<div class="jack jack-output jack-bottom"><i></i><b>R</b></div>'
        )
    else:
        left_label, right_label = "L MONO + R MONO", "STEREO OUTPUT"
        jacks = (
            '<div class="jack jack-input jack-top active"><i></i><b>L</b></div>'
            '<div class="jack jack-input jack-bottom active"><i></i><b>R</b></div>'
            '<div class="jack jack-output jack-center"><i></i></div>'
        )
    return f"""
        <div class="patchbay">
          <span class="panel-screw screw-a"></span><span class="panel-screw screw-b"></span>
          <div class="patchbay-plate">VS ROUTING MATRIX / 06 <b>● SIGNAL PATH</b></div>
          <div class="patch-field patch-{mode}" role="img" aria-label="{left_label} to {right_label}">
            <span class="route-label route-left">{left_label}</span>
            <span class="route-label route-right">{right_label}</span>
            {jacks}
          </div>
          <div class="patchbay-note">{'ONE SOURCE / TWO DISCRETE CHANNELS' if mode == 'split' else 'TWO SOURCES / ONE INTERLEAVED FILE'}</div>
        </div>
    """


track_page_view("stereo_mono_converter")
show_header()
show_tool_header(
    "Transform / 06",
    "Stereo / Mono Converter",
    "Route a stereo master into separate L and R files, or wire two mono tracks into one stereo output.",
)

st.markdown(
    """
    <style>
    .patchbay{position:relative;margin:.35rem 0 1.45rem;padding:.65rem 1rem .75rem;border:1px solid rgba(216,201,167,.32);border-radius:3px;background:repeating-linear-gradient(95deg,rgba(255,255,255,.018) 0 1px,transparent 1px 7px),linear-gradient(145deg,#292a23,#171b17 58%,#30251b);box-shadow:inset 0 0 0 3px rgba(0,0,0,.3),inset 0 1px rgba(238,227,199,.09),0 12px 26px rgba(0,0,0,.24);overflow:hidden}
    .patchbay::after{content:"";position:absolute;inset:2.25rem 1rem 1.8rem;border:1px solid rgba(0,0,0,.5);pointer-events:none}
    .patchbay-plate{display:flex;justify-content:space-between;padding:.25rem .35rem .5rem;color:var(--sand);font:700 .58rem/1 var(--font-technical);letter-spacing:.16em}.patchbay-plate b{color:var(--lamp-green);font-weight:700}
    .patch-field{position:relative;height:185px;margin:.05rem 0 .35rem;border:1px solid rgba(0,0,0,.55);background-color:rgba(13,17,14,.16);background-repeat:no-repeat;background-position:center;background-size:100% 100%}
    .patch-field.patch-split{background-image:radial-gradient(circle at 50% 48%,rgba(89,68,49,.2),transparent 46%),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 185' preserveAspectRatio='none'%3E%3Cdefs%3E%3Cfilter id='s' x='-10%25' y='-30%25' width='120%25' height='170%25'%3E%3CfeDropShadow dx='0' dy='5' stdDeviation='3' flood-color='%23000000' flood-opacity='.8'/%3E%3C/filter%3E%3C/defs%3E%3Cg fill='none' stroke-linecap='round' filter='url(%23s)'%3E%3Cpath d='M134 94 C250 94 270 68 390 68 C550 68 670 53 884 66' stroke='%2320201c' stroke-width='17'/%3E%3Cpath d='M134 94 C250 94 270 68 390 68 C550 68 670 53 884 66' stroke='%23b9aa82' stroke-width='11'/%3E%3Cpath d='M137 91 C250 91 270 65 390 65 C550 65 670 50 881 63' stroke='%23eee0b8' stroke-opacity='.42' stroke-width='2'/%3E%3Cpath d='M134 94 C250 94 270 116 390 116 C550 116 670 139 884 128' stroke='%23201816' stroke-width='17'/%3E%3Cpath d='M134 94 C250 94 270 116 390 116 C550 116 670 139 884 128' stroke='%239b543e' stroke-width='11'/%3E%3Cpath d='M137 91 C250 91 270 113 390 113 C550 113 670 136 881 125' stroke='%23e29a76' stroke-opacity='.38' stroke-width='2'/%3E%3C/g%3E%3C/svg%3E")}
    .patch-field.patch-merge{background-image:radial-gradient(circle at 50% 48%,rgba(89,68,49,.2),transparent 46%),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 185' preserveAspectRatio='none'%3E%3Cdefs%3E%3Cfilter id='s' x='-10%25' y='-30%25' width='120%25' height='170%25'%3E%3CfeDropShadow dx='0' dy='5' stdDeviation='3' flood-color='%23000000' flood-opacity='.8'/%3E%3C/filter%3E%3C/defs%3E%3Cg fill='none' stroke-linecap='round' filter='url(%23s)'%3E%3Cpath d='M134 66 C340 54 520 70 650 82 C760 92 810 94 884 94' stroke='%2320201c' stroke-width='17'/%3E%3Cpath d='M134 66 C340 54 520 70 650 82 C760 92 810 94 884 94' stroke='%23b9aa82' stroke-width='11'/%3E%3Cpath d='M137 63 C340 51 520 67 650 79 C760 89 810 91 881 91' stroke='%23eee0b8' stroke-opacity='.42' stroke-width='2'/%3E%3Cpath d='M134 128 C340 140 520 119 650 106 C760 96 810 94 884 94' stroke='%23201816' stroke-width='17'/%3E%3Cpath d='M134 128 C340 140 520 119 650 106 C760 96 810 94 884 94' stroke='%239b543e' stroke-width='11'/%3E%3Cpath d='M137 125 C340 137 520 116 650 103 C760 93 810 91 881 91' stroke='%23e29a76' stroke-opacity='.38' stroke-width='2'/%3E%3C/g%3E%3C/svg%3E")}
    .route-label{position:absolute;top:10px;z-index:4;color:rgba(216,201,167,.72);font:700 .62rem var(--font-technical);letter-spacing:.16em}.route-left{left:7%;}.route-right{right:7%;text-align:right}
    .jack{position:absolute;z-index:3;width:42px;height:42px;border:3px solid #89887c;border-radius:50%;background:radial-gradient(circle,#050705 0 18%,#111410 20% 43%,#b0a789 46% 51%,#46473f 54%);box-shadow:0 3px 5px #000}.jack i{position:absolute;inset:15px;border-radius:50%;background:#050705}.jack.active{border-color:#d99a45}.jack.active i{background:#87966c;box-shadow:0 0 7px rgba(135,150,108,.8)}.jack b{position:absolute;left:50%;top:46px;transform:translateX(-50%);color:var(--amber);font:800 .68rem var(--font-technical)}
    .jack-input{left:11%}.jack-output{right:11%}.jack-top{top:45px}.jack-center{top:73px}.jack-bottom{top:110px}
    .panel-screw{position:absolute;width:8px;height:8px;border-radius:50%;top:10px;background:radial-gradient(circle at 35% 30%,#aaa99d,#3b3c37 55%,#111);box-shadow:0 1px 2px #000}.screw-a{left:9px}.screw-b{right:9px}
    .patchbay-note{text-align:center;color:rgba(216,201,167,.55);font:600 .52rem var(--font-technical);letter-spacing:.18em}
    .stage-label{display:flex;align-items:center;gap:.65rem;margin:1.3rem 0 .55rem;color:var(--amber);font:800 .62rem var(--font-technical);letter-spacing:.18em}.stage-label::after{content:"";height:1px;flex:1;background:var(--line)}
    @media(max-width:600px){.patchbay{padding-left:.4rem;padding-right:.4rem}.patchbay-plate{font-size:.49rem}.patch-field{height:165px}.route-label{font-size:.48rem;max-width:38%}.jack{transform:scale(.82)}.jack-input{left:7%}.jack-output{right:7%}.cable{left:16%;width:68%}}
    </style>
    """,
    unsafe_allow_html=True,
)

mode = st.radio(
    "Routing mode",
    ["STEREO → L MONO + R MONO", "L MONO + R MONO → STEREO"],
    horizontal=True,
)

if mode == "STEREO → L MONO + R MONO":
    st.markdown(patchbay("split"), unsafe_allow_html=True)
    st.markdown('<div class="stage-label">INPUT STAGE / STEREO</div>', unsafe_allow_html=True)
    upload = st.file_uploader("Upload a stereo file", type=["wav", "mp3", "m4a", "flac"], key="split_upload")
    if upload is not None:
        try:
            source_info = inspect_upload(upload)
        except StereoConverterError as error:
            st.error(str(error)); st.stop()
        st.caption(info_line(source_info))
        if source_info.channels != 2:
            st.error("This mode requires a file with exactly two channels."); st.stop()
        st.markdown('<div class="stage-label">OUTPUT STAGE / DUAL MONO</div>', unsafe_allow_html=True)
        output_format = st.radio("Output format", ["WAV", "MP3"], horizontal=True, key="split_format")
        bitrate = None
        source_bitrate = source_bitrate_kbps(source_info)
        if output_format == "MP3":
            bitrate = bitrate_control(source_bitrate, "split_bitrate")
            if source_bitrate and bitrate > source_bitrate:
                st.info("A higher bitrate makes a larger file, but cannot restore detail already lost in the source.")
        if st.button("SPLIT CHANNELS", type="primary"):
            with st.spinner("Routing stereo into L and R..."):
                try:
                    settings = resolve_output_settings(output_format, bitrate, source_info)
                    with tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        source = root / f"source{Path(upload.name).suffix.lower()}"
                        left = root / f"left{settings.extension}"
                        right = root / f"right{settings.extension}"
                        source.write_bytes(upload.getvalue())
                        split_stereo(source, left, right, settings)
                        st.session_state["split_result"] = {
                            "signature": (upload.name, upload.size, output_format, bitrate),
                            "left": left.read_bytes(), "right": right.read_bytes(),
                            "settings": settings,
                        }
                    track_event("audio_processing_completed", {"tool": "stereo_mono_converter", "mode": "split", "format": output_format.lower()})
                except (StereoConverterError, OSError) as error:
                    st.error("The channels could not be split."); st.code(str(error))
        result = st.session_state.get("split_result")
        signature = (upload.name, upload.size, output_format, bitrate)
        if result and result["signature"] == signature:
            settings = result["settings"]
            stem = Path(upload.name).stem
            left_name, right_name = f"{stem}_L{settings.extension}", f"{stem}_R{settings.extension}"
            st.success("Independent L and R mono files are ready.")
            col_left, col_right = st.columns(2)
            with col_left:
                st.write("**LEFT / MONO**"); st.audio(result["left"], format=settings.mime_type)
                st.download_button("DOWNLOAD L", result["left"], left_name, settings.mime_type)
            with col_right:
                st.write("**RIGHT / MONO**"); st.audio(result["right"], format=settings.mime_type)
                st.download_button("DOWNLOAD R", result["right"], right_name, settings.mime_type)
            archive = BytesIO()
            with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
                zip_file.writestr(left_name, result["left"]); zip_file.writestr(right_name, result["right"])
            st.download_button("DOWNLOAD L + R / ZIP", archive.getvalue(), "vibes_supplier_L_R.zip", "application/zip")

else:
    st.markdown(patchbay("merge"), unsafe_allow_html=True)
    st.markdown('<div class="stage-label">INPUT STAGE / DUAL MONO</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns(2)
    with col_left:
        left_upload = st.file_uploader("LEFT / mono", type=["wav", "mp3", "m4a", "flac"], key="merge_left")
    with col_right:
        right_upload = st.file_uploader("RIGHT / mono", type=["wav", "mp3", "m4a", "flac"], key="merge_right")
    if left_upload is not None and right_upload is not None:
        try:
            left_info, right_info = inspect_upload(left_upload), inspect_upload(right_upload)
        except StereoConverterError as error:
            st.error(str(error)); st.stop()
        col_left.caption(info_line(left_info)); col_right.caption(info_line(right_info))
        if left_info.channels != 1 or right_info.channels != 1:
            st.error("Both inputs must be mono files."); st.stop()
        if abs(left_info.duration_seconds - right_info.duration_seconds) > 0.01:
            st.warning("The files have different lengths. The shorter channel will be completed with silence; nothing will be cut.")
        st.markdown('<div class="stage-label">OUTPUT STAGE / STEREO BUS</div>', unsafe_allow_html=True)
        swap = st.toggle("SWAP L ↔ R", help="Exchange the channel assignment before export.")
        output_format = st.radio("Output format", ["WAV", "MP3"], horizontal=True, key="merge_format")
        source_bitrate = max(filter(None, (source_bitrate_kbps(left_info), source_bitrate_kbps(right_info))), default=None)
        bitrate = bitrate_control(source_bitrate, "merge_bitrate") if output_format == "MP3" else None
        if output_format == "MP3" and source_bitrate and bitrate > source_bitrate:
            st.info("A higher bitrate cannot improve the uploaded sources; it only increases the output size.")
        if st.button("WIRE STEREO OUTPUT", type="primary"):
            with st.spinner("Wiring L and R into stereo..."):
                try:
                    settings = resolve_output_settings(output_format, bitrate, left_info)
                    with tempfile.TemporaryDirectory() as directory:
                        root = Path(directory)
                        left_path = root / f"left{Path(left_upload.name).suffix.lower()}"
                        right_path = root / f"right{Path(right_upload.name).suffix.lower()}"
                        output = root / f"stereo{settings.extension}"
                        left_path.write_bytes(left_upload.getvalue()); right_path.write_bytes(right_upload.getvalue())
                        routed_left, routed_right = (right_path, left_path) if swap else (left_path, right_path)
                        merge_mono(routed_left, routed_right, output, settings)
                        st.session_state["merge_result"] = {
                            "signature": (left_upload.name, left_upload.size, right_upload.name, right_upload.size, swap, output_format, bitrate),
                            "audio": output.read_bytes(), "settings": settings,
                        }
                    track_event("audio_processing_completed", {"tool": "stereo_mono_converter", "mode": "merge", "format": output_format.lower()})
                except (StereoConverterError, OSError) as error:
                    st.error("The stereo file could not be created."); st.code(str(error))
        result = st.session_state.get("merge_result")
        signature = (left_upload.name, left_upload.size, right_upload.name, right_upload.size, swap, output_format, bitrate)
        if result and result["signature"] == signature:
            settings = result["settings"]
            st.success("Stereo output ready. Monitor it before downloading.")
            st.audio(result["audio"], format=settings.mime_type)
            st.download_button("DOWNLOAD STEREO", result["audio"], f"vibes_supplier_stereo{settings.extension}", settings.mime_type)

st.caption("Stereo routing does not invent stereo width. It preserves or assigns the L/R channel structure you provide.")
