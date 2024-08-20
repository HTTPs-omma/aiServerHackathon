import sqlite3
import queue
from contextlib import contextmanager

# 참고 : https://codereview.stackexchange.com/questions/285730/simple-connection-pool-for-sqlite-in-python
class ConnectionPool :
    def __init__(self, max_connections) :
        # self.databaseName = "url"
        self.path = "./models/db.db"
        self.pool : sqlite3.Connection = queue.Queue(maxsize=max_connections)
        
        for _ in range(max_connections) :
            conn = self.create_connection()
            self.pool.put(conn)
            
    def create_connection(self):
        return sqlite3.connect(self.path)
    
    def getConn(self, timeout) -> sqlite3.Connection :
        try :
            return self.pool.get(timeout=timeout)
        except queue.Empty :
            raise RuntimeError("Timeout : No available pool,")
    
    def retConn(self, conn):
        self.pool.put(conn)
        
    @contextmanager
    def connection(self, timeout=10):
        conn = self.getConn(timeout)
        try:
            yield conn
        finally:
            self.retConn(conn)
            
            
        

class UserUrl :
    def __init__(self) :
        self.databaseName = "UserUrl"
        self.createSql = f"""
            CREATE TABLE IF NOT EXISTS {self.databaseName} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                createAt DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.connPool : ConnectionPool = ConnectionPool(5)
        
        
        
    def createDB(self) :
        conn = self.connPool.getConn(10)
        cursor = conn.cursor()
        try :
            rst = cursor.execute(self.createSql)
            return True
        except :
            print("create DB 에러!!")    
        return False
        
        
    def createRecord(self, url : str) :
        conn = self.connPool.getConn(10)
        cursor = conn.cursor()
        
        query = f"INSERT INTO {self.databaseName} (url) VALUES (?)"
        
        try :
            rst = cursor.execute(query, (url,))
            conn.commit()
            return True
        except Exception as e :
            print(f"create Redcord 에러 : {e}") 
            return False
        finally :
            self.connPool.retConn(conn)
            
        
        
    def readRecord(self) :
        conn = self.connPool.getConn(10)
        cursor = conn.cursor()
        
               
        query = f"SELECT * FROM {self.databaseName}"
        
        try :
            rst = cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Exception as e :
            print("read DB 에러 : {e}") 
            return []
        finally :
            self.connPool.retConn(conn)
        
        
        
    def deleteRecord(self) :
        conn = self.connPool.getConn(10)
        cursor = conn.cursor()
        
        query = "DELETE FROM %s where url = ?".format((self.databaseName))
        
        try :
            rst = cursor.execute(query)
            conn.commit()
            return True
        except Exception as e :
            print("create DB 에러 : {e}") 
            return False
        finally :
            self.connPool.retConn(conn)


if __name__ == '__main__':
    user = UserUrl()
    user.createDB()
    # user.createRecord("http://naver.com")
    print( user.readRecord() )
    
    
    