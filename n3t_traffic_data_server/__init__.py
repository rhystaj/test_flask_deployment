from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource

from mongoengine import connect

from .values import DATABASE_ALIAS

from .flask_resources.stations_resource import StationsResource
from .flask_resources.station_history_resources.traffic_readings_resource import TrafficReadingsResource
from .flask_resources.readings_submission_resource import ReadingsRawCSVSubmissionResource
from .flask_resources.station_history_resources.station_summary_resource import StationSummaryResource
from .flask_resources.station_history_resources.traffic_counts_resource import TrafficCountsResource
from .flask_resources.station_history_resources.class_counts_resource import ClassCountsResource
from .flask_resources.station_history_resources.traffic_weights_resource import TrafficWeightsResource
from .flask_resources.station_csv_data_resource import StationDataCSVResource


def configure_traffic_database(host_url):
    connect(
        alias=DATABASE_ALIAS,
        host=host_url
    )

def start_server(mongo_host_url):
    
    #Create the API
    flaskApp = Flask(__name__)
    cors = CORS(flaskApp)
    api = Api(flaskApp)


    #Configure the Mongo connection.
    configure_traffic_database(mongo_host_url)


    #Add the api resources.
    stations_query = "/stations"
    specific_station_query = stations_query + "/<string:road_position_string>"
    station_history_query = specific_station_query + "/history/<int:start_date_timestamp>/<int:end_date_timestamp>"

    api.add_resource(StationsResource, "/stations")
    api.add_resource(TrafficReadingsResource, station_history_query)
    api.add_resource(ReadingsRawCSVSubmissionResource, "/submitReadings/<string:road_position_string>/raw-csv")
    api.add_resource(StationSummaryResource, station_history_query + "/summary")
    api.add_resource(ClassCountsResource, station_history_query + "/classCounts")
    api.add_resource(TrafficCountsResource, station_history_query + "/trafficCounts/<int:granularity>")
    api.add_resource(TrafficWeightsResource, station_history_query + "/trafficWeights/<int:granularity>")
    api.add_resource(StationDataCSVResource, specific_station_query + "/csv")
    

    #Start the server
    flaskApp.run(debug=True)