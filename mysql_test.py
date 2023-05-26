import mysql.connector as sql #BASE DE DATOS MYSQL
from sys import argv

def connect(db:str = None) -> sql.connection:
    try:
        if db:
            connection = sql.connect(
                host="localhost",
                user="root",
                password="password"
            )
        else:
            connection = sql.connect(
                host="localhost",
                user="root",
                password="password",
                database=db
            )
        return connection
    except Exception as e:
        raise e

def testDB():
    """
    connection = sql.connect(
        host="localhost:3306",
        user="root",
        password="password"
    )"""
    connection = connect()
    if connection.is_connected():
        connection.close()
        return True
    else:
        connection.close()
        return False
    
print(testDB())
print(argv[1:])