from src.config import setup_environment_and_logging
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import pandas as pd
import os

logger = setup_environment_and_logging()

class DB:
  def __init__(self):
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
      raise ValueError("MONGODB_URI environment variable not set")
    self.client = MongoClient(mongodb_uri)
    self.db = self.client["saudi_stocks"]
    self.collection = "eod_data"
  
  def init_mongo(self):
    if self.collection not in self.db.list_collection_names():
      logger.info(f"{self.collection} collection not found")
      logger.info(f"Creating a collection")
      self.db.create_collection(self.collection)

      collections = self.db.list_collection_names(filter={"name": self.collection})
      if self.collection in collections:
        logger.info("Collection created!")
        self.db[self.collection].create_index(
        [("symbol", 1), ("date", 1)],
        unique=True
    )
    else:
      logger.info(f"{self.collection} collection already exists")
      logger.info("Skipping")
  
  def load_into_mongo(self, df: pd.DataFrame):
    try:
      collection = self.db.get_collection(self.collection)
      data_dict = df.to_dict(orient="records")
      collection.insert_many(data_dict, ordered=False)
    except BulkWriteError as bwe:
      pass

  def load_from_mongo(self):
    collection = self.db.get_collection(self.collection)
    data = collection.find()
    df = pd.DataFrame(list(data))
    df.drop(columns=['_id'], inplace=True, errors="ignore")
    return df