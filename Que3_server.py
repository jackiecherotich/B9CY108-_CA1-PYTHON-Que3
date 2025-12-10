import socket
import threading
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()




def Db_Connection():

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT","3306")))
        print("Connected to database")

    except mysql.connector.Error as error:
        print("Failed connecting to database: {}".format(error))
        exit()

    try:
        cursor = connection.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS NewStudents (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), 
                           address VARCHAR(100),  education_qualifications TEXT, course VARCHAR(255), start_year INT,
                           start_month VARCHAR(50),application_number VARCHAR(100));
                       """)
        print("\n Table is created.....")
        connection.commit()
    except mysql.connector.Error as error:
        print("Failed connecting to database: {}".format(error))
        connection.rollback()

    return connection

def GenerateUniqueNumber(connection,course):
    COURSE_CODES = {
        "MSc Cyber Security": "MSC-CYB",
        "MSc Information Systems & Computing": "MSC-INF",
        "MSc Data Analytics": "MSC-DAT"
    }

    prefix = COURSE_CODES.get(course, "MSC-GEN")

    # Count how many students are in the db
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM NewStudents")
    total_count = cursor.fetchone()[0] + 1
    return f"{prefix}-{str(total_count)}"


def SaveDetails(connection, data):
    try:
        cursor = connection.cursor()

        application_number = GenerateUniqueNumber(connection, data["course"])

        sql = """INSERT INTO NewStudents 
                 (name, address, education_qualifications, course, start_year, start_month, application_number)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)
              """

        values = (
            data["name"],
            data["address"],
            data["education"],
            data["course"],
            data["year"],
            data["month"],
            application_number
        )

        cursor.execute(sql, values)
        connection.commit()

        print("Details saved successfully:", application_number)
        return application_number

    except mysql.connector.Error as error:
        print(" Error saving the details:", error)
        connection.rollback()





# Registration Server has to listen for requests from clients
# used TCP
SERVER = socket.gethostbyname(socket.gethostname()) # IP of the server
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))

def Handle_Client(conn, addr):
    try:
        print(f"New client connected and was initiated by {addr}")
        connected = True
        while connected:
            data = conn.recv(1024).decode()
            print(f"Data received from {addr}: {data}")

            student_data = json.loads(data)

            student_details = SaveDetails(connection, student_data)
            if student_details:
                conn.send(f"Application received. {student_details}".encode())
            else:
                conn.send(f"Error saving details.".encode())



    except Exception as e:
        print(" Error connecting to server: ".encode())
    finally:
        conn.close()


def Server_Start():
    Db_Connection()
    try:
       server.listen()
       print("Waiting for clients...\n")
       while True:
           conn, addr = server.accept()
           thread = threading.Thread(target=Handle_Client, args=(conn, addr)) # server get multiple requests
           thread.start()
           print(f"Client connected are: (threading.active_count() - 1)")

    except socket.error:
       print("\nCheck the server")






if __name__ == "__main__":
    Server_Start()





