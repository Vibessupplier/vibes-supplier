import streamlit as st

from ui import load_design


st.set_page_config(
    page_title="Vibes Supplier",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded",
)

load_design()

pages = {
    "HOME": [
        st.Page(
            "pages/0_Home.py",
            title="Vibes Supplier",
            default=True,
        ),
    ],
    "ANALYZE": [
        st.Page(
            "pages/1_Key_BPM_Finder.py",
            title="Key & BPM Finder",
            url_path="key-bpm-finder",
        ),
        st.Page(
            "pages/4_Mastering_Analyzer.py",
            title="Mastering Analyzer",
            url_path="mastering-analyzer",
        ),
    ],
    "TRANSFORM": [
        st.Page(
            "pages/2_Speed_Changer.py",
            title="Speed Changer",
            url_path="speed-changer",
        ),
        st.Page(
            "pages/5_Audio_Chopper.py",
            title="Audio Chopper",
            url_path="audio-chopper",
        ),
        st.Page(
            "pages/7_Stereo_Mono_Converter.py",
            title="Stereo / Mono Converter",
            url_path="stereo-mono-converter",
        ),
    ],
    "SEPARATE": [
        st.Page(
            "pages/3_Vocal_Split.py",
            title="Vocal Split · Soon",
            url_path="vocal-split",
        ),
    ],
    "SUPPORT": [
        st.Page(
            "pages/6_Feedback.py",
            title="Feedback",
            url_path="feedback",
        ),
    ],
}

navigation = st.navigation(pages, position="sidebar")
navigation.run()
