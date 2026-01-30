"""
LangGraph Workflow Module
Implements multi-node workflow with classifier, RAG responder, and escalation
"""
from typing import TypedDict, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from src.config import settings
from src.rag_chain import RAGChain


class GraphState(TypedDict):
    """State schema for the graph"""
    query: str              # User's original query
    category: str           # Classified category
    answer: str             # Final response
    metadata: dict          # Additional information


class RAGWorkflow:
    """LangGraph workflow for RAG chatbot"""
    
    def __init__(self, rag_chain: RAGChain):
        """
        Initialize workflow
        
        Args:
            rag_chain: RAGChain instance
        """
        self.rag_chain = rag_chain
        
        # Initialize LLM for classification
        self.classifier_llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=0.1,  # Very low temperature for faster, more consistent classification
            convert_system_message_to_human=True,
            max_output_tokens=10  # Limit output to just the category name
        )
        
        # Build the workflow graph
        self.app = self._build_graph()
    
    def classifier_node(self, state: GraphState) -> GraphState:
        """
        Node 1: Classify the user query into categories
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with category
        """
        query = state["query"]
        
        classification_prompt = f"""Classify the following customer query into ONE category only.
        
Categories:
- "products": Questions about product features, prices, specifications, warranties, or comparisons
- "returns": Questions about return policy, refund process, or exchange procedures
- "general": General support questions, contact information, or business hours
- "unknown": Queries that are out of scope, unclear, or not related to our products/services

Query: {query}

Respond with ONLY the category name (products, returns, general, or unknown). No explanation."""
        
        try:
            response = self.classifier_llm.invoke(classification_prompt)
            category = response.content.strip().lower()
            
            # Validate category
            valid_categories = ["products", "returns", "general", "unknown"]
            if category not in valid_categories:
                category = "unknown"
            
            state["category"] = category
            state["metadata"] = {"classifier": "success"}
            
            print(f"🔍 Classified as: {category}")
            
        except Exception as e:
            print(f"❌ Classification error: {e}")
            state["category"] = "unknown"
            state["metadata"] = {"classifier": "error", "error": str(e)}
        
        return state
    
    def rag_responder_node(self, state: GraphState) -> GraphState:
        """
        Node 2: Use RAG to generate answer based on retrieved context
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with answer
        """
        query = state["query"]
        
        try:
            print("📚 Retrieving context and generating answer...")
            
            # Get answer from RAG chain
            result = self.rag_chain.get_context_and_answer(query)
            
            state["answer"] = result["answer"]
            state["metadata"]["rag"] = {
                "sources": result["sources"],
                "context_used": True
            }
            
        except Exception as e:
            print(f"❌ RAG error: {e}")
            state["answer"] = "I apologize, but I'm having trouble accessing the information right now. Please try again or contact support."
            state["metadata"]["rag"] = {"error": str(e)}
        
        return state
    
    def escalation_node(self, state: GraphState) -> GraphState:
        """
        Node 3: Handle queries that need escalation to human support
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with escalation message
        """
        category = state.get("category", "unknown")
        
        if category == "general":
            # For general queries, provide support information
            escalation_message = """For general inquiries and support:

📧 Email: support@techgear.com
⏰ Support Hours: Monday-Saturday, 9AM-6PM IST

Our team will be happy to assist you with your questions!"""
        else:
            # For unknown/out-of-scope queries
            escalation_message = """I apologize, but I'm unable to assist with that specific request.

For personalized support, please contact our team:
📧 Email: support@techgear.com
⏰ Support Hours: Monday-Saturday, 9AM-6PM IST

Our support team will be happy to help you!"""
        
        state["answer"] = escalation_message
        state["metadata"]["escalation"] = True
        
        print("🔼 Query escalated to support")
        
        return state
    
    def route_query(self, state: GraphState) -> Literal["rag_responder", "escalation"]:
        """
        Routing function: Decide which node to go to based on category
        
        Args:
            state: Current graph state
            
        Returns:
            Name of the next node
        """
        category = state.get("category", "unknown")
        
        # Route product and return queries to RAG
        if category in ["products", "returns"]:
            print(f"→ Routing to RAG Responder")
            return "rag_responder"
        
        # Route general and unknown queries to escalation
        else:
            print(f"→ Routing to Escalation")
            return "escalation"
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        
        Returns:
            Compiled graph application
        """
        # Create the graph
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("classifier", self.classifier_node)
        workflow.add_node("rag_responder", self.rag_responder_node)
        workflow.add_node("escalation", self.escalation_node)
        
        # Set entry point
        workflow.set_entry_point("classifier")
        
        # Add conditional edges from classifier
        workflow.add_conditional_edges(
            "classifier",
            self.route_query,
            {
                "rag_responder": "rag_responder",
                "escalation": "escalation"
            }
        )
        
        # Both nodes end the workflow
        workflow.add_edge("rag_responder", END)
        workflow.add_edge("escalation", END)
        
        # Compile the graph
        app = workflow.compile()
        
        print("✅ LangGraph workflow compiled successfully")
        return app
    
    def invoke(self, query: str) -> dict:
        """
        Execute the workflow with a query
        
        Args:
            query: User question
            
        Returns:
            Final state with answer
        """
        print(f"\n🚀 Processing query: {query}")
        
        initial_state = {
            "query": query,
            "category": "",
            "answer": "",
            "metadata": {}
        }
        
        # Execute the graph
        result = self.app.invoke(initial_state)
        
        print(f"✅ Answer generated\n")
        
        return result
