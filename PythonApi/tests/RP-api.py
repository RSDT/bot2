import unittest
import PythonApi.RPApi.Base as rp_api
import PythonApi.tests.mockrequests as mockrequests
rp_api.requests = mockrequests


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.api = rp_api.Api.get_instance('test', 'test')

    def tearDown(self):
        del self.api
        del rp_api.Api.instances['test']

    def test_same_instance(self):
        self.assertTrue(self.api is rp_api.Api.get_instance('test', 'test'))

    def test_something(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
