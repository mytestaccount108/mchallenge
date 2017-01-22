import logging
import os

from flask import (
    Flask,
    abort,
    render_template,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

from helpers import get_storage_path, has_enough_space


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = get_storage_path()

log = logging.getLogger(__name__)

"""
Entry point for BLOB storage API.

Requirements:
* POST /store/<location> - Create new blob at location
* PUT /store/<location> - Update, or replace blob
* GET /store/<location> - Get blob
* DELETE /store/<location> - Delete blob
"""


@app.route('/admin')
def admin():
    """ Health check endpoint to ensure that server is up. """
    return 'GOOD'


@app.route('/debug/upload-page')
def upload_page():
    """ A page to upload files for debugging purposes. """
    return render_template('upload.html')


def _create_blob(location):
    """ Handle the creation logic for a new blob.
    :param location: The location we want to create the blob at.
    :return: The return code.
    :rtype: int
    """
    if location == '':
        abort(400, 'Location for blob is missing from client request.')

    if 'file' not in request.files:
        # Raise HTTP error to signal bad input.
        abort(400, 'File is missing from client request.')

    file = request.files['file']

    if file.filename == '':
        # Raise HTTP error to signal missing file.
        abort(400, 'Filename is missing from client request.')

    # Sanitizes input to ensure secure filename.
    filename = secure_filename(location)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return '200'


def _delete_blob(location):
    """ Handle the deletion logic for a new blob.
    :param location: The location we want to delete the blob at.
    :return: The return code.
    :rtype: int
    """
    try:
        os.remove(app.config['UPLOAD_FOLDER'] + '/' + location)
    except OSError:
        abort(404, 'Location could not be found')
    return '200'


@app.route('/store/<location>', methods=['POST'])
def post_blob(location):
    """ Create a new blob at the location.
    # TODO: If file already exist, we need to throw an exception.
    """
    if not has_enough_space():
        abort(507, 'Rejecting request due to limited disk space.')
    if os.path.isfile(app.config['UPLOAD_FOLDER'] + '/' + location):
        abort(422,
              'Trying to add new BLOB when one already exist at location.')
    return _create_blob(location)


@app.route('/store/<location>', methods=['PUT'])
def put_blob(location):
    """ Idempotent request to update or replace the blob. """
    if not has_enough_space():
        abort(507, 'Rejecting request due to limited disk space.')
    # We should also look into not doing a complete deletion especially if
    # contents doesn't change or if this only for instance, an append
    # only action.
    _delete_blob(location)
    return _create_blob(location)


@app.route('/store/<location>')
def get_blob(location):
    """ Get back the blog given the location. """
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               location)


@app.route('/store/<location>', methods=['DELETE'])
def delete_blob(location):
    """ Delete a blob at a given location. """
    return _delete_blob(location)


if __name__ == "__main__":
    # Start server with debug settings.
    # TODO: Move to click, argparse, optparse, etc.
    # Use manage.py for this type of functionality.
    app.config['UPLOAD_FOLDER'] = get_storage_path(test=True)
    app.run(port=20333, debug=True)
