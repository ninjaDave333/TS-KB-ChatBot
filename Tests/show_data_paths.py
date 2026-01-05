#!/usr/bin/env python3
"""
Show runtime data file paths for TSKB-RAG system
"""

import os
from pathlib import Path

def show_data_paths():
    """Display all data file paths used at runtime"""
    
    print("🗂️  TSKB-RAG Runtime Data File Paths")
    print("=" * 50)
    
    # Core data directory
    data_dir = Path("/app/data")
    print(f"📁 Data Directory: {data_dir}")
    print(f"   Exists: {data_dir.exists()}")
    print(f"   Absolute: {data_dir.absolute()}")
    
    # Key data files
    files = {
        "traces.jsonl": "Production query traces",
        "production_metrics.json": "Performance metrics",
        "query_patterns.json": "Learned patterns",
        "self_learning_report.json": "Analysis reports",
        "eval_results.jsonl": "Judge model evaluations",
        "self_improvement_results.json": "Improvement analysis",
        "production_insights.json": "User behavior insights",
        "user_feedback.jsonl": "User ratings"
    }
    
    print(f"\n📄 Data Files:")
    for filename, description in files.items():
        filepath = data_dir / filename
        exists = "✅" if filepath.exists() else "❌"
        print(f"   {exists} {filepath}")
        print(f"      {description}")
        if filepath.exists():
            try:
                size = filepath.stat().st_size
                print(f"      Size: {size:,} bytes")
            except:
                print(f"      Size: Unknown")
    
    # Environment info
    print(f"\n🔧 Environment:")
    print(f"   Current Working Dir: {os.getcwd()}")
    print(f"   Python Path: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Docker volume mapping (if applicable)
    persistent_path = Path("/home/ubuntu/meetingsBotLogs/persistentData")
    print(f"\n🐳 Docker Volume Mapping:")
    print(f"   Container Path: {data_dir}")
    print(f"   Host Path: {persistent_path}")
    print(f"   Host Exists: {persistent_path.exists() if persistent_path.is_absolute() else 'Unknown (not in container)'}")

if __name__ == "__main__":
    show_data_paths()