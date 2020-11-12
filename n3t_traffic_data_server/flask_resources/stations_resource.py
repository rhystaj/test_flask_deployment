from flask_restful import Resource

from ..mongo_documents.station import Station

class StationsResource(Resource):

    def get(self):
        return [ 
            {
               "roadPosition" : str(station.roadPosition),
               "address" : station.address,
               "coordinates" : [station.lat, station.lon],
               "postedSpeedLimit" : station.postedSpeedLimit
            }
            for station in Station.objects.all()
        ] 