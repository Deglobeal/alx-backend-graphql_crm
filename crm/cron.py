#!/usr/bin/env python3
"""
CRM Heartbeat Logger with GraphQL integration and Low Stock Updates
Uses gql library to verify GraphQL endpoint and update low stock products
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

def updateLowStockProducts():
    """
    Update low stock products via GraphQL mutation
    Logs updates to /tmp/low_stock_updates_log.txt
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"
    
    try:
        # Create GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # Define mutation to update low stock products
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    updatedCount
                    products {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        # Execute mutation
        result = client.execute(mutation)
        
        if result and 'updateLowStockProducts' in result:
            updated_count = result['updateLowStockProducts']['updatedCount']
            products = result['updateLowStockProducts']['products']
            
            # Log the update
            log_message = f"{timestamp} Updated {updated_count} low stock products\n"
            
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(log_message)
                
            print(f"Low stock update logged: {log_message.strip()}")
            
            # Log individual product updates
            for product in products:
                product_log = f"{timestamp} Updated: {product['name']} (ID: {product['id']}) -> Stock: {product['stock']}\n"
                with open(log_file, 'a') as f:
                    f.write(product_log)
                    
        else:
            print("No low stock products updated")
            
    except Exception as e:
        error_message = f"{timestamp} Error updating low stock products: {e}\n"
        try:
            with open(log_file, 'a') as f:
                f.write(error_message)
        except:
            pass
        print(f"Error in updateLowStockProducts: {e}")

# For standalone testing
if __name__ == "__main__":
    log_crm_heartbeat()
    updateLowStockProducts()