"""
Demonstration of genpark-ast-diff-semantic-pr-reviewer-skill
"""

from client import SemanticPRReviewerClient

def main():
    reviewer = SemanticPRReviewerClient()

    old_code = """
def fetch_user_data(user_id, timeout=30):
    """Fetch user record from persistence layer."""
    if user_id <= 0:
        return None
    return {"id": user_id, "active": True}
"""

    new_code = """
def fetch_user_data(user_id):
    # Removed timeout parameter without backwards compatibility
    global _LAST_ACCESSED
    _LAST_ACCESSED = user_id
    if user_id <= 0:
        for i in range(3):
            if i % 2 == 0:
                while False:
                    pass
        return None
    return {"id": user_id, "active": True}

def calculate_analytics():
    pass
"""

    result = reviewer.review_diff(old_code, new_code)
    print("=== SEMANTIC PR REVIEW REPORT ===")
    print(f"Status: {result['status']}")
    print(f"Impact Score: {result['impact_score']}")
    print(f"Complexity Delta: +{result['complexity_delta']} ({result['old_complexity']} -> {result['new_complexity']})")
    print(f"Added Symbols: {result['added_symbols']}")
    print(f"Findings Count: {result['findings_count']}")
    for f in result['findings']:
        print(f"  [{f['severity'].upper()}] ({f.get('type', 'generic')}): {f['message']}")

if __name__ == "__main__":
    main()
