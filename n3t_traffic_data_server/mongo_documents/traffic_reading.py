import re
from enum import IntEnum, unique

from ..values import DATABASE_ALIAS

from mongoengine import Document, EmbeddedDocument, DateTimeField, FloatField, BooleanField, StringField, \
                        IntField, EmbeddedDocumentField, ValidationError

from .station import RoadPosition

'''
@summary: Represents the level at which data is determined to be valid.
'''
@unique
class ValidationLevel(IntEnum):
    
    INVALID_FORMAT = 0 #The data from the source can't even be parsed properly and likely corrupted.
    INVALID_DATA = 1 #The data's format is valid, but does not produce a reliable reading.
    FULL = 2 #The data is correctly formatted and reliable.


def validateValidationLevel(validationLevel):
    if not (validationLevel in set([ l.value for l in ValidationLevel ])):
        raise ValidationError(str(validationLevel) + " is not a valid ValidationLevel.")


def validateClassString(classString):
    if not (TrafficReading.classStringHasValidFormat(classString)):
        raise ValidationError("'" + classString + "' is not a valid vehicle class string.")


class VehicleClass(EmbeddedDocument):

    main = IntField() #The vehicle's main class.
    sub = IntField() #The vehicle's sub class.

    
    def __str__(self) -> str:
        return "class-{0}-{1}".format(self.main, self.sub)


class TrafficReading(Document):

    dateTime = DateTimeField()
    speed = FloatField()
    directionLeftToRight = BooleanField()
    vehicleClass = EmbeddedDocumentField(VehicleClass)
    sourceRoadPosition = EmbeddedDocumentField(RoadPosition)
    validationLevel = IntField(required=True, validation=validateValidationLevel)
    rawSourceData = StringField(required=True)

    meta = {
        "db_alias": DATABASE_ALIAS,
        "collection": "traffic_readings"
    }

    
    '''
    @summary: Determine if a string representing a vehicle class is of the valid format, i.e
    "class-<1 to 14>-<1 to 9>"
    '''
    @classmethod
    def classStringHasValidFormat(cls, classString):

        #The string decribing the vehicle class should match "class-<1 to 14>-<1 to 9>",
        #e.g "class-11-3", but not "class-7" or "class-15-3"
        classRegexPattern = re.compile("^class-(([1-9])|(1[0-4]))-[1-9]$")
        
        return classRegexPattern.match(classString)
            

    @classmethod
    def convertVehicleClassString(cls, classString):

        if not cls.classStringHasValidFormat(classString):
            raise ValueError("The class string '" + classString + "' is not of the valid format.")

        classStringParts = classString.split("-")
        
        vehicleClass = VehicleClass()
        vehicleClass.main = int(float(classStringParts[1]))
        vehicleClass.sub = int(float(classStringParts[2]))

        return vehicleClass


    def __str__(self):
        return self.to_json();


    def __eq__(self, other):

        return isinstance(other, TrafficReading) \
            and self.dateTime == other.dateTime \
            and self.speed == other.speed \
            and self.directionLeftToRight == other.directionLeftToRight \
            and self.vehicleClass == other.vehicleClass \
            and self.sourceRoadPosition == other.sourceRoadPosition \
            and self.validationLevel == other.validationLevel


    def __hash__(self):
        return hash(self.dateTime) + hash(self.speed) + \
            hash(self.directionLeftToRight) + hash(self.vehicleClass.main) + hash(self.vehicleClass.sub) + \
            hash(self.sourceRoadPosition) + hash(self.validationLevel)
        

        