import os

# class Config:
#     SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for testing