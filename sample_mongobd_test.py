from core.settings import settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from helpers.loging_helper import logger

"""
### Sample MongoDB Test Script
This script demonstrates how to connect to a MongoDB database using
the connection string and perform a simple operation to verify the connection.
"""

uri = f"mongodb+srv://herik:{settings.mongodb_password}@cluster0.4tbavfq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    logger.info(message="Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    logger.error(message=f"Error connecting to MongoDB: {e}")