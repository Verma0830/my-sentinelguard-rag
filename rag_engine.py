import os
import sys
import glob
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

class RAGEngine:
    def __init__(self, google_api_key: str = None):
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.vectorizer = None
        self.tfidf_matrix = None
        self.chunks = []
        self._initialize_index()

    def _initialize_index(self):
        """Loads security documents and builds a lightweight TF-IDF Vector Index in RAM (Zero disk space required)."""
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
        self.chunks = text_splitter.split_documents(all_docs)

        # Fit TF-IDF Vectorizer across all security chunks in RAM
        corpus = [doc.page_content for doc in self.chunks]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def create_vector_store(self, file_paths: List[str] = None, **kwargs) -> int:
        """Compatibility helper."""
        return len(self.chunks)

    def query(
        self, 
        user_query: str, 
        top_k: int = 4, 
        model_name: str = "nvidia/nemotron-3.5-lightning:free"
    ) -> Dict[str, Any]:
        """Queries the RAG pipeline using zero-disk TF-IDF Vector Similarity & LLM."""
        if not self.chunks or self.vectorizer is None:
            return {
                "answer": "No security documents found in index.",
                "sources": []
            }

        # Vector similarity search via Cosine Similarity
        query_vector = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        # Get top-k indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        retrieved_docs = [self.chunks[i] for i in top_indices if similarities[i] > 0]

        # Fallback if query terms didn't match specific n-grams
        if not retrieved_docs:
            retrieved_docs = self.chunks[:top_k]

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
