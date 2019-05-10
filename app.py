#!/usr/bin/env python3
import os
import time

from flask import Flask, url_for, Response, request, jsonify
from pymongo import MongoClient 
from pymongo.errors import AutoReconnect
from bson.objectid import ObjectId 
from bson.errors import InvalidId 
import googlemaps

MONGODB_HOST = os.environ.get('MONGO_HOST', 'mongo')
MONGODB_PORT = int(os.environ.get('MONGO_PORT', '27017'))
API_KEY = os.environ.get('API_KEY')

MAX_TIME = 300

app = Flask(__name__)
app.config.from_object(__name__)


def wait_duration(attempt):
    """ Calculate the wait time based on the number of past attempts.
    The time grows exponentially with the attempts up to a maximum
    of 10 seconds.
    Args:
        attempt: Current count of reconnection attempts.
    Returns:
        int: The number of seconds to wait before next attempt
    """
    return min(10, pow(2, attempt))

def get_distance(start, end):
    """
    Calls distance_matrix API from google maps

    Args:
        start: a tuple containing origin lattitude and longitude values
        end: a tuple containing destination lattitude and longitude values

    Returns:
        A tuple containing result status, element status and destination value (in meters).
    """
    gmaps = googlemaps.Client(key=API_KEY)
    res = gmaps.distance_matrix(start, end, mode='driving')
    res_status = res['status']
    if res_status == 'OK':
        elem_status = res['rows'][0]['elements'][0]['status']
        if elem_status == 'OK':
            distance = res['rows'][0]['elements'][0]['distance']['value']
        else:
            distance = None
    else:
        elem_status, distance = None, None
    return res_status, elem_status, distance

def format_order_dict(order):
    """
    A helper method to convert objectId from BSON to string and
    to strip out unnecessary keys from the result dict

    Args:
        start: a tuple containing origin lattitude and longitude values
        end: a tuple containing destination lattitude and longitude values

    Returns:
        formatted dictionary. For e.g:

            {
                "id": <order_id>,
                "distance": <total_distance>,
                "status": <ORDER_STATUS>
            }
    """
    order['id'] = str(order.pop('_id'))
    _ = order.pop('origin')
    _ = order.pop('destination')
    return order

def test_positive_digit(s):
    """
    Return True only for datatype that can be cast as a positive integer
    """
    if s.isdigit():
        return int(s) > 0


start_time = time.time()

for attempt in range(5):
    try:
        client = MongoClient(app.config['MONGODB_HOST'],
                            app.config['MONGODB_PORT'])
    except AutoReconnect:
        duration = time.time() - start_time

        if duration >= MAX_TIME:
            break

        time.sleep(wait_duration(attempt))

client = MongoClient(app.config['MONGODB_HOST'],
                    app.config['MONGODB_PORT'])
db = client.orders_db    
orders = db.orders 

@app.route('/')
def root():
    return 'Hello'

@app.route('/orders', methods = ['POST'])
def new_order():
    """
    Takes a new order. Accepts only POST method.

    Args:
        origin: an array of origin lattitude and longitude values stored as strings
        destination: an array of destination lattitude and longitude values stored as strings

    Returns:
       Valid HTTP Response. 
       
       For successful transaction, return header HTTP 200 with the following json body:

            {
                "id": <order_id>,
                "distance": <total_distance>,
                "status": "UNASSIGNED"
            }

        For any unsuccesful transaction, return header HTTP 500 with the appropriate error message as json body

            {
                "error" : "ERROR_DESCRIPTION"
            }
    """
    origin = request.get_json().get("origin")
    destination = request.get_json().get('destination')

    if len(origin) != 2 or len(destination) != 2:
        res_status = "VALUE_ERROR"
    else:
        try:
            start = (float(origin[0]), float(origin[1]))
            end = (float(destination[0]), float(destination[1]))
            res_status, elem_status, distance = get_distance(start, end)
        except ValueError:
            res_status = "VALUE_ERROR"

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
    elif res_status =='VALUE_ERROR':
        response = jsonify({ "error": "ERROR: Input co-ordinates are not in proper format" })
        response.status_code = 500
    else:
        response = jsonify({ "error": "ERROR: Unable to access maps API" })
        response.status_code = 500
    return response

@app.route('/orders/<order_id>', methods = ['PATCH'])
def take_order(order_id):
    """
    Accepts an order specified by the order_id. Accepts only PATCH method.

    Args:
        order_id: Order ID in string format

    Returns:
       Valid HTTP Response. 
       
       For successful transaction, return header HTTP 200 with the following json body:

            {
                "id": <order_id>,
                "distance": <total_distance>,
                "status": "UNASSIGNED"
            }

        For any unsuccesful transaction, return header HTTP 500 with the appropriate error message as json body

            {
                "error" : "ERROR_DESCRIPTION"
            }
    """
    order = orders.find_one({'_id': ObjectId(order_id)})
    if order:
        order['status'] = 'TAKEN'

        # Find and modify is an atomic DB update so if two concurrent processes execute 
        # it at the same time, only one will succeed 
        # https://docs.mongodb.com/manual/reference/command/findAndModify
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
    """
    Prints a paginated list of orders

    Args:
        page_no: Page number
        limit: Number of elements per page

    Returns:
       Valid HTTP Response. 
       
       Return header HTTP 200 with the following json body:

            [
                {
                    "id": <order_id>,
                    "distance": <total_distance>,
                    "status": <ORDER_STATUS>
                },
                ...
            ]

        If there are no more elements to display return an empty array:

        For improper requests, return header HTTP 500 with the appropriate error message as json body

            {
                "error" : "ERROR_DESCRIPTION"
            }
    """
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