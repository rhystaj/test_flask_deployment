import json
import mongoengine

from n3t_traffic_data_server import configure_traffic_database

from n3t_traffic_data_server.mongo_documents.estimated_class_weight import EstimatedClassWeight


if __name__ == "__main__":

    configure_traffic_database("localhost", 27017, "test_traffic_db")

    EstimatedClassWeight.objects().delete()

    input_file_path = input('Input File: ')

    json_data = {}
    with open(input_file_path) as input_file:
        json_data = json.load(input_file)

    for vehicleClassString in json_data.keys():
        vehicleClass = int(float(vehicleClassString))
        EstimatedClassWeight(vehicleClass=vehicleClass, weight=json_data[vehicleClassString]).save()