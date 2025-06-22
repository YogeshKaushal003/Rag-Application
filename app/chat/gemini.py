import os
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def stream_gemini_response(query):
    try:
        # Fix: Use correct free tier model name
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        logger.info(f"Generating response for query: {query[:50]}...")
        
        stream = model.generate_content(query, stream=True)

        for chunk in stream:
            yield chunk.text if chunk.text else ""

    except Exception as e:
        error_message = f"An error occurred with Gemini fallback: {str(e)}"
        logger.error(error_message)
        yield error_message