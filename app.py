#!/usr/bin/env python3

from flask import Flask, url_for, Response
from flask_mongoalchemy import MongoAlchemy

app = Flask(__name__)

# TODO: Use nnvironment variables 
app.config['MONGOALCHEMY_DATABASE'] = 'orders'
app.config['SECRET_KEY'] = 'top secret'
app.config['DEBUG'] = True

#db = MongoAlchemy(app)

@app.route('/')
def root():
    return 'Hello'

@app.route('/orders', methods = ['POST'])
def new_order():
    return 'TODO: new order'

@app.route('/orders/<int:order_id>', methods = ['PATCH'])
def take_order(order_id):
    return 'TODO: take order ' + str(order_id)

@app.route('/orders', methods = ['GET'])
def list_orders():
    return 'TODO: list orders'

if __name__ == "__main__":
    app.run(host="0.0.0.0", 
                debug=True)