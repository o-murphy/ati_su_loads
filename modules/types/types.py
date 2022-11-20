from typing import NamedTuple

import requests


class CarType(NamedTuple):
    Id: str
    Id2: str
    Name: str
    Attribs: int
    Position: int
    TypeId: int
    NameEng: str
    ShortName: str
    ShortNameEng: str


class CargoType(NamedTuple):
    Id: str
    Id2: str
    Name: str
    NameEng: str


class LoadingType(NamedTuple):
    Id: int
    Id2: str
    Name: str
    NameEng: str
    ShortName: str
    ShortNameEng: str


def get_json(url):
    resp = requests.get(url)
    return resp.json()


car_types = get_json('https://files.ati.su/glossary/carTypesStringified.json')
cargo_types = get_json('https://files.ati.su/glossary/cargoTypes.json')
load_types = get_json('https://files.ati.su/glossary/loadingTypes.json')

carTypes = {f"{item['Id']}": CarType(**item) for item in car_types}
cargoTypes = {f"{item['Id']}": CargoType(**item) for item in cargo_types}
loadingTypes = {f"{item['Id']}": LoadingType(**item) for item in load_types}
