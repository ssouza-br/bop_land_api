from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Create SQLite engine and session
engine = create_engine('sqlite:///mydatabase.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Define the data model for Role
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Define one-to-many relationship with User
    users = relationship('User', backref='role')

# Define the data model for User
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    role_id = Column(Integer, ForeignKey('roles.id'))  # Foreign key referencing roles.id

# Create tables
Base.metadata.create_all(engine)

# Insert data using ORM
# Create roles
admin_role = Role(name='admin')
user_role = Role(name='user')
session.add_all([admin_role, user_role])
session.commit()

# Insert users with roles
users_data = [
    User(name='Alice', age=25, role=admin_role),
    User(name='Bob', age=30, role=user_role),
    User(name='Charlie', age=28, role=user_role)
]
session.add_all(users_data)
session.commit()
