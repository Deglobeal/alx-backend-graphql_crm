from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from celery import shared_task
import os

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

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        timeout=10
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
        query {
            totalCustomers
            totalOrders
            totalRevenue
        }
    """)

    try:
        result = client.execute(query)
        data = result.get("data", {})
        customers = data.get("totalCustomers", 0)
        orders = data.get("totalOrders", 0)
        revenue = data.get("totalRevenue", 0)

        report = f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n"

        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a") as f:
            f.write(report)

        print(report.strip())
        return report
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
        raise