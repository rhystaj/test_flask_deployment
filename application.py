import n3t_traffic_data_server as server

if __name__ == "__main__":
    server.start_server(
        "mongodb+srv://rhys:10%26W5Y%5EUptG%23@deployment-experiment.5bxke.mongodb.net/test_traffic_db"
    )