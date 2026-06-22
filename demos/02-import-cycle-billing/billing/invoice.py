"""Invoice model — imports the customer model to resolve the bill-to party.

This module and `customer.py` import each other at module scope, which is a
classic circular import: it works by luck of import order today and raises
ImportError the moment that order changes.
"""

from billing.customer import Customer


class Invoice:
    """A single invoice for a customer."""

    def __init__(self, customer_id, amount):
        self.customer = Customer(customer_id)
        self.amount = amount

    def bill_to(self):
        """Return the display name to print on the invoice."""
        return self.customer.display_name()
