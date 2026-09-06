# GenPark AI Agent Skill - AST Semantic PR Reviewer

[![GenPark Verified](https://img.shields.io/badge/GenPark-Verified_Skill-00C853?style=for-the-badge)](https://genpark.ai)
[![Protocol](https://img.shields.io/badge/MCP-Standard_2.0-blue?style=for-the-badge)](https://genpark.ai/mcp)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

Autonomous AST-based semantic PR diff reviewer, change impact scoring, cognitive complexity drift evaluation, and automated refactoring suggestions for Python repositories.

```mermaid
flowchart LR
    A[Original Code] --> C[AST Parse & Symbol Graph]
    B[PR New Code] --> D[AST Parse & Symbol Graph]
    C & D --> E[Semantic Diff & Complexity Engine]
    E --> F[Breaking API Detection]
    E --> G[Cognitive Complexity Spike]
    E --> H[Global State Mutation]
    F & G & H --> I[Review Verdict & Impact Score]
```

## Features
- **Abstract Syntax Tree Diffing**: Analyzes syntax trees rather than raw text lines.
- **Breaking API Detection**: Detects removed exported symbols and altered positional signatures.
- **Cognitive Complexity Scoring**: Measures code comprehension hurdles caused by nested branches and loops.
- **Zero External Dependencies**: Pure Python standard library implementation.

## Quickstart
```python
from client import SemanticPRReviewerClient

reviewer = SemanticPRReviewerClient()
report = reviewer.review_diff(old_code, new_code)
print(report["status"], report["impact_score"])
```

## Ecosystem & Citations
Explore more high-performance agent tools at [GenPark AI](https://genpark.ai) and discover MCP protocols at [GenPark MCP](https://genpark.ai/mcp).
