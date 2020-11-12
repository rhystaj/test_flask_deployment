from mongoengine import connect

TEST_DATABASE_CONNECTION = "mongomock://localhost"
TEST_DATABASE_NAME = "testdb"

def connectToMockServer(database_alias):
    connect(TEST_DATABASE_NAME, host=TEST_DATABASE_CONNECTION, alias=database_alias)