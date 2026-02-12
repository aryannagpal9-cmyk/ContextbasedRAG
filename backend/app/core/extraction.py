import pandas as pd
from typing import List, Dict, Any, Optional
import os
from groq import Groq
import json

class DataExtractor:
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            self.client = None
            print("Warning: GROQ_API_KEY not set. Structured extraction will fail.")
        else:
            self.client = Groq(api_key=key)

    def extract_table_data(self, parsed_document) -> List[Dict[str, Any]]:
        """
        Extracts tables from the parsed document.
        """
        tables = []
        for item, level in parsed_document.iterate_items():
            if item.type == "table":
                df = item.metadata.get("df")
                if df is not None:
                    tables.append({
                        "dataframe": df,
                        "page_number": item.page_no,
                        "table_index": len(tables)
                    })
        return tables

    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structured data using Llama 3.3 via Groq in JSON format.
        """
        from app.core.logging_config import logger
        logger.info("Starting structured data extraction with Llama 3.3")
        schema_str = json.dumps(schema, indent=2)

        system_prompt = """
        You are Ultra Doc-Intelligence Structured Extraction Engine.
        MISSION: Extract structured logistics data strictly from provided document text in JSON format.
        """

        user_prompt = f"""
        ### TARGET SCHEMA
        {schema_str}
        
        ### TASK
        Extract values for the above schema from the text below. 
        Return the result as a raw JSON object.
        
        ### DOCUMENT TEXT
        {text}
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            result = json.loads(completion.choices[0].message.content)
            logger.info("Structured extraction completed successfully")
            return result

        except Exception as e:
            logger.error(f"Extraction error: {e}", exc_info=True)
            return {}

    def propose_schema(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text and proposes a JSON schema for extraction.
        """
        system_prompt = """
        You are Ultra Doc-Intelligence Schema Design Engine.
        MISSION: Design a JSON extraction schema using semantic understanding of document context.
        OUTPUT: Return only a valid JSON object defining the schema (field_name: type).
        """

        user_prompt = f"""
        ### DOCUMENT TEXT
        {text}
        ---
        ### TASK
        Generate a JSON schema for all extractable logistics operational data found in the text.
        Return ONLY the raw JSON object.
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            result = json.loads(completion.choices[0].message.content)
            if not result or "error" in result:
                return {"note": "Sparse document, no complex schema proposed", "standard_fields": "string"}
            return result

        except Exception as e:
            print(f"Schema proposal error: {e}")
            return {"note": "Automated schema proposal not available for this document structure"}

    def map_query_to_schema(self, question: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Maps a user query to relevant fields in the extracted schema in JSON format.
        """
        schema_keys = list(schema.keys())
        if not schema_keys:
            return []

        prompt = f"""
        Analyze the user's question and determine which fields from the provided document schema are relevant for answering it.
        
        ### SCHEMA FIELDS:
        {json.dumps(schema_keys, indent=2)}
        
        ### USER QUESTION:
        {question}
        
        ### REQUIREMENTS:
        1. **SEMANTIC MATCHING**: Identify fields that semantically relate to the question.
        2. **CONFIDENCE SCORING**: Assign a confidence score (0.0 to 1.0).
        3. **FORMAT**: Return ONLY a JSON object: {{"fields": [{{"field": "name", "confidence": 0.9, "reason": "why relevant"}}]}}
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a logistics data analyst. You excel at mapping natural language queries to structured data schemas. Return JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            if isinstance(data, dict):
                return data.get("fields", data.get("mappings", []))
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Mapping error: {e}")
            return []
