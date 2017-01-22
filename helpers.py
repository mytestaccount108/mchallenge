import os

import psutil


def get_storage_path(test=False):
    """ Get the storage path where the blobs will be held.
    Set the test flag to true if you want the testing path.
    :returns: An absolute path.
    :rtype: str
    """
    cwd = os.getcwd()
    if test:
        return os.path.join(cwd, 'test_storage')
    else:
        return os.path.join(cwd, 'storage')


def get_executable_path():
    """ Get the path for the executable.
    :returns: An absolute path.
    :rtype: str
    """
    cwd = os.getcwd()
    return os.path.join(cwd, 'bin', 'challenge-executable')


def has_enough_space():
    """ Reject requests when diskspace left is less than 5%
    # TODO: This needs to be more complex where we consider space left
    on mount and space of BLOB being inserted.
    :returns: Whether you should still take request.
    :rtype: bool
    """
    return psutil.disk_usage('/')[3] > 5
