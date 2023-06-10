from flask import Flask
from timetable_planner.routes import pages
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app=Flask(__name__)
    app.config["MONGODB_URI"]=os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"]=os.environ.get(
        "SECRET_KEY","2e1fce589e723ebfea0a0b1b9a92059a11f47ac4c295"
    )
    app.db=MongoClient(app.config["MONGODB_URI"]).timetable_planner
    app.register_blueprint(pages)
    return app
