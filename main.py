from fastapi import FastAPI, UploadFile, File, HTTPException
import requests
from huggingface_hub import InferenceClient
import fitz  # PyMuPDF for PDF parsing
from io import BytesIO
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uvicorn

# Securely fetch Hugging Face API key
HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("Hugging Face API key not found. Set HF_API_KEY as an environment variable.")

# Initialize FastAPI app
app = FastAPI()

# Initialize Hugging Face Inference API Client
client = InferenceClient(api_key=HF_API_KEY)
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
HF_API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Load Hugging Face Embeddings
print("[INFO] Loading Hugging Face Embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Global variable for FAISS vector store
vector_store = None

async def extract_text_from_pdf(file: UploadFile):
    """Extract text from PDF using PyMuPDF."""
    try:
        file_bytes = await file.read()
        doc = fitz.open(stream=BytesIO(file_bytes), filetype="pdf")
        text = "\n".join([doc.load_page(i).get_text("text") for i in range(len(doc))])

        if not text.strip():
            raise ValueError("[ERROR] Extracted text is empty!")

        print(f"[INFO] Extracted {len(text)} characters from PDF.")
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")

def process_text(text):
    """Process text using LangChain and FAISS embeddings."""
    try:
        print(f"[DEBUG] Processing text of length {len(text)}.")

        # Text splitting
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(text)

        print(f"[INFO] Created {len(chunks)} text chunks.")

        # Store in FAISS
        global vector_store
        vector_store = FAISS.from_texts(chunks, embeddings)

        print("[INFO] FAISS Vector Store created successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during text processing: {str(e)}")

extracted_text = ""  # Global variable to store the PDF text

@app.post("/process/")
async def process_pdf(file: UploadFile = File(...)):
    """Endpoint to process and store PDF content."""
    global extracted_text  # Store extracted text globally

    try:
        extracted_text = await extract_text_from_pdf(file)
        process_text(extracted_text)
        print("[INFO] PDF processed successfully.")
        return {"message": "PDF processed and stored successfully!"}
    except Exception as e:
        print(f"[ERROR] PDF processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")



@app.post("/ask/")
async def ask_question(query: str):
    """Retrieve relevant text from FAISS and generate a response using LLM."""
    global extracted_text, vector_store

    if not extracted_text:
        raise HTTPException(status_code=400, detail="No PDF text available. Please upload and process a PDF first.")

    # Retrieve relevant chunks from FAISS
    relevant_chunks = ""
    if vector_store:
        results = vector_store.similarity_search(query, k=5)  # Get top 5 relevant chunks
        relevant_chunks = "\n".join([res.page_content for res in results])

    # Formulate the prompt
    full_prompt = f"Document Context:\n{relevant_chunks}\n\nUser Query: {query}\n\nAnswer:"

    # Send the prompt to Hugging Face API
    payload = {
        "inputs": full_prompt,
        "parameters": {"max_new_tokens": 500, "temperature": 0.7}
    }

    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        generated_text = response.json()[0]["generated_text"]
        return {"answer": generated_text}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
