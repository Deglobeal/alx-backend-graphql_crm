#!/usr/bin/env python3
"""
CRM Heartbeat Logger
Logs heartbeat messages every 5 minutes to confirm CRM health
"""

import os
import sys
import requests
from datetime import datetime
from django.conf import settings

def log_crm_heartbeat():
    """
    Log heartbeat message to confirm CRM is alive
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    """
    # Get current timestamp in required format
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Log file path
    log_file = "/tmp/crm_heartbeat_log.txt"
    
    # Create log message
    log_message = f"{timestamp} CRM is alive\n"
    
    try:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        # Append to log file
        with open(log_file, 'a') as f:
            f.write(log_message)
            
        print(f"Heartbeat logged: {log_message.strip()}")
        
        # Optional: Test GraphQL endpoint
        try:
            graphql_endpoint = "http://localhost:8000/graphql"
            query = {
                "query": "{ hello }"
            }
            
            response = requests.post(
                graphql_endpoint,
                json=query,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'hello' in data['data']:
                    print(f"GraphQL endpoint responsive: {data['data']['hello']}")
            else:
                print(f"GraphQL endpoint not responsive: {response.status_code}")
                
        except Exception as e:
            print(f"GraphQL check failed: {e}")
            
    except Exception as e:
        print(f"Error writing heartbeat: {e}")

# For standalone testing
if __name__ == "__main__":
    log_crm_heartbeat()