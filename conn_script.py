from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/deepdetect")
conn = engine.connect()
print("Connected successfully!")
conn.close()
