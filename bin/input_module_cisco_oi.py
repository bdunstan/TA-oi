
# encoding = utf-8

import os
import sys
import time
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "site-packages"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import csv
import importlib
from fastapi.encoders import jsonable_encoder
from dataclasses import dataclass
from typing import List, Optional, Tuple
import bcs_oi_api
import jsonlines
import yaml
import re
import json

TA_OI_PATH = os.path.abspath(os.path.dirname(__file__))+"/.."
CSV_PREFIX='cisco_bcs-'
from bcs_oi_api_export import Customer, get_data

# Load the CSV file
def load_csv(filename):
    
    data = []
    # Open file in read mode
    with open(filename, encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)
        for row in csv_reader:
            if not row:
                continue
            data.append(row)

    return data


'''
function to merge the CSV files that match a given file-format
<cpyKey>-<source>.csv
This is horrible, but I didnt want to us pandas...
Back and forward in data types - shows I dont understand python yet.
'''
def merge_csv( helper ):
    
    files = {}
    for filename in os.listdir( f'{TA_OI_PATH}/lookups' ):
        result = re.match(r'^(\d+)-(.*?).csv', filename)
        if result:
            result.group(2)
            if not result.group(2) in files:
                files[result.group(2)] = []
            files[result.group(2)].append( f'{TA_OI_PATH}/lookups/{filename}' )

    for query in files:
        aggregate = []
        for file in files[query]:
            data = load_csv( file )
            
            for row in data:
                aggregate.append(row)

        jaggregate = json.loads(json.dumps(aggregate))
        
        with open( f'{TA_OI_PATH}/lookups/{query}.csv', "w") as outf:
            csv_writer = csv.writer( outf )
            header_row = True
            for row in jaggregate:
                if header_row:
                    csv_writer.writerow( row.keys() )
                    header_row = False
                
                csv_writer.writerow( row.values() )
        
        with open( f'{TA_OI_PATH}/lookups/{CSV_PREFIX}{query}.csv', "w") as outf:
            csv_writer = csv.writer( outf )
            header_row = True
            for row in jaggregate:
                if header_row:
                    csv_writer.writerow( row.keys() )
                    header_row = False
                
                csv_writer.writerow( row.values() )

'''
function to merge the CSV files that match a given file-format
<cpyKey>-<source>.csv
This is horrible, but I didnt want to us pandas...
Back and forward in data types - shows I dont understand python yet.
'''
def write_index( helper, ew, company_key ):
    
    index=helper.get_output_index()
    
    helper.log_info(f'write_index: {index}')
    
    for filename in os.listdir( f'{TA_OI_PATH}/data/{company_key}' ):
        sourcetype = re.match(r'^([^\/]+?).jsonl', filename)
        if sourcetype:
            st = sourcetype.group(1)
            
            helper.log_info(f'process: {TA_OI_PATH}/data/{company_key}/{filename} - {st}')
            
            with open (f'{TA_OI_PATH}/data/{company_key}/{filename}', 'r') as source:
                for line in source:
                    jline = json.loads(line)
                    # To create a splunk event
                    if 'timestamp' in jline:
                         # Assumes all data is going into the same index and not an index per customer
                        event = helper.new_event(line, time=jline['timestamp'], host=None, index=index, source=None, sourcetype=f'cisco:bcs:{st}', done=True, unbroken=True)
                        ew.write_event( event )
                        # Below was for debug purposes only
                        #helper.log_info(f'event: {line} {st}')
                        #break

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # company_key = definition.parameters.get('company_key', None)
    # client_id = definition.parameters.get('client_id', None)
    # client_secret = definition.parameters.get('client_secret', None)
    # region = definition.parameters.get('region', None)
    # index_data = definition.parameters.get('index_data', None)
    pass

def collect_events(helper, ew):
    customers = []
    
    company_key         = helper.get_arg('company_key')
    client_id           = helper.get_arg('client_id')
    client_secret       = helper.get_arg('client_secret')
    region              = helper.get_arg('region')
    index_data          = helper.get_arg('index_data')
    security_vulnerable = helper.get_arg('security_vulnerable')
    
    
    proxy_settings = helper.get_proxy()

    if 'proxy_url' in proxy_settings:
        os.environ['http_proxy']  = f"http://{proxy_settings['proxy_username']}:{proxy_settings['proxy_password']}@{proxy_settings['proxy_url']}:{proxy_settings['proxy_port']}"
        os.environ['HTTP_PROXY']  = f"http://{proxy_settings['proxy_username']}:{proxy_settings['proxy_password']}@{proxy_settings['proxy_url']}:{proxy_settings['proxy_port']}"
        os.environ['https_proxy'] = f"http://{proxy_settings['proxy_username']}:{proxy_settings['proxy_password']}@{proxy_settings['proxy_url']}:{proxy_settings['proxy_port']}"
        os.environ['HTTPS_PROXY'] = f"http://{proxy_settings['proxy_username']}:{proxy_settings['proxy_password']}@{proxy_settings['proxy_url']}:{proxy_settings['proxy_port']}"
    
    customers.append( Customer( 
        cpy_key       = company_key,
        client_id     = client_id,
        client_secret = client_secret,
        region        = region,
    ))
    
     # This is a bit of a hack as the yaml files are managed at the core and this needs to be managed by Splunk.
    if security_vulnerable:
        get_data(customers=customers, base_directory=TA_OI_PATH, config_file=TA_OI_PATH+"/etc/conf-vulnerable.yaml")
    else:
        get_data(customers=customers, base_directory=TA_OI_PATH, config_file=TA_OI_PATH+"/etc/conf.yaml")
    
    if index_data:
        write_index(helper, ew, company_key)
    
    merge_csv( helper )
    
