#!/bin/bash
# Customer cleanup script - removes inactive customers
# Usage: ./clean_inactive_customers.sh

# Set the current date for logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Navigate to the Django project root (adjust path as needed)
# Assuming script is run from project root or adjust accordingly
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$0")")")"

# Execute the Django shell command to delete inactive customers
DELETED_COUNT=$(python3 "$PROJECT_ROOT/manage.py" shell -c "
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from customers.models import Customer

# Get customers with no orders in the last year
one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.annotate(
    order_count=Count('orders')
).filter(
    order_count=0
) | Customer.objects.filter(
    orders__order_date__lt=one_year_ago
).distinct()

# Count before deletion
count = inactive_customers.count()

# Delete the inactive customers
inactive_customers.delete()

# Print the count
print(count)
")

# Log the result
LOG_FILE="/tmp/customer_cleanup_log.txt"
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"

# Also output to console
echo "Customer cleanup completed. $DELETED_COUNT customers deleted."