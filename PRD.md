# PRD: Ultra Doc-Intelligence

## 1. Executive Summary
Ultra Doc-Intelligence is a high-precision RAG (Retrieval-Augmented Generation) platform designed for complex logistics documents (Rate Confirmations, BOLs, Invoices). It prioritizes deterministic confidence and role-based reasoning to ensure audit-grade accuracy.

## 2. Target Audience
- Logistics Auditors
- Freight Forwarders
- Supply Chain Analysts

## 3. Key Problems Solved
- **Role Confusion**: Distinguishing between financial payers (Bill-To) and operational entities (Carrier).
- **Template Noise**: Ignoring platform headers and "contracted via" branding.
- **Confidence Calibration**: Moving away from "hallucinated" LLM confidence scores to mathematical similarity metrics.

## 4. Feature Requirements

### 4.1. Intelligent Ingestion
- Support for PDF, DOCX, and HTML.
- Layout-preserving parsing that understands tables, headers, and semantic groups.

### 4.2. Advanced RAG Flow
- **Semantic Chunking**: Context-aware text blocks that include hierarchical heading info.
- **Weighted Confidence**: 50/50 scoring between Schema Mapping (Contextual) and Vector Search (Semantic).
- **Hard Refusal**: Automatic denial of answers if confidence falls below 45% threshold.

### 4.3. Structured Extraction
- Automatic schema proposal based on document content.
- Precise extraction of rates, dates, and entities into JSON format.

### 4.4. User Experience
- **Glassmorphism UI**: Premium dark-mode aesthetic.
- **Intelligence Transparency**: Expandable details for every answer showing internal metrics and sources.
- **Real-time Processing**: Visual feedback for multi-stage document processing.

## 5. Success Metrics
- **Zero Hallucination Rate**: Correct refusal on out-of-document queries.
- **Role Accuracy**: 95%+ accuracy in identifying "Financially Responsible" entities.
- **Efficiency**: Reduction in manual audit time by 70%.
