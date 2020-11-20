
import os
import hashlib
import time

from pymongo import MongoClient
from pprint import pprint

from utils import tools

from tqdm import tqdm
from quark.utils import colors

DATABASE_NAME = "quark"
DATABASE_HOST = "localhost"
DATABASE_PORT = 27017

DATABASE_USERNAME = "root"
DATABASE_PASSWORD = "pass"


class DataBase:

    def __init__(self):
        """
        MongoDB dashboard module, provide a few functionality for data control.

        """
        client = MongoClient(
            f'mongodb://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}')

        self.db = client[DATABASE_NAME]

        return

    def insert_api(self, api):
        """
        Insert native api into database.

        :parm: the model of api
        :return: True for succeed, False for failed
        """
        collection = self.db["android_api"]
        result = collection.find_one({"api_id": api.id})

        if result:
            return False

        try:
            collection.insert_one(api.api_obj)
        except:
            tqdm.write(f"cuurent api insert failed: {api.api_obj}")
            return False

        return True

    def save_matched_comb(self, apk_id, matched_combs, id_list):
        """
        Save method combination m_id to match collection.

        :parms: apk id, A list of first method id and second method id
        :reuturn: True if succeed or false
        """
        collection = self.db["matched_method_comb"]
        fst_collection = self.db["first_stage_rules"]

        collection.update_one({"sample": apk_id},
                              {"$addToSet": {"matched_combs": {"$each": id_list}}},
                              upsert=True
                              )

        for r in matched_combs:

            # generate first stage rule id
            _id = r["m1"] + r["m2"]

            # Check if currunt rule exist
            result = fst_collection.find_one({"id": _id})

            # check if rule exist
            if result:

                # check if sample included
                if apk_id in result["sample"]:
                    continue

                # if rule exist but not in this sample, add sample count
                fst_collection.update_one({"id": _id}, {
                    "$addToSet": {"sample": apk_id},
                    "$inc": {"matched_number": 1}
                },
                    upsert=False
                )

                continue

            # get method content
            api_content = self.get_method_api(r["m1"], r["m2"])

            md_obj = {
                "id": _id,
                "api_id": {
                    "m1": r["m1"],
                    "m2": r["m2"]
                },
                "api_content": api_content,
                "matched_number": 1,
                "sample": [apk_id]
            }

            fst_collection.insert_one(md_obj)

        return True

    def get_progress_status(self, apk_id):
        """
        Get apk analysis status from database.

        :param: a string of apk hash id
        :return: an Integer to represent apk progress status
        """

        collection = self.db["android_sample"]

        progress = collection.find_one({"_id": apk_id})

        if progress["status"] is not None:
            return progress["status"]
        else:
            print("status none")
            return 2
        return False

    def set_status(self, apk_id, status):
        """
        Set the apk progress status.

        :parm: 
            1. apk hash id
            2. status: 
                '0': none. 
                '1': done
                '2': in progress 
                '4': failed
        :return: True if query succeed
        """
        collection = self.db["android_sample"]
        progress = collection.find_one({"_id": apk_id})

        collection.update_one({"_id": apk_id}, {
            "$set": {"status": status, "checking": False}})
        return True

    def check_analysis_progress(self, api_id, apk_id):
        """
        Check current api has exist in analysis progress.

        :parm:
            api_id: a string of current api id
            apk_id: a string of current analyze apk

        :return: False if exist or True 
        """
        collection = self.db["android_sample"]

        progress = collection.find_one({"_id": apk_id})

        if api_id in progress["progress"]:
            return False
        return True

    def update_analysis_progress(self, api_id, apk_id):
        """
        Update progress to database.

        :parm:
            api_id: a string of current api id
            apk_id: a string of current analyze apk
        """
        collection = self.db["android_sample"]
        result = collection.update_one({"_id": apk_id}, {
            "$addToSet": {"progress": api_id},
        }, upsert=False)

        if not result:
            return False
        return True

    def get_method_api(self, api1, api2):
        """
        Get api content from database by given id.

        :parm: two string of api id
        :return: a dict for api content
        """
        collection = self.db["android_api"]
        api1_content = collection.find_one({"api_id": api1})
        api2_content = collection.find_one({"api_id": api2})

        return {
            "m1": api1_content,
            "m2": api2_content
        }

    def create_sample_data(self, data):
        """
        Create a document of sample data to database.

        :parm: an dict from SampleModel
        """
        collection = self.db["android_sample"]

        progress = collection.find_one({"_id": data["_id"]})

        if not progress:
            collection.insert_one(data)
        return

    def search_sample_data(self, apk_id):
        """
        Get sample document from database by given apk id.

        :parm: a hash value of sample id
        :return: a dict of searching result
        """
        collection = self.db["android_sample"]

        result = collection.find_one({"_id": apk_id})
        return result

    def delete_sample_data(self, apk_id):
        """
        Delete sample document in database by given apk id.

        :parm: a hash value of apk id
        """
        collection = self.db["android_sample"]
        collection.delete_one({"_id": apk_id})

        return

    def find_rules_by_sample(self, apk_id):
        """
        Get all first stage rules content by given apk id.

        :parm: a hash value of apk id
        :return: a list of all rules content
        """
        collection = self.db["first_stage_rules"]
        result = collection.aggregate([
            {"$unwind": "$api_content"},
            {"$match": {"sample": apk_id}},
            {"$project": {
                "md_comb": {
                    "api1": {
                        "class_name": "$api_content.m1.class_name",
                        "method_name": "$api_content.m1.method_name",
                        "descriptor": "$api_content.m1.descriptor"
                    },
                    "api2": {
                        "class_name": "$api_content.m2.class_name",
                        "method_name": "$api_content.m2.method_name",
                        "descriptor": "$api_content.m2.descriptor"
                    }
                }
            }}
        ])

        md_l = [o["md_comb"] for o in result]

        md_l = tools.set_dict_list(md_l)
        md_l = tools.remove_same_combination(md_l)

        return md_l
