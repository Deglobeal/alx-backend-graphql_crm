#!/usr/bin/env python3
"""
Test script for customer cleanup
"""

import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from django.db.models import Count

def cleanup_inactive_customers():
    """Delete customers with no orders in the last year"""
    one_year_ago = timezone.now() - timedelta(days=365)
    
    # Get customers with no orders at all
    customers_no_orders = Customer.objects.annotate(
        order_count=Count('orders')
    ).filter(order_count=0)
    
    # Count before deletion
    count = customers_no_orders.count()
    
    # Delete the inactive customers
    customers_no_orders.delete()
    
    # Log the result
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = os.path.join(os.environ.get('TEMP', '.'), 'customer_cleanup_log.txt')
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] Deleted {count} inactive customers\n")
    
    print(f"Customer cleanup completed. {count} customers deleted.")
    print(f"Log saved to: {log_file}")

if __name__ == "__main__":
    cleanup_inactive_customers()