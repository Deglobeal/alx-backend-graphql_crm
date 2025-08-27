#!/usr/bin/env python3
"""
GraphQL-based Order Reminder Script
Queries pending orders from the last 7 days and logs reminders
"""

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

def create_graphql_client():
    """Create and return a GraphQL client instance"""
    transport = AIOHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    return client

def get_pending_orders():
    """Query GraphQL for orders from the last 7 days"""
    client = create_graphql_client()
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    date_str = seven_days_ago.isoformat()
    
    query = gql("""
        query GetPendingOrders($dateFrom: String!) {
            orders(where: {orderDate: {gte: $dateFrom}}) {
                id
                customer {
                    email
                }
                orderDate
                status
            }
        }
    """)
    
    try:
        result = client.execute(query, variable_values={"dateFrom": date_str})
        return result.get('orders', [])
    except Exception as e:
        print(f"Error querying GraphQL: {e}")
        return []

def log_order_reminders(orders):
    """Log order reminders to the specified file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(LOG_FILE, 'a') as f:
            for order in orders:
                order_id = order.get('id')
                customer_email = order.get('customer', {}).get('email', 'N/A')
                log_entry = f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n"
                f.write(log_entry)
        return True
    except Exception as e:
        print(f"Error writing to log file: {e}")
        return False

def main():
    """Main function to process order reminders"""
    try:
        # Get pending orders from last 7 days
        orders = get_pending_orders()
        
        if orders:
            # Log the reminders
            if log_order_reminders(orders):
                print("Order reminders processed!")
            else:
                print("Failed to log order reminders")
                sys.exit(1)
        else:
            print("No pending orders found from the last 7 days")
            print("Order reminders processed!")
            
    except Exception as e:
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()