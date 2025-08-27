#!/usr/bin/env python3
"""
Simple mock GraphQL server for testing order reminders
Uses Flask instead of aiohttp-graphql to avoid dependency issues
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Mock order data
mock_orders = [
    {
        "id": "order-001",
        "orderDate": (datetime.now() - timedelta(days=2)).isoformat(),
        "status": "PENDING",
        "customer": {"email": "customer1@example.com"}
    },
    {
        "id": "order-002", 
        "orderDate": (datetime.now() - timedelta(days=5)).isoformat(),
        "status": "PROCESSING", 
        "customer": {"email": "customer2@example.com"}
    },
    {
        "id": "order-003",
        "orderDate": (datetime.now() - timedelta(days=10)).isoformat(),
        "status": "COMPLETED",
        "customer": {"email": "customer3@example.com"}
    }
]

@app.route('/graphql', methods=['POST'])
def graphql_endpoint():
    try:
        data = request.get_json()
        query = data.get('query', '')
        variables = data.get('variables', {})
        
        # Simple query parsing - look for orders query
        if 'orders' in query:
            # Filter orders based on dateFrom variable
            date_from_str = variables.get('dateFrom', '')
            if date_from_str:
                try:
                    date_from = datetime.fromisoformat(date_from_str.replace('Z', '+00:00'))
                    filtered_orders = [
                        order for order in mock_orders 
                        if datetime.fromisoformat(order['orderDate'].replace('Z', '+00:00')) >= date_from
                    ]
                except:
                    filtered_orders = mock_orders[:2]  # Default to first 2 orders
            else:
                filtered_orders = mock_orders
            
            return jsonify({
                "data": {
                    "orders": filtered_orders
                }
            })
        
        return jsonify({"data": {"orders": []}})
        
    except Exception as e:
        return jsonify({"errors": [{"message": str(e)}]}), 400

@app.route('/graphql', methods=['GET'])
def graphql_playground():
    return '''
    <html>
    <body>
    <h2>Mock GraphQL Server Running</h2>
    <p>POST to /graphql with GraphQL queries</p>
    <p>Example query:</p>
    <pre>
    {
      orders(where: {orderDate: {gte: "2024-01-01"}}) {
        id
        customer { email }
        orderDate
        status
      }
    }
    </pre>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)