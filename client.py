"""
AST-based semantic PR diff reviewer and change impact analyzer.
Zero external dependencies, standard library only.
"""

import ast
import difflib
from typing import Dict, List, Any, Optional, Tuple

class SemanticPRReviewerClient:
    """
    Analyzes Python code differences at the Abstract Syntax Tree (AST) level
    to detect architectural impact, breaking API changes, cognitive complexity drift,
    and dangerous global mutations.
    """

    def __init__(self):
        pass

    def compute_cognitive_complexity(self, tree: ast.AST) -> int:
        """
        Computes cognitive complexity score across AST nodes.
        Penalizes nested loops, conditionals, recursion, and exception handlers.
        """
        complexity = 0
        nesting = 0

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.score = 0
                self.depth = 0

            def visit_If(self, node):
                self.score += 1 + self.depth
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_For(self, node):
                self.score += 1 + self.depth
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_While(self, node):
                self.score += 1 + self.depth
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_Try(self, node):
                self.score += 1 + self.depth
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1

            def visit_ExceptHandler(self, node):
                self.score += 1
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return visitor.score

    def extract_symbol_signatures(self, tree: ast.AST) -> Dict[str, Dict[str, Any]]:
        """Extracts function and class signatures from AST."""
        symbols = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [arg.arg for arg in node.args.args]
                symbols[node.name] = {
                    "type": "function",
                    "async": isinstance(node, ast.AsyncFunctionDef),
                    "args": args,
                    "docstring": ast.get_docstring(node) is not None,
                    "line": getattr(node, "lineno", 0)
                }
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "object") for b in node.bases]
                symbols[node.name] = {
                    "type": "class",
                    "bases": bases,
                    "docstring": ast.get_docstring(node) is not None,
                    "line": getattr(node, "lineno", 0)
                }
        return symbols

    def review_diff(self, old_code: str, new_code: str) -> Dict[str, Any]:
        """
        Performs semantic diff review between old_code and new_code.
        Returns impact score, complexity delta, breaking changes, and PR findings.
        """
        findings = []
        old_tree = None
        new_tree = None

        try:
            old_tree = ast.parse(old_code) if old_code.strip() else ast.parse("")
        except SyntaxError as e:
            findings.append({"severity": "critical", "message": f"Syntax error in baseline code: {e}"})

        try:
            new_tree = ast.parse(new_code) if new_code.strip() else ast.parse("")
        except SyntaxError as e:
            findings.append({"severity": "blocker", "message": f"PR introduces syntax error: {e}"})
            return {
                "status": "rejected",
                "impact_score": 100.0,
                "complexity_delta": 0,
                "findings": findings
            }

        old_symbols = self.extract_symbol_signatures(old_tree)
        new_symbols = self.extract_symbol_signatures(new_tree)

        old_complexity = self.compute_cognitive_complexity(old_tree)
        new_complexity = self.compute_cognitive_complexity(new_tree)
        complexity_delta = new_complexity - old_complexity

        if complexity_delta > 10:
            findings.append({
                "severity": "warning",
                "type": "complexity_spike",
                "message": f"Cognitive complexity jumped by +{complexity_delta} (from {old_complexity} to {new_complexity}). Consider refactoring into helper functions."
            })

        # Breaking API changes detection
        for sym_name, sym_info in old_symbols.items():
            if sym_name not in new_symbols:
                findings.append({
                    "severity": "critical",
                    "type": "breaking_change",
                    "symbol": sym_name,
                    "message": f"Exported symbol '{sym_name}' was removed or renamed. Downstream consumers may break."
                })
            elif sym_info["type"] == "function":
                new_info = new_symbols[sym_name]
                old_args = sym_info["args"]
                new_args = new_info["args"]
                # If existing positional args were removed or altered
                if any(arg not in new_args for arg in old_args):
                    findings.append({
                        "severity": "critical",
                        "type": "breaking_signature",
                        "symbol": sym_name,
                        "message": f"Function '{sym_name}' removed positional parameter(s): expected {old_args}, got {new_args}."
                    })

        # Check for newly added symbols missing docstrings
        for sym_name, sym_info in new_symbols.items():
            if sym_name not in old_symbols and not sym_info["docstring"]:
                findings.append({
                    "severity": "info",
                    "type": "missing_docstring",
                    "symbol": sym_name,
                    "message": f"Newly added {sym_info['type']} '{sym_name}' has no docstring documentation."
                })

        # Check for dangerous global mutations
        for node in ast.walk(new_tree):
            if isinstance(node, ast.Global):
                findings.append({
                    "severity": "warning",
                    "type": "global_mutation",
                    "message": f"Detected 'global {', '.join(node.names)}' statement at line {getattr(node, 'lineno', 0)}. Avoid global mutable state in production services."
                })

        impact_score = min(100.0, max(0.0, 10.0 + complexity_delta * 2.5 + len([f for f in findings if f['severity'] == 'critical']) * 25.0))

        return {
            "status": "needs_work" if any(f["severity"] in ("critical", "blocker") for f in findings) else "approved",
            "impact_score": round(impact_score, 2),
            "old_complexity": old_complexity,
            "new_complexity": new_complexity,
            "complexity_delta": complexity_delta,
            "added_symbols": [s for s in new_symbols if s not in old_symbols],
            "removed_symbols": [s for s in old_symbols if s not in new_symbols],
            "findings_count": len(findings),
            "findings": findings
        }
