import unittest
from utils import sanitize_filename

class TestSanitize(unittest.TestCase):
    
    def test_sanitize(self):
        self.assertEqual(sanitize_filename('a/\\:*?"<>|'), 'a_________')

if __name__ == '__main__':
    unittest.main()