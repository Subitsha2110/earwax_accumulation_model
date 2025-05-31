import mysql.connector

MYSQL_CONFIG_NO_DB = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': ''
}

def create_database_and_table():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG_NO_DB)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS earwax_monitoring")
        cursor.execute("USE earwax_monitoring")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS earwax_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age INT,
                pollen FLOAT,
                dust FLOAT,
                humidity FLOAT,
                temperature FLOAT,
                traveling VARCHAR(10),
                pollen_season VARCHAR(10),
                earwax_percentage FLOAT,
                date_recorded DATETIME
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and table ready.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    create_database_and_table()
