import sqlalchemy
import databases

# 2. Initialization
# DATABASE_URL = "sqlite:///./student.db"
TEST_DATABASE_URL = "postgresql://postgres:welcome@localhost:5432/Student"
DATABASE_URL = "postgresql://postgres:welcome@localhost:5432/Student_db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


