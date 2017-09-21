import unittest

import requests


class TestRequests(unittest.TestCase):

    def test_HTTP_200_OK_GET(self):
        r = requests.get("http://www.baidu.com")
        self.assertEqual(r.status_code, 200)


if __name__ == '__main__':
    unittest.main()

