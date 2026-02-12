from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import shutil
import os
import uuid

# Import core modules
from app.core.parsing import DocumentParser
from app.core.chunking import ContentChunker
from app.core.embedding import EmbeddingModel
from app.core.vector_store import VectorStore
from app.core.extraction import DataExtractor
from app.core.rag import RAGEngine

router = APIRouter()

# Global instances (simplified for MVP)
parser = DocumentParser()
chunker = ContentChunker()
embedder = EmbeddingModel()
vector_store = VectorStore()
extractor = DataExtractor()
rag_engine = RAGEngine()

# In-memory document storage for parsed objects (needed for table extraction)
# In production, this would be a database or object store
document_store = {}

class AskRequest(BaseModel):
    question: str
    document_id: str

class ExtractionRequest(BaseModel):
    document_id: str
    schema_definition: Optional[Dict[str, Any]] = None

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Save file temporarily
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        temp_path = f"temp_{file_id}{file_ext}"
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 1. Parse
        parsed_doc = parser.parse(temp_path)
        
        # 2. Chunk
        chunks = chunker.chunk(parsed_doc)
        
        # 3. Embed
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedder.embed(texts)
        
        # 4. Add to Vector Store
        # Add metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk["document_id"] = file_id
            # Ensure metadata matches what vector_store expects
            
        vector_store.add_documents(embeddings, chunks)
        
        # Store parsed document and extraction results
        document_store[file_id] = {
            "parsed_doc": parsed_doc,
            "extraction_results": None, # Will update below
            "proposed_schema": None
        }
        
        # 5. AUTOMATION: Propose Schema & Extract
        # Aggregate text for LLM
        full_text = ""
        for item, level in parsed_doc.iterate_items():
            if hasattr(item, "text") and item.text:
                full_text += item.text + "\n"
        
        # Propose Schema
        proposed_schema = extractor.propose_schema(full_text)
        
        # Extract Structured Data
        extraction_results = {}
        if proposed_schema and "error" not in proposed_schema:
            extraction_results = extractor.extract_structured_data(full_text[:30000], proposed_schema)

        # Extraction Tables (Deterministic)
        tables = extractor.extract_table_data(parsed_doc)
        serialized_tables = []
        for tbl in tables:
            serialized_tables.append({
                "page": tbl["page_number"],
                "data": tbl["dataframe"].to_dict(orient="records")
            })

        # Store results
        document_store[file_id]["extraction_results"] = extraction_results
        document_store[file_id]["proposed_schema"] = proposed_schema

        # Cleanup
        os.remove(temp_path)
        
        return {
            "document_id": file_id, 
            "message": "Document uploaded and processed successfully",
            "chunks_count": len(chunks),
            "chunks": chunks,
            "proposed_schema": proposed_schema,
            "extraction": {
                "tables": serialized_tables,
                "structured_data": extraction_results
            }
        }
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/ask")
async def ask_question(request: AskRequest):
    try:
        # 1. Embed question 
        # Note: BGE-small requires instruction for queries? 
        # "Represent this sentence for searching relevant passages: "
        # Checking BGE usage... usually "Represent this sentence for searching relevant passages: " is for query.
        # But SentenceTransformer handles it if configured, or we prepend.
        # For BGE-small-en-v1.5, instruction is not strictly mandatory but recommended for asymmetric tasks.
        # Keeping it simple for now, can refine if retrieval is poor.
        
        q_embedding = embedder.embed([request.question])
        
        # 2. Search
        # We assume one document for now, or we filter by document_id if we supported multiple.
        # Our vector store doesn't explicitly filter by doc_id in search yet, 
        # but for Single-Document scope (PRD #4), we might just clear the store or filter.
        # Let's filter manually in search results if needed, or rely on the user only uploading one doc for the demo.
        # PRD says "Single-document scope only". 
        
        results = vector_store.search(q_embedding.flatten(), k=5)
        
        # Filter by document_id if we have multiple in store (good practice)
        doc_results = [r for r in results if r['metadata'].get('document_id') == request.document_id]
        
        if not doc_results:
             return {"answer": "I'm sorry, I cannot find sufficient information in the document to answer that accurately.", "sources": []}

        # 3. Intelligent Mapping (Query to Schema)
        doc_data = document_store.get(request.document_id)
        structured_context = ""
        mappings = []
        schema_score = 0.0
        
        if doc_data and doc_data.get("extraction_results"):
            schema_keys = list(doc_data["extraction_results"].keys())
            if schema_keys:
                # Deterministic similarity scoring via embeddings
                scores = embedder.get_similarity_scores(request.question, schema_keys)
                
                # Zip and filter
                for key, score in zip(schema_keys, scores):
                    if score > 0.4: # Mapping candidate threshold
                        val = doc_data["extraction_results"].get(key)
                        if val is not None:
                            mappings.append({
                                "field": key,
                                "confidence": float(score),
                                "reason": "Semantic similarity (embedding distance)"
                            })
                
                # Sort by confidence
                mappings.sort(key=lambda x: x["confidence"], reverse=True)
                mappings = mappings[:3] # Top 3 matches
                
                if mappings:
                    schema_score = mappings[0]["confidence"]
                    structured_context = "\n### IDENTIFIED STRUCTURED DATA (HIGH CONFIDENCE):\n"
                    for m in mappings:
                        structured_context += f"- {m['field']}: {doc_data['extraction_results'].get(m['field'])} (Score: {m['confidence']:.2f})\n"

        # 4. Final Confidence Calculation
        # Semantic Score from Vector results
        semantic_score = doc_results[0]["score"] if doc_results else 0.0
        
        # Weighted Confidence (50/50)
        # Normalize semantic score if needed (FAISS scores are often distance-based, 
        # but BGE small usually gives cosine similarity > 0.6 for good matches)
        final_confidence = (schema_score * 0.5) + (semantic_score * 0.5)
        
        # 5. Refusal Logic
        if final_confidence < 0.45: # Adjusted threshold for reliability
            return {
                "answer": "I'm sorry, I cannot find sufficient information in the document with enough confidence to answer that accurately.",
                "sources": [],
                "confidence_metrics": {
                    "schema_score": float(schema_score),
                    "semantic_score": float(semantic_score),
                    "final_confidence": float(final_confidence),
                    "status": "refused"
                }
            }

        # 6. RAG
        context_items = doc_results[:5]
        response = rag_engine.answer_question(request.question, context_items, structured_context=structured_context)
        
        # Add metrics for UI transparency
        response["mappings"] = mappings
        response["confidence_metrics"] = {
            "schema_score": float(schema_score),
            "semantic_score": float(semantic_score),
            "final_confidence": float(final_confidence),
            "status": "accepted"
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@router.post("/extract")
async def extract_structured_data(request: ExtractionRequest):
    try:
        doc_id = request.document_id
        if doc_id not in document_store:
            raise HTTPException(status_code=404, detail="Document not found")
            
        doc_data = document_store[doc_id]
        parsed_doc = doc_data["parsed_doc"] if isinstance(doc_data, dict) else doc_data
        
        # 1. Table Extraction (Deterministic)
        tables = extractor.extract_table_data(parsed_doc)
        
        # 2. Schema Extraction (LLM)
        structured_data = {}
        if request.schema_definition:
            # Re-collect text from doc
            full_text = ""
            for item, level in parsed_doc.iterate_items():
                 if hasattr(item, "text") and item.text:
                     full_text += item.text + "\n"
                     
            structured_data = extractor.extract_structured_data(full_text[:30000], request.schema_definition)

        # Serialize DataFrames for JSON response
        serialized_tables = []
        for tbl in tables:
            serialized_tables.append({
                "page": tbl["page_number"],
                "data": tbl["dataframe"].to_dict(orient="records")
            })

        return {
            "tables": serialized_tables,
            "structured_data": structured_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@router.post("/propose_schema")
async def propose_schema(request: ExtractionRequest):
    try:
        doc_id = request.document_id
        if doc_id not in document_store:
            raise HTTPException(status_code=404, detail="Document not found")
            
        doc_data = document_store[doc_id]
        parsed_doc = doc_data["parsed_doc"] if isinstance(doc_data, dict) else doc_data
        
        # Aggregate text (similar to extract)
        full_text = ""
        for item, level in parsed_doc.iterate_items():
                if hasattr(item, "text") and item.text:
                    full_text += item.text + "\n"
                    
        # Generate schema
        schema = extractor.propose_schema(full_text)
        
        return schema
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema proposal failed: {str(e)}")
