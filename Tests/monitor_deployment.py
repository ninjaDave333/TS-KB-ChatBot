#!/usr/bin/env python3
"""
Monitor deployment effectiveness by comparing trace counts and success rates
"""

import subprocess
import json
from datetime import datetime

def check_remote_traces():
    """Check current trace count on remote server"""
    cmd = ['ssh', '-i', 'D:\\Projects\\aipg.pem', 'ubuntu@aipg.dudelabz.com', 
           'wc -l /home/ubuntu/meetingsBotLogs/persistentData/traces.jsonl']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        line_count = int(result.stdout.strip().split()[0])
        print(f"📊 Remote traces.jsonl: {line_count} lines")
        return line_count
    except Exception as e:
        print(f"❌ Error checking remote traces: {e}")
        return None

def analyze_recent_traces(baseline_count=186):
    """Analyze only traces after deployment"""
    local_file = "ref_data/traces.jsonl"
    
    try:
        with open(local_file, 'r') as f:
            all_traces = [json.loads(line) for line in f if line.strip()]
        
        if len(all_traces) <= baseline_count:
            print(f"📈 No new traces yet ({len(all_traces)} total, baseline: {baseline_count})")
            return
        
        # Analyze only new traces
        new_traces = all_traces[baseline_count:]
        print(f"🆕 Found {len(new_traces)} new traces since deployment")
        
        # Quick analysis of new traces
        general_queries = [t for t in new_traces if t.get('intent') == 'general']
        if general_queries:
            successful = sum(1 for t in general_queries if t.get('neo4j_result_summary', {}).get('has_data', False))
            success_rate = (successful / len(general_queries)) * 100
            print(f"🎯 New general intent performance: {success_rate:.1f}% ({successful}/{len(general_queries)})")
        
        return len(new_traces)
        
    except FileNotFoundError:
        print(f"❌ Local traces file not found: {local_file}")
        return None

if __name__ == "__main__":
    print(f"🔍 Deployment Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check remote count
    remote_count = check_remote_traces()
    
    # Analyze local traces
    new_count = analyze_recent_traces()
    
    if remote_count and remote_count > 186:
        print(f"\n💡 Action needed: Copy new traces from remote ({remote_count} total)")
        print("Command: scp -i D:\\Projects\\aipg.pem ubuntu@aipg.dudelabz.com:/home/ubuntu/meetingsBotLogs/persistentData/traces.jsonl ref_data/")
    else:
        print(f"\n⏳ Waiting for new production queries...")