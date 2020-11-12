from enum import IntEnum

from mongoengine.fields import SequenceField

import re

from ..values import DATABASE_ALIAS

from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, \
                        StringField, FloatField, IntField, ValidationError


class RoadSide(IntEnum):
    
    A = 1,
    B = 2

    @classmethod
    def parseFromString(cls, roadSideString):

        if roadSideString in ["", None]:
            return None

        elif roadSideString == "A":
            return RoadSide.A

        elif roadSideString == "B":
            return RoadSide.B

        else:
            raise ValueError("'" + roadSideString + "' is not a valid RoadSide");


def validateRoadSide(roadSide):
    if not (roadSide in set([ rs.value for rs in RoadSide ])):
        raise ValidationError(message=str(roadSide) + " is not a valid RoadSide value.");


class RoadPosition(EmbeddedDocument):

    '''
    @summary: Create a road position document from a string describing it, if that string is valid.
    Throw a ValueError otherwise.
    '''
    @classmethod
    def parseFromString(cls, road_position_string):

        rp_string_regex = re.compile("^[0-9]+_[0-9]+,( )?[0-9]+(\.[0-9]+)?(A|B)?$")
        rp_string_delimeter_regex = re.compile("(_|(,( )?))")

        if not rp_string_regex.fullmatch(road_position_string):
            raise ValueError("The string " + road_position_string + " is not a valid Road Position String")

        split_string = rp_string_delimeter_regex.split(road_position_string)

        road_position = RoadPosition()

        road_position.regionId = int(split_string[0])
        road_position.roadId = int(split_string[4])
        
        #Check if the position has a letter for the side appended to it, in which case, split it from the
        #position and store it separately.
        position_string = split_string[8]
        road_side_string = None
        if position_string[len(position_string) - 1].isalpha():
            road_side_string = position_string[len(position_string) - 1]
            position_string = position_string[:(len(position_string) - 1)]
        
        road_position.position = float(position_string)

        if road_side_string is not None:
            road_position.roadSide = RoadSide.parseFromString(road_side_string)

        return road_position


    regionId = IntField(required=True)
    roadId = IntField(required=True)
    position = FloatField(required=True)
    roadSide = IntField(validation=validateRoadSide)


    def __eq__(self, other):
        return isinstance(other, RoadPosition) \
            and self.regionId == other.regionId  \
            and self.roadId == other.roadId \
            and self.position == other.position \
            and self.roadSide == other.roadSide


    def __hash__(self):
        return hash(self.regionId) + hash(self.roadId) + hash(self.position) + hash(self.roadSide)


    def __str__(self):

        road_side_suffix = ""
        if(self.roadSide == RoadSide.A):
            road_side_suffix = "A"
        elif(self.roadSide == RoadSide.B):
            road_side_suffix = "B"

        return "{0}_{1}, {2}{3}".format(self.regionId, self.roadId, self.position, road_side_suffix);


class Station(Document):

    roadPosition = EmbeddedDocumentField(RoadPosition, required=True, unique=True)
    address = StringField(required=True)
    lat = FloatField(required=True)
    lon = FloatField(required=True)
    postedSpeedLimit = FloatField()

    meta = {
        "db_alias": DATABASE_ALIAS,
        "collection": "stations"
    }