# 💬 ChatPulse — WhatsApp Chat Analyzer

> Decode your WhatsApp conversations with deep insights, beautiful charts, and AI-powered analysis.

---

## 🚀 Live Demo
👉 **[chatpulse.streamlit.app](https://chatpulse-farazcodes-pro.streamlit.app/)**

---

## ✨ Features

- 📊 **Message Statistics** — total messages, words, media, and links shared
- 📅 **Timelines** — monthly and daily message activity charts
- 🗺️ **Activity Heatmap** — see which days and hours are most active
- 😊 **Sentiment Analysis** — positive, neutral, and negative tone breakdown
- 🧠 **Personality Analysis** — communication style traits per user
- ⚡ **Response Time Analysis** — who replies fastest in the group
- 🏆 **Conversation Starters** — who kicks off the most conversations
- ☁️ **Word Cloud** — most used words visualized
- 😂 **Emoji Breakdown** — top emojis with pie chart distribution
- 📄 **PDF Export** — download a full analysis report

---

## 📁 Project Structure

```
chatpulse/
├── app.py                  # Main Streamlit UI
├── chat_insights.py        # All analysis functions
├── chat_parser.py          # WhatsApp export parser
├── pdf_export.py           # PDF report generator
├── stop_hinglish.txt       # Stopwords (English + Hindi)
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/FarazCodes-pro/chatpulse.git
cd chatpulse
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run app.py
```

---

## 📤 How to Export Your WhatsApp Chat

**Android:** Open chat → Three dots → More → Export chat → Without media

**iPhone:** Open chat → Contact/Group name → Export chat → Without media

Upload the `.txt` file in the sidebar and hit **Run Analysis**.

---

## 🧰 Tech Stack

| Tool | Purpose |
|---|---|
| Streamlit | Web app framework |
| Pandas | Data processing |
| Matplotlib / Seaborn | Charts |
| Plotly | Interactive pie charts |
| TextBlob | Sentiment analysis |
| WordCloud | Word cloud generation |
| ReportLab | PDF export |
| URLExtract | Link detection |
| Emoji | Emoji parsing |

---

## 👨‍💻 Author

Built by **[FarazCodes-pro](https://github.com/FarazCodes-pro)**

---

## ⭐ Support

If you found this useful, please **star the repo** — it helps a lot!
