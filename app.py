import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
import plotly.express as px
import seaborn as sns
import streamlit as st
import pdf_export
import chat_insights as ci
import chat_parser

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChatPulse",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

/* ── Root palette ── */
:root {
    --bg:       #0d1117;
    --surface:  #161b22;
    --border:   #21262d;
    --accent:   #25d366;       /* WhatsApp green */
    --accent2:  #128c7e;
    --text:     #e6edf3;
    --muted:    #7d8590;
    --positive: #25d366;
    --neutral:  #58a6ff;
    --negative: #f85149;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Remove default Streamlit whitespace at top */
.block-container { padding-top: 2rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stFileUploader label,
[data-testid="stSidebar"] .stSelectbox label {
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 600;
}

/* ── Sidebar brand ── */
.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: -0.03em;
}
.brand-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: -4px;
    margin-bottom: 24px;
}

/* ── Section headings ── */
.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    border-left: 3px solid var(--accent);
    padding-left: 10px;
    margin: 2rem 0 1rem;
}

/* ── Stat cards ── */
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    transition: border-color .2s;
}
.stat-card:hover { border-color: var(--accent); }
.stat-card .label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 6px;
}
.stat-card .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}

/* ── Sentiment pills ── */
.sentiment-row { display: flex; gap: 12px; }
.pill {
    flex: 1;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.pill-pos { background: rgba(37,211,102,.12); border: 1px solid rgba(37,211,102,.3); }
.pill-neu { background: rgba(88,166,255,.12); border: 1px solid rgba(88,166,255,.3); }
.pill-neg { background: rgba(248,81,73,.12);  border: 1px solid rgba(248,81,73,.3);  }
.pill-pos .pct { color: var(--positive); }
.pill-neu .pct { color: var(--neutral);  }
.pill-neg .pct { color: var(--negative); }
.pill .pct {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
}
.pill .plabel {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--muted);
    font-weight: 600;
    margin-top: 4px;
}

/* ── Trait badges ── */
.trait-badge {
    display: inline-block;
    background: rgba(37,211,102,.10);
    border: 1px solid rgba(37,211,102,.25);
    color: var(--accent);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 4px 4px 4px 0;
}

/* ── Metric row ── */
.metric-row {
    display: flex;
    gap: 12px;
    margin: 0.5rem 0 1rem;
}
.mini-metric {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.mini-metric .m-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text);
}
.mini-metric .m-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--muted);
    font-weight: 600;
    margin-top: 3px;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Chart area ── */
.chart-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.4rem !important;
}
.stDownloadButton > button:hover {
    background: var(--accent2) !important;
    color: #fff !important;
}

/* ── Primary button ── */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    width: 100%;
    padding: 0.6rem 0 !important;
    font-size: 0.9rem !important;
    letter-spacing: .03em;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    color: #fff !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Plotly chart background ── */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }

/* ── Success boxes → replace with badges ── */
div[data-testid="stAlert"] {
    background: rgba(37,211,102,.08) !important;
    border: 1px solid rgba(37,211,102,.25) !important;
    border-radius: 10px !important;
    color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Matplotlib dark theme ─────────────────────────────────────────────────────
PLOT_BG   = "#161b22"
PLOT_FG   = "#e6edf3"
ACCENT    = "#25d366"
ACCENT2   = "#128c7e"

def _style_ax(ax, fig):
    fig.patch.set_facecolor(PLOT_BG)
    ax.set_facecolor(PLOT_BG)
    ax.tick_params(colors=PLOT_FG, labelsize=8)
    ax.xaxis.label.set_color(PLOT_FG)
    ax.yaxis.label.set_color(PLOT_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor("#21262d")

def _line_fig(x, y, color=ACCENT):
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(x, y, color=color, linewidth=2, marker='o', markersize=3)
    ax.fill_between(x, y, alpha=0.15, color=color)
    plt.xticks(rotation=45, ha='right')
    _style_ax(ax, fig)
    fig.tight_layout()
    return fig

def _bar_fig(x, y, color=ACCENT, horizontal=False):
    fig, ax = plt.subplots(figsize=(8, 3))
    if horizontal:
        ax.barh(x, y, color=color)
    else:
        ax.bar(x, y, color=color, width=0.6)
        plt.xticks(rotation=45, ha='right')
    _style_ax(ax, fig)
    fig.tight_layout()
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-title">💬 ChatPulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Decode your WhatsApp conversations</div>', unsafe_allow_html=True)

    st.markdown("**Upload chat export**")
    uploaded_file = st.file_uploader("", type=["txt"], label_visibility="collapsed")

    if uploaded_file:
        raw_bytes = uploaded_file.getvalue()
        raw_text  = raw_bytes.decode("utf-8")

        try:
            df = chat_parser.preprocess(raw_text)
        except ValueError as exc:
            st.error(f"Couldn't read this export: {exc}")
            st.stop()

        user_list = sorted(u for u in df['user'].unique() if u != 'group_notification')
        user_list.insert(0, "Overall")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**View analysis for**")
        selected_user = st.selectbox("", user_list, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("▶  Run Analysis")

        st.markdown("---")
        st.caption("Export WhatsApp chat → More options → Export chat → Without media")

# ── Guard: nothing uploaded yet ───────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div style="text-align:center; padding: 5rem 2rem;">
        <div style="font-size:4rem;">💬</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; color:#e6edf3; margin-top:1rem;">
            ChatPulse
        </div>
        <div style="color:#7d8590; font-size:1rem; margin-top:.5rem; max-width:400px; margin-left:auto; margin-right:auto;">
            Upload your WhatsApp chat export in the sidebar to get deep insights into your conversations.
        </div>
        <div style="margin-top:2.5rem; display:flex; gap:1.5rem; justify-content:center; flex-wrap:wrap;">
            <div style="background:#161b22; border:1px solid #21262d; border-radius:12px; padding:1rem 1.5rem; font-size:.85rem; color:#7d8590;">📊 Timelines & Heatmaps</div>
            <div style="background:#161b22; border:1px solid #21262d; border-radius:12px; padding:1rem 1.5rem; font-size:.85rem; color:#7d8590;">😊 Sentiment Analysis</div>
            <div style="background:#161b22; border:1px solid #21262d; border-radius:12px; padding:1rem 1.5rem; font-size:.85rem; color:#7d8590;">🧠 Personality Traits</div>
            <div style="background:#161b22; border:1px solid #21262d; border-radius:12px; padding:1rem 1.5rem; font-size:.85rem; color:#7d8590;">⚡ Response Times</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not run:
    st.info("👈  Choose a user and click **Run Analysis** to get started.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS OUTPUT
# ══════════════════════════════════════════════════════════════════════════════

# ── Top stats ─────────────────────────────────────────────────────────────────
num_messages, num_words, num_media, num_links = ci.get_summary_stats(selected_user, df)

st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
for col, label, val in zip(
    [c1, c2, c3, c4],
    ["Messages", "Words", "Media shared", "Links shared"],
    [num_messages, num_words, num_media, num_links],
):
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="label">{label}</div>
            <div class="value">{val:,}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Chat summary row ──────────────────────────────────────────────────────────
summary = ci.get_chat_summary(selected_user, df)
if summary:
    st.markdown('<div class="section-header">Chat Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-row">
        <div class="mini-metric">
            <div class="m-val">{summary["messages"]:,}</div>
            <div class="m-label">Total Messages</div>
        </div>
        <div class="mini-metric">
            <div class="m-val">{summary["peak_hour"]}:00</div>
            <div class="m-label">Peak Hour</div>
        </div>
        <div class="mini-metric">
            <div class="m-val">{summary["top_emoji"]}</div>
            <div class="m-label">Top Emoji</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Sentiment + Personality ───────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-header">Sentiment</div>', unsafe_allow_html=True)
    sentiment = ci.get_sentiment_analysis(selected_user, df)
    st.markdown(f"""
    <div class="sentiment-row">
        <div class="pill pill-pos">
            <div class="pct">{sentiment["positive"]}%</div>
            <div class="plabel">Positive</div>
        </div>
        <div class="pill pill-neu">
            <div class="pct">{sentiment["neutral"]}%</div>
            <div class="plabel">Neutral</div>
        </div>
        <div class="pill pill-neg">
            <div class="pct">{sentiment["negative"]}%</div>
            <div class="plabel">Negative</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-header">Personality</div>', unsafe_allow_html=True)
    traits = ci.get_personality_analysis(selected_user, df)
    badges = "".join(f'<span class="trait-badge">{t}</span>' for t in traits)
    st.markdown(f'<div style="padding-top:4px">{badges}</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Response time (Overall only) ──────────────────────────────────────────────
if selected_user == "Overall":
    st.markdown('<div class="section-header">Response Times</div>', unsafe_allow_html=True)
    rs = ci.get_response_time_analysis(df)
    st.markdown(f"""
    <div class="metric-row">
        <div class="mini-metric">
            <div class="m-val">{rs["avg_response"]}</div>
            <div class="m-label">Avg (mins)</div>
        </div>
        <div class="mini-metric">
            <div class="m-val">{rs["fastest"]}</div>
            <div class="m-label">Fastest (mins)</div>
        </div>
        <div class="mini-metric">
            <div class="m-val">{rs["slowest"]}</div>
            <div class="m-label">Slowest (mins)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Timelines ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Message Timeline</div>', unsafe_allow_html=True)
tab_monthly, tab_daily = st.tabs(["Monthly", "Daily"])

with tab_monthly:
    timeline = ci.get_monthly_timeline(selected_user, df)
    st.pyplot(_line_fig(timeline['time'], timeline['message']))

with tab_daily:
    daily = ci.get_daily_timeline(selected_user, df)
    st.pyplot(_line_fig(daily['only_date'], daily['message'], color=ACCENT2))

# ── Activity map ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Activity Map</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.caption("Busiest days of the week")
    busy_day = ci.get_weekly_activity(selected_user, df)
    st.pyplot(_bar_fig(busy_day.index, busy_day.values))
with col2:
    st.caption("Busiest months")
    busy_month = ci.get_monthly_activity(selected_user, df)
    st.pyplot(_bar_fig(busy_month.index, busy_month.values, color=ACCENT2))

st.markdown("**Hourly Heatmap**")
heatmap_data = ci.get_activity_heatmap(selected_user, df)
fig, ax = plt.subplots(figsize=(12, 3))
sns.heatmap(
    heatmap_data, ax=ax,
    cmap="Greens", linewidths=0.3, linecolor="#0d1117",
    cbar_kws={"shrink": 0.6}
)
ax.tick_params(colors=PLOT_FG, labelsize=7)
ax.set_xlabel("Hour Period", color=PLOT_FG, fontsize=8)
ax.set_ylabel("", color=PLOT_FG)
fig.patch.set_facecolor(PLOT_BG)
ax.set_facecolor(PLOT_BG)
fig.tight_layout()
st.pyplot(fig)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Group-level: most active users ────────────────────────────────────────────
if selected_user == "Overall":
    st.markdown('<div class="section-header">Most Active Users</div>', unsafe_allow_html=True)
    top_counts, share_df = ci.get_most_active_users(df)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.pyplot(_bar_fig(top_counts.index, top_counts.values, color="#f85149"))
    with col2:
        st.dataframe(share_df, use_container_width=True, hide_index=True)

    # ── Conversation starters ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Conversation Starters</div>', unsafe_allow_html=True)
    starter_df = ci.get_conversation_starters(df)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.pyplot(_bar_fig(starter_df['User'], starter_df['Conversations Started']))
    with col2:
        st.dataframe(starter_df, use_container_width=True, hide_index=True)
        if not starter_df.empty:
            leader = starter_df.iloc[0]['User']
            count  = starter_df.iloc[0]['Conversations Started']
            st.success(f"🏆 {leader} — {count} conversations started")

    # ── Response time leaderboard ──────────────────────────────────────────
    st.markdown('<div class="section-header">Response Time Leaderboard</div>', unsafe_allow_html=True)
    leaderboard_df = ci.get_response_time_leaderboard(df)
    if not leaderboard_df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.pyplot(_bar_fig(
                leaderboard_df['User'],
                leaderboard_df['Average Response Time (mins)'],
                color=ACCENT2, horizontal=True
            ))
        with col2:
            st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
            fastest = leaderboard_df.iloc[0]
            st.success(f"⚡ {fastest['User']} — {fastest['Average Response Time (mins)']} mins avg")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Word cloud + common words ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Words</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.caption("Word cloud")
    wc_img = ci.build_wordcloud(selected_user, df)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.imshow(wc_img)
    ax.axis('off')
    fig.patch.set_facecolor(PLOT_BG)
    ax.set_facecolor(PLOT_BG)
    fig.tight_layout(pad=0)
    st.pyplot(fig)

with col2:
    st.caption("Most common words")
    common_df = ci.get_most_common_words(selected_user, df)
    st.pyplot(_bar_fig(common_df['word'], common_df['count'], horizontal=True))

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Emoji breakdown ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Emoji Breakdown</div>', unsafe_allow_html=True)
emoji_df = ci.get_emoji_breakdown(selected_user, df)
col1, col2 = st.columns(2)
with col1:
    if not emoji_df.empty:
        st.dataframe(emoji_df.head(15), use_container_width=True, hide_index=True)
    else:
        st.write("No emojis found.")
with col2:
    if not emoji_df.empty:
        fig = px.pie(
            emoji_df.head(10), values='Count', names='Emoji',
            color_discrete_sequence=px.colors.sequential.Greens_r,
            hole=0.4,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=PLOT_FG,
            legend=dict(font=dict(color=PLOT_FG)),
            margin=dict(l=0, r=0, t=20, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── PDF export ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Export Report</div>', unsafe_allow_html=True)

summary_stats = ci.get_summary_stats(selected_user, df)
personality   = ci.get_personality_analysis(selected_user, df)
sentiment_    = ci.get_sentiment_analysis(selected_user, df)

starter_df_   = ci.get_conversation_starters(df) if selected_user == "Overall" else None
response_df_  = ci.get_response_time_leaderboard(df) if selected_user == "Overall" else None

pdf_path = pdf_export.generate_pdf(
    f"{selected_user}_ChatPulse_Report.pdf",
    selected_user,
    summary_stats,
    personality,
    sentiment_,
    starter_df_,
    response_df_,
)

with open(pdf_path, "rb") as pdf_file:
    st.download_button(
        label="📄  Download PDF Report",
        data=pdf_file,
        file_name=f"{selected_user}_ChatPulse_Report.pdf",
        mime="application/pdf",
    )

