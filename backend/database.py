import mysql.connector
from mysql.connector import pooling, Error
from config import settings

try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="patient_case_pool",
        pool_size=5,  
        pool_reset_session=True,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    print("Successfully connected to MySQL database pool.")
except Error as e:
    print("Error connecting to MySQL Pool: ",e)
    db_pool = None

def get_db():
    """
    Yields a database cursor for an API request, commits if successful,
    rolls back if there is an error, and always closes the connection.
    """
    if db_pool is None:
        raise Exception("Database connection pool is not initialized.")
        
    connection = db_pool.get_connection()
    cursor = connection.cursor(dictionary=True)
    
    try:
        yield cursor
        connection.commit()  
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close() 