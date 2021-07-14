import os
import hashlib
import timeit
import time

from db.database import DataBase
from generator.api_generator import ApiGenerator
from quark.utils import colors
from utils import tools
from tqdm import tqdm
from generator.object.genrule_obj import GenRuleObject


class MethodCombGenerator:

    def __init__(self, apk, pbar=1):
        """
        Input AndroidSampleModel
        """
        self.apk = apk
        self.db = DataBase()
        self.pbar = pbar

    def check_apk_parsable(self):
        """
        Check if given apk are parsable
        """
        if not self.apk.parsable:
            print(self.apk.obj)
            return False

        return True

    def parse_apk(self):
        """
        Parse apk by androguard.
        :return: failed or succeed
        """
        try:
            self.apk_analysis = Quark(self.apk)
        except:
            return False
        return True

    def get_permissions(self):
        """
        Return all native permissions usage from apk.

        :return: a set() for all native permissions usage
        """
        perm = set(self.apk_analysis.apkinfo.permissions)
        for p in perm.copy():
            if not "android.permission" in p:
                perm.discard(p)
        return perm

    def set_progress_status(self, status):

        if not self.db.set_status(self.apk.id, status):
            print("There is some mistake while setting progress, recheck")
            if not self.check_progress:
                return False

        return True

    def check_progress(self):

        apk_status = self.db.get_progress_status(self.apk.id)

        if not apk_status:
            print(colors.yellow("wait for a second then check"))
            return False
        if apk_status == 1:
            print("{} as known as {} has done analysis!".format(
                colors.yellow(self.apk.name), self.apk.id))
            return False
        elif apk_status == 4:
            print("{} as known as {} is failed parsing!".format(
                colors.yellow(self.apk.name), self.apk.id))
            return False

        return True

    def first_stage_rule_generate(self, first_apis_pool, second_apis_pool):
        """
        Extract all api usage in apk current apk then generate method combination.

        """

        # Check if apk parsable
        if not self.check_apk_parsable():
            self.set_progress_status(4)
            return

        # Check apk progress
        if not self.check_progress():
            return

        api_generator = ApiGenerator(second_apis_pool)
        inner_api_pool = list(api_generator.generate())

        # Setup progress bar
        second_api_pool_num = len(inner_api_pool)
        outter_desc = f"Core No.{self.pbar}"
        outter_loop = tqdm(first_apis_pool, desc=outter_desc,
                           position=self.pbar, leave=False)

        for api1 in first_apis_pool:
            outter_loop.update(1)

            # Tag the method
            if not self.db.check_analysis_progress(api1.id, self.apk.id):
                tqdm.write("{}, {}->{} has done in apk progress move forward".format(
                    colors.lightblue(api1.id), api1.class_name, api1.method_name))
                continue

            # Skip current api if it is not exist
            if self.apk.apk_analysis.apkinfo.find_method(api1.class_name, api1.method_name, api1.descriptor) is None:
                tqdm.write("{}, {}->{} does not exist in apk move forward".format(
                    api1.id,  api1.class_name, api1.method_name))
                continue

            matched_list = []
            id_list = []
            for num, api2 in enumerate(inner_api_pool, start=1):
                inner_desc = f"{num}/{second_api_pool_num}"
                outter_loop.set_postfix(inner_loop=inner_desc, refresh=True)

                api = api2

                # Skip same api
                if api2.id == api1.id:
                    continue

                _comb = {
                    "crime": "",
                    "permission": [],
                    "api": [
                        {
                            "class": api1.class_name,
                            "method": api1.method_name,
                            "descriptor": api1.descriptor
                        },
                        {
                            "class": api2.class_name,
                            "method": api2.method_name,
                            "descriptor": api2.descriptor
                        }
                    ],
                    "score": 1
                }
                comb = GenRuleObject(_comb)

                try:
                    result = self.apk.apk_analysis.run(comb)
                except KeyboardInterrupt:
                    self.set_progress_status(2)
                    raise
                except Exception as e:
                    tqdm.write("{} and {} combination has some error when analyzing, ERROR MESSAGE: {}".format(
                        api1.id, api2.id, e))
                    continue

                if not comb.check_item[4]:
                    continue

                # tqdm.write("{} and {} matched check!".format(
                #     colors.green(api1.id), colors.green(api2.id)))
                matched_list.append({
                    "m1": api1.id,
                    "m2": api2.id
                })

                id_list.append(api1.id + api2.id)

            # Insert matched combination to database and update progress
            if not self.db.update_analysis_progress(api1.id, self.apk.id):
                tqdm.write(f"Error occured while update progress: {api1.id}")
            if not self.db.save_matched_comb(self.apk.id, matched_list, id_list):
                tqdm.write("some Error occure")

            # Second stage rule generate
            # self.sec_stage_rule_generate(matched_list)

        # Apk completed analyzing
        outter_loop.clear()
        outter_loop.close()

        self.set_progress_status(1)
        return
