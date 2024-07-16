from sqlalchemy import create_engine
import pandas as pd

# Replace with your SQL Server connection details
server = 'localhost'  # IP address and port of the Docker container
database = 'AdventureWorksDW2019_Dimension'
username = 'sa'
password = 'reallyStrongPwd123'

# Create a connection string
conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

# Create an engine
engine = create_engine(conn_str)

# Connect to the database
connection = engine.connect()
print(connection)

query = 'SELECT * FROM AdventureWorksDW2019_Dimension.dbo.AdventureWorksDWBuildVersion'
df = pd.read_sql(query, engine)

print(df.head(5))
