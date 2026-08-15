import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from rag_engine import RAGEngine

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "microsoft_security")
os.makedirs(DATA_DIR, exist_ok=True)

# Curated documentation sources for MS Defender, Sentinel, and KQL
MS_DOC_SOURCES = [
    {
        "filename": "defender_advanced_hunting_guide.md",
        "url": "https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview",
        "title": "Microsoft Defender XDR Advanced Hunting Comprehensive Guide"
    },
    {
        "filename": "defender_kql_best_practices.md",
        "url": "https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-best-practices",
        "title": "Microsoft Defender Advanced Hunting KQL Performance & Best Practices"
    },
    {
        "filename": "sentinel_siem_architecture.md",
        "url": "https://learn.microsoft.com/en-us/azure/sentinel/overview",
        "title": "Microsoft Sentinel SIEM & SOAR Security Architecture"
    },
    {
        "filename": "sentinel_threat_detection_analytics.md",
        "url": "https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-built-in",
        "title": "Microsoft Sentinel Analytics Rules & Incident Detection"
    },
    {
        "filename": "kql_operator_quick_reference.md",
        "url": "https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/kql-quick-reference",
        "title": "Kusto Query Language (KQL) Operators & Functions Quick Reference"
    },
    {
        "filename": "sentinel_github_rules_guide.md",
        "url": "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/README.md",
        "title": "Azure Sentinel Official Repository Detection & Hunting Queries"
    }
]

def clean_learn_html(html_content: str, title: str, source_url: str) -> str:
    """Parses Microsoft Learn HTML pages to extract clean technical article text."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Decompose unwanted elements
    for el in soup.find_all(["nav", "footer", "header", "script", "style", "form", "button", "aside"]):
        el.decompose()
        
    for el in soup.find_all("div", class_=re.compile(r"feedback|metadata|action-container|nav|header|footer", re.I)):
        el.decompose()

    # Locate main article content
    main_el = soup.find("article") or soup.find("main") or soup.find("div", {"id": "main"}) or soup.body
    
    # Extract headers and paragraphs cleanly
    paragraphs = []
    paragraphs.append(f"# {title}")
    paragraphs.append(f"Source URL: {source_url}\n")

    for tag in main_el.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "code", "pre", "table"]):
        text = tag.get_text().strip()
        if text and not any(skip in text for skip in ["Feedback", "Summarize this article", "Is this page helpful?"]):
            paragraphs.append(text)

    return "\n\n".join(paragraphs)

def download_and_ingest():
    """Downloads official documentation and indexes into Chroma DB."""
    downloaded_files = []
    print("📥 Ingesting Microsoft Defender & Sentinel Knowledge Base...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for item in MS_DOC_SOURCES:
        file_path = os.path.join(DATA_DIR, item["filename"])
        try:
            resp = requests.get(item["url"], headers=headers, timeout=15)
            if resp.status_code == 200:
                if item["url"].endswith(".md") or "raw.githubusercontent.com" in item["url"]:
                    clean_text = f"# {item['title']}\nSource URL: {item['url']}\n\n" + resp.text
                else:
                    clean_text = clean_learn_html(resp.text, item["title"], item["url"])
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)
                
                downloaded_files.append(file_path)
                print(f"  ✓ Ingested: {item['filename']} ({len(clean_text)} chars)")
            else:
                print(f"  ⚠️ HTTP {resp.status_code} for {item['url']}")
        except Exception as e:
            print(f"  ❌ Error fetching {item['url']}: {e}")

    # Scan DATA_DIR for any manually added files (e.g. ms_defender_and_sentinel_5yo_guide.md)
    for fname in os.listdir(DATA_DIR):
        fpath = os.path.join(DATA_DIR, fname)
        if fpath not in downloaded_files and (fname.endswith(".md") or fname.endswith(".txt")):
            downloaded_files.append(fpath)

    if not downloaded_files:
        print("No files were downloaded or found.")
        return 0

    print(f"\n⚡ Vectorizing and Indexing {len(downloaded_files)} security resources into Chroma DB...")
    api_key = os.getenv("GOOGLE_API_KEY")
    engine = RAGEngine(google_api_key=api_key)
    
    # Re-index with clean high-density vector store
    chunks = engine.create_vector_store(
        file_paths=downloaded_files,
        chunk_size=1000,
        chunk_overlap=200,
        reset_db=True
    )
    print(f"\n✅ Successfully indexed {len(downloaded_files)} files into {chunks} vector chunks in Chroma DB!")
    return chunks

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    download_and_ingest()
