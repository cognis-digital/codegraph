"""Customer model — imports the invoice model to list a customer's invoices.

Imports `billing.invoice` at module scope, while `billing.invoice` imports this
module: a two-module circular dependency.
"""

from billing.invoice import Invoice


class Customer:
    """A billable customer."""

    def __init__(self, customer_id):
        self.customer_id = customer_id

    def display_name(self):
        """Human-readable name for invoices."""
        return f"Customer #{self.customer_id}"

    def open_invoice(self, amount):
        """Create a new invoice for this customer."""
        return Invoice(self.customer_id, amount)
