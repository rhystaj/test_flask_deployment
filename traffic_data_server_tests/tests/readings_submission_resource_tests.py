import unittest

import math
from datetime import datetime

from mongoengine import disconnect

from ..utils.mongo_testing_utils import connectToMockServer

from n3t_traffic_data_server.values import DATABASE_ALIAS
from n3t_traffic_data_server.flask_resources.readings_submission_resource \
import constructValidatedTrafficReading

from n3t_traffic_data_server.mongo_documents.station import RoadSide, Station, RoadPosition
from n3t_traffic_data_server.mongo_documents.traffic_reading import VehicleClass, ValidationLevel

TEST_VALIDATION_DATE_TIMESTAMP = datetime.strptime("2020-10-24 15:11:34", "%Y-%m-%d %H:%M:%S").timestamp()

STATION_A_ROAD_POSITION_STRING = "31_78, 7.17A"
STATION_B_ROAD_POSITION_STRING = "95_12, 54.22"
STATION_C_ROAD_POSITION_STRING = "627_55, 12.93B"

STATION_A_ROAD_POSITION = RoadPosition(regionId=31, roadId=78, position=7.17, roadSide=RoadSide.A)
STATION_B_ROAD_POSITION = RoadPosition(regionId=95, roadId=12, position=54.22)
STATION_C_ROAD_POSITION = RoadPosition(regionId=627, roadId=55, position=12.93, roadSide=RoadSide.B)

class ReadingsSubmissionResourceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connectToMockServer(DATABASE_ALIAS)

        Station(roadPosition=STATION_A_ROAD_POSITION, address="Station A", lat=10, lon=10).save()
        Station(roadPosition=STATION_B_ROAD_POSITION, address="Station B", lat=20, lon=20).save()


    @classmethod
    def tearDownClass(cls):
        disconnect()


    def test_constructValidatedTrafficReading_allDataValid_constructCorrectReadingWithFullValidationLevel(self):
        
        test_data = ["2020-05-25", "17:34:12", "35.87", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.FULL)

        self.assertEqual(result.dateTime, datetime.strptime("2020-05-25 17:34:12", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)


    def test_constructValidatedTrafficReading_speedValueHasUnit_stripUnitAndConsiderDataValid(self):
        
        test_data = ["2020-05-25", "17:34:12", "35.87 km/h", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87 km/h,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.FULL)

        self.assertEqual(result.dateTime, datetime.strptime("2020-05-25 17:34:12", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)


    def test_constructValidTrafficReading_directionRLeft_directionLeftToRightFalse(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "R-Left", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,R-Left,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.FULL)

        self.assertEqual(result.directionLeftToRight, False)


    def test_constructValidTrafficReading_directionLeftToRight_directionLeftToRightTrue(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "Left-to-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,Left-to-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.FULL)

        self.assertEqual(result.directionLeftToRight, True)


    def test_constructValidTrafficReading_directionRightToLeft_directionLeftToRightFalse(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "Right-to-Left", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,Right-to-Left,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.FULL)

        self.assertEqual(result.directionLeftToRight, False)


    def test_constructValidTrafficReading_roadPositionHasNoSideSuffix_dataStillValid(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "Right-to-Left", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_B_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,Right-to-Left,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.FULL)

        self.assertEqual(result.sourceRoadPosition, STATION_B_ROAD_POSITION)


    def test_constructValidTrafficReading_invalidDateFormat_constructReadingWithInvalidFormatValidationLevel(self):

        test_data = ["2020-30-25", "17:34:12", "35.87", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-30-25,17:34:12,35.87,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_FORMAT)

        self.assertIsNone(result.dateTime)
        
        #The other, valid, fields should still be populated.
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)

    
    def test_constructValidTrafficReading_invalidTimeFormat_constructReadingWithInvalidFormatValidationLevel(self):

        test_data = ["2020-05-25", "17:34:70", "35.87", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:70,35.87,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_FORMAT)

        self.assertIsNone(result.dateTime)
        
        #The other, valid, fields should still be populated.
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)


    def test_constructValidTrafficReading_invalidSpeedFormat_constructReadingWithInvalidFormatValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "35.87g", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87g,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_FORMAT)

        self.assertIsNone(result.speed)

        #The other, valid, fields should still be populated.
        self.assertEqual(result.dateTime, datetime.strptime("2020-05-25 17:34:12", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)

    
    def test_constructValidTrafficReading_invalidDirectionFormat_constructReadingWithInvalidFormatValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "F-Back", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,F-Back,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_FORMAT)

        self.assertIsNone(result.directionLeftToRight)

        #The other, valid, fields should still be populated.
        self.assertEqual(result.dateTime, datetime.strptime("2020-05-25 17:34:12", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)


    def test_constructValidTrafficReading_invalidClassFormat_constructReadingWithInvalidFormatValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "L-Right", "class-17-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,L-Right,class-17-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_FORMAT)

        self.assertIsNone(result.vehicleClass)

        #The other, valid, fields should still be populated.
        self.assertEqual(result.dateTime, datetime.strptime("2020-05-25 17:34:12", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.sourceRoadPosition, STATION_A_ROAD_POSITION)


    def test_constructValidTrafficReading_invalidSourceRoadPosition_constructReadingWithInvalidFormatValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, "completely and utterly invalid", TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_FORMAT)

        self.assertIsNone(result.sourceRoadPosition)

        #The other, valid, fields should still be populated.
        self.assertEqual(result.dateTime, datetime.strptime("2020-05-25 17:34:12", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(result.speed, 35.87)
        self.assertEqual(result.directionLeftToRight, True)
        self.assertEqual(result.vehicleClass, VehicleClass(main=2, sub=1))


    def test_constructValidTrafficReading_stationNotInDatabase_constructReadingWithInvalidDataValidationLevel(self):
        
        test_data = ["2020-05-25", "17:34:12", "35.87", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_C_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertEqual(result.sourceRoadPosition, STATION_C_ROAD_POSITION)

    
    def test_constructValidTrafficReading_dateAfterValidationDate_constructReadingWithInvalidDataValidationLevel(self):

        test_data = ["2020-11-25", "17:34:12", "35.87", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-11-25,17:34:12,35.87,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertEqual(result.dateTime, datetime.strptime("2020-11-25 17:34:12", "%Y-%m-%d %H:%M:%S"))


    def test_constructValidTrafficReading_speedIsNaN_constructReadingWithInvalidDataValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "NaN", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,NaN,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertTrue(math.isnan(result.speed), "result.speed should be nan, but is " + str(result.speed) + ".")


    def test_constructValidTrafficReading_speedNegative_constructReadingWithInvalidDataValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "-27.44", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,-27.44,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertEqual(result.speed, -27.44)


    def test_constructValidTrafficReading_speedExceedsMax_constructReadingWithInvalidDataValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "229.17", "L-Right", "class-2-1", "sdkfjb.nsdkjf.stationA"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,229.17,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertEqual(result.speed, 229.17)


    def test_constructValidTrafficReading_speedExceedsMax_constructReadingWithInvalidDataValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "229.17", "L-Right", "class-2-1"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,229.17,L-Right,class-2-1")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertEqual(result.speed, 229.17)


    def test_constructValidTrafficReading_subclassInvalidForClass_constructReadingWithInvalidDataValidationLevel(self):

        test_data = ["2020-05-25", "17:34:12", "35.87", "L-Right", "class-3-4"]
        result = constructValidatedTrafficReading(test_data, STATION_A_ROAD_POSITION_STRING, TEST_VALIDATION_DATE_TIMESTAMP)

        self.assertEqual(result.rawSourceData, "2020-05-25,17:34:12,35.87,L-Right,class-3-4")
        self.assertEqual(result.validationLevel, ValidationLevel.INVALID_DATA)

        #As the data has a valid format, it should still be populated, even if its value is invalid.
        self.assertEqual(result.vehicleClass, VehicleClass(main=3, sub=4))  



if __name__ == "__main__":
    unittest.main()