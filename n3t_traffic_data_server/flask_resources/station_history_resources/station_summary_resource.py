from flask_restful import Resource

from ...mongo_query_utils import LOOKUP_WEIGHTS_AGGREGATION_PIPELINE, queryStationReadingsForDateRange

def queryStationSummary(road_position_string, start_date_timestamp, end_date_timestamp):
        
    query = queryStationReadingsForDateRange(road_position_string, start_date_timestamp, end_date_timestamp).aggregate(
        
        LOOKUP_WEIGHTS_AGGREGATION_PIPELINE + 
        
        [
            #Aggregate the required summary fields for each direction.
            {
                "$group": {
                    "_id": "$directionLeftToRight",
                    "trafficCount": { "$sum": 1 },
                    "minSpeed": { "$min": "$speed" },
                    "averageSpeed": { "$avg": "$speed" },
                    "maxSpeed": { "$max": "$speed" },
                    "weight": { "$sum": "$classWeight" }
                }
            }
        ]
        
    )

    query_results_list = list(query)

    #If there is no data for a direction retrieved from the query, then add zero values for that direction.
    while len(query_results_list) < 2:
        directionLeftToRight = False if len(query_results_list) <= 0 else bool(abs(int(query_results_list[0]["_id"]) - 1))
        query_results_list.append({
            "_id": directionLeftToRight,
            "trafficCount": 0,
            "minSpeed": 0,
            "averageSpeed": 0,
            "maxSpeed": 0,
            "weight": 0
        })
    
    #Ensuring the results are in a consistent order by thier direction will make the next bit easier.
    query_results_list.sort(key=lambda entry: entry["_id"])

    def constructDirectionalDataDict(query_results_list, property_name):
        return { 
            "leftToRight": query_results_list[1][property_name], 
            "rightToLeft": query_results_list[0][property_name] 
        }

    return {
        "trafficCount": constructDirectionalDataDict(query_results_list, "trafficCount"),
        "minSpeed": constructDirectionalDataDict(query_results_list, "minSpeed"),
        "averageSpeed": constructDirectionalDataDict(query_results_list, "averageSpeed"),
        "maxSpeed": constructDirectionalDataDict(query_results_list, "maxSpeed"),
        "weight": constructDirectionalDataDict(query_results_list, "weight")
    }


class StationSummaryResource(Resource):
    
    def get(self, road_position_string, start_date_timestamp, end_date_timestamp):
      return queryStationSummary(road_position_string, start_date_timestamp, end_date_timestamp)  


        