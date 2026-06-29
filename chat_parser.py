"""
chat_parser.py
Parses a raw WhatsApp chat export (.txt) into a structured pandas DataFrame.

Handles both common export variants:
  - Android: "12/05/23, 10:15 - Name: message"          (24-hour clock, often 2-digit year)
  - iPhone:  "12/05/2023, 10:15 AM - Name: message"      (12-hour clock, often 4-digit year)
"""

import re
import pandas as pd

# One pattern per known WhatsApp export variant. We try each in turn so the
# parser works regardless of which phone/OS produced the export.
DATETIME_PATTERNS = [
    r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',                 # 24-hour clock
    r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s',      # 12-hour clock w/ AM/PM
]

DATETIME_FORMATS = [
    '%d/%m/%y, %H:%M - ',
    '%d/%m/%Y, %H:%M - ',
    '%d/%m/%y, %I:%M %p - ',
    '%d/%m/%Y, %I:%M %p - ',
]

USERNAME_SPLIT_REGEX = re.compile(r'([^:]+?):\s')


def _split_into_messages(raw_text: str):
    """
    Try each known datetime pattern until one actually matches the export.
    Returns (message_chunks, matched_timestamps).
    """
    for pattern in DATETIME_PATTERNS:
        timestamps = re.findall(pattern, raw_text)
        if timestamps:
            message_chunks = re.split(pattern, raw_text)[1:]
            return message_chunks, timestamps
    raise ValueError(
        "Could not detect a known WhatsApp date/time format in this file. "
        "The export format may differ from the supported Android/iPhone patterns."
    )


def _parse_timestamps(raw_timestamps: pd.Series) -> pd.Series:
    """
    Try each known strftime format until one parses the whole column without error.
    """
    last_error = None
    for fmt in DATETIME_FORMATS:
        try:
            return pd.to_datetime(raw_timestamps, format=fmt)
        except ValueError as exc:
            last_error = exc
            continue
    raise ValueError(f"Unable to parse timestamps with any known format: {last_error}")


def _split_user_and_message(message_block: str):
    """
    Splits a single chat block into (username, message_text).
    Falls back to 'group_notification' for system messages
    (e.g. 'X added Y', 'Messages are end-to-end encrypted...').
    """
    match = USERNAME_SPLIT_REGEX.match(message_block)
    if match:
        username = match.group(1)
        message_text = message_block[match.end():]
        return username.strip(), message_text
    return 'group_notification', message_block


def _assign_time_period(hour: int) -> str:
    """Builds a human-readable hour bucket, e.g. '14-15', '23-00', '00-01'."""
    if hour == 23:
        return "23-00"
    if hour == 0:
        return "00-01"
    return f"{hour}-{hour + 1}"


def preprocess(raw_text: str) -> pd.DataFrame:
    """
    Main entry point: turns the raw exported .txt content into a clean DataFrame
    with one row per message, plus derived date/time columns used throughout
    the rest of the app (timelines, heatmaps, activity maps, etc).
    """
    message_chunks, raw_timestamps = _split_into_messages(raw_text)

    df = pd.DataFrame({'user_message': message_chunks, 'message_date': raw_timestamps})
    df['date'] = _parse_timestamps(df['message_date'])
    df.drop(columns=['message_date'], inplace=True)

    users, messages = [], []
    for block in df['user_message']:
        user, msg = _split_user_and_message(block)
        users.append(user)
        messages.append(msg)

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Derived date/time columns used by helper.py
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['period'] = df['hour'].apply(_assign_time_period)

    return df
