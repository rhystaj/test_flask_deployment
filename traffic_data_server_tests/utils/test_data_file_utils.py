import csv
import json

from datetime import datetime
from typing import List

from n3t_traffic_data_server.mongo_documents.station import RoadPosition
from n3t_traffic_data_server.mongo_documents.traffic_reading import TrafficReading
from n3t_traffic_data_server.mongo_documents.estimated_class_weight import EstimatedClassWeight

'''
@summary: Create a traffic reading from a list representing a CSV row
is assumed to have valid data.
'''
def readTrafficReadingFromCSVRow(row: List[str]) -> TrafficReading:

    reading = TrafficReading()

    reading.dateTime = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    reading.speed = float(row[1])
    reading.directionLeftToRight = row[2].strip() == "true"
    reading.vehicleClass = TrafficReading.convertVehicleClassString(row[3].strip())

    roadPosition = RoadPosition()
    roadPosition.regionId = int(row[4].strip())
    roadPosition.roadId = int(row[5].strip())
    roadPosition.position = float(row[6].strip())
    roadPosition.roadSide = int(row[7].strip())
    reading.sourceRoadPosition = roadPosition

    reading.rawSourceData = ''.join([ s for s in row ])
    reading.validationLevel = int(float(row[8].strip()))

    return reading


'''
@summary: create a list of TrafficReadings from a csv file of test data.
It is assumed that the data is valid.
'''
def readTrafficReadingsFromCSV(filename: str) -> List[TrafficReading]:
    
    with open(filename) as csvFile:
        readings = [ readTrafficReadingFromCSVRow(row) for row in csv.reader(csvFile) ]
    
    return readings;


'''
@summary: create a list of EsitmatedClassWeights from a json file of test data.
'''
def readClassWeightsFromCSV(filename: str) -> List[EstimatedClassWeight]:

    weights_data = []
    with open(filename) as jsonFile:
        weights_data = json.load(jsonFile)

    return [ 
        EstimatedClassWeight(vehicleClass=datum['vehicleClass'], weight=datum['weight'])
        for datum in weights_data 
    ]