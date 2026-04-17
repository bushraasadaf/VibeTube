# Importing essential modules
import pyodbc

# server = 'DESKTOP-HLSHUJ9\MYSQLSERVER2' #nabiha
server = server = 'DELL_LATITUDE' #bushra
database = 'vibetube' 
use_windows_authentication = False # Set to True to use Windows Authentication
username = 'sa' # Specify a username if not using Windows Authentication 
password = 'Fall2022.dbms' # Specify a password if not using Windows Authentication
# Create the connection string based on the authentication method chosen 
if use_windows_authentication: 
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;' 
else: connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_connection():
    return pyodbc.connect(connection_string)