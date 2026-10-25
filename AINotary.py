# v0.3.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import genlayer.std as gl


class AIContentNotary(gl.Contract):
    # Storage mappings and variables
    records: gl.TreeMap[str, str]
    statuses: gl.TreeMap[str, str]
    submission_count: int

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
        # 1. Prevent duplicate verification
        if self.statuses.has(content_hash):
            return f"Hash {content_hash} already notarized with status: {self.statuses.get(content_hash)}"

        # 2. Build task evaluation payload
        def evaluate_content() -> str:
            return f"""
            Analyze the following text for authenticity, originality, and AI-generation markers:
            
            Claimed Author: {claimed_author}
            Source URL: {source_url}
            Text: "{text_content}"
            
            Respond ONLY with a valid JSON object matching this exact schema:
            {{
                "authenticity_score": 85,
                "is_ai_generated": false,
                "flagged_issues": [],
                "reasoning": "Text appears human written with consistent tone."
            }}
            """

        task_desc = "Evaluate text authenticity and generate structured json verdict."
        criteria_rules = """
        Output must be valid JSON matching the exact schema provided.
        authenticity_score must be an integer between 0 and 100.
        is_ai_generated must be a boolean.
        reasoning must accurately summarize text authenticity.
        """

        # 3. GenLayer Equivalence Principle consensus
        raw_result = gl.eq_principle.prompt_non_comparative(
            evaluate_content,
            task=task_desc,
            criteria=criteria_rules,
        )

        # 4. Parse JSON verdict and execute consequential state transitions
        try:
            verdict = json.loads(str(raw_result))
            score = int(verdict.get("authenticity_score", 0))

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

            # 5. Commit to contract state
            self.statuses.set(content_hash, status)
            self.records.set(content_hash, json.dumps(record_payload))
            self.submission_count += 1

            return status

        except Exception:
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
