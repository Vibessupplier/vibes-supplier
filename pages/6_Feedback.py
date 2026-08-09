from html import escape
import time

import streamlit as st

from analytics import track_page_view
from feedback import (
    FEEDBACK_CATEGORIES,
    MAX_MESSAGE_LENGTH,
    FeedbackError,
    contact_email,
    submit_feedback,
)
from ui import show_header, show_tool_header


SUBMISSION_COOLDOWN_SECONDS = 30


track_page_view("feedback")
show_header()
show_tool_header(
    "Support / 06",
    "Feedback",
    "Help shape better audio tools for producers, DJs and artists.",
)

st.markdown(
    """
    ### Tell us what happened

    Found a bug, have an idea, or heard something that could sound better?
    Specific feedback helps us improve the tools faster.
    """
)

with st.form("product_feedback", clear_on_submit=True):
    category = st.selectbox("Feedback type", FEEDBACK_CATEGORIES)
    rating = st.slider(
        "Overall experience",
        min_value=1,
        max_value=5,
        value=4,
        help="1 is frustrating; 5 is excellent.",
    )
    message = st.text_area(
        "Your feedback",
        placeholder=(
            "Which tool were you using? What did you expect, and what happened?"
        ),
        max_chars=MAX_MESSAGE_LENGTH,
        height=170,
    )
    submitted = st.form_submit_button("SEND FEEDBACK", type="primary")

if submitted:
    now = time.monotonic()
    last_submission = st.session_state.get("last_feedback_submission", 0.0)
    if now - last_submission < SUBMISSION_COOLDOWN_SECONDS:
        st.warning("Please wait a moment before sending another message.")
    else:
        try:
            delivered = submit_feedback(category, rating, message)
        except FeedbackError as error:
            st.warning(str(error))
        else:
            if delivered:
                st.session_state["last_feedback_submission"] = now
                st.success("Thank you — your feedback has been received.")
            else:
                st.error(
                    "Feedback could not be delivered right now. Please use "
                    "the contact email below instead."
                )

st.caption(
    "No account is required. Your message, category and rating are sent to "
    "our product analytics workspace. Audio, filenames and contact details "
    "are not included."
)

email = contact_email()
st.markdown("### Prefer email?")
if email is None:
    st.info("A public support email will be added before the public beta.")
else:
    safe_email = escape(email)
    st.markdown(
        f'<a class="feedback-email" href="mailto:{safe_email}">{safe_email}</a>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Please do not attach copyrighted audio unless you have permission to share it."
    )

st.markdown(
    """
    <style>
    .feedback-email {
        display:inline-flex;
        padding:.85rem 1rem;
        border:1px solid rgba(184,255,61,.38);
        border-radius:10px 4px 10px 4px;
        background:rgba(16,39,27,.78);
        color:var(--lime) !important;
        font-family:var(--font-technical);
        text-decoration:none !important;
    }
    .feedback-email:hover { border-color:var(--lime); }
    </style>
    """,
    unsafe_allow_html=True,
)
