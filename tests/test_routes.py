import unittest
from types import SimpleNamespace
from aiohttp import web
from genereticore.routes import require_local

class RouteTests(unittest.TestCase):
    def request(self, remote='127.0.0.1', origin='http://127.0.0.1:8003'):
        return SimpleNamespace(remote=remote, headers={'Origin':origin}, host='127.0.0.1:8003')
    def test_loopback_only(self):
        require_local(self.request())
        require_local(self.request('::1'))
        with self.assertRaises(web.HTTPForbidden): require_local(self.request('192.168.0.4'))
    def test_cross_origin_rejected(self):
        with self.assertRaises(web.HTTPForbidden): require_local(self.request(origin='https://example.com'))

if __name__ == '__main__': unittest.main()
