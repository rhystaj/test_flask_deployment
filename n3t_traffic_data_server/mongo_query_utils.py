from datetime import datetime
from enum import IntEnum

from .mongo_documents.station import RoadPosition
from .mongo_documents.traffic_reading import TrafficReading, ValidationLevel


LOOKUP_WEIGHTS_AGGREGATION_PIPELINE = [
    #Join to the estimated_class_weights table based on the TrafficReading's main class.
    #Note that the resulting field, classed 'classWeight' will contain an array that is
    #either empty or will contian a single class weight document. This is dealt with below.
    {
        "$lookup": {
            'from': 'estimated_class_weights',
            'localField': 'vehicleClass.main',
            'foreignField': 'vehicleClass',
            'as': 'classWeight'
        }
    },

    #Get the one estimated_class_weights entry from the array, or nothing if
    #the array is empty.   
    {
        "$addFields": {
            "classWeight": {
                "$cond": {
                    "if": { "$eq": [ 1, { "$size": "$classWeight" } ] },
                    "then": { "$arrayElemAt": [ "$classWeight", 0 ] },
                    "else": {}
                }
            } 
        }
    },

    #We are only interetsed in the 'weight' value of the entry, so
    #just get that.
    {
        "$addFields": {
            "classWeight": "$classWeight.weight"
        }
    }
]


'''
@summary: The granularity of points within a time period.
@important: The corresponing number should be kept in order of granularity.
'''
class TimeDataGranularity(IntEnum):

    Hourly = 0,
    HalfDaily = 1,
    Daily = 2,
    Weekly = 3


'''
Create a query for getting a date from the database of a specified granularity.
'''
def getDateByGranularityQuery(granularity: TimeDataGranularity) -> dict:

    date_parts_expression: dict = { 
        "isoWeekYear": { "$isoWeekYear": "$dateTime" },
        "isoWeek": { "$isoWeek": "$dateTime" } 
    }

    if granularity <= TimeDataGranularity.Daily:
        date_parts_expression["isoDayOfWeek"] = { "$isoDayOfWeek": "$dateTime" }

    if granularity == TimeDataGranularity.HalfDaily:
        date_parts_expression["hour"] = { 
            "$cond": {
                "if": { "$lt": [ { "$hour": "$dateTime" }, 12 ] }, "then": 0, "else": 12
            }
        }
    elif granularity <= TimeDataGranularity.Hourly:
        date_parts_expression["hour"] = { "$hour": "$dateTime" }

    return { "$dateFromParts": date_parts_expression }


'''
@description Creates a MongoDB query for the traffic reading for a station between a date range specified
by timestamps.
'''
def queryStationReadingsForDateRange(road_position_string, start_date_timestamp, end_date_timestamp):

    #Convert timestamps into datetimes.
    start_date = datetime.fromtimestamp(start_date_timestamp)
    end_date = datetime.fromtimestamp(end_date_timestamp)

    road_position = RoadPosition.parseFromString(road_position_string)

    return TrafficReading.objects(sourceRoadPosition=road_position,
                                  validationLevel__gte=ValidationLevel.FULL, #Data must be fully valid 
                                  dateTime__gte=start_date, 
                                  dateTime__lte=end_date) \
                         .order_by('dateTime') #Data should be ordered by the date it was recoreded.