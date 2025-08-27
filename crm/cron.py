#!/usr/bin/env python3
"""
CRM Heartbeat Logger with GraphQL integration
Uses gql library to verify GraphQL endpoint health
"""

import os
import sys
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Log heartbeat message to confirm CRM is alive
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Uses gql library to test GraphQL endpoint
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
        
        # Use gql library to test GraphQL endpoint
        try:
            # Create transport with gql
            transport = RequestsHTTPTransport(
                url="http://localhost:8000/graphql",
                verify=True,
                retries=3,
            )
            
            # Create client
            client = Client(transport=transport, fetch_schema_from_transport=False)
            
            # Define GraphQL query
            query = gql("""
                query {
                    hello
                }
            """)
            
            # Execute query
            result = client.execute(query)
            
            if result and 'hello' in result:
                print(f"GraphQL endpoint responsive: {result['hello']}")
            else:
                print("GraphQL endpoint check completed")
                
        except Exception as e:
            print(f"GraphQL check failed: {e}")
            
    except Exception as e:
        print(f"Error writing heartbeat: {e}")

# For standalone testing
if __name__ == "__main__":
    log_crm_heartbeat()