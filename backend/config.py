import os

class Config:
    SECRET_KEY = 'emergency-helpline-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/emergency.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True