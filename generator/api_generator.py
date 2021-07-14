import os
import sys
import json
import re

from tqdm import tqdm
from db.database import DataBase
from model.api_model import APIModel

class ApiGenerator:

    def __init__(self, apis):
        self.apis = apis
        self.db = DataBase()
        
        # The list of all api id in current apk
        self.api_pool = []

    
    def initialize(self):
        for api in tqdm(self.apis, desc="Initialize APIs", leave=False):
            api_model = APIModel(api)
            self.db.insert_api(api_model)

            yield api_model

    def generate(self):
        """
        generate apis and insert to database
        """
        
        for api in self.apis:
            api_model = APIModel(api)
            yield api_model
