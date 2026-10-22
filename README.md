# GenLayer AI Notary & Content Verification Primitive

An Intelligent Contract written for GenLayer that leverages LLM validators to verify and notarize text content on-chain.

## Features
- **Nondeterministic Execution:** Uses `gl.nondet.exec_prompt` to allow LLM validators to assess raw text input for safety or validity.
- **Equivalence Principle Consensus:** Applies `gl.eq_principle.strict_eq` to ensure all validating nodes reach consensus on the returned verdict before writing state to the ledger.
- **On-Chain Record:** Persists verification status alongside document hash for immutable lookup.

## How to Deploy in GenLayer Studio
1. Copy `AINotary.py` into [GenLayer Studio](https://studio.genlayer.com).
2. Instantiate the contract with an initial `document_hash` string.
3. Call `verify_document_text(text_content)` to process text through validator consensus.
4. Call `get_notary_record()` to view stored status.
