import sqlalchemy
import databases

# 2. Initialization
# DATABASE_URL = "sqlite:///./student.db"
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:welcome@localhost:5432/Student_db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


