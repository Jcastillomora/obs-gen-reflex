from typing import Dict
from reflex.components.radix.themes.base import LiteralAccentColor

# Años
años_dict: Dict[str, LiteralAccentColor] = {
    "2018": "gold",
    "2019": "blue",
    "2020": "green",
    "2021": "red",
    "2022": "purple",
    "2023": "orange",
    "2024": "gray",
    "2025": "ruby",
}

años_list = list(años_dict.keys())

# Disciplinas
disciplinas_dict: Dict[str, LiteralAccentColor] = {
    "Ciencias Agrícolas": "green",
    "Ciencias Naturales": "blue",
    "Ciencias Sociales": "red",
    "Ingeniería y Tecnología": "purple",
    "Humanidades": "orange",
    "Medicina y Ciencias de la Salud": "gold",
}   

disciplinas_list = list(disciplinas_dict.keys())

# Unidades
unidades_dict: Dict[str, LiteralAccentColor] = {
    "DADI": "green",
    "FCAM": "blue",
    "FCJE": "red",
    "FECSH": "purple",
    "FICA": "orange",
    "FMED": "gold",
    "FODO": "gray",
    "VIPRE": "ruby",
    "VRAC": "brown",
    "VRIP": "black",
}

unidades_list = list(unidades_dict.keys())

all_items = {
    "años": años_list,
    "disciplinas": disciplinas_list,
    "unidades": unidades_list
}