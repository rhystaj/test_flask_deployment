import unittest

from datetime import datetime

from ..utils.mongo_testing_utils import connectToMockServer
from ..utils.test_data_file_utils import readTrafficReadingsFromCSV

from mongoengine import disconnect

from n3t_traffic_data_server.mongo_query_utils import TimeDataGranularity, getDateByGranularityQuery, queryStationReadingsForDateRange

from n3t_traffic_data_server.values import DATABASE_ALIAS
from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading

class MongoQueryUtilsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connectToMockServer(DATABASE_ALIAS)


    @classmethod
    def tearDown(cls):
        #Clear all readings from the database between tests to ensure a fresh database for each test.
        TrafficReading.objects().delete()


    @classmethod
    def tearDownClass(cls):
        disconnect()


    def test_queryStationReadingsForDateRange_returnsCorrectEntries(self):

        test_start_date = datetime.strptime("2020-10-18 11:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 8:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\traffic_readings_a.csv");
        expected_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\expected_outputs" + 
                "\\queryStationReadingsForDateRange_returnsCorrectEntries.csv");

        [ reading.save() for reading in test_readings ]

        actual_result_set = set(queryStationReadingsForDateRange("1_32,87.999A", datetime.timestamp(test_start_date),
            datetime.timestamp(test_end_date)))

        self.assertEqual(set(expected_readings), actual_result_set)

    
    def test_queryStationReadingsForDateRange_someReadingsInvalid_invalidReadingsFilteredOut(self):
        
        test_start_date = datetime.strptime("2020-10-18 02:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 15:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\"+
                "traffic_readings_b_some_invalid_data.csv");
        expected_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\expected_outputs" + 
                "\\queryStationReadingsForDateRange_someReadingsInvalid_invalidReadingsFilteredOut.csv");

        [ reading.save() for reading in test_readings ]

        actual_result_set = set(queryStationReadingsForDateRange("45_666, 23.44A", datetime.timestamp(test_start_date),
            datetime.timestamp(test_end_date)))

        self.assertEqual(set(expected_readings), actual_result_set)


    def test_queryStationReadingsForDateRange_readingsOrderedByDate(self):

        test_start_date = datetime.strptime("2020-10-18 02:00:00", "%Y-%m-%d %H:%M:%S")
        test_end_date = datetime.strptime("2020-10-19 15:00:00", "%Y-%m-%d %H:%M:%S")

        test_readings = readTrafficReadingsFromCSV(
            "traffic_data_server_tests\\test_data\\input\\"+
                "traffic_readings_a.csv");

        [ reading.save() for reading in test_readings ]

        actual_result_list = queryStationReadingsForDateRange("1_32, 87.999A", datetime.timestamp(test_start_date),
            datetime.timestamp(test_end_date)).all()

        for i in range(0, len(actual_result_list) - 1):
            self.assertLessEqual(actual_result_list[i].dateTime, actual_result_list[i + 1].dateTime)


    def test_getRecordingDateQueryForGranularity_hourlyGranularity_returnsCorrectQuery(self):

        expected_result = {
            "$dateFromParts": {
                "isoWeekYear" : { "$isoWeekYear" : "$dateTime" },
                "isoWeek" : { "$isoWeek" : "$dateTime" },
                "isoDayOfWeek" : { "$isoDayOfWeek" : "$dateTime" },
                "hour" : { "$hour" : "$dateTime" }
            }
        }

        result = getDateByGranularityQuery(TimeDataGranularity.Hourly)

        self.assertEqual(expected_result, result)


    def test_getRecordingDateQueryForGranularity_halfDailyGranularity_returnsCorrectQuery(self):

        expected_result = {
            "$dateFromParts": {
                "isoWeekYear" : { "$isoWeekYear" : "$dateTime" },
                "isoWeek" : { "$isoWeek" : "$dateTime" },
                "isoDayOfWeek" : { "$isoDayOfWeek" : "$dateTime" },
                "hour" : { 
                    "$cond" : {
                        "if" : { "$lt": [ { "$hour" : "$dateTime" }, 12 ] }, "then" : 0, "else" : 12 
                    } 
                }
            }
        }

        result = getDateByGranularityQuery(TimeDataGranularity.HalfDaily)

        self.assertEqual(expected_result, result)


    def test_getRecordingDateQueryForGranularity_dailyGranularity_returnsCorrectQuery(self):

        expected_result = {
            "$dateFromParts": {
                "isoWeekYear" : { "$isoWeekYear" : "$dateTime" },
                "isoWeek" : { "$isoWeek" : "$dateTime" },
                "isoDayOfWeek" : { "$isoDayOfWeek" : "$dateTime" }
            }
        }

        result = getDateByGranularityQuery(TimeDataGranularity.Daily)

        self.assertEqual(expected_result, result)


    def test_getRecordingDateQueryForGranularity_weeklyGranularity_returnsCorrectQuery(self):

        expected_result = {
            "$dateFromParts": {
                "isoWeekYear" : { "$isoWeekYear" : "$dateTime" },
                "isoWeek" : { "$isoWeek" : "$dateTime" }
            }
        }

        result = getDateByGranularityQuery(TimeDataGranularity.Weekly)

        self.assertEqual(expected_result, result)

        
if __name__ == "__main__":
    unittest.main();