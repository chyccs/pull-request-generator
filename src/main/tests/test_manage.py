import unittest

from manage import _required


class TestManage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def test_required(self):
        self.assertFalse(_required('return title'))
        self.assertTrue(_required('fill me'))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
