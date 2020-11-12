from enum import IntEnum

from flask_restful import Resource

from ...mongo_documents.traffic_reading import TrafficReading

from datetime import datetime

from ...mongo_query_utils import TimeDataGranularity, getDateByGranularityQuery, queryStationReadingsForDateRange

def queryTrafficCounts(road_position_string: str, start_date_timestamp: int, end_date_timestamp: int, granularity: TimeDataGranularity):

    date_query = getDateByGranularityQuery(granularity)

    query_result = queryStationReadingsForDateRange(road_position_string, start_date_timestamp, end_date_timestamp).aggregate(
        [
            {
                "$project": {
                    "recordingDate": date_query
                }
            },
            {
                "$group": {
                    "_id": "$recordingDate",
                    "trafficCount": { "$sum": 1 }
                }
            }
        ]
    )

    return list(query_result)


class TrafficCountsResource(Resource):

    def get(self, road_position_string: str, start_date_timestamp: int, end_date_timestamp: int, granularity: TimeDataGranularity):
        return [
            {
                "timestamp": countReading["_id"].timestamp(),
                "count": countReading["trafficCount"]
            }
            for countReading 
            in queryTrafficCounts(road_position_string, start_date_timestamp, end_date_timestamp, granularity)
        ]
        