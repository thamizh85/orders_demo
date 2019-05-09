#!/usr/bin/env python3
import os

from flask import Flask, url_for, Response, request, jsonify
from pymongo import MongoClient 
from pymongo.errors import AutoReconnect
from bson.objectid import ObjectId 
from bson.errors import InvalidId 
import googlemaps
# from flask_mongoalchemy import MongoAlchemy

MONGODB_HOST = os.environ.get('MONGO_HOST', 'mongo')
MONGODB_PORT = int(os.environ.get('MONGO_PORT', '27017'))
API_KEY = os.environ.get('API_KEY')

app = Flask(__name__)
app.config.from_object(__name__)

client = MongoClient(app.config['MONGODB_HOST'],
                     app.config['MONGODB_PORT'])

db = client.orders_db    
orders = db.orders 

def get_distance(start, end):
    gmaps = googlemaps.Client(key=API_KEY)
    res = gmaps.distance_matrix(start, end, mode='driving')
    res_status = res['status']
    elem_status = res['rows'][0]['elements'][0]['status']
    distance = res['rows'][0]['elements'][0]['distance']['value']
    return res_status, elem_status, distance

def format_order_dict(order):
    order['id'] = str(order.pop('_id'))
    _ = order.pop('origin')
    _ = order.pop('destination')
    return order

def test_positive_digit(s):
    if s.isdigit():
        return int(s) > 0
    else:
        return False

@app.route('/')
def root():
    return 'Hello'

@app.route('/orders', methods = ['POST'])
def new_order():
    origin = request.get_json().get("origin")
    destination = request.get_json().get('destination')

    start = (float(origin[0]), float(origin[1]))
    end = (float(destination[0]), float(destination[1]))

    res_status, elem_status, distance = get_distance(start, end)

    if res_status == 'OK':
        if elem_status == 'OK':
            # TODO: Wrap inside try and catch exceptions including validation errors 
            objectId = orders.insert({ "origin": origin, 
                            "destination": destination,
                            "distance": distance,
                            "status" : "UNASSIGNED"})
            id = str(objectId)
            response = jsonify({"id": id,
                "distance": distance,
                "status": "UNASSIGNED"})
            response.status_code = 200
        # TODO: catch specific error codes and return useful error messages
        else:
            response = jsonify({ "error": "ERROR: No route found or co-ordinates could not be geocoded" })
            response.status_code = 500
    else:
        response = jsonify({ "error": "ERROR: Unable to access maps API" })
        response.status_code = 500
    return response

@app.route('/orders/<order_id>', methods = ['PATCH'])
def take_order(order_id):
    order = orders.find_one({'_id': ObjectId(order_id)})
    if order:
        order['status'] = 'TAKEN'
        update = orders.find_and_modify(query={'_id': ObjectId(order_id), 'status': 'UNASSIGNED'}, update=order)
        if update:
            response = jsonify({ "status": "SUCCESS" })
            response.status_code = 200
        else:
            response = jsonify({ "error": "ERROR: Order already taken" })
            response.status_code = 500
    else:
        response = jsonify({ "error": "ERROR: Order not found" })
        response.status_code = 500
    return response

@app.route('/orders', methods = ['GET'])
def list_orders():
    if 'page' in request.args and 'limit' in request.args:
        page_no = request.args['page']
        limit = request.args['limit']
        if test_positive_digit(page_no) and test_positive_digit(limit):
            limit = int(limit)
            page_no = int(page_no)
            skip_length = limit * ( page_no - 1)
            orders_list = orders.find().skip(skip_length).limit(limit)
            response = jsonify([format_order_dict(order) for order in orders_list])
            response.status_code = 200
        else:
            response = jsonify({ "error": "ERROR: Malformed GET request" })
            response.status_code = 500
    else:
        response = jsonify({ "error": "ERROR: Malformed GET request" })
        response.status_code = 500
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", 
                debug=True)