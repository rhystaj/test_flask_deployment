from n3t_traffic_data_server.mongo_query_utils import TimeDataGranularity
from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading
from n3t_traffic_data_server import configure_traffic_database
import unittest
import json

from datetime import datetime

from traffic_data_server_tests.utils.test_data_file_utils import readTrafficReadingsFromCSV


from mongoengine import disconnect

from ..utils.mongo_testing_utils import connectToMockServer
from ..utils.dict_set_wrapper import dictSet

from n3t_traffic_data_server.values import DATABASE_ALIAS

from n3t_traffic_data_server.flask_resources.station_history_resources.traffic_counts_resource import queryTrafficCounts

TEST_START_DATE = datetime.strptime("2020-11-01 00:00:00", "%Y-%m-%d %H:%M:%S")
TEST_END_DATE = datetime.strptime("2020-11-16 00:00:00", "%Y-%m-%d %H:%M:%S")


def readExpectedDateResultsFromJSONFile(filepath: str):

    jsonData = []
    with open(filepath) as jsonFile:
        jsonData = json.load(jsonFile)

    return [
        {
            "_id": datetime.strptime(data["_id"], "%Y-%m-%d %H:%M:%S"),
            "trafficCount": data["trafficCount"]
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
              

    @classmethod
    def tearDownClass(cls):
        TrafficReading.objects().delete()
        disconnect()


    def test_queryTrafficCounts_hourlyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficCounts\\" +
            "hourlyGranularity_returnsCorrectCounts.json")

        result = queryTrafficCounts("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.Hourly)

        self.assertEqual(dictSet(expected_result), dictSet(result))


    def test_queryTrafficCounts_halfDailyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficCounts\\" +
            "halfDailyGranularity_returnsCorrectCounts.json")

        result = queryTrafficCounts("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.HalfDaily)

        self.assertEqual(dictSet(expected_result), dictSet(result))


    def test_queryTrafficCounts_dailyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficCounts\\" +
            "dailyGranularity_returnsCorrectCounts.json")

        result = queryTrafficCounts("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.Daily)

        self.assertEqual(dictSet(expected_result), dictSet(result))


    def test_queryTrafficCounts_weeklyGranularity_returnsCorrectResults(self):

        expected_result = readExpectedDateResultsFromJSONFile(
            "traffic_data_server_tests\\test_data\\expected_outputs\\queryTrafficCounts\\" +
            "weeklyGranularity_returnsCorrectCounts.json")

        result = queryTrafficCounts("6_33, 38.33A", TEST_START_DATE.timestamp(), TEST_END_DATE.timestamp(), 
            TimeDataGranularity.Weekly)

        self.assertEqual(dictSet(expected_result), dictSet(result))


if __name__ == "__main__":
    unittest.main()