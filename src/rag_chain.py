"""
RAG Chain Module
Implements Retrieval Augmented Generation using LangChain
"""
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from src.config import settings
from src.vectorstore import VectorStore


class RAGChain:
    """RAG Chain for context-aware question answering"""
    
    def __init__(self, vectorstore: VectorStore):
        """
        Initialize RAG Chain
        
        Args:
            vectorstore: VectorStore instance with retriever
        """
        self.vectorstore = vectorstore
        self.retriever = vectorstore.get_retriever()
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            convert_system_message_to_human=True,
            max_output_tokens=150  # Limit output for faster responses
        )
        
        # Define RAG prompt template
        self.prompt_template = ChatPromptTemplate.from_template(
            """You are a helpful customer support assistant for TechGear, an electronics company.
Use the following context to answer the customer's question accurately and concisely.
If the answer is not in the context, politely say you don't have that information.

Context:
{context}

Question: {question}

Answer:"""
        )
        
        # Build the RAG chain
        self.chain = self._build_chain()
    
    def _build_chain(self):
        """Build the RAG chain with retriever and LLM"""
        
        def format_docs(docs):
            """Format retrieved documents into a single string"""
            return "\n\n".join([doc.page_content for doc in docs])
        
        # Create the chain
        rag_chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    def invoke(self, query: str) -> str:
        """
        Invoke RAG chain with a query
        
        Args:
            query: User question
            
        Returns:
            Generated answer
        """
        answer = self.chain.invoke(query)
        return answer
    
    def get_context_and_answer(self, query: str) -> Dict[str, Any]:
        """
        Get both retrieved context and answer
        
        Args:
            query: User question
            
        Returns:
            Dictionary with context and answer
        """
        # Retrieve relevant documents
        docs = self.retriever.get_relevant_documents(query)
        
        # Format context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Generate answer
        answer = self.invoke(query)
        
        return {
            "query": query,
            "context": context,
            "answer": answer,
            "sources": [doc.metadata for doc in docs]
        }
