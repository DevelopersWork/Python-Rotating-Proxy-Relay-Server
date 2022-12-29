import sqlite3
import sys
import os

from src.Utils import createLogger

class Database:

    def __init__(self, dbName = "myDB") -> None:
        self.logger = createLogger(
            dbName, 
            "/var/log/{0}/{1}/".format(os.getenv('APP_NAME'), __name__)
        )
        
        _dir = "/tmp/{0}".format(os.getenv('APP_NAME'))
        os.makedirs(_dir, exist_ok=True)
        self.dbLocation = "{0}/{1}.db".format(_dir, dbName)
        
        try:
            self.connection = sqlite3.connect(
                self.dbLocation, check_same_thread=False, 
                isolation_level=None, timeout=30000
            )
            cursor = self.connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS proxies(ip, port, type, alive, available)")
        except Exception as ex:
            self.logger.error("Database:__init__():: {0}".format(ex), exc_info=True)
            sys.exit(0)

    def executeQuery(self, query = "") -> sqlite3.Cursor:
        try:
            cursor = self.connection.cursor()
            self.logger.debug("Database:executeQuery():: {0}".format(query))
            return cursor.execute(query)
        except Exception as ex:
            self.logger.error("Database:executeQuery():: {0}".format(ex), exc_info=True)

        return None

    def insert(self, tableName: str, values = "") -> bool:
        try:
            cursor = self.connection.cursor()
            self.logger.debug("Database:insert():: {0}".format(
                "INSERT INTO {0} VALUES ({1});".format(tableName, values)
            ))
            cursor.execute("INSERT INTO {0} VALUES ({1});".format(tableName, values))
            return True
        except Exception as ex:
            self.logger.error("Database:insert():: {0}".format(ex), exc_info=True)
        return False

    def update(self, tableName: str, values = "", filter = "") -> bool:
        try:
            cursor = self.connection.cursor()
            if filter:
                filter = "WHERE " + filter
            self.logger.debug("Database:update():: {0}".format(
                "UPDATE {0} SET {1} {2}".format(tableName, values, filter)
            ))
            cursor.execute("UPDATE {0} SET {1} {2}".format(tableName, values, filter))
            return True
        except Exception as ex:
            self.logger.error("Database:update():: {0}".format(ex), exc_info=True)
        return False

    def delete(self, tableName: str, filter="") -> bool:
        try:
            cursor = self.connection.cursor()
            if filter:
                filter = "WHERE " + filter
            self.logger.debug("Database:delete():: {0}".format(
                "DELETE FROM {0} {1}".format(tableName, filter)
            ))
            cursor.execute("DELETE FROM {0} {1}".format(tableName, filter))
            return True
        except Exception as ex:
            self.logger.error("Database:delete():: {0}".format(ex), exc_info=True)
        return False