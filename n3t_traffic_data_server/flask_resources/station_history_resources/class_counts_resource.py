from flask_restful import Resource

from ...mongo_query_utils import queryStationReadingsForDateRange

'''
@description Retrieve the counts for each class recorded by a station within a date range specified by timestamps.
'''
def queryClassCounts(road_position_string, start_date_timestamp, end_date_timestamp):

    countQuery = queryStationReadingsForDateRange(road_position_string, start_date_timestamp, end_date_timestamp).aggregate(
        [
            {
                "$group": {
                    "_id": "$vehicleClass.main",
                    "trafficCount": { "$sum": 1 }
                }
            }
        ]
    )

    return [
        {
            "vehicleClass": class_count["_id"],
            "trafficCount": class_count["trafficCount"]
        }
        for class_count
        in list(countQuery)
    ]


class ClassCountsResource(Resource):

    def get(self, road_position_string, start_date_timestamp, end_date_timestamp):
        return queryClassCounts(road_position_string, start_date_timestamp, end_date_timestamp)
    