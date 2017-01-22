from StringIO import StringIO
import glob
import os
import requests

import pytest

from webapp import app
from helpers import get_storage_path


app.config['UPLOAD_FOLDER'] = get_storage_path(test=True)


"""
Integration tests to trigger the entire flow are added here.
"""


BASE_URL = 'http://0.0.0.0:20333'


@pytest.fixture()
def remove_old_blobs():
    """ Remove the blobs created after each test. """
    files = glob.glob(get_storage_path(test=True) + '/*')
    for f in files:
        os.remove(f)


@pytest.fixture()
def start_gunicorn():
    """ Start up the executable for testing. """
    # TODO: Add teardown and start up of web server.
    # In the mean time, manually startup the web server
    # before running tests.
    pass


@pytest.mark.integration
def test_admin(start_gunicorn):
    assert requests.get(BASE_URL + '/admin').status_code == 200


@pytest.mark.integration
def test_multiple_post(start_gunicorn, remove_old_blobs):
    """ Test multiple POST to same BLOB location. """
    new_location = 'testme'
    test_content = 'Here is the test content.'
    files = {'file': StringIO(test_content)}
    requests.post(BASE_URL + '/store/' + new_location, files=files)
    resp = requests.get(BASE_URL + '/store/' + new_location)
    assert resp.status_code == 200
    assert resp.content == test_content
    resp = requests.post(BASE_URL + '/store/' + new_location, files=files)
    assert resp.status_code == 422


@pytest.mark.integration
def test_basic_flow(start_gunicorn, remove_old_blobs):
    """ Test each of the basic flows for GET, PUT, POST, and DELETE.
    TODO: Break this up and utilize helper utilities.
    """
    # Check BLOB that does not exist.
    location = 'startingpoint'
    assert requests.get(BASE_URL + '/storage/' + location).status_code == 404

    # Add first BLOB and check for existence.
    new_location = 'testme'
    test_content = 'Here is the test content.'
    files = {'file': StringIO(test_content)}
    requests.post(BASE_URL + '/store/' + new_location, files=files)
    resp = requests.get(BASE_URL + '/store/' + new_location)
    assert resp.status_code == 200
    assert resp.content == test_content

    # Modify the original BLOB with a PUT request.
    new_content = 'Here is the new PUT content.'
    files = {'file': StringIO(new_content)}
    requests.put(BASE_URL + '/store/' + new_location, files=files)
    resp = requests.get(BASE_URL + '/store/' + new_location)
    assert resp.status_code == 200
    assert resp.content == new_content
    assert new_content != test_content

    # Add additional BLOB and check for existence.
    new_location = 'testme2'
    test_content = 'Here is the test content. Here is the difference'
    files = {'file': StringIO(test_content)}
    requests.post(BASE_URL + '/store/' + new_location, files=files)
    resp = requests.get(BASE_URL + '/store/' + new_location)
    assert resp.status_code == 200
    assert resp.content == test_content

    # Delete one entry and see if it still exist.
    delete_location = 'testme2'
    resp = requests.delete(BASE_URL + '/store/' + delete_location)
    assert resp.status_code == 200
    resp = requests.get(BASE_URL + '/store/' + delete_location)
    assert resp.status_code == 404
