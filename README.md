# ⚡ RAG Navigator

An intelligent, modular Retrieval-Augmented Generation (RAG) web application built with **Python**, **LangChain**, **ChromaDB**, and **Streamlit**.

---

## 🌟 Features

- 📄 **Multi-Format Support:** Ingest PDF (`.pdf`), Text (`.txt`), and Markdown (`.md`) files.
- ⚡ **ChromaDB Vector Store:** Fast, persistent local vector embeddings and similarity search.
- 🤖 **Free Gemini Integration:** Powered by Google's `gemini-1.5-flash` / `gemini-2.0-flash` & `text-embedding-004` (100% free via Google AI Studio).
- 🔍 **Source Citations:** Every answer displays exact source files, page numbers, and text snippets used during context augmentation.
- 🎛️ **Customizable Parameters:** Tune chunk sizes, chunk overlap, and top-K retrieved passages directly from the UI sidebar.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Make sure Python 3.10+ is installed on your machine.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API Key** and create a free key.
3. (Optional) Create a `.env` file from `.env.example`:
   ```bash
   GOOGLE_API_KEY=your_actual_key_here
   ```
   *Or pass your key directly through the Streamlit sidebar UI!*

### 4. Run the Streamlit Web Application
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 📂 Project Structure

```
my-rag-app/
│── app.py             # Streamlit dashboard and interactive chat UI
│── rag_engine.py      # Core RAG pipeline (loaders, chunking, embeddings, Chroma, Gemini LLM)
│── requirements.txt   # Python dependencies
│── .env.example       # Environment template for API keys
└── README.md          # Project documentation
```
