import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
from rag_engine import RAGEngine

def test_rag_pipeline():
    sample_file = os.path.join(os.path.dirname(__file__), "data", "sample_doc.txt")
    print(f"Testing RAG pipeline with sample file: {sample_file}")

    # Test indexing with Gemini API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    engine = RAGEngine(google_api_key=api_key)
    chunks_created = engine.create_vector_store(
        file_paths=[sample_file],
        chunk_size=300,
        chunk_overlap=50,
        reset_db=False
    )
    print(f"[SUCCESS] Document split into {chunks_created} chunks and stored in Chroma DB.")

    # Test Enterprise SecOps LSASS Pass-the-Hash KQL query
    res = engine.query(
        "How do I write a KQL query to correlate LSASS credential dumping with Pass-the-Hash lateral movement?", 
        top_k=3,
        model_name="nvidia/nemotron-3.5-lightning:free"
    )
    print("\n--- Security RAG Query Result ---")
    print(f"Answer: {res['answer']}\n")
    print(f"Retrieved {len(res['sources'])} source chunks:")
    for idx, src in enumerate(res['sources'], 1):
        print(f"\nChunk {idx} ({os.path.basename(src['source'])}):")
        print(f"{src['content'][:250]}...")

if __name__ == "__main__":
    test_rag_pipeline()
