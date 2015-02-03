from datetime import datetime
import unittest
from WatcherLib import *

class WatcherTestCase(unittest.TestCase):

    def test_time(self):
        self.assertTrue(games_allowed([{"Tue": "15:30-16"}], datetime(2015, 1, 27, 15, 45)))
        self.assertTrue(games_allowed([{"Tue": "3:30-4"}, {"Wed": "0-12"}], datetime(2015, 1, 28, 0, 45)))
        self.assertFalse(games_allowed([{"Tue": "3:30-4"}, {"Wed": "0-12"}], datetime(2015, 1, 28, 12, 01)))
        self.assertTrue(games_allowed([{"Tue": "3:30-4"}, {"Tue": "0-12"}], datetime(2015, 1, 27, 0, 45)))



if __name__ == '__main__':
    unittest.main()