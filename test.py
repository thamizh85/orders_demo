import unittest
import json
import app

# URL path: /orders
class PlaceOrdersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.client = self.app.test_client

    def test_place_order_response(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        self.assertEqual(res.status_code, 200)

    def test_place_order_response_has_id(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        order_response_json = json.loads(res.data.decode('utf-8'))
        self.assertTrue('id' in order_response_json)

    def test_place_order_response_has_distance(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        order_response_json = json.loads(res.data.decode('utf-8'))
        self.assertTrue('distance' in order_response_json)

    def test_place_order_impossible_route(self):
        order_body = {
            "origin" : ["4", "3"],
            "destination" : ["2", "1"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        order_response_json = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 500)

    def test_place_order_response_has_status(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        order_response_json = json.loads(res.data.decode('utf-8'))
        self.assertTrue('status' in order_response_json)

    def test_place_order_response_distance_value(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        order_response_json = json.loads(res.data.decode('utf-8'))
        distance = int(order_response_json['distance'])
        self.assertAlmostEqual(distance,1620, delta=10)

    def test_place_order_response_status_value(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }
        res = self.client().post('/orders', 
                                  json=order_body)
        order_response_json = json.loads(res.data.decode('utf-8'))
        status = order_response_json['status']
        self.assertEqual(status,"UNASSIGNED")

# URL path: /orders/:id
class TakeOrdersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.client = self.app.test_client

    def test_take_order_response(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }

        res0 = self.client().post('/orders', 
                                   json=order_body)
        order_response_json = json.loads(res0.data.decode('utf-8'))
        order_id = order_response_json['id']

        request_body = { "status" : "TAKEN" }
        res1 = self.client().patch('/orders/' + order_id,
                                    json=request_body)
        self.assertEqual(res1.status_code, 200)

    def test_take_order_response_has_status(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }

        res0 = self.client().post('/orders', 
                                   json=order_body)
        order_response_json = json.loads(res0.data.decode('utf-8'))
        order_id = order_response_json['id']

        request_body = { "status" : "TAKEN" }
        res1 = self.client().patch('/orders/' + order_id,
                                    json=request_body)
        order_response_json = json.loads(res1.data.decode('utf-8'))
        self.assertTrue('status' in order_response_json)

    def test_take_order_response_status_value(self):
        order_body = {
            "origin" : ["22.348624", "114.064814"],
            "destination" : ["22.352703", "114.079926"]
        }

        res0 = self.client().post('/orders', 
                                   json=order_body)
        order_response_json = json.loads(res0.data.decode('utf-8'))
        order_id = order_response_json['id']

        request_body = { "status" : "TAKEN" }
        res1 = self.client().patch('/orders/' + order_id,
                                    json=request_body)
        order_response_json = json.loads(res1.data.decode('utf-8'))
        status = order_response_json['status']
        self.assertEqual(status,"SUCCESS")

class ListOrdersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app
        self.client = self.app.test_client
    
    def response_to_set(self, res):
        page = json.loads(res.data.decode('utf-8'))
        id_set = set([o['id'] for o in page])
        return id_set

    def test_list_order_response(self):
        res = self.client().get('/orders?page=1&limit=5')
        self.assertEqual(res.status_code, 200)

    def test_list_order_response_limit(self):
        res = self.client().get('/orders?page=1&limit=5')
        orders = json.loads(res.data.decode('utf-8'))
        self.assertEqual(len(orders), 5)

    def test_list_order_negative_input(self):
        res1 = self.client().get('/orders?page=-1&limit=5')
        res2 = self.client().get('/orders?page=1&limit=-5')
        self.assertEqual(res1.status_code, 500)
        self.assertEqual(res2.status_code, 500)

    def test_list_order_string_input(self):
        res1 = self.client().get('/orders?page=x&limit=5')
        res2 = self.client().get('/orders?page=1&limit=x')
        self.assertEqual(res1.status_code, 500)
        self.assertEqual(res2.status_code, 500)

    def test_list_order_response_paging(self):
        res1 = self.client().get('/orders?page=1&limit=5')
        set1 = self.response_to_set(res1)
        res2 = self.client().get('/orders?page=2&limit=5')
        set2 = self.response_to_set(res2)
        self.assertFalse(set1.intersection(set2))

def orders_test_suite():
    suite = unittest.TestSuite()
    suite.addTest(PlaceOrdersTestCase('test_place_order_response'))
    suite.addTest(PlaceOrdersTestCase('test_place_order_response_has_id'))
    suite.addTest(PlaceOrdersTestCase('test_place_order_response_has_distance'))
    suite.addTest(PlaceOrdersTestCase('test_place_order_response_has_status'))
    suite.addTest(PlaceOrdersTestCase('test_place_order_response_distance_value'))
    suite.addTest(PlaceOrdersTestCase('test_place_order_response_status_value'))
    suite.addTest(PlaceOrdersTestCase('test_place_order_impossible_route'))
    suite.addTest(TakeOrdersTestCase('test_take_order_response'))
    suite.addTest(TakeOrdersTestCase('test_take_order_response_has_status'))
    suite.addTest(TakeOrdersTestCase('test_take_order_response_status_value'))
    suite.addTest(ListOrdersTestCase('test_list_order_response'))
    suite.addTest(ListOrdersTestCase('test_list_order_response_limit'))
    suite.addTest(ListOrdersTestCase('test_list_order_response_paging'))
    suite.addTest(ListOrdersTestCase('test_list_order_negative_input'))
    suite.addTest(ListOrdersTestCase('test_list_order_string_input'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(orders_test_suite())