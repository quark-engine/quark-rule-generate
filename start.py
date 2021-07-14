

import os
import sys
import atexit
import time
import click
import json

from pymongo import MongoClient
from multiprocessing import Pool, Process

from tqdm import tqdm
from model.android_sample_model import AndroidSampleModel
from generator.method_generator import MethodCombGenerator
from generator.api_generator import ApiGenerator
from quark.Objects.quark import Quark

from db.database import DataBase

from utils.tools import distribute, api_filter
from itertools import repeat

db = DataBase()


@click.command()
@click.option(
    "-a",
    "--apk",
    help="APK file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option(
    "-e",
    "--export",
    help="Export all rules of apk to JSON file",
    type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    "-m",
    "--multiprocess",
    default=1,
    help="Analyze APK with multiple processing, defaut will be single process",
    type=click.INT,
    show_default=True
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Debug mode, it will delete apk analying progress after finish",
)
@click.option(
    "-s",
    "--stage",
    default=1,
    type=click.INT,
    show_default=True,
    help="The stage of rule generate",
)
def main(apk, multiprocess, debug, export, stage):
    """Quark rule generate project"""

    apk = AndroidSampleModel(apk)

    # Export all rules into JSON files
    if export:
        
        result = db.find_rules_by_sample(apk.id)

        if result["status"] is not 1:
            if not click.confirm(f'The apk generate progress is not complete, Do you sure want to continue?'):
                return

        rules_num = len(result)

        tqdm.write(f"Rules number: {rules_num}")
        if click.confirm(f'This command will create {rules_num} file into {export}, Do you sure want to continue?'):
            count = 1

            tqdm.write(f"Start export rule into {export}")
            for obj in tqdm(result):
                rules = rule_obj_generate(obj, count)
                f_name = f"{str(count)}.json"
                path = os.path.join(export, f_name)

                with open(path, "w") as f:
                    json.dump(rules, f, indent=4)

                count += 1
        return

    # Apis generate
    primary, secondary, p_count = api_filter(apk, 0.2)
    
    if stage == 1:
        first_apis = primary
        second_apis = primary
    elif stage == 2:
        first_apis = primary
        second_apis = secondary
    elif stage == 3:
        first_apis = secondary
        second_apis = primary
    elif stage == 4:
        first_apis = secondary
        second_apis = secondary
        
    api_generator = ApiGenerator(first_apis)
    apis = list(api_generator.initialize())

    tqdm.write(f"Analyzing apk with {multiprocess} process")
    if multiprocess == 1:

        result = db.search_sample_data(apk.id)

        new_apis = []

        if result is not None:
            done_apis = result["progress"]
            new_apis = []
            for single_api in apis:
                if not single_api.id in done_apis:
                    new_apis.append(single_api)
        else:
            new_apis = apis

        tqdm.write(f"APIs usage number: {len(apis)}")
        tqdm.write(f"Analysis api done: {len(done_apis)}")
        tqdm.write(f"The rest of APIs number: {len(new_apis)}")

        generator = MethodCombGenerator(apk)
        generator.first_stage_rule_generate(new_apis, primary)

    else:

        result = db.search_sample_data(apk.id)

        new_apis = []

        if result is not None:
            done_apis = result["progress"]

            new_apis = []
            for single_api in apis:
                if not single_api.id in done_apis:
                    new_apis.append(single_api)
        else:
            new_apis = apis

        tqdm.write(f"APIs usage number: {len(apis)}")
        tqdm.write(f"Analysis api done: {len(done_apis)}")
        tqdm.write(f"The rest of APIs number: {len(new_apis)}")

        api_pools = distribute(new_apis, multiprocess)

        jobs = list()
        for i in range(multiprocess):
            p = Process(target=generate, args=(api_pools[i], second_apis, i+1, apk))
            jobs.append(p)
            p.start()

        for j in jobs:
            j.join()

    if debug:
        tqdm.write("Start with debug mode, will delete data after process.")
        db.search_sample_data(apk.id)
        filename = result["filename"]
        progress = result["progress"]
        api_num = result["api_num"]
        tqdm.write(f"Filename: {filename}")
        tqdm.write(f"Progress number: {len(progress)}")
        tqdm.write(f"APIS number: {api_num}")
        db.delete_sample_data(apk.id)


def rule_obj_generate(rule, f_name):

    api1 = rule["api1"]
    api2 = rule["api2"]
    cls1 = api1["class_name"]
    cls2 = api2["class_name"]
    md1 = api1["method_name"]
    md2 = api2["method_name"]
    des1 = api1["descriptor"]
    des2 = api2["descriptor"]

    description = f"{f_name}. {cls1}{md1}->{cls2}{md2}"
    rule_obj = {
        "crime": description,
        "permission": [],
        "api": [
            {
                "class": cls1,
                "method": md1,
                "descriptor": des1
            },
            {
                "class": cls2,
                "method": md2,
                "descriptor": des2
            }
        ],
        "score": 1,
    }
    return rule_obj


def generate(f_pool, s_pool, pbar, apk):
    generator = MethodCombGenerator(apk, pbar)
    generator.first_stage_rule_generate(f_pool, s_pool)


if __name__ == "__main__":
    main()
