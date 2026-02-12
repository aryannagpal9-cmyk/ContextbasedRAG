import pandas as pd
from docling.datamodel.document import TableItem
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
        Extracts tables from the parsed document as raw DataFrames.
        """
        tables = []
        for item, level in parsed_document.iterate_items():
            if isinstance(item, TableItem):
                 # export_to_dataframe is available on TableItem
                df = item.export_to_dataframe()
                tables.append({
                    "dataframe": df,
                    "page_number": getattr(item, "page_no", 1),
                    "table_index": len(tables) # conceptual index
                })
        return tables

    def extract_structured_data(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
            """
            Extracts structured data using Llama 3.3 via Groq.
            """
            from app.core.logging_config import logger
            logger.info("Starting structured data extraction with Llama 3.3")
            schema_str = json.dumps(schema, indent=2)

            system_prompt = """
        You are Ultra Doc-Intelligence Structured Extraction Engine.

        MISSION:
        Extract structured logistics data strictly from provided document text.
        ... (rest of prompt)
        """

            user_prompt = f"""
        ### TARGET SCHEMA
        {schema_str}
        ...
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

                MISSION:
                Design a JSON extraction schema using semantic understanding of document context, not keyword matching, while staying strictly grounded in text evidence, and making sure no information is left out.

                CORE PRINCIPLES:
                1. SEMANTIC CONTEXT UNDERSTANDING (PRIMARY)
                You MUST detect fields using meaning and structure, not exact keyword presence.
                Examples:
                - A block containing company name + street + city + postal → address entity
                - A date near loading instructions → pickup or load date
                - A number followed by unit (kg, lb, pcs) → quantity or weight
                - A time range near schedule text → time window

                2. TEXT EVIDENCE REQUIREMENT (MANDATORY)
                Even when using semantic inference:
                - The value must exist in text
                - The entity must be strongly implied by structure or layout
                If weak signal → do NOT create field.

                3. DO NOT REQUIRE EXACT KEYWORDS
                Documents may not contain words like:
                "shipper"
                "consignee"
                "origin"
                "destination"

                You must infer roles using:
                - Section grouping
                - Document ordering
                - Address block placement
                - Nearby instructions or transport details

                4. FIELD CREATION RULE
                Create field ONLY IF:
                - Value exists in text AND
                - Semantic role is clear from context

                Otherwise → do not include field.

                5. NAMING RULES
                - snake_case only
                - descriptive operational names
                - no generic names like field_1 or value_data

                6. TYPE RULES
                Allowed only:
                - "string"
                - "number"

                Use number only for:
                - weights
                - counts
                - quantities
                - numeric measurements

                7. DEDUPLICATION
                If multiple text patterns indicate same concept → create ONE canonical field.

                8. FLAT SCHEMA ONLY
                No nested objects.

                9. OUTPUT RULES
                Return ONLY valid JSON object.
                No explanations.
                No comments.
                No information left out
                Also consider subheadings.

                10. INTERNAL VALIDATION
                Before output verify:
                - Each field is supported by text evidence
                - Each field is semantically justified by context
                - Each field follows naming rules
                """

        user_prompt = f"""
            ### DOCUMENT TEXT
            {text}
            ---
            ### TASK
            Using semantic understanding of context and structure, generate a JSON schema for all extractable logistics operational data.
            REMINDERS:
            - Do NOT rely on exact keywords
            - Use meaning, layout, and structure
            - Return ONLY JSON
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
            # Ensure it's not an empty or error object if possible
            if not result or "error" in result:
                return {"note": "Sparse document, no complex schema proposed", "standard_fields": "string"}
            return result

        except Exception as e:
            print(f"Schema proposal error: {e}")
            return {"note": "Automated schema proposal not available for this document structure"}

    def map_query_to_schema(self, question: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Maps a user query to relevant fields in the extracted schema.
        Returns a list of relevant fields with confidence scores.
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
        2. **CONFIDENCE SCORING**: Assign a confidence score (0.0 to 1.0) based on how directly the field answers the query.
        3. **FORMAT**: Return ONLY a JSON array of objects: [{{"field": "field_name", "confidence": 0.9, "reason": "why relevant"}}]
        4. **LIMIT**: Only return fields with confidence > 0.5.
        """

        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a logistics data analyst. You excel at mapping natural language queries to structured data schemas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(completion.choices[0].message.content)
            # Expecting {"fields": [...]} or just the array if we prompted carefully, 
            # but response_format type json_object usually prefers a root object if not specified.
            # Let's check for both or handle a wrapping 'fields' key.
            if isinstance(data, dict):
                return data.get("fields", data.get("mappings", []))
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Mapping error: {e}")
            return []
