"""
MCP Server for genpark-ast-diff-semantic-pr-reviewer-skill
Standard JSON-RPC 2.0 protocol over stdio.
"""

import sys
import json
from client import SemanticPRReviewerClient

client = SemanticPRReviewerClient()

def handle_request(req):
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "review_pr_diff",
                        "description": "Perform AST-level semantic diff review of Python code.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "old_code": {"type": "string", "description": "Baseline code"},
                                "new_code": {"type": "string", "description": "Proposed PR code"}
                            },
                            "required": ["old_code", "new_code"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "review_pr_diff":
            res = client.review_diff(args.get("old_code", ""), args.get("new_code", ""))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
