from flask_restful import Resource

from .traffic_counts_resource import TimeDataGranularity

from ...mongo_query_utils import LOOKUP_WEIGHTS_AGGREGATION_PIPELINE, getDateByGranularityQuery, queryStationReadingsForDateRange

'''
Create a query for getting a date from the database of a specified granularity.
'''
def queryTrafficWeights(road_position_string: str, start_date_timestamp: int, end_date_timestamp: int, granularity: TimeDataGranularity):

    date_query = getDateByGranularityQuery(granularity)

    query_result = queryStationReadingsForDateRange(road_position_string, start_date_timestamp, end_date_timestamp).aggregate(
        
        LOOKUP_WEIGHTS_AGGREGATION_PIPELINE + 
        
        [
            {
                "$project": {
                    "recordingDate": date_query,
                    "classWeight": "$classWeight" #classWeight comes from LOOKUP_WEIGHTS_AGGREGATION_PIPELINE
                }
            },
            {
                "$group": {
                    "_id": "$recordingDate",
                    "totalWeight": { "$sum": "$classWeight" }
                }
            }
        ]

    )

    return list(query_result)


class TrafficWeightsResource(Resource):

    def get(self, road_position_string: str, start_date_timestamp: int, end_date_timestamp: int, granularity: TimeDataGranularity):
        return [
            {
                "timestamp": countReading["_id"].timestamp(),
                "totalWeight": countReading["totalWeight"]
            }
            for countReading 
            in queryTrafficWeights(road_position_string, start_date_timestamp, end_date_timestamp, granularity)
        ]
        