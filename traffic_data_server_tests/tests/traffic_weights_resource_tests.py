from n3t_traffic_data_server.mongo_documents.estimated_class_weight import EstimatedClassWeight
from n3t_traffic_data_server.mongo_query_utils import TimeDataGranularity
from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading
from n3t_traffic_data_server import configure_traffic_database
import unittest
import json

from datetime import datetime

from n3t_traffic_data_server.flask_resources.station_history_resources.traffic_weights_resource import queryTrafficWeights

from traffic_data_server_tests.utils.test_data_file_utils import readClassWeightsFromCSV, readTrafficReadingsFromCSV


from mongoengine import disconnect

from ..utils.dict_set_wrapper import dictSet


TEST_START_DATE = datetime.strptime("2020-11-01 00:00:00", "%Y-%m-%d %H:%M:%S")
TEST_END_DATE = datetime.strptime("2020-11-16 00:00:00", "%Y-%m-%d %H:%M:%S")


def readExpectedDateResultsFromJSONFile(filepath: str):

    jsonData = []
    with open(filepath) as jsonFile:
        jsonData = json.load(jsonFile)

    return [
        {
            "_id": datetime.strptime(data["_id"], "%Y-%m-%d %H:%M:%S"),
            "totalWeight": data["totalWeight"]
        }
        for data in jsonData
    ]


class TrafficCountsResourceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configure_traffic_database("localhost", 27017, "testhost")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_readings_c.csv")
        [ reading.save() for reading in test_readings ]

        test_weights = readClassWeightsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_weights.json")
        [ weight.save() for weight in test_weights ]
              

    @classmethod
    def tearDownClass(cls):
        TrafficReading.objects().delete()
        EstimatedClassWeight.objects().delete()
        disconnect()


    def test_queryTrafficWeights_hourlyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficWeights\\" +
            "hourlyGranularity_returnsCorrectWeights.json")

        result = queryTrafficWeights("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.Hourly)

        self.assertEqual(dictSet(expected_result), dictSet(result))

    
    def test_queryTrafficWeights_halfDailyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficWeights\\" +
            "halfDailyGranularity_returnsCorrectWeights.json")

        result = queryTrafficWeights("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.HalfDaily)

        self.assertEqual(dictSet(expected_result), dictSet(result))

    
    def test_queryTrafficWeights_dailyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficWeights\\" +
            "dailyGranularity_returnsCorrectWeights.json")

        result = queryTrafficWeights("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.Daily)

        self.assertEqual(dictSet(expected_result), dictSet(result))

    
    def test_queryTrafficWeights_weeklyGranularity_returnsCorrectResults(self):

        #NOTE: Due to some weird floating-point quirk, this test will fail as the totalWeight for
        #the week of 02/11/2020 will be returned as 164.144999999998, when it should be 164.145.
        #This probably isn't worth looking into for now, as otherwise the test runs fine.
        #It might be worth changing to a different value later on for cleaner output, but that
        #would involve modifying the test data, which will affect more than just this test.

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficWeights\\" +
            "weeklyGranularity_returnsCorrectWeights.json")

        result = queryTrafficWeights("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.Weekly)

        self.assertEqual(dictSet(expected_result), dictSet(result))
    

if __name__ == "__main__":
    unittest.main()