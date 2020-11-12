import unittest

from datetime import datetime
import json

from mongoengine import connect, disconnect

from ..utils.mongo_testing_utils import connectToMockServer
from ..utils.test_data_file_utils import readTrafficReadingsFromCSV
from ..utils.dict_set_wrapper import dictSet

from n3t_traffic_data_server.values import DATABASE_ALIAS
from n3t_traffic_data_server.flask_resources.station_history_resources.class_counts_resource import queryClassCounts

class ClassCountsResourceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connectToMockServer(DATABASE_ALIAS)


    @classmethod
    def tearDownClass(cls):
        disconnect()


    def test_queryClassCounts_returnsCorrectClassCounts(self):
        
        test_start_date = datetime.strptime("2020-10-18 00:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-20 00:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_readings_a.csv")
        [ reading.save() for reading in test_readings ]
        
        expected_json_file_path = 'traffic_data_server_tests\\test_data\\expected_outputs\\queryClassCounts_returnsCorrectClassCounts.json'
        expected_counts = []
        with open(expected_json_file_path) as json_file:
            expected_counts = dictSet(json.load(json_file))

        result = queryClassCounts("45_653, 12.3B", datetime.timestamp(test_start_date), 
                datetime.timestamp(test_end_date))

        self.assertEqual(dictSet(result), expected_counts)    



if __name__ == "__main__":
    unittest.main();