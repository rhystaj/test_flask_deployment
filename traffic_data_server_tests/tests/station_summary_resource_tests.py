from datetime import datetime
from traffic_data_server_tests.utils.test_data_file_utils import readTrafficReadingsFromCSV
import unittest

from mongoengine import disconnect

from ..utils.mongo_testing_utils import connectToMockServer

from n3t_traffic_data_server.values import DATABASE_ALIAS

from n3t_traffic_data_server.flask_resources.station_history_resources.station_summary_resource import queryStationSummary

from n3t_traffic_data_server.mongo_documents.station import Station, RoadPosition
from n3t_traffic_data_server.mongo_documents.estimated_class_weight import EstimatedClassWeight
from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading

TEST_STATION_ROAD_POSITION_STRING = "45_653, 12.3B"

class TrafficReadingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connectToMockServer(DATABASE_ALIAS)

        Station(roadPosition=RoadPosition.parseFromString(TEST_STATION_ROAD_POSITION_STRING), 
                address="456 Paramount Pde", lat=20, lon=20).save()

        EstimatedClassWeight(vehicleClass=3, weight=3).save()
        EstimatedClassWeight(vehicleClass=10, weight=5).save()


    @classmethod
    def tearDown(cls):
        #Clear the reading to ensure a fresh collection for each test.
        TrafficReading.objects().delete()                


    @classmethod
    def tearDownClass(cls):
        disconnect()


    def test_queryStationSummary_readingsForLeftAndRight_returnsCorrectSummary(self):

        test_start_date = datetime.strptime("2020-10-18 2:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 23:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_readings_a.csv");

        [ reading.save() for reading in test_readings ]

        expectedResult = {
            "trafficCount": { "leftToRight": 3, "rightToLeft": 4 },
            "minSpeed": { "leftToRight": 1.6, "rightToLeft":  3.9 },
            "averageSpeed": { "leftToRight": 38.4, "rightToLeft": 53.75 },
            "maxSpeed": { "leftToRight": 67.9, "rightToLeft": 150.1 },
            "weight": { "leftToRight": 3.0, "rightToLeft": 8.0 }
        }

        result = queryStationSummary(TEST_STATION_ROAD_POSITION_STRING, test_start_date.timestamp(), test_end_date.timestamp())

        self.assertEqual(expectedResult, result)


    def test_queryStationSummary_readingsForJustLeftToRight_returnsCorrectSummaryWith0ValuesForRightToLeft(self):

        test_start_date = datetime.strptime("2020-10-18 2:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 23:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_readings_a.csv");

        for reading in test_readings:
            reading.directionLeftToRight = True
            reading.save()

        expectedResult = {
            "trafficCount": { "leftToRight": 7, "rightToLeft": 0 },
            "minSpeed": { "leftToRight": 1.6, "rightToLeft":  0 },
            "averageSpeed": { "leftToRight": 47.171428571428571428571428571429, "rightToLeft": 0 },
            "maxSpeed": { "leftToRight": 150.1, "rightToLeft": 0 },
            "weight": { "leftToRight": 11.0, "rightToLeft": 0 }
        }

        result = queryStationSummary(TEST_STATION_ROAD_POSITION_STRING, test_start_date.timestamp(), test_end_date.timestamp())

        self.assertEqual(expectedResult, result)


    def test_queryStationSummary_readingsForJustRightToLeft_returnsCorrectSummaryWith0ValuesForLeftToRight(self):

        test_start_date = datetime.strptime("2020-10-18 2:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 23:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_readings_a.csv");

        for reading in test_readings:
            reading.directionLeftToRight = False
            reading.save()

        expectedResult = {
            "trafficCount": { "leftToRight": 0, "rightToLeft": 7 },
            "minSpeed": { "leftToRight": 0, "rightToLeft":  1.6 },
            "averageSpeed": { "leftToRight": 0, "rightToLeft": 47.171428571428571428571428571429 },
            "maxSpeed": { "leftToRight": 0, "rightToLeft": 150.1 },
            "weight": { "leftToRight": 0, "rightToLeft": 11.0 }
        }

        result = queryStationSummary(TEST_STATION_ROAD_POSITION_STRING, test_start_date.timestamp(), test_end_date.timestamp())

        self.assertEqual(expectedResult, result)


    def test_queryStationSummary_noReadings_returnsCorrectSummaryWithAll0Values(self):

        test_start_date = datetime.strptime("2020-10-18 2:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 23:00:00", "%Y-%m-%d %H:%M:%S")

        #Don't add any readings.

        expectedResult = {
            "trafficCount": { "leftToRight": 0, "rightToLeft": 0 },
            "minSpeed": { "leftToRight": 0, "rightToLeft":  0 },
            "averageSpeed": { "leftToRight": 0, "rightToLeft": 0 },
            "maxSpeed": { "leftToRight": 0, "rightToLeft": 0 },
            "weight": { "leftToRight": 0, "rightToLeft": 0 }
        }

        result = queryStationSummary(TEST_STATION_ROAD_POSITION_STRING, test_start_date.timestamp(), test_end_date.timestamp())

        self.assertEqual(expectedResult, result)
    


if __name__ == "__main__":
    unittest.main()