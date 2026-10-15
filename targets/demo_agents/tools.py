customers = {
    "101": {
        "name": "Alice",
        "email": "alice@example.com",
        "status": "active",
    },
    "102": {
        "name": "Bob",
        "email": "bob@example.com",
        "status": "inactive",
    },
}


def search_customer(name: str) -> list[dict]:
    """Search customers by name."""
    results = []
    for customer_id, customer in customers.items():
        if name.lower() in customer["name"].lower():
            results.append({
                "customer_id": customer_id,
                **customer,
            })
    return results


def get_customer(customer_id: str) -> dict | None:
    """Get a customer by ID."""
    return customers.get(customer_id)


def delete_customer(customer_id: str) -> str:
    """Delete a customer."""
    if customer_id not in customers:
        return "Customer not found"
    del customers[customer_id]
    return f"Customer {customer_id} deleted successfully"

