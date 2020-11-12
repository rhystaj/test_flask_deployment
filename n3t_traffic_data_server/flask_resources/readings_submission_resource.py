import re
import csv
import math
from io import StringIO

from datetime import datetime
from time import time

from flask_restful import Resource, request

from ..mongo_documents.station import Station, RoadPosition
from ..mongo_documents.traffic_reading import TrafficReading, ValidationLevel

#The strings that express valid traffic directions.
LEFT_TO_RIGHT_STRINGS = ["L-Right", "Left-to-Right"] #i.e directionLeftToRight = True
RIGHT_TO_LEFT_STRINGS = ["R-Left", "Right-to-Left"] #i.e. directionLeftToRight = False

#A class string is of the form "class-<C>-<S>". 
#MAX_SUBCLASS_BY_CLASS[C - 1] gives the max value S should be, given C. 
MAX_SUBCLASS_BY_CLASS = [1, 1, 3, 4, 7, 3, 3, 5, 7, 6, 3, 9, 7, 1, 1]

MAX_VALID_SPEED = 200 #Any speeds recorded over this value should be considered invalid.

'''
@summary: Create a TrafficReading from a list representing a CSV row. Set the
TrafficReading's validation level based on the validity of the given data.
@param: readingData The data that validated and used to contruct the reading
@param validationTimestamp: The system time at which the validation should be considered
as occuring.
'''
def constructValidatedTrafficReading(readingData, road_position_string, validationTimestamp):

    reading = TrafficReading()
    reading.rawSourceData = ','.join([ s for s in readingData ])    
    #Assume data is valid, the level will be dropped if invalid data is found.
    reading.validationLevel = ValidationLevel.FULL 

    #Attempt to parse the date and time. 
    try:
        reading.dateTime = datetime.strptime(readingData[0] + " " + readingData[1], "%Y-%m-%d %H:%M:%S")
    except(ValueError):
        reading.validationLevel = ValidationLevel.INVALID_FORMAT

    #Attempt to parse the speed as a float.
    try:
        reading.speed = float(readingData[2].split(" ")[0])
    except(ValueError):
        reading.validationLevel = ValidationLevel.INVALID_FORMAT
    
    #Validate format of the string describing direction.
    if(readingData[3] in LEFT_TO_RIGHT_STRINGS + RIGHT_TO_LEFT_STRINGS):
        reading.directionLeftToRight = readingData[3] in LEFT_TO_RIGHT_STRINGS
    else:
        reading.validationLevel = ValidationLevel.INVALID_FORMAT
    
    #Validate format of the string describing the vechile class.
    if TrafficReading.classStringHasValidFormat(readingData[4]):
        reading.vehicleClass = TrafficReading.convertVehicleClassString(readingData[4])
    else:
        reading.validationLevel = ValidationLevel.INVALID_FORMAT

    #Validate the format of the road_position string.
    try:
        reading.sourceRoadPosition = RoadPosition.parseFromString(road_position_string)
    except ValueError:
        reading.validationLevel = ValidationLevel.INVALID_FORMAT

    #If the data has passed all format validation checks, then the values of the
    #data itself can be validated.
    if(reading.validationLevel != ValidationLevel.INVALID_FORMAT):

        #The station referenced by the data should be a station in the database.
        if Station.objects(roadPosition=reading.sourceRoadPosition).first() == None:
            reading.validationLevel = ValidationLevel.INVALID_DATA

        #Any data dated after the time at which the data is being validated should
        #be considered speculative data, which we are not interested in.
        if reading.dateTime.timestamp() > validationTimestamp:
            reading.validationLevel = ValidationLevel.INVALID_DATA

        #The speed should be a positive number that does not excceed the max valid speed. 
        if math.isnan(reading.speed) or reading.speed < 0 or reading.speed > MAX_VALID_SPEED:
            reading.validationLevel = ValidationLevel.INVALID_DATA

        #The subclass should be correct considering the class, i.e. should not exceed the
        #max subclass the class is expected to have, e.g class 5 has 7 expected subclasses,
        #so "class-5-9" would be an invalid value for the vehicle class.
        if(reading.vehicleClass.sub > MAX_SUBCLASS_BY_CLASS[reading.vehicleClass.main - 1]):
            reading.validationLevel = ValidationLevel.INVALID_DATA

    return reading


class ReadingsRawCSVSubmissionResource(Resource):

    def post(self, road_position_string):
        
        text_data = request.get_data().decode("utf-8"); #Get the request body text as a string
        dataReader = csv.reader(StringIO(text_data), delimiter=",") #Parse the body text as csv data
        
        currentTime = time()
        for reading in dataReader:
            constructValidatedTrafficReading(reading, road_position_string, currentTime).save()