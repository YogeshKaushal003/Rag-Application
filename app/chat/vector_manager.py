import os
import pickle
import faiss
from langchain_community.vectorstores import FAISS
# Fix the deprecation warning
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use absolute path to avoid permission issues
VECTORSTORE_BASE = os.path.abspath("vectorstores")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_vector_store(user_id):
    """
    Load FAISS vector store for a user with better path handling
    """
    try:
        # Use absolute paths
        user_vectorstore_path = os.path.join(VECTORSTORE_BASE, str(user_id))
        index_path = os.path.join(user_vectorstore_path, "index.faiss")
        pkl_path = os.path.join(user_vectorstore_path, "index.pkl")
        
        logger.info(f"Attempting to load vector store for user {user_id}")
        logger.info(f"Index path: {index_path}")
        logger.info(f"PKL path: {pkl_path}")
        
        # Check if files exist
        if not os.path.exists(index_path) or not os.path.exists(pkl_path):
            logger.info(f"Vector store files don't exist for user {user_id}")
            return None
        
        # Try to close any existing file handles (Windows specific issue)
        import gc
        gc.collect()
        time.sleep(0.1)  # Small delay to ensure file handles are released
        
        # Load FAISS index with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                index = faiss.read_index(index_path)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1} for loading index: {e}")
                    time.sleep(1)
                else:
                    raise e
        
        # Load metadata
        with open(pkl_path, 'rb') as f:
            store_data = pickle.load(f)
        
        # Reconstruct FAISS store
        faiss_store = FAISS(
            embedding_function=embedding_model.embed_query,
            index=index,
            docstore=store_data['docstore'],
            index_to_docstore_id=store_data['index_to_docstore_id']
        )
        
        logger.info(f"Successfully loaded vector store for user {user_id}")
        return faiss_store
        
    except Exception as e:
        logger.error(f"[FAISS LOAD ERROR]: {str(e)}")
        return None

def save_vector_store(user_id, faiss_store):
    """
    Save FAISS vector store for a user with better path handling
    """
    try:
        # Use absolute paths
        user_vectorstore_path = os.path.join(VECTORSTORE_BASE, str(user_id))
        index_path = os.path.join(user_vectorstore_path, "index.faiss")
        pkl_path = os.path.join(user_vectorstore_path, "index.pkl")
        
        # Ensure directory exists
        os.makedirs(user_vectorstore_path, exist_ok=True)
        
        logger.info(f"Attempting to save vector store for user {user_id}")
        
        # Force garbage collection to release any file handles
        import gc
        gc.collect()
        
        # Save FAISS index with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                faiss.write_index(faiss_store.index, index_path)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1} for saving index: {e}")
                    time.sleep(1)
                else:
                    raise e
        
        # Save metadata
        store_data = {
            'docstore': faiss_store.docstore,
            'index_to_docstore_id': faiss_store.index_to_docstore_id
        }
        
        with open(pkl_path, 'wb') as f:
            pickle.dump(store_data, f)
        
        logger.info(f"Successfully saved vector store for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"[FAISS SAVE ERROR]: {str(e)}")
        return False