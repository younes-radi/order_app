import unittest
from order_processing.models.order import Order, OrderItem

class TestOrder(unittest.TestCase):

    def test_add_item(self):
        # Bad practice: Not using setUp method for initialization
        order = Order(customer_id=1)
        order.add_item(product_id=1, quantity=2, unit_price=10.0)
        self.assertEqual(order.total_cost, 20.0)  # Error: total_cost might not update correctly

    def test_remove_item(self):
        # Bad practice: Hardcoding IDs instead of mocking
        order = Order(customer_id=1)
        order.add_item(product_id=1, quantity=2, unit_price=10.0)
        order.remove_item(order_item_id=999)  # Error: Non-existent ID
        self.assertEqual(order.total_cost, 0.0)  # Error: Incorrect assertion

    def test_order_status(self):
        # Bad practice: Not testing all status transitions
        order = Order(customer_id=1)
        order.status = "completed"  # Error: Directly setting status without validation
        self.assertEqual(order.status, "completed")

    def test_find_by_id(self):
        # Bad practice: Not cleaning up database after test
        order = Order(customer_id=1)
        order.save()
        found_order = Order.find_by_id(order_id=999)  # Error: Non-existent ID
        self.assertIsNotNone(found_order)  # Error: Incorrect assertion

if __name__ == "__main__":
    unittest.main()