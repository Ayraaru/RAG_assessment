"""
Document Loader Module
Loads and splits documents into chunks for embedding
"""
from pathlib import Path
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from src.config import settings


class DocumentLoader:
    """Load and split documents for RAG"""
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path: str) -> str:
        """
        Load text document from file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Document content as string
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    def split_documents(self, content: str) -> List[Document]:
        """
        Split document content into chunks
        
        Args:
            content: Document content as string
            
        Returns:
            List of Document objects with chunks
        """
        # Create documents with metadata
        chunks = self.text_splitter.split_text(content)
        
        documents = [
            Document(
                page_content=chunk,
                metadata={"source": settings.knowledge_base_path, "chunk_id": i}
            )
            for i, chunk in enumerate(chunks)
        ]
        
        return documents
    
    def load_and_split(self, file_path: str = None) -> List[Document]:
        """
        Load document and split into chunks
        
        Args:
            file_path: Optional path to document (uses config default if not provided)
            
        Returns:
            List of Document chunks
        """
        if file_path is None:
            file_path = settings.knowledge_base_path
        
        content = self.load_document(file_path)
        documents = self.split_documents(content)
        
        print(f"✅ Loaded and split document into {len(documents)} chunks")
        return documents
