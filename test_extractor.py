import pytest
import tempfile
import os
import pandas as pd
import xml.etree.ElementTree as ET
from etl import extract_from_csv, extract_from_json, extract_from_xml

###Fixtures 


#CSV

@pytest.fixture
def double_csv_dir():
    with tempfile.TemporaryDirectory() as tempdir:
        file1 = os.path.join(tempdir, 'cars1.csv')
        file2 = os.path.join(tempdir, 'cars2.csv')
        with open(file1, 'w') as f:
            f.write("car_model,year_of_manufacture,price,fuel\n")
            f.write("Volkswagen,2020,40000,Gasoline\n")
            f.write("Honda,2012,18000,Gasoline\n")
        with open(file2, 'w') as f:
            f.write("car_model,year_of_manufacture,price,fuel\n")
            f.write("Toyota,2015,15000,Diesel\n")
            f.write("Ford,2018,22000,Gasoline\n")

        yield tempdir

@pytest.fixture
def empty_csv_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def malformed_csv_dir():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode="w") as f:
        f.write("car_model,year_of_manufacture,price,fuel\n")
        f.write("Toyota,2015,15000\n")
        f.write("Honda,2018,18000\n")
        return f.name

#JSON

@pytest.fixture
def temp_json_dir():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode="w") as f:
        f.write('[{"car_model": "Ford", "year_of_manufacture": 2020, "price": 20000, "fuel": "Gasoline"}]\n')
        return f.name

@pytest.fixture
def malformed_json_dir():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode="w") as f:
        f.write('{"car_model": "Tesla", "year_of_manufacture": 2022')  
        return f.name
    
@pytest.fixture
def json_with_empty_fields():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('[{"car_model": "", "year_of_manufacture": null, "price": null, "fuel": ""},'
                '{"car_model": "Ford", "year_of_manufacture": null, "price": 18000, "fuel": "Gasoline"}]')
        return f.name

#XML

@pytest.fixture
def temp_xml_dir():
    xml_content = '''<cars>
    <row><car_model>Tesla</car_model><year_of_manufacture>2021</year_of_manufacture><price>35000</price><fuel>Electric</fuel></row>
    <row><car_model>BMW</car_model><year_of_manufacture>2019</year_of_manufacture><price>30000</price><fuel>Gasoline</fuel></row>
</cars>'''
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', mode="w") as f:
        f.write(xml_content)
        return f.name

@pytest.fixture
def invalid_estructure_xml_dir():
    xml_content = '''<cars>
    <row><car_model>Tesla</car_model><year_of_manufact'''
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', mode="w") as f:
        f.write(xml_content)
        return f.name

@pytest.fixture
def missing_data_xml_dir():
    xml_content = '''<cars>
    <row><car_model>Tesla</car_model><year_of_manufacture>2021</year_of_manufacture><price>35000</price></row>
    <row><car_model>Audi</car_model><fuel>Gasoline</fuel></row>
</cars>'''
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml', mode="w") as f:
        f.write(xml_content)
        return f.name
###TEST

# test csv files 

def test_double_csv_extraction(double_csv_dir):
    df = extract_from_csv(double_csv_dir)
    assert not df.empty
    assert len(df) == 4
    assert set(df['car_model']) == {'Volkswagen', 'Honda', 'Toyota', 'Ford'}

def test_empty_csv_extraction(empty_csv_dir):
    df = extract_from_csv(empty_csv_dir)
    assert df.empty

def test_malformed_csv_extraction(malformed_csv_dir):
    df = extract_from_csv(malformed_csv_dir)   
    assert not df.empty
    assert len(df) == 2
    assert set(df['car_model']) == {'Toyota', 'Honda'}

#test json files

def test_json_extraction(temp_json_dir):
    df = extract_from_json(temp_json_dir)   
    assert not df.empty
    assert len(df) == 1
    assert df['car_model'].iloc[0] == 'Ford'

def test_malformed_json_extraction(malformed_json_dir):
    with pytest.raises(ValueError):
        extract_from_json(malformed_json_dir)   
    
def test_extract_from_json_with_empty_fields(json_with_empty_fields):
    df = extract_from_json(json_with_empty_fields)
    assert len(df) == 2
    assert df.iloc[0]["car_model"] == ""
    assert pd.isnull(df.iloc[0]["year_of_manufacture"])
    assert pd.isnull(df.iloc[0]["price"])
    assert df.iloc[0]["fuel"] == ""

# tests xml files

def test_xml_extraction(temp_xml_dir):
    df = extract_from_xml(temp_xml_dir)   
    assert not df.empty
    assert len(df) == 2
    assert set(df['car_model']) == {'Tesla', 'BMW'}

def test_invalid_structure_xml_extraction(invalid_estructure_xml_dir):
    with pytest.raises(ET.ParseError):
        extract_from_xml(invalid_estructure_xml_dir)   

def test_missing_data_xml_extraction(missing_data_xml_dir):
    df = extract_from_xml(missing_data_xml_dir)   
    assert not df.empty
    assert len(df) == 2
    assert 'car_model' in df.columns
    assert 'year_of_manufacture' in df.columns
    assert 'price' in df.columns
    assert 'fuel' in df.columns
    assert df['car_model'].iloc[1] == 'Audi'

