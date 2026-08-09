"""Shared Jungle Analog presentation helpers for Streamlit pages."""

import base64
from pathlib import Path

import streamlit as st


def _asset_data_uri(filename: str) -> str:
    """Embed a versioned visual asset without relying on a public static URL."""
    asset_path = Path(__file__).parent / "static" / filename
    encoded = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def load_design() -> None:
    """Load the shared Jungle Analog visual system."""
    design = """
        <style>
        :root {
            --jungle-black: #101a14;
            --deep-forest: #172219;
            --forest-panel: #1c281e;
            --tropical-green: #3d543c;
            --wood: #30251b;
            --walnut: #594431;
            --metal: #77766b;
            --olive: #667052;
            --moss: #3d543c;
            --sand: #d8c9a7;
            --bone: #eee3c7;
            --amber: #d99a45;
            --lamp-green: #87966c;
            --warning: #b85f3d;
            --mango: var(--amber);
            --muted: rgba(216, 201, 167, 0.68);
            --line: rgba(216, 201, 167, 0.20);
            --line-strong: rgba(216, 201, 167, 0.34);
            --font-interface: "Avenir Next", Avenir, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            --font-display: "Avenir Next Condensed", "Arial Narrow", "Helvetica Neue", sans-serif;
            --font-technical: "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
            --jungle-background: none;
        }

        html, body, [class*="css"] {
            color: var(--bone);
            font-family: var(--font-interface);
        }

        button, input, select, textarea {
            font-family: var(--font-interface) !important;
        }

        .stApp {
            background-color: var(--jungle-black);
            background-image:
                linear-gradient(rgba(16,26,20,.26), rgba(16,26,20,.50)),
                radial-gradient(circle at 50% 32%, transparent 0 18rem, rgba(16,26,20,.14) 44rem),
                var(--jungle-background);
            background-position: center top;
            background-repeat: no-repeat;
            background-size: cover;
            background-attachment: fixed;
            color: var(--bone);
        }

        .stApp::before,
        .stApp::after {
            display: none;
        }

        [data-testid="stAppViewContainer"] > .main {
            position: relative;
            z-index: 1;
        }

        .block-container {
            max-width: 960px;
            padding-top: 2.4rem;
            padding-bottom: 5rem;
        }

        .block-container::before {
            content: "";
            position: fixed;
            z-index: -1;
            inset: auto -7rem -8rem auto;
            width: 28rem;
            height: 28rem;
            border: 1px solid rgba(102, 112, 82, 0.10);
            border-radius: 48% 52% 62% 38%;
            box-shadow: inset 0 0 0 5rem rgba(61, 84, 60, 0.025);
            transform: rotate(-18deg);
            pointer-events: none;
        }

        /* Brand */
        .vs-inner-brand {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0 0 3.5rem;
            padding-bottom: 0.9rem;
            border-bottom: 1px solid var(--line-strong);
            color: var(--bone);
            font-size: 0.72rem;
            font-weight: 850;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-family: var(--font-technical);
        }

        .vs-inner-index {
            color: var(--amber);
            font-size: 0.6rem;
        }

        .vs-inner-brand b {
            color: var(--bone);
            font-weight: 850;
        }

        .vs-inner-system {
            margin-left: auto;
            color: var(--muted);
            font-size: 0.54rem;
            letter-spacing: 0.18em;
        }

        /* Tool identity */
        .vs-tool-header {
            margin-bottom: 2rem;
        }

        .vs-family {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 0.65rem;
            color: var(--amber);
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            font-family: var(--font-technical);
        }

        .vs-family::before {
            content: "";
            width: 1.6rem;
            height: 1px;
            background: currentColor;
            box-shadow: none;
        }

        .vs-tool-title {
            margin: 0;
            color: var(--bone);
            font-size: clamp(2.25rem, 6vw, 4.25rem);
            font-weight: 700;
            line-height: 0.92;
            letter-spacing: 0.005em;
            text-transform: uppercase;
            font-family: var(--font-display);
        }

        .vs-tool-description {
            max-width: 39rem;
            margin: 0.85rem 0 0;
            color: var(--sand);
            font-size: 1.02rem;
            line-height: 1.65;
        }

        /* Typography */
        h1, h2, h3, h4 {
            color: var(--bone) !important;
            letter-spacing: -0.025em;
            font-family: var(--font-display) !important;
            font-weight: 650 !important;
        }

        h2, h3 {
            margin-top: 2rem !important;
        }

        p, label, [data-testid="stCaptionContainer"] {
            color: var(--sand);
            font-family: var(--font-interface);
        }

        [data-testid="stCaptionContainer"] {
            opacity: 0.76;
        }

        hr {
            border-color: var(--line) !important;
        }

        /* Sidebar / taxonomy */
        [data-testid="stSidebar"] {
            position: relative;
            overflow: hidden;
            background:
                linear-gradient(180deg, rgba(28, 40, 30, 0.98), rgba(13, 21, 16, 0.99)),
                var(--jungle-black);
            border-right: 1px solid var(--line);
            box-shadow: inset -5px 0 0 rgba(48, 37, 27, 0.72), 12px 0 40px rgba(8, 17, 13, 0.22);
        }

        [data-testid="stSidebar"]::before {
            content: "VS / AUDIO SYSTEM  ·  UNIT 09";
            display: block;
            margin: 1.5rem 1.25rem 0.8rem;
            color: var(--sand);
            font-size: 0.66rem;
            font-weight: 800;
            letter-spacing: 0.2em;
            font-family: var(--font-technical);
        }

        [data-testid="stSidebar"]::after {
            content: "";
            position: absolute;
            z-index: 0;
            right: -5.2rem;
            bottom: 1.5rem;
            width: 12.5rem;
            height: 23rem;
            opacity: .21;
            background:
                radial-gradient(ellipse at 63% 10%, #667052 0 10%, transparent 10.8%),
                radial-gradient(ellipse at 34% 25%, #3d543c 0 13%, transparent 13.8%),
                radial-gradient(ellipse at 72% 41%, #667052 0 12%, transparent 12.8%),
                radial-gradient(ellipse at 35% 58%, #3d543c 0 16%, transparent 16.8%),
                radial-gradient(ellipse at 71% 78%, #667052 0 15%, transparent 15.8%),
                linear-gradient(73deg, transparent 49%, rgba(135,150,108,.68) 49.3% 50.7%, transparent 51%);
            transform: rotate(-11deg);
            pointer-events: none;
        }

        [data-testid="stSidebar"] > div {
            position: relative;
            z-index: 1;
        }

        [data-testid="stSidebarNavSeparator"] {
            border-color: var(--line);
        }

        [data-testid="stSidebar"] [data-testid="stNavSectionHeader"] {
            color: rgba(216, 195, 154, 0.58);
            font-size: 0.63rem;
            font-weight: 800;
            letter-spacing: 0.2em;
            margin-top: 0.65rem;
            font-family: var(--font-interface);
        }

        [data-testid="stSidebar"] a {
            border: 1px solid transparent;
            border-radius: 3px;
            color: var(--sand);
            transition: background 140ms ease, border-color 140ms ease;
            font-family: var(--font-interface);
            font-size: 0.88rem;
            font-weight: 550;
            letter-spacing: -0.01em;
        }

        [data-testid="stSidebar"] a:hover {
            background: rgba(89, 68, 49, 0.18);
            border-color: rgba(216, 201, 167, 0.10);
        }

        [data-testid="stSidebar"] a[aria-current="page"] {
            background: rgba(48, 37, 27, 0.58);
            border-color: rgba(216, 201, 167, 0.26);
            color: var(--bone);
            box-shadow: inset 3px 0 0 var(--amber);
        }

        [data-testid="stSidebar"] a[aria-current="page"]::before {
            content: "";
            width: 0.48rem;
            height: 0.48rem;
            flex: 0 0 auto;
            border-radius: 50%;
            background: var(--amber);
            box-shadow: 0 0 7px rgba(217, 154, 69, 0.46);
        }

        /* Input surfaces */
        [data-testid="stFileUploader"] {
            padding: 0.7rem;
            border: 1px solid var(--line);
            border-radius: 4px;
            background:
                linear-gradient(90deg, rgba(89, 68, 49, 0.16), transparent 45%),
                rgba(28, 40, 30, 0.94);
            box-shadow: inset 0 1px 0 rgba(238, 227, 199, 0.035), 0 8px 24px rgba(7, 12, 9, 0.16);
        }

        [data-testid="stFileUploaderDropzone"] {
            min-height: 8.5rem;
            border: 1px dashed rgba(216, 195, 154, 0.34);
            border-radius: 2px;
            background: rgba(8, 17, 13, 0.48);
        }

        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: rgba(217, 154, 69, 0.66);
            background: rgba(89, 68, 49, 0.12);
        }

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-testid="stNumberInputContainer"] > div {
            border: 1px solid var(--line) !important;
            background: rgba(16, 39, 27, 0.82) !important;
            border-radius: 3px !important;
            box-shadow: inset 0 1px 0 rgba(241, 233, 213, 0.03);
        }

        [data-testid="stTextArea"] textarea {
            border: 1px solid var(--line) !important;
            border-radius: 3px !important;
            background: rgba(16, 39, 27, 0.82) !important;
            color: var(--bone) !important;
            caret-color: var(--amber);
            box-shadow: inset 0 1px 0 rgba(241, 233, 213, 0.03);
        }

        [data-testid="stTextArea"] textarea::placeholder {
            color: rgba(216, 195, 154, 0.48) !important;
        }

        [data-testid="stTextArea"] textarea:focus {
            border-color: rgba(217, 154, 69, 0.72) !important;
            box-shadow: 0 0 0 2px rgba(217, 154, 69, 0.10) !important;
            outline: none !important;
        }

        [data-baseweb="input"] > div:focus-within,
        [data-testid="stNumberInputContainer"] > div:focus-within {
            border-color: rgba(217, 154, 69, 0.72) !important;
            box-shadow: 0 0 0 2px rgba(217, 154, 69, 0.10);
        }

        [data-testid="stNumberInput"] input {
            color: var(--bone) !important;
            font-weight: 720;
            font-family: var(--font-technical) !important;
        }

        [data-testid="stNumberInput"] button {
            color: var(--amber) !important;
        }

        [data-testid="stWidgetLabel"] p {
            color: var(--bone);
            font-size: 0.75rem;
            font-weight: 720;
            letter-spacing: 0.045em;
        }

        [data-testid="stTooltipIcon"] {
            color: var(--amber) !important;
            opacity: 1 !important;
            filter: none;
        }

        [data-testid="stTooltipIcon"] svg {
            width: 1.08rem !important;
            height: 1.08rem !important;
            color: var(--amber) !important;
            fill: transparent !important;
            stroke: currentColor !important;
            stroke-width: 2.2px;
        }

        [data-testid="stRadio"] [role="radiogroup"] {
            gap: 0.55rem;
        }

        [data-testid="stRadio"] label {
            min-height: 2.65rem;
            margin: 0;
            padding: 0.58rem 0.78rem;
            border: 1px solid var(--line);
            border-radius: 3px;
            background: rgba(28, 40, 30, 0.88);
            transition: border-color 140ms ease, background 140ms ease;
        }

        [data-testid="stRadio"] label:hover {
            border-color: rgba(217, 154, 69, 0.45);
            background: rgba(89, 68, 49, 0.26);
        }

        [data-testid="stRadio"] label:has(input:checked) {
            border-color: var(--amber);
            background: rgba(89, 68, 49, 0.38);
            box-shadow: inset 3px 0 0 var(--amber);
        }

        [data-baseweb="radio"] > div {
            background-color: var(--amber) !important;
            border-color: var(--amber) !important;
            box-shadow: none !important;
        }

        [data-testid="stRadio"] input {
            accent-color: var(--amber) !important;
        }

        [data-testid="stRadio"] svg {
            color: var(--amber) !important;
            fill: var(--amber) !important;
        }

        [data-testid="stSlider"] {
            margin: 0.25rem 0 0.85rem;
            padding: 0.75rem 0.95rem 0.95rem;
            border: 1px solid var(--line);
            border-radius: 3px;
            background:
                linear-gradient(90deg, rgba(89, 68, 49, 0.18), transparent 60%),
                rgba(28, 40, 30, 0.90);
        }

        [data-testid="stSlider"] [data-baseweb="slider"] > div {
            height: 4px;
            border-radius: 0;
        }

        [data-testid="stSlider"] [role="slider"] {
            width: 16px !important;
            height: 16px !important;
            border: 3px solid var(--jungle-black) !important;
            border-radius: 2px !important;
            background: var(--bone) !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.35);
        }

        /* Actions */
        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button,
        [data-testid="stFormSubmitButton"] button {
            min-height: 3.25rem;
            border: 1px solid rgba(216, 201, 167, 0.46);
            border-radius: 3px;
            font-size: 0.82rem;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            transition: transform 150ms ease, box-shadow 150ms ease, background 150ms ease;
            font-family: var(--font-interface);
        }

        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stDownloadButton"] button,
        [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(#e4d5b3, #cdbc94);
            color: var(--jungle-black);
            box-shadow: 0 3px 0 #6f6149, 0 8px 18px rgba(0, 0, 0, 0.18);
        }

        [data-testid="stButton"] button[kind="secondary"] {
            background: rgba(16, 39, 27, 0.84);
            color: var(--bone);
            box-shadow: inset 0 1px 0 rgba(241, 233, 213, 0.04);
        }

        [data-testid="stButton"] button p,
        [data-testid="stDownloadButton"] button p,
        [data-testid="stFormSubmitButton"] button p {
            color: inherit !important;
            font-weight: inherit !important;
        }

        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            border-color: var(--bone);
            transform: translateY(-1px);
            box-shadow: 0 2px 0 #6f6149, 0 7px 16px rgba(0, 0, 0, 0.22);
        }

        [data-testid="stButton"] button:focus:not(:active),
        [data-testid="stDownloadButton"] button:focus:not(:active),
        [data-testid="stFormSubmitButton"] button:focus:not(:active) {
            border-color: var(--bone);
            box-shadow: 0 0 0 3px rgba(217, 154, 69, 0.28);
        }

        /* Results, players and states */
        [data-testid="stMetric"] {
            min-height: 8.3rem;
            padding: 1.25rem;
            border: 1px solid var(--line);
            border-radius: 3px;
            background:
                linear-gradient(180deg, rgba(119, 118, 107, 0.09), transparent 38%),
                rgba(23, 24, 21, 0.88);
            box-shadow: inset 0 0 0 3px rgba(0, 0, 0, 0.16), 0 7px 20px rgba(0, 0, 0, 0.16);
        }

        [data-testid="stMetricLabel"] {
            color: var(--sand);
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            font-family: var(--font-interface);
        }

        [data-testid="stMetricValue"] {
            color: var(--amber);
            font-weight: 780;
            text-shadow: 0 0 8px rgba(217, 154, 69, 0.14);
            font-family: var(--font-technical);
            letter-spacing: -0.035em;
        }

        [data-testid="stSlider"] [data-testid="stThumbValue"],
        [data-testid="stSlider"] [data-testid="stTickBarMin"],
        [data-testid="stSlider"] [data-testid="stTickBarMax"],
        [data-testid="stTable"] td,
        [data-testid="stDataFrame"] {
            font-family: var(--font-technical) !important;
        }

        [data-testid="stAudio"] {
            padding: 0.55rem;
            border: 1px solid var(--line);
            border-radius: 3px;
            background: rgba(16, 39, 27, 0.78);
        }

        [data-testid="stAlert"] {
            border: 1px solid rgba(216, 195, 154, 0.18);
            border-radius: 3px;
            background: rgba(16, 39, 27, 0.76);
            color: var(--bone);
        }

        [data-baseweb="notification"] {
            border-color: rgba(216, 195, 154, 0.18) !important;
            background: rgba(16, 39, 27, 0.88) !important;
            color: var(--bone) !important;
        }

        [data-testid="stAlert"] svg {
            color: var(--amber);
        }

        [data-testid="stSpinner"] > div {
            border-top-color: var(--amber) !important;
        }

        code, pre {
            border-color: var(--line) !important;
            background: var(--jungle-black) !important;
        }

        .vs-panel-label {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: 2.2rem 0 0.55rem;
            padding: 0.5rem 0.68rem;
            border: 1px solid rgba(216, 201, 167, 0.18);
            border-bottom-color: rgba(216, 201, 167, 0.34);
            border-radius: 2px;
            background: rgba(48, 37, 27, 0.62);
            color: var(--sand);
            font: 600 0.61rem/1.2 var(--font-technical);
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .vs-panel-label::before {
            content: "";
            position: absolute;
            top: 50%;
            left: -1.05rem;
            width: .72rem;
            height: 1.25rem;
            border: 1px solid rgba(102,112,82,.30);
            border-radius: 70% 30% 68% 32%;
            background: rgba(61,84,60,.13);
            transform: translateY(-50%) rotate(-28deg);
        }

        .vs-panel-status {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: var(--muted);
        }

        .vs-panel-status i {
            width: 0.46rem;
            height: 0.46rem;
            border-radius: 50%;
            background: var(--lamp-green);
            box-shadow: 0 0 7px rgba(135, 150, 108, 0.42);
        }

        @media (max-width: 700px) {
            .block-container {
                padding-top: 1.5rem;
                padding-left: 1.15rem;
                padding-right: 1.15rem;
            }

            .vs-inner-brand {
                margin-bottom: 2.6rem;
            }

            .vs-inner-system {
                display: none;
            }

            [data-testid="stMetric"] {
                min-height: auto;
            }

            .vs-panel-label::before {
                display: none;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                scroll-behavior: auto !important;
                transition: none !important;
            }
        }
        </style>
        f"""
    # Apply controls and typography first, then inject the versioned jungle art.
    st.markdown(design, unsafe_allow_html=True)
    jungle_background = _asset_data_uri("jungle-tech-background.png")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: var(--jungle-black) !important;
            background-image:
                linear-gradient(rgba(16,26,20,.24), rgba(16,26,20,.46)),
                radial-gradient(circle at 50% 32%, transparent 0 18rem, rgba(16,26,20,.12) 44rem),
                url("{jungle_background}") !important;
            background-position: center top !important;
            background-repeat: no-repeat !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}

        [data-testid="stSidebar"] {{
            background-image:
                linear-gradient(rgba(16,26,20,.88), rgba(13,21,16,.96)),
                url("{jungle_background}") !important;
            background-position: left top !important;
            background-repeat: no-repeat !important;
            background-size: auto 100% !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_header() -> None:
    """Render the compact editorial identity used inside tools."""
    st.markdown(
        """
        <header class="vs-inner-brand">
            <span class="vs-inner-index">●</span>
            <span>VIBES <b>SUPPLIER</b></span>
            <span class="vs-inner-system">VS / AUDIO SYSTEM · UNIT 09</span>
        </header>
        """,
        unsafe_allow_html=True,
    )


def show_homepage() -> None:
    """Render the Jungle Analog home hero and tool-family navigation."""
    hero_background = _asset_data_uri("jungle-tech-home-hero.png")
    st.markdown(
        f"""
        <style>
        .block-container {{ max-width: 1120px; }}

        .vs-home-hero {{
            position: relative;
            min-height: 570px;
            overflow: hidden;
            margin-bottom: 4.5rem;
            border: 1px solid var(--line);
            border-radius: 4px;
            background-image:
                linear-gradient(90deg, rgba(16,26,20,.54), rgba(16,26,20,.10) 62%),
                linear-gradient(0deg, rgba(48,37,27,.26), transparent 58%),
                url("{hero_background}");
            background-position: center;
            background-size: cover;
            box-shadow: 0 0 0 5px rgba(48, 37, 27, 0.72), 0 28px 80px rgba(8, 17, 13, 0.42);
        }}

        .vs-home-copy {{
            position: absolute;
            z-index: 1;
            top: 50%;
            left: clamp(1.6rem, 5vw, 4.5rem);
            width: min(43%, 27rem);
            transform: translateY(-50%);
        }}

        .vs-home-index {{
            margin-bottom: 1.15rem;
            color: var(--amber);
            font-size: 0.7rem;
            font-weight: 850;
            letter-spacing: 0.18em;
        }}

        .vs-home-vibes {{
            margin: 0;
            color: var(--bone);
            font-family: var(--font-display);
            font-size: clamp(5.2rem, 11vw, 8.8rem);
            font-weight: 900;
            letter-spacing: 0.025em;
            line-height: 0.78;
            text-transform: uppercase;
            text-shadow: 0 8px 28px rgba(8, 17, 13, 0.50);
        }}

        .vs-home-supplier {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-top: 1.45rem;
            color: var(--bone);
            font-size: clamp(0.78rem, 1.8vw, 1.1rem);
            font-weight: 850;
            letter-spacing: 0.36em;
            text-transform: uppercase;
        }}

        .vs-home-supplier::before,
        .vs-home-supplier::after {{
            content: "";
            height: 1px;
            flex: 1;
            background: rgba(216, 201, 167, 0.52);
        }}

        .vs-home-tagline {{
            margin-top: 1.25rem;
            color: var(--sand);
            font-size: 0.72rem;
            font-weight: 720;
            letter-spacing: 0.14em;
            line-height: 1.7;
            text-transform: uppercase;
        }}

        .vs-home-section {{ margin-bottom: 1.5rem; }}
        .vs-home-section h2 {{
            max-width: 38rem;
            margin: 0.55rem 0 0 !important;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.04;
        }}

        .vs-tool-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
        }}

        .vs-home-card {{
            display: flex;
            min-height: 245px;
            flex-direction: column;
            padding: 1.35rem;
            border: 1px solid var(--line);
            border-radius: 3px;
            background:
                linear-gradient(180deg, rgba(119, 118, 107, 0.08), transparent 38%),
                rgba(28, 40, 30, 0.94);
            color: var(--bone) !important;
            text-decoration: none !important;
            box-shadow: inset 0 0 0 3px rgba(0, 0, 0, 0.12), 0 8px 22px rgba(0, 0, 0, 0.14);
            transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
        }}

        .vs-home-card:hover {{
            border-color: rgba(217, 154, 69, 0.56);
            background:
                linear-gradient(180deg, rgba(89, 68, 49, 0.20), transparent 58%),
                rgba(28, 40, 30, 0.98);
            transform: translateY(-3px);
        }}

        .vs-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--amber);
            font-size: 0.62rem;
            font-weight: 850;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}

        .vs-card-status {{
            padding: 0.25rem 0.45rem;
            border: 0;
            border-radius: 0;
            padding-left: 1rem;
            position: relative;
        }}

        .vs-card-status::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 50%;
            width: .46rem;
            height: .46rem;
            border-radius: 50%;
            background: var(--amber);
            box-shadow: 0 0 7px rgba(217, 154, 69, .45);
            transform: translateY(-50%);
        }}

        .vs-card-status.soon {{
            color: var(--muted);
        }}

        .vs-card-status.soon::before {{
            background: var(--metal);
            box-shadow: none;
        }}

        .vs-home-card h3 {{
            margin: auto 0 0.7rem !important;
            font-size: 1.55rem;
        }}

        .vs-home-card p {{
            min-height: 3.2rem;
            margin: 0;
            color: var(--sand);
            font-size: 0.85rem;
            line-height: 1.55;
        }}

        .vs-card-enter {{
            margin-top: 1.2rem;
            color: var(--amber);
            font-size: 0.66rem;
            font-weight: 850;
            letter-spacing: 0.15em;
            text-transform: uppercase;
        }}

        @media (max-width: 760px) {{
            .vs-home-hero {{ min-height: 620px; background-position: 64% center; }}
            .vs-home-hero::after {{
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(0deg, rgba(8, 17, 13, 0.94) 0 38%, transparent 74%);
            }}
            .vs-home-copy {{
                top: auto;
                right: 1.4rem;
                bottom: 2.1rem;
                left: 1.4rem;
                width: auto;
                transform: none;
            }}
            .vs-home-vibes {{ font-size: clamp(4.4rem, 23vw, 6.6rem); }}
            .vs-tool-grid {{ grid-template-columns: 1fr; }}
            .vs-home-card {{ min-height: 205px; }}
        }}
        </style>

        <section class="vs-home-hero">
            <div class="vs-home-copy">
                <div class="vs-home-index">09 / AUDIO SYSTEM</div>
                <div class="vs-home-vibes">VIBES</div>
                <div class="vs-home-supplier">SUPPLIER</div>
                <div class="vs-home-tagline">
                    Independent audio tools<br>
                    for producers, DJs &amp; artists
                </div>
            </div>
        </section>

        <section class="vs-home-section">
            <div class="vs-family">Enter the system</div>
            <h2>Three ways into the sound.</h2>
        </section>

        <nav class="vs-tool-grid" aria-label="Audio tool families">
            <a class="vs-home-card" href="/key-bpm-finder" target="_self">
                <div class="vs-card-top"><span>Analyze / 01</span><span class="vs-card-status">Live</span></div>
                <h3>Read the signal.</h3>
                <p>Find key, BPM and Camelot position before you mix, DJ or create.</p>
                <span class="vs-card-enter">Open Key &amp; BPM →</span>
            </a>
            <a class="vs-home-card" href="/speed-changer" target="_self">
                <div class="vs-card-top"><span>Transform / 02</span><span class="vs-card-status">Live</span></div>
                <h3>Reshape the motion.</h3>
                <p>Set exact tempo and control the relationship between speed and pitch.</p>
                <span class="vs-card-enter">Open Speed Changer →</span>
            </a>
            <a class="vs-home-card" href="/vocal-split" target="_self">
                <div class="vs-card-top"><span>Separate / 03</span><span class="vs-card-status soon">Soon</span></div>
                <h3>Pull voice from rhythm.</h3>
                <p>High-quality acapella and instrumental separation is being prepared.</p>
                <span class="vs-card-enter">Preview the tool →</span>
            </a>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def show_tool_header(family: str, title: str, description: str) -> None:
    """Render a consistent family label and tool introduction."""
    st.markdown(
        f"""
        <section class="vs-tool-header">
            <div class="vs-family">{family}</div>
            <h1 class="vs-tool-title">{title}</h1>
            <p class="vs-tool-description">{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def show_panel_label(index: str, label: str, status: str = "READY") -> None:
    """Render a small equipment-style label without wrapping widget behavior."""
    st.markdown(
        f"""
        <div class="vs-panel-label">
            <span>{index} / {label}</span>
            <span class="vs-panel-status"><i></i>{status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
