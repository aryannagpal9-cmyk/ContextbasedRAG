import os
from groq import Groq

class RAGEngine:
    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            self.client = None
            print("Warning: GROQ_API_KEY not set. RAG will fail.")
        else:
            self.client = Groq(api_key=key)

    def answer_question(self, question: str, context: list[dict], structured_context: str = "") -> dict:
        """
        Generates an answer using Llama 3.1 8B with strict brevity and relevance constraints.
        """
        from app.core.logging_config import logger
        logger.info(f"RAG Engine: Answering question: {question}")
        
        # Format context
        context_str = ""
        for i, item in enumerate(context):
            meta = item['metadata']
            context_str += f"[Source {i+1}] (Page {meta.get('page_number')}): {meta.get('text')}\n\n"

        system_prompt = """
            You are the AI assistant for Ultra Doc-Intelligence.
            
            CORE DIRECTIVES:
            1. BREVITY: Keep answers short, crisp, and direct. No fluff.
            2. RELEVANCE: Answer ONLY what is asked. Do not provide extra information or context unless vital.
            3. GROUNDING: Use ONLY the provided document context.
            4. ACCURACY: If the answer isn't in the text, say you don't know.
            """

        user_prompt = f"""
            ### DOCUMENT CONTEXT
            {context_str}
            
            {structured_context}
            ---
            ### USER QUESTION
            {question}
            ---
            ### INSTRUCTIONS
            - Provide a short, crisp answer (max 3 sentences).
            - Focus strictly on answering the specific query.
            - Use the context provided above.
            """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0
            )
            logger.info("RAG completion successful")
            return {
                "answer": completion.choices[0].message.content,
                "sources": context
            }
        except Exception as e:
            logger.error(f"RAG Engine error: {e}", exc_info=True)
            return {
                "answer": "I encountered an error while generating the answer.",
                "error": str(e),
                "sources": []
            }
