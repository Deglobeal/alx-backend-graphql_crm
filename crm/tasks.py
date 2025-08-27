from datetime import datetime
import requests  # ✅ required for HTTP call instead of gql
from celery import shared_task
from django.conf import settings

@shared_task
def generate_crm_report():
    """
    Weekly CRM report:
    - total customers
    - total orders
    - total revenue
    Logs to /tmp/crm_report_log.txt
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    query = """
    {
      totalCustomers
      totalOrders
      totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        customers = data.get("totalCustomers", 0)
        orders = data.get("totalOrders", 0)
        revenue = data.get("totalRevenue", 0)

        report = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

        # ensure directory exists
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(report)

        print(report.strip())
        return report
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
        raise