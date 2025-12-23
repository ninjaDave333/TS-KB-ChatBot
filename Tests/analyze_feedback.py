#!/usr/bin/env python3
"""
Analyze user feedback to track satisfaction and identify improvement areas.
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def analyze_feedback():
    feedback_file = Path("/home/ubuntu/meetingsBotLogs/persistentData/user_feedback.jsonl")
    
    if not feedback_file.exists():
        return {"error": "No feedback data yet"}
    
    total = 0
    positive = 0
    negative = 0
    by_intent = defaultdict(lambda: {"positive": 0, "negative": 0})
    by_user = defaultdict(lambda: {"positive": 0, "negative": 0})
    recent_feedback = []
    
    with open(feedback_file) as f:
        for line in f:
            entry = json.loads(line)
            total += 1
            
            if entry["feedback"] == "positive":
                positive += 1
            else:
                negative += 1
            
            # Track by intent
            intent = entry.get("metadata", {}).get("method", "unknown")
            by_intent[intent][entry["feedback"]] += 1
            
            # Track by user
            user = entry.get("user", "anonymous")
            by_user[user][entry["feedback"]] += 1
            
            # Keep recent
            recent_feedback.append({
                "query": entry["query"][:60],
                "feedback": entry["feedback"],
                "user": user,
                "timestamp": entry["timestamp"]
            })
    
    satisfaction_rate = (positive / total * 100) if total > 0 else 0
    
    return {
        "total_feedback": total,
        "positive": positive,
        "negative": negative,
        "satisfaction_rate": round(satisfaction_rate, 1),
        "by_intent": dict(by_intent),
        "by_user": dict(by_user),
        "recent": recent_feedback[-10:]
    }

if __name__ == "__main__":
    results = analyze_feedback()
    print(json.dumps(results, indent=2))
