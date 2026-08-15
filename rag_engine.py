import os
import shutil
from typing import List, Dict, Any, Tuple

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "chroma_db")

class RAGEngine:
    def __init__(self, google_api_key: str = None):
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.embeddings = self._get_embeddings()

    def _get_embeddings(self):
        """Uses lightweight ONNX FastEmbed embeddings for vector storage (No PyTorch)."""
        return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    def load_document(self, file_path: str) -> List[Document]:
        """Loads a PDF, TXT, or Markdown document into LangChain Document format."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        return loader.load()

    def create_vector_store(
        self, 
        file_paths: List[str], 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        reset_db: bool = True
    ) -> int:
        """Processes files, splits into chunks, and saves to Chroma Vector DB."""
        if reset_db and os.path.exists(PERSIST_DIRECTORY):
            try:
                shutil.rmtree(PERSIST_DIRECTORY)
            except Exception as e:
                print(f"Notice: Could not clear existing vector DB directory ({e}). Overwriting existing collection.")

        all_docs = []
        for file_path in file_paths:
            docs = self.load_document(file_path)
            all_docs.extend(docs)

        if not all_docs:
            return 0

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(all_docs)

        # Build & persist Chroma database
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=PERSIST_DIRECTORY
        )
        return len(chunks)

    def query(
        self, 
        user_query: str, 
        top_k: int = 4, 
        model_name: str = "nvidia/nemotron-3.5-lightning:free"
    ) -> Dict[str, Any]:
        """Searches vector store and generates an answer using LLM."""
        if not os.path.exists(PERSIST_DIRECTORY):
            return {
                "answer": "No documents have been indexed yet. Please upload a document first.",
                "sources": []
            }

        vector_store = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=self.embeddings
        )

        # Retrieve relevant chunks
        results = vector_store.similarity_search_with_score(user_query, k=top_k)
        
        retrieved_docs = [doc for doc, score in results]
        
        context_str = "\n\n---\n\n".join(
            [f"[Source: {doc.metadata.get('source', 'Unknown')} Page: {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}" 
             for doc in retrieved_docs]
        )

        prompt_template = ChatPromptTemplate.from_template(
            """You are a helpful and accurate assistant powered by Retrieval-Augmented Generation (RAG).
Answer the user's question using strictly the retrieved context provided below.
If the context does not contain enough information to answer, state clearly that the provided documents do not contain the answer.
Do not hallucinate facts outside the context.

Retrieved Context:
{context}

User Question: {question}

Answer:"""
        )

        formatted_prompt = prompt_template.format(context=context_str, question=user_query)

        active_key = self.google_api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_API_KEY") or "openrouter"

        # Initialize LLM (OpenRouter for NVIDIA Nemotron or Google GenAI)
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
                    "⚠️ **Authentication Required:** Please provide your free OpenRouter API key "
                    "(or set `OPENROUTER_API_KEY` in `.env`) to generate answers using `nvidia/nemotron-3.5-lightning:free`."
                )
            else:
                answer_text = f"⚠️ Generation error: {e}"

        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "N/A"),
                "content": doc.page_content
            }
            for doc in retrieved_docs
        ]

        return {
            "answer": answer_text,
            "sources": sources
        }
