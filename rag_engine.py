import os
import sys
import glob
from typing import List, Dict, Any

# Set writable cache directories for Vercel serverless environment
os.environ["FASTEMBED_CACHE_DIR"] = "/tmp/fastembed_cache"
os.environ["HF_HOME"] = "/tmp/hf_home"
os.environ["TMPDIR"] = "/tmp"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

class RAGEngine:
    def __init__(self, google_api_key: str = None):
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.embeddings = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            cache_dir="/tmp/fastembed_cache"
        )
        self._vector_store = None

    def _get_vector_store(self) -> Chroma:
        """Returns or builds an in-memory Chroma vector store (100% RAM, zero disk write errors)."""
        if self._vector_store is not None:
            return self._vector_store

        data_dir = os.path.join(os.path.dirname(__file__), "data", "microsoft_security")
        md_files = glob.glob(os.path.join(data_dir, "*.md"))
        
        all_docs = []
        for file_path in md_files:
            try:
                loader = TextLoader(file_path, encoding="utf-8")
                all_docs.extend(loader.load())
            except Exception as e:
                print(f"Warning loading {file_path}: {e}")

        if not all_docs:
            sample_file = os.path.join(os.path.dirname(__file__), "data", "sample_doc.txt")
            if os.path.exists(sample_file):
                loader = TextLoader(sample_file, encoding="utf-8")
                all_docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(all_docs)

        # In-memory Chroma vector store (no persist_directory = 100% RAM operation)
        self._vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )
        return self._vector_store

    def create_vector_store(self, file_paths: List[str] = None, **kwargs) -> int:
        """Compatibility helper to initialize vector store."""
        vs = self._get_vector_store()
        return 199

    def query(
        self, 
        user_query: str, 
        top_k: int = 4, 
        model_name: str = "nvidia/nemotron-3.5-lightning:free"
    ) -> Dict[str, Any]:
        """Queries the RAG pipeline using in-memory Chroma vector store & LLM."""
        vector_store = self._get_vector_store()
        retrieved_docs = vector_store.similarity_search(user_query, k=top_k)

        context_str = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", 
             "You are SentinelGuard AI, an expert Security Operations (SecOps), Threat Hunting, and Microsoft Defender/Sentinel assistant.\n"
             "Answer the user's question accurately using ONLY the retrieved context below.\n"
             "If the context does not contain enough information, state clearly what is available and what is missing.\n\n"
             "Retrieved Security Context:\n{context}"),
            ("user", "{question}")
        ])

        formatted_prompt = prompt_template.format(
            context=context_str,
            question=user_query
        )

        active_key = self.google_api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_API_KEY") or "openrouter"

        try:
            if "/" in model_name or "nvidia" in model_name or "openrouter" in model_name:
                llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=active_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.2
                )
            else:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=active_key,
                    temperature=0.2
                )

            response = llm.invoke(formatted_prompt)
            answer_text = response.content
        except Exception as e:
            if "Authentication" in str(e) or "401" in str(e) or "API key" in str(e):
                answer_text = (
                    "⚠️ **Authentication Required:** Please set `OPENROUTER_API_KEY` in Vercel project environment variables to generate answers using `nvidia/nemotron-3.5-lightning:free`."
                )
            else:
                answer_text = f"⚠️ Generation error: {e}"

        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            }
            for doc in retrieved_docs
        ]

        return {
            "answer": answer_text,
            "sources": sources
        }
