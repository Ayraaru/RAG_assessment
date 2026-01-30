"""
Vector Store Module
Manages ChromaDB vector store for document embeddings and retrieval
"""
from typing import List
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import settings


class VectorStore:
    """ChromaDB Vector Store Manager"""
    
    def __init__(self):
        self.chroma_db_dir = settings.chroma_db_dir
        self.collection_name = settings.collection_name
        
        # Initialize embeddings model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.google_api_key
        )
        
        self.vectorstore = None
        self.retriever = None
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        Create ChromaDB vector store from documents
        
        Args:
            documents: List of Document objects
            
        Returns:
            Chroma vectorstore instance
        """
        print(f"📦 Creating ChromaDB vector store with {len(documents)} documents...")
        
        # Create Chroma vectorstore
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.chroma_db_dir
        )
        
        print(f"✅ Vector store created successfully")
        return self.vectorstore
    
    def load_vectorstore(self) -> Chroma:
        """
        Load existing ChromaDB vector store
        
        Returns:
            Chroma vectorstore instance
        """
        print("📂 Loading existing vector store...")
        
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.chroma_db_dir
        )
        
        print("✅ Vector store loaded successfully")
        return self.vectorstore
    
    def get_retriever(self, k: int = None):
        """
        Get retriever from vector store
        
        Args:
            k: Number of documents to retrieve (uses config default if not provided)
            
        Returns:
            Retriever instance
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_vectorstore first.")
        
        if k is None:
            k = settings.top_k_results
        
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": k,
                "fetch_k": k * 2  # Fetch more initially for better diversity
            }
        )
        
        return self.retriever
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized")
        
        if k is None:
            k = settings.top_k_results
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
