# orders_demo

## Introduction

The objective is to create a backend system which implements a RESTful API to accept and process orders.

## Tech stack

The main software components are:

* **API Server** 
    * flask : Python based web framework
    * pymongo : Database connector

* **DB backend**
    * mongodb : NoSQL DB server

* **Third Party Maps API**
    * Google Maps

## Data Model

The data model is a simple NoSQL database. 

## How to run

All the components have been dockerized for easier deployment. 

### Configuration variables

The  rest API needs google maps key. Edit the `docker-compose.yml` to provide the API key. 

```yaml
    environment:
     - API_KEY=<INSERT YOUR KEY HERE>
     - MONGO_HOST=mongo
     - MONGO_PORT=27017
```


Alternatively docker-compose can be rewritten to read the API key from the host environment variable.

### Docker run

Application can be launched by using docker-compose

    docker-compose up -d

This launches two containers with the 

### Running tests

The code include unit test for the Web API. Tests can be executed by connecting  to the API server container and running the test script

    docker exec -it orders_demo_api_1 /bin/sh
    python test.py

## Future work

* Add support for deployment options on hosted platforms such as:
    * Google app engine 
    * AWS Elastic Beanstalk
* Add more exception handling to catch potential exceptions happening at all interfaces such as Python -> Google Maps or Python -> MongoDB