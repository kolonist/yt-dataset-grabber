import os

from typing import NoReturn, Iterable, Any

from yaml import load as load_yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import csv


def load_dataset(rootdir:str) -> list[dict[str,str]]:
    dataset_file = os.path.join(rootdir, "dataset.csv")

    with open(dataset_file, "r") as f:
        reader = csv.DictReader(f)
        return [ line for line in reader ]

def create_protocol_line(isTarget:bool, etalon:dict[str,str], test:dict[str,str]) -> str:
    return " ".join([
        "1" if isTarget else "0",
        os.path.join(etalon["id"], etalon["year"], "00001.wav"),
        os.path.join(test["id"], test["year"], "00001.wav"),
    ]) + "\n"

if __name__ == "__main__":
    # load parameters
    with open("params.yaml", "r") as f:
        params = load_yaml(f, Loader=Loader)

    # load dataset
    rootdir = params["dataset_path"]
    dataset = load_dataset(rootdir)

    # create protocols
    very_tests = {
        1: set(),  # разница в 1 год
        2: set(),  # разница в 2 года
        3: set(),  # разница в 3 года
    }

    for etalon in dataset:
        for test in dataset:
            # same sample
            if etalon["id"] == test["id"] and etalon["year"] == test["year"]:
                continue

            # target
            if etalon["id"] == test["id"]:
                etalon_year = int(etalon["year"])
                test_year = int(test["year"])
                distance = etalon_year - test_year

                if distance not in very_tests:
                    continue

                protocol_line = create_protocol_line(
                    True,
                    etalon,
                    test
                )
                very_tests[distance].add(protocol_line)

            # impostor
            else:
                protocol_line = create_protocol_line(False, etalon, test)

                for key in very_tests:
                    very_tests[key].add(protocol_line)

    # save protocols
    for (distance, very_test) in very_tests.items():
        filename = os.path.join(rootdir, f"veri_test{distance}.txt")
        with open(filename, "w") as f:
            f.writelines(very_test)
