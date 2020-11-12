import unittest

from mongoengine.errors import ValidationError

from n3t_traffic_data_server.mongo_documents.station import RoadPosition, RoadSide

TEST_SIDE_SUFFIXES = ["", "A", "B"]

class RoadPositionTests(unittest.TestCase):

    def subtestParseValidStringWithEachPossibleSuffix(self, road_position_string: str, expected_road_position: RoadPosition):

        for suffix in TEST_SIDE_SUFFIXES:

            expected_road_side = RoadSide.parseFromString(suffix)
            expected_road_position.roadSide = expected_road_side

            result = RoadPosition.parseFromString(road_position_string + suffix)
            self.assertEqual(expected_road_position, result)


    def subtestParseInvalidStringWithEachPossibleSuffix(self, road_position_string: str):

        for suffix in TEST_SIDE_SUFFIXES:
            try:
                RoadPosition.parseFromString(road_position_string + suffix)
            except ValueError:
                pass


    def test_parseFromString_validRoadPosition_returnsRoadCorrectPositionObject(self):
        
        test_string = "1534_456, 33.55"
        expected_result = RoadPosition(regionId=1534, roadId=456, position=33.55)
        
        self.subtestParseValidStringWithEachPossibleSuffix(test_string, expected_result)


    def test_parseFromString_validRoadPositionWithNoSpaceAfterComma_returnsRoadCorrectPositionObject(self):
        
        test_string = "1534_456,33.55"
        expected_result = RoadPosition(regionId=1534, roadId=456, position=33.55)
        
        self.subtestParseValidStringWithEachPossibleSuffix(test_string, expected_result)


    def test_parseFromString_noRegionIdGiven_throwsValidationError(self):
    
        test_string = "456, 33.55"        
        
        self.subtestParseInvalidStringWithEachPossibleSuffix(test_string)


    def test_parseFromString_noRoadIdGiven_throwsValidationError(self):
    
        test_string = "1534, 33.55"        
        
        self.subtestParseInvalidStringWithEachPossibleSuffix(test_string)

    
    def test_parseFromString_noPositionGiven_throwsValidationError(self):

        test_string = "1534_456"

        self.subtestParseInvalidStringWithEachPossibleSuffix(test_string)


    def test_parseFromString_invalidSideLetter_thowsValidationError(self):

        test_string = "1534_456,33.55C"

        try:
            RoadPosition.parseFromString(test_string)
        except ValueError:
            pass


    def test_parseFromString_invalidString_throwsValidationError(self):

        test_string = "Totally Not Valid 123"

        self.subtestParseInvalidStringWithEachPossibleSuffix(test_string)


if __name__ == "__main__":
    unittest.main()