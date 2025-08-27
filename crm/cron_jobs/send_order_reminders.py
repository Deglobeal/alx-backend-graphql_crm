#!/usr/bin/env python3
"""
GraphQL-based Order Reminder Script
Queries pending orders from the last 7 days and logs reminders
"""

import os
import sys
import requests
from datetime import datetime, timedelta

# Configuration
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Windows-compatible log file path
LOG_FILE = os.path.join(os.environ.get('TEMP', 'C:\\temp'), 'order_reminders_log.txt')

# Alternative: Use current directory
# LOG_FILE = 'order_reminders_log.txt'

def get_pending_orders():
    """Query GraphQL for orders from the last 7 days using requests"""
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    date_str = seven_days_ago.isoformat()
    
    query = """
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
    """
    
    variables = {
        "dateFrom": date_str
    }
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={'query': query, 'variables': variables},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('orders', [])
        else:
            print(f"GraphQL request failed with status {response.status_code}")
            return []
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to GraphQL server. Make sure it's running on localhost:8000")
        return []
    except Exception as e:
        print(f"Error querying GraphQL: {e}")
        return []

def log_order_reminders(orders):
    """Log order reminders to the specified file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Ensure the directory exists
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
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