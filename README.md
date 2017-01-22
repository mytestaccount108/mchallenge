BLOBSTOREpy
===============

An implementation of a BLOB storage through a Flask API.

## Requirements ##

Server was developed on an OSX machine with

  * Python 2.7
  
and tested against Ubuntu 16.04.
  
The following API is implemented:

* POST /store/<location> - Create new blob at location
* PUT /store/<location> - Update, or replace blob
* GET /store/<location> - Get blob
* DELETE /store/<location> - Delete blob

##  Usage  ##

Start up server workers with:

    ./challenge/bin/challenge-executable
    
For development, build with:
    
    # Go into challenge directory if not already there
    cd challenge
    virtualenv buildvenv
    source buildvenv/bin/activate
    # For development
    pip install -r requirements.txt
    # For testing, linting, and coverage
    pip install -r test-requirements.txt

Run tests with (after activating virtual environment):
    
    # Go into challenge directory if not already there
    cd challenge
    # Start up development server in another screen/window.
    python webapp.py
    # In another screen/window, run unit and integration tests
    python -m py.test tests/

Run linting with (after activating virtual environment):
    
    flake8

Run coverage with (after activating virtual environment):
  
    python -m py.test --cov-config .coveragerc --cov=. tests/
  

## Implementation ##


Implementation relies on the following technologies:

* gunicorn: Web Server
* flask: API Framework
* pex: Packaging to produce executable binary.

## Features ##

## Priorities ##

Be able to be restarted

* There is no dependency on in-memory caching so restarting individual workers when nothing is being written would not cause data loss.
* Gunicorn itself can be configured to restart its workers upon exception or upon timeout. A supervisor can also be run to create restart process upon crash.
Conditions to be careful with include:
* Disk leakage could occur when a request fails without completing and is restarted. We make a complexity tradeoff to intentionally drop partially failed requests and to have the client retry.  
We may need to consider making a periodic, scheduled pass to examine disk for files that do not belong to a finished request.

Be crash-tolerant
* Current model is to drop partially completed requests. This leaves the responsibility to the client to make another request if their initial call fails. Crash tolerance could be mitigated by replicating independent requests to multiple BLOB stores but synchronization then becomes a key issue. Since a Flask worker could crash while blob is still buffered in memory before being written to disk, it is difficult to retrieve the bytes that were in memory.

Be tolerant to as many other failures you can think about.
* Many expensive writes may require queueing to avoid dropping requests. This could be implemented by having the Flask server be a pass through to schedule jobs onto a dedicated job queue (beanstalkd, celery, etc). Worker and consumer pattern can be used to pull jobs off of queue to write to disk. Job queue also has the advantage of requeueing failed events or persisting events to pluggable backend (disk, redis, mysql, etc) to prevent job loss when host with job queue does down. 

## Failure Conditions ##

* Disk is full and error code 507 will be returned on all writes. On PUT requests, this allows us to avoid the complexity of examining file size before updating a BLOB. If blob store has TTL or seldomly used data, we could move to cold storage or remove data in case of TTL.
* Stream interruption should propagate exception up the stack and it will be up to the client to retry.

## TODO ##

* PEX executable should be a self contained executable with entire web service and not just wrapping the 
gunicorn entry point.
* Integration tests should not require manually starting up server.
* Queueing needs to be implemented.
* Deletion or compaction of unused blobs needs to be implemented.
* File system lock needs to be added to deal with concurrent writes/read to the same blob. Once queueing is in place, an alternative would be to do sequential writes on same blob.
* Cache control tags can also be added for blobs that seldomly change for the client.


