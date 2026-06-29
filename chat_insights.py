"""
chat_insights.py
Computes all statistics, timelines, and visual-data structures shown in the
WhatsApp Chat Analyzer dashboard. Each function takes (selected_user, df) and
returns either a scalar, a pandas object, or a small DataFrame ready to plot.
"""

import os
from collections import Counter
from textblob import TextBlob
import numpy as np
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
import emoji

_URL_EXTRACTOR = URLExtract()

# Both known WhatsApp media placeholder *prefixes* (Android vs iPhone differ,
# and iPhone appends a variable filename, e.g. "<attached: 00001.jpg>").
MEDIA_PLACEHOLDER_PREFIXES = ('<media omitted>', '<attached:')

# Resolve the stopwords file relative to this module, not the current working
# directory — Streamlit can be launched from anywhere, and a relative path
# like 'stop_hinglish.txt' silently breaks the moment that's no longer true.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_STOPWORDS_PATH = os.path.join(_THIS_DIR, 'stop_hinglish.txt')


def _load_stopwords() -> set:
    """Loads stopwords as a whole-word set (not a raw string) so membership
    checks can't match on substrings, e.g. 'is' incorrectly matching inside 'this'."""
    try:
        with open(_STOPWORDS_PATH, 'r', encoding='utf-8') as f:
            return set(f.read().split())
    except FileNotFoundError:
        return set()


def _filter_by_user(df: pd.DataFrame, selected_user: str) -> pd.DataFrame:
    """Shared filter used by almost every function below."""
    if selected_user != "Overall":
        return df[df['user'] == selected_user]
    return df


def _is_media_message(message: str) -> bool:
    cleaned = message.strip().lower()
    return cleaned.startswith(MEDIA_PLACEHOLDER_PREFIXES)


def get_summary_stats(selected_user: str, df: pd.DataFrame):
    """Returns (total_messages, total_words, total_media, total_links)."""
    df = _filter_by_user(df, selected_user)

    total_messages = df.shape[0]
    total_words = sum(len(message.split()) for message in df['message'])
    total_media = df['message'].apply(_is_media_message).sum()
    total_links = sum(len(_URL_EXTRACTOR.find_urls(message)) for message in df['message'])

    return total_messages, total_words, int(total_media), total_links


def get_most_active_users(df: pd.DataFrame):
    """
    Group-level only. Returns:
      - top_counts: Series of the top 5 users by message count
      - share_df:   DataFrame of every user's % share of total messages

    System rows ('group_notification') are excluded so they don't appear
    as a fake "participant" in the chart.
    """
    real_users_df = df[df['user'] != 'group_notification']

    top_counts = real_users_df['user'].value_counts().head()
    share_df = (
        round((real_users_df['user'].value_counts() / real_users_df.shape[0]) * 100, 2)
        .reset_index()
        .rename(columns={'user': 'name', 'count': 'percent'})
    )
    return top_counts, share_df


def build_wordcloud(selected_user: str, df: pd.DataFrame):
    """Generates a WordCloud image (PIL-compatible array) of the most-used words."""
    stop_words = _load_stopwords()
    df = _filter_by_user(df, selected_user)

    real_messages = df[
        (df['user'] != 'group_notification') & (~df['message'].apply(_is_media_message))
    ]

    def clean_message(message: str) -> str:
        words = [w for w in message.lower().split() if w not in stop_words]
        return " ".join(words)

    cleaned_text = real_messages['message'].apply(clean_message).str.cat(sep=' ')

    wc = WordCloud(width=500, height=500, background_color='white', min_font_size=10)
    return wc.generate(cleaned_text if cleaned_text.strip() else "no_messages")


def get_most_common_words(selected_user: str, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    stop_words = _load_stopwords()
    df = _filter_by_user(df, selected_user)

    real_messages = df[
        (df['user'] != 'group_notification') & (~df['message'].apply(_is_media_message))
    ]

    words = []
    for message in real_messages['message']:
        words.extend(w for w in message.lower().split() if w not in stop_words)

    return pd.DataFrame(Counter(words).most_common(top_n), columns=['word', 'count'])


def get_emoji_breakdown(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    df = _filter_by_user(df, selected_user)

    emojis = []
    for message in df['message']:
        emojis.extend(c for c in message if c in emoji.EMOJI_DATA)

    if not emojis:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    return pd.DataFrame(Counter(emojis).most_common(), columns=['Emoji', 'Count'])


def get_monthly_timeline(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    df = _filter_by_user(df, selected_user)

    timeline = df.groupby(['year', 'month_num', 'month'])['message'].count().reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def get_daily_timeline(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    df = _filter_by_user(df, selected_user)
    return df.groupby('only_date')['message'].count().reset_index()


def get_weekly_activity(selected_user: str, df: pd.DataFrame) -> pd.Series:
    df = _filter_by_user(df, selected_user)
    return df['day_name'].value_counts()


def get_monthly_activity(selected_user: str, df: pd.DataFrame) -> pd.Series:
    df = _filter_by_user(df, selected_user)
    return df['month'].value_counts()


def get_activity_heatmap(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    df = _filter_by_user(df, selected_user)
    return df.pivot_table(
        index='day_name', columns='period', values='message', aggfunc='count'
    ).fillna(0)

#Additions
def get_chat_summary(selected_user: str, df: pd.DataFrame):

    filtered_df = _filter_by_user(df, selected_user)

    total_messages = filtered_df.shape[0]

    if total_messages == 0:
        return {}

    most_active_hour = (
        filtered_df['hour']
        .value_counts()
        .idxmax()
    )

    emoji_df = get_emoji_breakdown(selected_user, df)

    most_used_emoji = "None"

    if not emoji_df.empty:
        most_used_emoji = emoji_df.iloc[0]['Emoji']

    return {
        "messages": total_messages,
        "peak_hour": most_active_hour,
        "top_emoji": most_used_emoji
    }

def get_sentiment_analysis(selected_user: str, df: pd.DataFrame):

    filtered_df = _filter_by_user(df, selected_user)

    positive = 0
    negative = 0
    neutral = 0

    for message in filtered_df['message']:

        polarity = TextBlob(str(message)).sentiment.polarity

        if polarity > 0:
            positive += 1

        elif polarity < 0:
            negative += 1

        else:
            neutral += 1

    total = positive + negative + neutral

    if total == 0:
        return {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }

    return {
        "positive": round((positive / total) * 100, 2),
        "negative": round((negative / total) * 100, 2),
        "neutral": round((neutral / total) * 100, 2)
    }

def get_response_time_analysis(df: pd.DataFrame):

    temp = df.copy()

    temp = temp[temp['user'] != 'group_notification']

    temp = temp.sort_values('date')

    response_times = []

    for i in range(1, len(temp)):

        current_user = temp.iloc[i]['user']
        previous_user = temp.iloc[i - 1]['user']

        if current_user != previous_user:

            diff = (
                temp.iloc[i]['date']
                - temp.iloc[i - 1]['date']
            ).total_seconds() / 60

            if 0 < diff < 1440:
                response_times.append(diff)

    if len(response_times) == 0:
        return {
            "avg_response": 0,
            "fastest": 0,
            "slowest": 0
        }

    return {
        "avg_response": round(np.mean(response_times), 2),
        "fastest": round(np.min(response_times), 2),
        "slowest": round(np.max(response_times), 2)
    }

def get_personality_analysis(selected_user: str, df: pd.DataFrame):

    filtered_df = _filter_by_user(df, selected_user)

    if filtered_df.empty:
        return []

    total_messages = filtered_df.shape[0]

    total_words = sum(
        len(str(message).split())
        for message in filtered_df['message']
    )

    avg_words_per_message = total_words / total_messages

    emoji_count = 0

    for message in filtered_df['message']:
        emoji_count += sum(
            1 for char in str(message)
            if char in emoji.EMOJI_DATA
        )

    links_shared = sum(
        len(_URL_EXTRACTOR.find_urls(str(message)))
        for message in filtered_df['message']
    )

    sentiment = get_sentiment_analysis(
        selected_user,
        df
    )

    traits = []

    # Activity
    if total_messages > 500:
        traits.append("🔥 Highly Active Participant")
    elif total_messages > 100:
        traits.append("💬 Regular Contributor")
    else:
        traits.append("🌱 Occasional Participant")

    # Message Length
    if avg_words_per_message > 12:
        traits.append("📝 Detailed Communicator")
    elif avg_words_per_message > 6:
        traits.append("📖 Balanced Communicator")
    else:
        traits.append("⚡ Short & Direct Communicator")

    # Sentiment
    if sentiment["positive"] > 50:
        traits.append("😊 Positive Tone")
    elif sentiment["negative"] > 30:
        traits.append("😅 Critical / Opinionated Tone")
    else:
        traits.append("😐 Neutral Tone")

    # Emojis
    if emoji_count > 50:
        traits.append("😂 Expressive Emoji User")

    # Links
    if links_shared > 20:
        traits.append("🔗 Resource Sharer")

    return traits

def get_conversation_starters(df: pd.DataFrame, threshold_hours: int = 8):

    temp = df.copy()

    temp = temp[temp['user'] != 'group_notification']

    temp = temp.sort_values('date')

    starters = []

    if len(temp) == 0:
        return pd.DataFrame(columns=['User', 'Conversations Started'])

    # First message always starts a conversation
    starters.append(temp.iloc[0]['user'])

    for i in range(1, len(temp)):

        current_time = temp.iloc[i]['date']
        previous_time = temp.iloc[i - 1]['date']

        gap_hours = (
            current_time - previous_time
        ).total_seconds() / 3600

        if gap_hours >= threshold_hours:
            starters.append(temp.iloc[i]['user'])

    starter_counts = (
        pd.Series(starters)
        .value_counts()
        .reset_index()
    )

    starter_counts.columns = [
        'User',
        'Conversations Started'
    ]

    return starter_counts

def get_response_time_leaderboard(df: pd.DataFrame):

    temp = df.copy()

    temp = temp[temp['user'] != 'group_notification']

    temp = temp.sort_values('date')

    response_dict = {}

    for i in range(1, len(temp)):

        current_user = temp.iloc[i]['user']
        previous_user = temp.iloc[i - 1]['user']

        if current_user != previous_user:

            response_time = (
                temp.iloc[i]['date']
                - temp.iloc[i - 1]['date']
            ).total_seconds() / 60

            # Ignore unrealistic gaps
            if 0 < response_time < 1440:

                if current_user not in response_dict:
                    response_dict[current_user] = []

                response_dict[current_user].append(response_time)

    leaderboard = []

    for user, times in response_dict.items():

        avg_time = round(sum(times) / len(times), 2)

        leaderboard.append(
            [user, avg_time, len(times)]
        )

    leaderboard_df = pd.DataFrame(
        leaderboard,
        columns=[
            "User",
            "Average Response Time (mins)",
            "Responses Count"
        ]
    )

    leaderboard_df = leaderboard_df.sort_values(
        "Average Response Time (mins)"
    )

    return leaderboard_df
