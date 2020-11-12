from datetime import datetime

from flask_restful import Resource

from ...mongo_query_utils import queryStationReadingsForDateRange

class TrafficReadingsResource(Resource):

    def get(self, road_position_string, start_date_timestamp, end_date_timestamp):
        
        return [
            {
                'timestamp': datetime.timestamp(traffic_reading.dateTime),
                'speed': traffic_reading.speed,
                'directionLeftToRight': traffic_reading.directionLeftToRight,
                'vehicleClass': traffic_reading.vehicleClass.to_json()
            }
            for traffic_reading
            in queryStationReadingsForDateRange(road_position_string, start_date_timestamp, end_date_timestamp).all()
        ] 
            