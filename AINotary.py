# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import hashlib
from genlayer import *

class AINotary(gl.Contract):
    records: TreeMap[str, str]
    admin: Address

    def __init__(self) -> None:
        self.admin = gl.message.sender_address

    @gl.public.write
    def notarize_document(self, doc_id: str, document_text: str, expected_claim: str) -> str:
        assert doc_id not in self.records, "Document record already exists."

        # Cryptographically bind the analyzed content to a hash
        doc_hash = "0x" + hashlib.sha256(document_text.encode('utf-8')).hexdigest()

        def verify_document() -> str:
            prompt = f"""
            You are an automated cryptographic and compliance notary agent.
            Analyze the following document text and verify whether it validly fulfills the expected claim: "{expected_claim}".

            Document Text:
            ---
            {document_text}
            ---

            Evaluate thoroughly. Return your evaluation strictly in valid JSON format with the following keys:
            {{
                "is_valid": boolean,
                "confidence_score": float,
                "reasoning": string,
                "extracted_entities": list<string>
            }}
            Do not include any markdown formatting, backticks, or extra text outside the JSON object.
            """
            return gl.nondet.exec_prompt(prompt).replace("```json", "").replace("```", "").strip()

        consensus_result = gl.eq_principle.strict_eq(verify_document)
        
        try:
            parsed_result = json.loads(consensus_result)
        except Exception:
            parsed_result = {
                "is_valid": False, 
                "confidence_score": 0.0, 
                "reasoning": "Failed to parse consensus JSON structure.", 
                "extracted_entities": []
            }

        record = {
            "doc_hash": doc_hash,
            "expected_claim": expected_claim,
            "is_valid": parsed_result.get("is_valid", False),
            "confidence": parsed_result.get("confidence_score", 0.0),
            "reasoning": parsed_result.get("reasoning", ""),
            "entities": parsed_result.get("extracted_entities", []),
        }

        # Store as a serialized JSON string in TreeMap[str, str]
        self.records[doc_id] = json.dumps(record)
        return json.dumps(record)

    @gl.public.view
    def get_notary_record(self, doc_id: str) -> dict:
        assert doc_id in self.records, "Document record not found."
        return json.loads(self.records[doc_id])
