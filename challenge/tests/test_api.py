import httplib
import unittest

from webapp import app


class APITests(unittest.TestCase):

    """ Unit testing where responses are mocked out from server. """

    def setUp(self):
        self.app = app.test_client()

    def test_admin(self):
        rv = self.app.get('/admin')
        assert rv.status_code == httplib.OK

    def test_bad_delete(self):
        rv = self.app.delete('/store/arbitrary_name_that_does_not_exist')
        assert rv.status_code == httplib.NOT_FOUND

    def test_bad_get(self):
        rv = self.app.get('/store/arbitrary_name_that_does_not_exist')
        assert rv.status_code == httplib.NOT_FOUND

    # TODO: Use mock to generate more unit tests or httpretty
    # to mock out HTTP responses.
