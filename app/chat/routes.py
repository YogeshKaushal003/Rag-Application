from flask import Blueprint, request, Response, stream_with_context, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.chat.helpers import handle_user_query
from app.chat.vector_manager import load_vector_store, save_vector_store

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# Fix the deprecation warning
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import os

chat_bp = Blueprint('chat', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'txt'}
UPLOAD_BASE = "uploaded_docs"

# Global embedding model instance (free)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Rest of your code remains the same...
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_chat():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400

    query = data['query']

    def generate():
        for chunk in handle_user_query(user_id, query):
            yield f"data: {chunk}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@chat_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_documents():
    user_id = get_jwt_identity()

    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400

    upload_path = os.path.join(UPLOAD_BASE, str(user_id))
    os.makedirs(upload_path, exist_ok=True)

    docs = []
    saved_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            saved_files.append(filename)

            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif filename.endswith(".txt"):
                loader = TextLoader(file_path)
            else:
                continue

            pages = loader.load()
            docs.extend(pages)

    if not docs:
        return jsonify({"error": "No content extracted from documents"}), 400

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    faiss_store = load_vector_store(user_id)
    if faiss_store:
        faiss_store.add_documents(chunks)
    else:
        faiss_store = FAISS.from_documents(chunks, embedding_model)

    save_vector_store(user_id, faiss_store)

    return jsonify({
        "message": "Documents uploaded and indexed successfully",
        "files": saved_files,
        "chunks_added": len(chunks)
    }), 200