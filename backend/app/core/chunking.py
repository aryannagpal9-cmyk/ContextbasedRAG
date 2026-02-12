import re
from typing import List, Dict, Any

class ContentChunker:
    def __init__(self):
        self.section_keywords = {
            "header": ["bill of lading", "rate confirmation", "invoice", "shipment instructions"],
            "parties": ["shipper", "consignee", "carrier", "bill to", "remit to"],
            "schedule": ["pickup", "delivery", "date", "time", "appointment"],
            "rate": ["rate", "charge", "amount", "total", "currency"],
            "equipment": ["truck", "trailer", "container", "weight", "dimensions"],
            "terms": ["terms", "conditions", "liability", "insurance"],
        }

    def _identify_section(self, text: str) -> str:
        text_lower = text.lower()
        for section, keywords in self.section_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return section
        return "misc"

    def chunk(self, parsed_document) -> List[Dict[str, Any]]:
        """
        Chunks the parsed document into semantic, context-aware blocks.
        """
        chunks = []
        current_heading = ""
        current_chunk = None
        
        for item, level in parsed_document.iterate_items():
            # 1. Context Tracking (Headings)
            # Identifying heading items by string representation or attribute
            item_type = str(type(item))
            if "Heading" in item_type or "SectionHeader" in item_type:
                # Update context
                current_heading = item.text.strip() if hasattr(item, "text") else current_heading
                continue

            # 2. Text Handling
            if hasattr(item, "text") and item.text:
                text = item.text.strip()
                if not text:
                    continue
                
                section = self._identify_section(text)
                page_no = getattr(item, "page_no", 1)
                
                # Semantic Merging: Join consecutive items of same section and page
                if current_chunk and current_chunk["section_type"] == section and current_chunk["page_number"] == page_no:
                    current_chunk["text"] += "\n" + text
                else:
                    # Finalize previous chunk
                    if current_chunk:
                        # Prepend context if exists
                        if current_heading:
                            current_chunk["text"] = f"[{current_heading}] {current_chunk['text']}"
                        chunks.append(current_chunk)
                    
                    # Start new chunk
                    current_chunk = {
                        "text": text,
                        "section_type": section,
                        "page_number": page_no
                    }
             
            # 3. Table Handling
            elif "Table" in item_type:
                # Finalize pending text chunk
                if current_chunk:
                    if current_heading:
                        current_chunk["text"] = f"[{current_heading}] {current_chunk['text']}"
                    chunks.append(current_chunk)
                    current_chunk = None
                
                try:
                    df = item.export_to_dataframe()
                    md_text = df.to_markdown(index=False)
                    page_no = getattr(item, 'page_no', 1)
                    table_text = f"Table Data (Page {page_no}):\n{md_text}"
                    
                    # Prepend context to table
                    if current_heading:
                         table_text = f"[{current_heading}] {table_text}"
                         
                    chunks.append({
                        "text": table_text,
                        "section_type": "rate",
                        "page_number": page_no
                    })
                except:
                    continue

        # Finalize last chunk
        if current_chunk:
            if current_heading:
                current_chunk["text"] = f"[{current_heading}] {current_chunk['text']}"
            chunks.append(current_chunk)
            
        return chunks
