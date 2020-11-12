import mongoengine

from n3t_traffic_data_server import configure_traffic_database

from n3t_traffic_data_server.mongo_documents.station import Station
from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading
from n3t_traffic_data_server.mongo_documents.estimated_class_weight import EstimatedClassWeight

if __name__ == "__main__":

    configure_traffic_database("localhost", 27017, "test_traffic_db")
    
    Station.objects().delete()
    TrafficReading.objects().delete()
    EstimatedClassWeight.objects().delete()