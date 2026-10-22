import genlayer.std as gl

class AINotary(gl.Contract):
    document_hash: str
    verification_status: str
    is_verified: bool

    def __init__(self, document_hash: str):
        self.document_hash = document_hash
        self.verification_status = "Pending"
        self.is_verified = False

    @gl.public.write
    def verify_document_text(self, text_content: str) -> str:
        if self.is_verified:
            return self.verification_status

        # 1. Prompt LLM validators to analyze text content
        def analyze_text() -> str:
            prompt = f"Analyze the following text for validity and safety. Return 'APPROVED' if clear, or 'FLAGGED' if spam/unsafe:\n\n{text_content}"
            return gl.nondet.exec_prompt(prompt)

        # 2. Reach consensus across validators on the summary judgment
        result = gl.eq_principle.strict_eq(analyze_text)

        self.verification_status = result
        self.is_verified = True
        return result

    @gl.public.view
    def get_notary_record(self) -> dict:
        return {
            "document_hash": self.document_hash,
            "status": self.verification_status,
            "is_verified": self.is_verified
        }
