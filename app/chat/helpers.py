from app.chat.vector_manager import load_vector_store
from app.chat.gemini import stream_gemini_response
from app.models.models import Message
from app import db
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_user_query(user_id, query):
    """
    Main function to handle user query and yield response chunks.
    """
    logger.info(f"Handling query for user {user_id}: {query[:50]}...")
    
    # Try to load user's vector store
    faiss_store = load_vector_store(user_id)
    
    if faiss_store:
        logger.info("Vector store loaded successfully, attempting RAG query")
        try:
            # Perform similarity search
            relevant_docs = faiss_store.similarity_search(query, k=3)
            
            if relevant_docs:
                # Create context from relevant documents
                context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                # Create a prompt with context
                rag_prompt = f"""
                Based on the following context, please answer the question. If the context doesn't contain relevant information, say so.
                
                Context:
                {context}
                
                Question: {query}
                
                Answer:
                """
                
                logger.info("Found relevant documents, generating RAG response")
                
                # Stream response from Gemini with context
                response = ""
                for chunk in stream_gemini_response(rag_prompt):
                    response += chunk
                    yield chunk
                
                # Save the conversation
                save_message(user_id, query, response)
                return
                
            else:
                logger.info("No relevant documents found in vector store")
                
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
    
    else:
        logger.info("No vector store found for user, using fallback")
    
    # Fallback: Direct Gemini response
    logger.info("Using Gemini fallback")
    response = ""
    for chunk in stream_gemini_response(query):
        response += chunk
        yield chunk
    
    # Save the conversation
    save_message(user_id, query, response)

def stream_response(response_text):
    """
    Simulates streaming by splitting into words.
    """
    words = response_text.split()
    for i, word in enumerate(words):
        # Add space except for the last word
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word

def save_message(user_id, question, answer):
    """
    Save conversation to database with error handling
    """
    try:
        msg = Message(user_id=user_id, question=question, answer=answer)
        db.session.add(msg)
        db.session.commit()
        logger.info(f"Message saved for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving message: {str(e)}")
        # Rollback in case of error
        db.session.rollback()