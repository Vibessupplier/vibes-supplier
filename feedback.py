"""Validation and delivery for anonymous product feedback."""

from dataclasses import dataclass

import streamlit as st

from analytics import send_event_now


FEEDBACK_CATEGORIES = (
    "General feedback",
    "Bug report",
    "Feature request",
    "Audio quality",
    "Design & usability",
)
MIN_MESSAGE_LENGTH = 10
MAX_MESSAGE_LENGTH = 2000
DEFAULT_CONTACT_EMAIL = "vibes.supplier@gmail.com"


class FeedbackError(ValueError):
    """Raised when submitted feedback is invalid."""


@dataclass(frozen=True)
class FeedbackSubmission:
    category: str
    rating: int
    message: str


def validate_feedback(category: str, rating: int, message: str) -> FeedbackSubmission:
    clean_message = message.strip()
    if category not in FEEDBACK_CATEGORIES:
        raise FeedbackError("Choose a valid feedback category.")
    if rating not in range(1, 6):
        raise FeedbackError("Rating must be between 1 and 5.")
    if len(clean_message) < MIN_MESSAGE_LENGTH:
        raise FeedbackError(
            f"Feedback must contain at least {MIN_MESSAGE_LENGTH} characters."
        )
    if len(clean_message) > MAX_MESSAGE_LENGTH:
        raise FeedbackError(
            f"Feedback cannot exceed {MAX_MESSAGE_LENGTH} characters."
        )
    return FeedbackSubmission(category, rating, clean_message)


def submit_feedback(category: str, rating: int, message: str) -> bool:
    """Validate and deliver anonymous feedback through configured analytics."""
    submission = validate_feedback(category, rating, message)
    return send_event_now(
        "feedback_submitted",
        {
            "category": submission.category,
            "rating": submission.rating,
            "message": submission.message,
        },
    )


def contact_email() -> str | None:
    """Return the intentionally public support address when configured."""
    try:
        email = str(st.secrets.get("feedback", {}).get("contact_email", "")).strip()
    except (FileNotFoundError, TypeError):
        return None
    if not email:
        return DEFAULT_CONTACT_EMAIL
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return DEFAULT_CONTACT_EMAIL
    return email
