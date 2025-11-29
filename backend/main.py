"""FastAPI backend for the QA Agent application."""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import uvicorn

import config
from document_processor import DocumentProcessor, TextChunker
from vector_store import vector_store
from llm_client import QAAgent

app = FastAPI(
    title="QA Agent API",
    description="Autonomous QA Agent for Test Case and Selenium Script Generation",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Startup event - log that server is starting."""
    print("=" * 60)
    print("QA Agent API Starting...")
    print(f"Port: {os.getenv('PORT', 8000)}")
    print("=" * 60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import heavy modules lazily to speed up startup
doc_processor = None
text_chunker = None
vector_store = None

def get_doc_processor():
    global doc_processor
    if doc_processor is None:
        from document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
    return doc_processor

def get_text_chunker():
    global text_chunker
    if text_chunker is None:
        from document_processor import TextChunker
        text_chunker = TextChunker(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    return text_chunker

def get_vector_store():
    global vector_store
    if vector_store is None:
        from vector_store import vector_store as vs
        vector_store = vs
    return vector_store

# Store HTML content in memory for script generation
html_content_store: Dict[str, str] = {}


class TestCaseRequest(BaseModel):
    query: str
    n_context: int = 10


class ScriptGenerationRequest(BaseModel):
    test_case: Dict[str, Any]
    html_filename: str = "checkout.html"


class TestCaseResponse(BaseModel):
    test_cases: List[Dict[str, Any]]
    raw_response: str
    sources_used: List[str]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "QA Agent API"}


@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics."""
    vs = get_vector_store()
    stats = vs.get_stats()
    return {
        "knowledge_base": stats,
        "html_files": list(html_content_store.keys())
    }


@app.post("/api/upload/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process support documents."""
    processor = get_doc_processor()
    chunker = get_text_chunker()
    vs = get_vector_store()
    
    results = []
    
    for file in files:
        try:
            content = await file.read()
            file_path = Path(file.filename)
            
            # Check if supported
            if file_path.suffix.lower() not in config.SUPPORTED_EXTENSIONS:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": f"Unsupported file type: {file_path.suffix}"
                })
                continue
            
            # Process document
            doc_data = processor.process(file_path, content)
            
            # Chunk the content
            chunks = chunker.split(
                doc_data["content"],
                metadata={
                    "source_document": doc_data["source_document"],
                    "filename": doc_data["filename"]
                }
            )
            
            # Add to vector store
            num_chunks = vs.add_documents(chunks)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "chunks_created": num_chunks
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}


@app.post("/api/upload/html")
async def upload_html(file: UploadFile = File(...)):
    """Upload the target HTML file."""
    try:
        processor = get_doc_processor()
        chunker = get_text_chunker()
        vs = get_vector_store()
        
        content = await file.read()
        file_path = Path(file.filename)
        
        # Store raw HTML content
        html_content_store[file.filename] = content.decode("utf-8", errors="ignore")
        
        # Also process and add to vector store for context
        doc_data = processor.process(file_path, content)
        chunks = chunker.split(
            doc_data["content"],
            metadata={
                "source_document": doc_data["source_document"],
                "filename": doc_data["filename"]
            }
        )
        num_chunks = vs.add_documents(chunks)
        
        return {
            "filename": file.filename,
            "status": "success",
            "chunks_created": num_chunks,
            "html_stored": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/build-knowledge-base")
async def build_knowledge_base():
    """Confirm knowledge base is built (documents already processed on upload)."""
    vs = get_vector_store()
    stats = vs.get_stats()
    return {
        "status": "success",
        "message": "Knowledge base is ready",
        "stats": stats
    }


@app.post("/api/generate/test-cases", response_model=TestCaseResponse)
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases based on user query."""
    try:
        vs = get_vector_store()
        
        # Check if knowledge base has documents
        stats = vs.get_stats()
        if stats.get("total_chunks", 0) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Knowledge base is empty. Please upload documents first."
            )
        
        from llm_client import QAAgent
        agent = QAAgent(vs)
        
        # Generate test cases
        print(f"Generating test cases for query: {request.query}")
        raw_response = agent.generate_test_cases(request.query, request.n_context)
        print(f"LLM Response received, length: {len(raw_response)}")
        
        # Parse test cases
        test_cases = agent.parse_test_cases(raw_response)
        
        # Get sources used
        context_results = vs.search(request.query, n_results=request.n_context)
        sources = list(set([
            r["metadata"].get("source_document", "unknown") 
            for r in context_results
        ]))
        
        return TestCaseResponse(
            test_cases=test_cases,
            raw_response=raw_response,
            sources_used=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error generating test cases: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/selenium-script")
async def generate_selenium_script(request: ScriptGenerationRequest):
    """Generate Selenium script for a test case."""
    try:
        vs = get_vector_store()
        
        # Get HTML content
        html_content = html_content_store.get(request.html_filename)
        if not html_content:
            # Try to get from vector store
            html_docs = vs.get_document_by_source(request.html_filename)
            if html_docs:
                html_content = "\n".join([d["content"] for d in html_docs])
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"HTML file '{request.html_filename}' not found"
                )
        
        from llm_client import QAAgent
        agent = QAAgent(vs)
        script = agent.generate_selenium_script(request.test_case, html_content)
        
        return {
            "status": "success",
            "test_case_id": request.test_case.get("test_id", "unknown"),
            "script": script
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/clear")
async def clear_knowledge_base():
    """Clear all data from the knowledge base."""
    try:
        vs = get_vector_store()
        vs.clear()
        html_content_store.clear()
        return {"status": "success", "message": "Knowledge base cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sources")
async def list_sources():
    """List all source documents in the knowledge base."""
    vs = get_vector_store()
    stats = vs.get_stats()
    return {"sources": stats.get("sources", [])}


@app.get("/api/search")
async def search_documents(query: str, n_results: int = 5):
    """Search the knowledge base."""
    vs = get_vector_store()
    results = vs.search(query, n_results)
    return {"query": query, "results": results}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )