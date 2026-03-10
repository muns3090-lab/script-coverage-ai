# 🎬 Script Coverage AI

> Professional script coverage reports generated in seconds — powered by Claude AI.

**[Live Demo →](#)**  *(link coming soon)*

---

## What is Script Coverage?

Script coverage is the industry-standard evaluation report that Hollywood development executives, producers, and literary managers use to assess screenplays before recommending them for purchase or production. A coverage report typically includes a logline, synopsis, character breakdown, thematic analysis, and a formal recommendation. Writing it by hand takes 2–4 hours per script.

**Script Coverage AI does it in under a minute.**

---

## Features

- **Instant PDF ingestion** — Upload any text-based screenplay PDF; the app extracts and cleans the full text automatically
- **AI-generated coverage** — Claude analyzes the script like a senior studio executive with 20+ years of experience
- **Structured report** — Every coverage includes:
  - Logline, synopsis, tone, and setting
  - Protagonist arc and supporting character breakdown
  - Themes and comparable titles
  - Strengths and weaknesses
  - Commercial marketability assessment
  - Formal recommendation: **PASS / CONSIDER / RECOMMEND**
  - Overall score out of 10
  - Analyst notes for the development team
- **Color-coded recommendations** — Green, amber, and red badges for instant visual triage
- **Downloadable report** — Export the full coverage as a formatted `.txt` file
- **Input validation** — Detects scanned/image PDFs, warns on oversized files
- **Dark cinematic UI** — Gold-accented professional interface built for the entertainment industry

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io) 1.55 |
| AI Model | [Anthropic Claude](https://www.anthropic.com) (`claude-opus-4-5`) |
| PDF Extraction | [PyMuPDF](https://pymupdf.readthedocs.io) 1.27 |
| Environment | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| Language | Python 3.10+ |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/script-coverage-ai.git
cd script-coverage-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Anthropic API key

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

> Get your API key at [console.anthropic.com](https://console.anthropic.com).

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Deploying to Streamlit Cloud

1. Push the repo to GitHub (the `.env` file is gitignored — never commit it)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repository
3. Under **Advanced settings → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "your_api_key_here"
   ```
4. Deploy — the app reads from `st.secrets` automatically when `.env` is not present

---

## Project Structure

```
script-coverage-ai/
├── app.py                        # Main Streamlit application
├── utils/
│   ├── pdf_extractor.py          # PDF ingestion and text cleaning
│   └── coverage_generator.py    # Claude API call and response parsing
├── .streamlit/
│   └── config.toml              # Dark theme configuration
├── requirements.txt
└── .env                         # API key (gitignored, never committed)
```

---

## Usage Notes

- Works with **text-based PDFs** exported from Final Draft, Highland, WriterDuet, Fade In, or any standard screenwriting software
- Does **not** work with scanned / image-only PDFs (the app will notify you)
- Recommended length: under 200 pages for fastest results; files up to 500 pages are supported with a performance warning

---

## Built By

**Sunil Sukumar** — AI Product Portfolio
[LinkedIn](https://www.linkedin.com/in/sunilsukumar)

---

*Built with [Streamlit](https://streamlit.io) · Powered by [Claude AI](https://www.anthropic.com)*
