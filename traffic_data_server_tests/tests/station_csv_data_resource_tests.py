import unittest

from mongoengine import disconnect

from ..utils.test_data_file_utils import readTrafficReadingsFromCSV

from n3t_traffic_data_server import configure_traffic_database

from n3t_traffic_data_server.flask_resources.station_csv_data_resource import generateCSVForStation

from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading

class StationCSVDataResourceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configure_traffic_database("localhost", 27017, "testhost")
              

    @classmethod
    def tearDownClass(cls):
        TrafficReading.objects().delete()
        disconnect()


    def test_generateCSVForStation_generatesCorrectCSV(self):

        test_readings = readTrafficReadingsFromCSV("traffic_data_server_tests\\test_data" +
                "\\input\\traffic_readings_b_some_invalid_data.csv")
        [ reading.save() for reading in test_readings ]

        expected_result = \
            "date,time,speed,direction,class\n" + \
            "2020-10-18,03:49:11,67.9,Right-To-Left,class-3-4\n" + \
            "2020-10-18,11:37:29,1.6,Left-To-Right,class-2-2\n" + \
            "2020-10-19,14:16:34,45.7,Left-To-Right,class-2-1\n"   

        result = generateCSVForStation("45_666, 23.44A")

        self.assertEqual(expected_result, result)


if __name__ == "__main__":
    unittest.main()