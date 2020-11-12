import unittest

from mongoengine import disconnect, ValidationError

from ..utils.mongo_testing_utils import connectToMockServer

from n3t_traffic_data_server.values import DATABASE_ALIAS
from n3t_traffic_data_server.mongo_documents.traffic_reading \
import TrafficReading, validateClassString, validateValidationLevel

class TrafficReadingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connectToMockServer(DATABASE_ALIAS)


    @classmethod
    def tearDownClass(cls):
        disconnect()


    def test_validateValidationLevel_validValidationLevel_functionSucceeds(self):

        def attemptToValidateValidValue(value):
            try:
                validateValidationLevel(value)
            except ValidationError as e :
                self.fail("A validation error thrown for ValidationLevel '" +
                        str(value) + "' when it should not have been.")

        attemptToValidateValidValue(0)
        attemptToValidateValidValue(1)
        attemptToValidateValidValue(2)


    def test_validateValidationLevel_invalidValidationLevel_functionRaisesValidationError(self):

        try:
            validateValidationLevel(5)
            self.fail("A invalid ValidationLevel value should cause a ValidationError to be thrown.")
        except ValidationError:
            pass #The error just needs to be caught, no futher action needed.

    
    def test_classStringHasValidFormat_validClassNumber_returnsTrue(self):
        for class_number in range(1, 15):
            for subclass_number in range(1, 10):
                class_string = "class-"+ str(class_number) + "-" + str(subclass_number)
                self.assertTrue(TrafficReading.classStringHasValidFormat(class_string),
                        "Class string '" + class_string + "' should be considered valid, but wasn't.")


    def test_classStringHasValidFromat_stringNotClassString_returnsFalse(self):
        self.assertFalse(TrafficReading.classStringHasValidFormat("random_string_123"))


    def test_classStringHasValidFormat_classSpeltIncorrectly_returnsFalse(self):
        self.assertFalse(TrafficReading.classStringHasValidFormat("clss-3-6"))

    
    def test_classStringHasValidFormat_classNegative_returnsFalse(self):
        self.assertFalse(TrafficReading.classStringHasValidFormat("class--4-3"))

    
    def test_classStringHasValidFormat_subclassNegative_returnsFalse(self):
        self.assertFalse(TrafficReading.classStringHasValidFormat("class-4--3"))


    def test_classStringHasValidFormat_classNumberOver14_returnsFalse(self):
        self.assertFalse(TrafficReading.classStringHasValidFormat("class-17-3"))

    
    def test_classStringHasValidFormat_subclassNumberOver9_returnsFalse(self):
        self.assertFalse(TrafficReading.classStringHasValidFormat("class-5-10"))


if __name__ == "__main__":
    unittest.main()