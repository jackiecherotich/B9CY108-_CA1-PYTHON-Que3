import socket
import threading
import mysql.connector
from mysql.connector import Error
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()


#--------------------------------------------------------------#
#------------------DATABASE CONNECTION-MYSQL-------------------#
def db_connection():

    try:
        config ={
            "host":os.getenv("DB_HOST"),
            "user":os.getenv("DB_USER"),
            "password":os.getenv("DB_PASSWORD"),
            "database":os.getenv("DB_NAME"),
            "port":int(os.getenv("DB_PORT","3306"))
        }
        cnx = mysql.connector.connect(**config)
        print("Connected to MySQL Server")
        return cnx

    except mysql.connector.Error as error:
        print("Failed connecting to database:",error)
        exit()
    except Exception as e:
        print("Unexpected error:", e)
        exit()

# -------------------------------------------------------------------#
#---------------------CREATING TABLES---------------------------------#
def create_tables(cnx):
    try:
        cursor = cnx.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS new_students (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), 
                           address VARCHAR(100),  education_qualifications TEXT, course VARCHAR(255), start_year INT,
                           start_month VARCHAR(50),application_number VARCHAR(100));
                       """)
        cnx.commit()
        print("\n Table is created.....")

    except mysql.connector.Error as error:
        print("Failed connecting to database: ", error)
        cnx.rollback()

#--------------------------------------------------------------------------#
#----------------------------UNIQUE NUMBER---------------------------------#
#check the ids existing in the system and add 1 to get new ID for new registration
def get_next_student_number(cnx):
    cursor = cnx.cursor()
    cursor.execute("SELECT id FROM new_students ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        return row[0] + 1
    else:
        return 1


# to generate unique number
# will use the course prefix ,id and year of start
def generate_unique_number(cnx,course,start_year):
    COURSE_CODES = {
        "MSc Cyber Security": "MSC-CYB",
        "MSc Information Systems & Computing": "MSC-INF",
        "MSc Data Analytics": "MSC-DAT"
    }

    prefix = COURSE_CODES.get(course, "MSC-GEN")
    next_id = get_next_student_number(cnx)
# Unique Application number to the applicant
    return f"{prefix}-{next_id}-{start_year}"

# to Save the details to the Database
def save_details(connection, data):
    try:
        cursor = connection.cursor()

        application_number = generate_unique_number(connection, data["course"], data["start_year"])

        sql = """
              INSERT INTO new_students
              (name, address, education_qualifications, course, start_year, start_month, application_number)
              VALUES (%s, %s, %s, %s, %s, %s, %s) 
              """

        values = (
            data["name"],
            data["address"],
            data["education"],
            data["course"],
            data["start_year"],
            data["start_month"],
            application_number
        )

        cursor.execute(sql, values)
        connection.commit()

        print("Details saved successfully:", application_number)
        return application_number

    except mysql.connector.Error as error:
        print(" Error saving the details:", error)
        connection.rollback()

#--------------------------------------------------------------------#
#----------------HANDLING CLIENT REQUEST-----------------------------#
# Registration Server has to listen for requests from clients
# used TCP and Multithreading
SERVER = "127.0.0.1"    #socket.gethostbyname(socket.gethostname()) # IP of the server
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((SERVER, PORT))

# To handle connections from various clients
def handle_client(conn, addr):
    connection = db_connection()
    try:
        print(f"New client connected and was initiated by {addr}")
        time.sleep(0.1)
        data = conn.recv(2048).decode()
        if not data:
            print("No data received")
            return
        print(f"Data received from {addr}:" ,data)

        student_data = json.loads(data)

        student_details = save_details(connection, student_data)
        if student_details:
            conn.send(f"Application received. {student_details}".encode())
        else:
            conn.send(f"Error saving details.".encode())

    except Exception as e:
        print(" Error connecting to server: ")
    finally:
        connection.close()
        conn.close()

#------------------------------------------------------------------------#
#----------------------SERVER STARTING FUNCTION-----------------------------------#
#Server to listen for connections from clients
def server_start():
    connection = db_connection()
    create_tables(connection)
    connection.close()
    try:
       server.listen()
       print("Waiting for clients...\n")
       while True:
           conn, addr = server.accept()
           thread = threading.Thread(target=handle_client, args=(conn, addr) )# server get multiple requests
           thread.start()
           print(f"Client connected are: ({threading.active_count()} - 1)")

    except socket.error:
       print("\nCheck the server")


#-----------------------------------------------------------------------#
#----------------MAIN FUNCTION------------------------------------------#
if __name__ == "__main__":
    server_start()





