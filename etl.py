import glob 
import pandas as pd 
import xml.etree.ElementTree as ET 
from datetime import datetime
import sqlite3
import os

###extract functions


def extract_from_csv(path):
    '''This function extracts data from csv files in the provided path.
    it returns a dataframe containing the extracted data.'''
    extracted_data = pd.DataFrame(columns=['car_model','year_of_manufacture','price','fuel'])
    if os.path.isfile(path):
        df = pd.read_csv(path)
        extracted_data = pd.concat([extracted_data, df], ignore_index=True)
    else:
        for file in glob.glob(path + "/*.csv"):
            df = pd.read_csv(file)
            extracted_data = pd.concat([extracted_data, df], ignore_index=True)
    return extracted_data


def extract_from_xml(path):
    '''This function extracts data from xml files in the provided path.
    it returns a dataframe containing the extracted data.'''
    records = []
    if os.path.isfile(path):
        files = [path]
    else:
        files = glob.glob(path + "/*.xml")
    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()
        for row in root.findall(".//row"):
            car_model = row.findtext('model') or row.findtext('car_model')
            year = row.findtext('year') or row.findtext('year_of_manufacture')
            price = row.findtext('price')
            fuel = row.findtext('fuel')
            # Permite valores vacíos o nulos
            records.append({
                'car_model': car_model if car_model is not None else "",
                'year_of_manufacture': int(year) if year and year.isdigit() else None,
                'price': float(price) if price and price.replace('.', '', 1).isdigit() else None,
                'fuel': fuel if fuel is not None else ""
            })
    return pd.DataFrame(records, columns=['car_model','year_of_manufacture','price','fuel'])

def extract_from_json(path):
    ''' This function extracts data from JSON files in the provided path. 
    It returns a DataFrame containing the extracted data. '''
    extracted_data = pd.DataFrame(columns=['car_model','year_of_manufacture','price','fuel'])
    if os.path.isfile(path):
        df = pd.read_json(path)
        extracted_data = pd.concat([extracted_data, df], ignore_index=True)
    else:
        for file in glob.glob(path + "/*.json"):
            df = pd.read_json(file)
            extracted_data = pd.concat([extracted_data, df], ignore_index=True)
    return extracted_data