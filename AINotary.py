import json
import genlayer.std as gl


class AIContentNotary(gl.Contract):
    # State tracking mappings and storage
    records: gl.TreeMap[str, str]  # content_hash -> JSON verification record
    statuses: gl.TreeMap[str, str]  # content_hash -> STATUS (VERIFIED/FLAGGED/REJECTED)
    submission_count: u256

    def __init__(self):
        self.submission_count = 0

    @gl.public.write
    def verify_and_notarize(
        self,
        content_hash: str,
        text_content: str,
        claimed_author: str,
        source_url: str,
    ) -> str:
        # 1. State check to prevent duplicate verification
        if self.statuses.has(content_hash):
            return f"Hash {content_hash} already notarized with status: {self.statuses.get(content_hash)}"

        # 2. Define validator evaluation task using GenLayer Equivalence Principle
        # GenLayer Consensus: Uses prompt_non_comparative to validate output against criteria
        task_prompt = f"""
        Analyze the following text for authenticity, originality, and AI-generation markers:
        
        Claimed Author: {claimed_author}
        Source URL: {source_url}
        Text: "{text_content}"
        
        Respond ONLY with a valid JSON object matching this exact schema:
        {{
            "authenticity_score": <integer 0-100>,
            "is_ai_generated": <boolean>,
            "flagged_issues": [<string>],
            "reasoning": "<short summary>"
        }}
        """

        criteria_rules = """
        Output must be valid JSON matching the exact schema provided.
        authenticity_score must be an integer between 0 and 100.
        is_ai_generated must be a boolean.
        reasoning must accurately summarize text authenticity.
        """

        # Execute non-deterministic consensus across validators
        raw_result = gl.eq_principle.prompt_non_comparative(
            input=task_prompt,
            task="Evaluate text authenticity and generate structured json verdict.",
            criteria=criteria_rules,
        )

        # 3. Parse JSON verdict and execute consequential state transitions
        try:
            verdict = json.loads(raw_result)
            score = int(verdict.get("authenticity_score", 0))

            # Consequential state transition logic based on threshold
            if score >= 75:
                status = "VERIFIED"
            elif score >= 40:
                status = "FLAGGED"
            else:
                status = "REJECTED"

            record_payload = {
                "content_hash": content_hash,
                "author": claimed_author,
                "source_url": source_url,
                "authenticity_score": score,
                "status": status,
                "verdict_details": verdict,
                "submitted_by": str(gl.message.sender),
            }

            # 4. Storage updates (only reached after consensus)
            self.statuses.set(content_hash, status)
            self.records.set(content_hash, json.dumps(record_payload))
            self.submission_count += 1

            return status

        except Exception as e:
            # Fallback state for parsing failures
            self.statuses.set(content_hash, "FAILED_EVALUATION")
            return "FAILED_EVALUATION"

    @gl.public.view
    def get_notary_status(self, content_hash: str) -> str:
        if self.statuses.has(content_hash):
            return self.statuses.get(content_hash)
        return "UNVERIFIED"

    @gl.public.view
    def get_notary_record(self, content_hash: str) -> str:
        if self.records.has(content_hash):
            return self.records.get(content_hash)
        return "{}"
