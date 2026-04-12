"""FastAPI web application for geological interpretation agent."""

import os
from pathlib import Path
from typing import Optional, List
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.ollama_client import OllamaClient
from agents.geological_interpreter import GeologicalInterpreterAgent
from agents.programming_agent import ProgrammingAgent
from visualization.plotter import GeologicalPlotter
from utils.document_parser import AlgorithmDocumentParser

app = FastAPI(title="Geological Interpretation Agent", version="1.0.0")

# Initialize components
ollama_client = OllamaClient()
# Use BGE-M3 for better Chinese embedding support
interpreter = GeologicalInterpreterAgent(
    ollama_client,
    enable_rag=True,
    embedding_type="bge-m3"
)
programming_agent = ProgrammingAgent(ollama_client)
plotter = GeologicalPlotter()
doc_parser = AlgorithmDocumentParser()

# Initialize Chat Agent for natural language interaction
from core.chat_agent import ChatAgent
chat_agent = ChatAgent(
    base_dir=Path.cwd(),
    enable_rag=True,
    embedding_type="bge-m3"
)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Template directory
template_dir = Path(__file__).parent / "templates"


class RegionAnalysisRequest(BaseModel):
    """Request model for region analysis."""
    region_name: str
    description: Optional[str] = None
    additional_data: Optional[dict] = None


class VelocityAnalysisRequest(BaseModel):
    """Request model for velocity structure analysis."""
    structure_description: str
    depth_range_min: Optional[float] = None
    depth_range_max: Optional[float] = None
    velocity_data: Optional[List[dict]] = None


@app.get("/")
async def home():
    """Home page."""
    html_file = template_dir / "index.html"
    with open(html_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {"message": "Geological Interpretation Agent API", "version": "1.0.0"}


@app.post("/api/analyze-region")
async def analyze_region(request: RegionAnalysisRequest):
    """Analyze geological information for a region."""
    try:
        result = interpreter.analyze_region(
            region_name=request.region_name,
            description=request.description,
            additional_data=request.additional_data
        )
        return {"success": True, "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-velocity")
async def analyze_velocity_structure(request: VelocityAnalysisRequest):
    """Analyze velocity structure data."""
    try:
        depth_range = None
        if request.depth_range_min is not None and request.depth_range_max is not None:
            depth_range = (request.depth_range_min, request.depth_range_max)

        result = interpreter.analyze_velocity_structure(
            structure_description=request.structure_description,
            depth_range=depth_range,
            velocity_data=request.velocity_data
        )
        return {"success": True, "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-velocity-image")
async def upload_velocity_image(
    file: UploadFile = File(...),
    description: str = Form("")
):
    """Upload and analyze velocity structure image."""
    try:
        # Save uploaded file
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Analyze image
        result = interpreter.analyze_velocity_structure(
            structure_description=description,
            image_path=file_path
        )

        return {
            "success": True,
            "analysis": result,
            "image_path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-code")
async def generate_code(
    algorithm_doc: UploadFile = File(...),
    task_description: str = Form("")
):
    """Generate code from algorithm documentation."""
    try:
        # Save uploaded document
        doc_dir = Path("./data/algorithms")
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / algorithm_doc.filename

        with open(doc_path, "wb") as f:
            f.write(await algorithm_doc.read())

        # Generate code
        code = programming_agent.generate_code_from_markdown(
            markdown_path=doc_path,
            task_description=task_description if task_description else None
        )

        return {
            "success": True,
            "code": code,
            "algorithm_doc": str(doc_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/execute-code")
async def execute_code(code: str = Form(...)):
    """Execute generated code."""
    try:
        result = programming_agent.execute_code(code=code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run-inversion")
async def run_inversion(
    algorithm_doc: UploadFile = File(...),
    input_data: UploadFile = File(...),
    parameters: Optional[str] = Form(None)
):
    """Run inversion based on algorithm documentation."""
    try:
        # Save files
        doc_dir = Path("./data/algorithms")
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / algorithm_doc.filename

        with open(doc_path, "wb") as f:
            f.write(await algorithm_doc.read())

        data_dir = Path("./data/input")
        data_dir.mkdir(parents=True, exist_ok=True)
        data_path = data_dir / input_data.filename

        with open(data_path, "wb") as f:
            f.write(await input_data.read())

        # Parse parameters
        params = None
        if parameters:
            import json
            params = json.loads(parameters)

        # Run inversion
        result = programming_agent.run_inversion(
            algorithm_doc=doc_path,
            input_data_file=data_path,
            parameters=params
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plot/velocity-profile")
async def plot_velocity_profile_example():
    """Generate example velocity profile plot."""
    try:
        # Create example data
        depths = np.linspace(0, 50, 100)
        velocities = 5.0 + 0.1 * depths + np.random.randn(100) * 0.2

        plot_path = plotter.plot_velocity_profile(
            depths=depths,
            velocities=velocities,
            title="Example Velocity Profile"
        )

        return FileResponse(str(plot_path), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    ollama_status = ollama_client.check_connection()
    return {
        "status": "healthy" if ollama_status else "degraded",
        "ollama_connected": ollama_status
    }


# RAG API Endpoints
@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), doc_id: Optional[str] = Form(None)):
    """Upload PDF to RAG knowledge base."""
    try:
        # Save uploaded file
        upload_dir = Path("./data/uploads/pdfs")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Upload to RAG
        result = interpreter.upload_pdf_to_rag(file_path, doc_id)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/stats")
async def rag_stats():
    """Get RAG database statistics."""
    try:
        stats = interpreter.get_rag_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rag/documents")
async def rag_documents():
    """List all documents in RAG database."""
    try:
        documents = interpreter.list_rag_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/rag/document/{doc_id}")
async def delete_rag_document(doc_id: str):
    """Delete a document from RAG database."""
    try:
        success = interpreter.delete_rag_document(doc_id)
        return {"success": success, "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/search")
async def search_rag(query: str = Form(...), n_results: int = Form(5)):
    """Search geological literature."""
    try:
        results = interpreter.search_literature(query, n_results)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat_command(message: str = Form(...)):
    """Process natural language command."""
    try:
        result = chat_agent.process_command(message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
