import mongoengine

from n3t_traffic_data_server import configure_traffic_database

from n3t_traffic_data_server.mongo_documents.station import Station, RoadPosition

if __name__ == "__main__":

    configure_traffic_database(
        "mongodb+srv://rhys:10%26W5Y%5EUptG%23@deployment-experiment.5bxke.mongodb.net/test_traffic_db", 
        "test_traffic_db"
    )

    Station(roadPosition=RoadPosition.parseFromString("12_983, 815.77A"), 
            address="HATEA DR", lat=-35.721138, lon=174.323866, postedSpeedLimit=50).save()
    Station(roadPosition=RoadPosition.parseFromString("328_444, 77.2B"), 
            address="PORT RD", lat=-35.736422, lon=174.332623, postedSpeedLimit=60).save()
    Station(roadPosition=RoadPosition.parseFromString("599_6, 22.94B"), 
            address="OKARA DR", lat=-35.732706, lon=174.326999).save()