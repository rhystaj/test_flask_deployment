from flask_restful import Resource

from ..mongo_documents.station import RoadPosition
from ..mongo_documents.traffic_reading import TrafficReading, ValidationLevel

'''
@summary: generate a string containing the contents of a CSV file recording each of the traffic
readings for a station.
'''
def generateCSVForStation(station_road_position_string: str) -> str:

    road_position = RoadPosition.parseFromString(station_road_position_string)
    query = TrafficReading.objects(sourceRoadPosition=road_position, validationLevel__gte=ValidationLevel.FULL)

    csv_rows = ['date,time,speed,direction,class\n'] + [
        ','.join([
            reading.dateTime.strftime("%Y-%m-%d"),
            reading.dateTime.strftime("%H:%M:%S"),
            str(reading.speed),
            "Left-To-Right" if reading.directionLeftToRight else "Right-To-Left",
            str(reading.vehicleClass)
        ]) + "\n"
        for reading in query
    ]

    return ''.join(csv_rows)


class StationDataCSVResource(Resource):

    def get(self, road_position_string: str):
        return generateCSVForStation(road_position_string)