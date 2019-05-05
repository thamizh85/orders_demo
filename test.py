import unittest
import json
import app

class OrdersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.client = self.app.test_client
        self.order_body = {}
        return "TODO"

    def test_place_order(self):
        res = self.client().post('/orders/', data=self.order_body)
        self.order_response_json = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 200)

    def test_take_order(self):
        order_id = self.order_response_json.id
        res = self.client().patch('/orders/' + order_id)
        self.assertEqual(res.status_code, 200)
    
    def test_list_order(self):
        res = self.client().get('/orders?page=1&limit=20')
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()