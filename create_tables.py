print("Running create_tables.py...")

import os
from app.database.database import Base, engine
from app.models.models import Project, Crew, Task, Finance

# Print the absolute path where the DB will be created
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'project.db'))
print(f"Expected database path: {db_path}")

# Create all tables in the database
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")

import os
print("Current working directory:", os.getcwd())
print("Does project.db exist?", os.path.exists("project.db"))
