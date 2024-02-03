# IMPORTS
import taipy as tp
from taipy.gui import Html as HTML
import numpy as np
import pandas as pd

#WEB APP
path_to_csv = 'dataset.csv'

def get_data(path_to_csv: str):
    # pandas.read_csv() returns a pd.DataFrame
    dataset = pd.read_csv(path_to_csv)
    dataset["Date"] = pd.to_datetime(dataset["Date"])
    return dataset

# Read the dataframe

dataset = get_data(path_to_csv)

# Initial value
n_week = 10

# Definition of the page
page = """
# Getting started with Taipy

Week number: *<|{n_week}|>*

Interact with this slider to change the week number:
<|{n_week}|slider|min=1|max=52|>

## Dataset:

Display the last three months of data:
<|{dataset[9000:]}|chart|type=bar|x=Date|y=Value|height=100%|>

<|{dataset}|table|height=400px|width=95%|>
"""

# Create a Gui object with our page content
tp.Gui(page=page).run(dark_mode=False)
