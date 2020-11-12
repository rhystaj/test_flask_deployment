from n3t_traffic_data_server.mongo_documents.traffic_reading import VehicleClass
from ..values import DATABASE_ALIAS

from mongoengine import Document, IntField, FloatField

#An entry for the estimate average weight for the vehicle of a class.
class EstimatedClassWeight(Document):

    vehicleClass = IntField(required=True, unique=True)
    weight = FloatField(required=True) #in tonnes


    meta = {
        "db_alias": DATABASE_ALIAS,
        "collection": "estimated_class_weights"
    }


    def __str__(self):
        return self.to_json()


    def __eq__(self, other: object) -> bool:
        return isinstance(other, EstimatedClassWeight) \
            and self.vehicleClass == other.VehicleClass \
            and self.weight == other.weight


    def __hash__(self) -> int:
        return hash(self.vehicleClass) + hash(self.weight)