# 🏢 Visitor Management System with Local AI (RAG)

A Streamlit web app that digitizes visitor check-in and check-out, and adds a **free, fully offline AI layer** powered by [Ollama](https://ollama.com). Visitors get a chatbot that answers questions from the organization's own documents, and admins can query the visitor log in plain English.

> No paid APIs. No visitor data leaves your machine.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-ff4b4b)
![SQLite](https://img.shields.io/badge/DB-SQLite-003b57)
![Ollama](https://img.shields.io/badge/LLM-Ollama%20(local)-black)

---

## ✨ Features

### Core
- **Visitor check-in** with validation (name, email, phone, purpose), consent checkbox and webcam photo
- **Check-out tracking** and a live "currently inside" list
- **Admin dashboard** with full log, CSV export and photo gallery
- **Analytics**: total visits, visits per day, busiest hours, top purposes

### AI / RAG
| Feature | What it does |
|---|---|
| 🤖 **Help Assistant** | Answers visitor questions (parking, Wi-Fi, policies) using only your documents, and shows the sources |
| 🧭 **Smart host routing** | Matches the visitor's purpose to the right staff member using semantic search |
| 🔎 **Ask the Log** | Converts a plain-English question into a safe, read-only SQL query and explains the result |
| 📝 **Daily AI summary** | Generates a short report of a day's visits |

### Security & privacy
- Admin password stored in `.env`, never in code (timing-safe comparison, lockout after 5 failed attempts)
- AI-generated SQL is validated (single `SELECT` only) **and** executed on a read-only database connection
- Parameterized queries throughout; random UUID photo filenames (no path traversal)
- Consent required; one-click deletion of photos older than N days
- Personal data and secrets excluded from Git via `.gitignore`

---

## 🏗️ Architecture

```
                ┌──────────────────────────────┐
                │      Streamlit UI (app.py)    │
                └──────────────┬───────────────┘
        ┌──────────────┬───────┴────────┬───────────────┐
        ▼              ▼                ▼               ▼
  validators.py      db.py            rag.py        sql_agent.py
  (input checks)   (SQLite)    (chunk→embed→search)  (question→SELECT)
                                       │               │
                                       └──────┬────────┘
                                              ▼
                                           llm.py
                                              ▼
                              Ollama (llama3.2 + nomic-embed-text)
```

### How RAG works here
1. **Index:** documents in `docs/` are split into ~700-character chunks, embedded with `nomic-embed-text`, normalized and saved to `data/index/`.
2. **Retrieve:** the question is embedded and compared by cosine similarity; the top 4 chunks are selected.
3. **Guard:** if the best match scores below `0.35`, the bot says it doesn't know instead of guessing.
4. **Generate:** the chunks plus the question go to the local LLM with an "answer only from this context" instruction. Sources are displayed with the answer.

---

## 📁 Project structure

```
project2/
├── app.py              # Streamlit UI (kiosk, assistant, admin)
├── config.py           # Settings loaded from .env
├── db.py               # SQLite layer (check-in/out, queries, photo purge)
├── auth.py             # Admin login
├── validators.py       # Form validation
├── llm.py              # Ollama client (chat + embeddings)
├── rag.py              # Chunking, indexing, retrieval, answering, host routing
├── sql_agent.py        # Text-to-SQL with safety checks, daily summary
├── docs/               # Knowledge base (edit these!)
│   ├── visitor_policy.md
│   ├── faq.md
│   └── directory.csv   # Staff directory used for host routing
├── tests/test_core.py  # Pytest suite
├── requirements.txt
├── .env.example
└── .gitignore
```

`data/` (database, photos, search index) is created automatically on first run and is git-ignored.

---

## 🚀 Getting started

### Prerequisites
- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- A webcam (optional, for visitor photos)
- About 4 GB of free RAM for the default model

### 1. Pull the local models (one time)
```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 2. Set up the project
```bash
# create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> **PowerShell blocked scripts?** Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.

### 3. Configure
```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```
Open `.env` and set a strong `ADMIN_PASSWORD`.

### 4. Run
```bash
streamlit run app.py
```
Open http://localhost:8501. The sidebar shows **🟢 Local AI online** when Ollama is reachable.

---

## ⚙️ Configuration

All settings live in `.env`:

| Variable | Default | Description |
|---|---|---|
| `ADMIN_PASSWORD` | *(empty)* | Admin login password. Admin is disabled until set |
| `OLLAMA_URL` | `http://localhost:11434` | Address of the Ollama server |
| `CHAT_MODEL` | `llama3.2:3b` | Model used for answers and SQL generation |
| `EMBED_MODEL` | `nomic-embed-text` | Model used for embeddings |

**Model tips:** on low-RAM PCs use `llama3.2:1b`. With 16 GB RAM, `qwen2.5:7b` generally writes better SQL. If you change `EMBED_MODEL`, rebuild the knowledge index.

RAG tuning values (`TOP_K`, `MIN_SCORE`) are in `config.py`.

---

## 🧑‍💻 Usage

**Visitors**
1. *Visitor Check-In*: fill the form, optionally click **Suggest who I should meet**, take a photo, accept consent, click **Check In**.
2. *Help Assistant*: ask questions like "Where can I park?" or "Is there Wi-Fi?".

**Admins** (*Admin* → log in)

| Tab | Purpose |
|---|---|
| Live & Log | See who is inside, check people out, export CSV, view photos |
| Analytics | Visit trends and top purposes |
| Ask the Log | e.g. "Who visited for billing issues this month?" |
| Daily Summary | AI-written report for a chosen date |
| Knowledge & Privacy | Upload documents, rebuild the index, delete old photos |

### Customize for your organization
1. Edit `docs/visitor_policy.md`, `docs/faq.md` and `docs/directory.csv` (or upload `.md`, `.txt`, `.pdf` files in the admin panel).
2. Click **Rebuild knowledge index**.

---

## 🧪 Testing

```bash
pytest
```

The tests cover validation, check-in/out, SQL safety (rejecting `DROP`, stacked statements, writes), read-only enforcement, chunking, retrieval, host routing and the text-to-SQL flow. AI calls are mocked, so tests run without Ollama.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Sidebar shows 🔴 Local AI offline | Start the Ollama app and refresh the page |
| "Model not found" | Re-run both `ollama pull` commands |
| `streamlit` not recognized | Use `python -m streamlit run app.py` |
| "Admin is disabled" | Create `.env` and set `ADMIN_PASSWORD`, then restart |
| Slow answers | Use a smaller model (`llama3.2:1b`) |
| Camera not showing | Allow camera access in the browser address bar |
| "Database is locked" | Move the project out of a OneDrive-synced folder |

---

## ⚠️ Limitations

- Vector search is brute-force over a numpy file: ideal for hundreds of chunks, not millions.
- Admin auth is a single shared password (no accounts, roles or hashing).
- Small local models can occasionally misread context or write incorrect SQL. The SQL is shown so admins can verify it.
- Photo deletion is manual, not scheduled.

## 🗺️ Roadmap

- [ ] Email / Slack notification to the host on arrival
- [ ] QR-code visitor badges
- [ ] Repeat-visitor recognition (with consent)
- [ ] RAG evaluation set (retrieval hit-rate and answer faithfulness)
- [ ] Multi-user admin accounts with hashed passwords
- [ ] Scheduled data-retention job
- [ ] Docker support and PostgreSQL option

---

## 🔒 Privacy note

This system stores names, contact details and optional photos. Only deploy it with a clear retention policy and visitor consent, and follow the data-protection laws that apply to you. Never commit `data/` or `.env` to Git.

## 📄 License

MIT License (add a `LICENSE` file to the repository).

## 👤 Author

**Karishma**: [github.com/karishma-0412](https://github.com/karishma-0412)
