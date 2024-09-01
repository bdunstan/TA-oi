import csv
import datetime
import importlib
import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Type
import time

import bcs_oi_api
import jsonlines
import requests
import yaml
from fastapi.encoders import jsonable_encoder

__all__ = ["Customer", "get_data"]

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class Customer:
    cpy_key: str
    client_id: str
    client_secret: str
    region: str


@dataclass
class EndpointQuery:
    model: Type[bcs_oi_api.BCSOIAPIBaseModel]
    filter: Optional[dict]
    addendum: Optional[str]

    @property
    def file_name_addendum(self) -> str:
         # Epmty string, so assume there is no addemdum
        if self.addendum is not None and not bool(self.addendum.strip()):
            return f'{self.addendum.strip()}'
        if self.addendum and self.addendum is not None:
            return f'_{self.addendum}'
        elif self.filter:
            return f'_{"_".join([f"{k}-{v}" for k, v in self.filter.items()])}'
        else:
            return ""

    def url_params(self, params: Optional[dict]) -> dict:
        if params is not None:
            params.update(self.filter)
            return params
        else:
            return self.filter


ENDPOINT_MODEL_MAPPING = {}
for k, v in dict([(name, cls) for name, cls in bcs_oi_api.models.__dict__.items() if isinstance(cls, type)]).items():
    if "url_path" in dir(v) and v.url_path():  # type: ignore
        ENDPOINT_MODEL_MAPPING[v.url_path()] = v  # type: ignore


def _my_json_converter(o) -> Optional[str]:
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    return None


def _create_directories(directory: str, cpy_key: str, config: dict) -> Tuple[str, str]:
    json_directory = f"{directory}/{config.get('directory', {}).get('json', 'json')}/{cpy_key}"
    csv_directory = f"{directory}/{config.get('directory', {}).get('csv', 'json')}"
    for d in [json_directory, csv_directory]:
        try:
            os.makedirs(d)
        except FileExistsError:
            pass
    return csv_directory, json_directory


def _vulnerable( bcs_oi_object ):
    bcs_oi_object_dict = bcs_oi_object.dict(by_alias=True)
    if bcs_oi_object_dict['matchConfidence'] == 'Not Vulnerable':
        return False
    return True

# Remvoe files before starting, it needs to be at the top level, so we can 
# aggregate multiplecollections into 1 files later - this is for when we 
# do filtering and want to use the same filename.
def _remove_file(
    file_name: str
) -> None:
  
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass

def _export(
    bcs_oi_objects: List[bcs_oi_api.BCSOIAPIBaseModel],
    csv_file_name: str,
    json_file_name: str,
    base_dict: dict,
    customer_index: int
) -> None:

    #if customer_index == 0:
        #try:
            #os.remove(csv_file_name)
        #except FileNotFoundError:
            #pass

    with jsonlines.open(f"{json_file_name}", mode="a") as json_writer:
        with open(rf"{csv_file_name}", "a") as csv_file:
            csv_writer = csv.writer(csv_file)
            for i, bcs_oi_object in enumerate(bcs_oi_objects):
                bcs_oi_object_dict = bcs_oi_object.dict(by_alias=True)
                if i == 0 and customer_index == 0:
                    csv_writer.writerow(list(base_dict.keys()) + list(bcs_oi_object_dict.keys()))
                if not i%50000:
                     # Incremet the timestamp value to the current time, every 50,000 records
                     # otherwise if its all at the sametime, splunk doesnt like it
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    base_dict["timestamp"] = timestamp
                base_dict_copy = base_dict.copy()
                base_dict_copy.update(bcs_oi_object_dict)
                serialized_dict = jsonable_encoder(base_dict_copy)
                csv_writer.writerow(list(serialized_dict.values()))
                json_writer.write(serialized_dict)


def _fetch_models(config: dict, config_file_directory: str) -> List[EndpointQuery]:
    endpoints = []
    endpoint_queries: List[EndpointQuery] = []
    try:
        endpoints_file = config["endpoints"]["file"]
    except KeyError:
        try:
            endpoints = config["endpoints"]["list"]
        except KeyError:
            endpoint_queries = []
        else:
            for endpoint in [endpoint for endpoint in endpoints if endpoint["endpoint"] in ENDPOINT_MODEL_MAPPING]:
                filter_dict = {}
                for filter in endpoint.get("filters", []):
                    filter_dict[filter["attribute"]] = filter["value"]
                endpoint_queries.append(
                    EndpointQuery(model=ENDPOINT_MODEL_MAPPING[endpoint["endpoint"]], filter=filter_dict, addendum=endpoint.get("addendum"))
                )
    else:
        if not os.path.isabs(endpoints_file):
            endpoints_file = os.path.join(config_file_directory, endpoints_file)
        with open(endpoints_file) as csvfile:
            endpointreader = csv.reader(csvfile)
            for row in endpointreader:
                if row[0] in ENDPOINT_MODEL_MAPPING:
                    endpoint_queries.append(EndpointQuery(model=ENDPOINT_MODEL_MAPPING[row[0]], filter={}), addendum=None)
                endpoints.append(row[0])
    return endpoint_queries


def get_data(customers: List[Customer], base_directory: str, config_file: str):
    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    endpoint_queries = _fetch_models(config=config, config_file_directory=os.path.dirname(os.path.abspath(config_file)))

    remove_file = {}
    for customer_index, customer in enumerate(customers):
        bcs_oi_api_instance = bcs_oi_api.bcs_oi_api.BCSOIAPI(
            client_id=customer.client_id, client_secret=customer.client_secret, region=customer.region
        )
        csv_directory, json_directory = _create_directories(
            directory=base_directory, cpy_key=customer.cpy_key, config=config
        )
            
        for endpoint_query in endpoint_queries:
            model = endpoint_query.model
            try:
                try:
                    i = importlib.import_module(f"src.bcs_oi_api_export.custom.{model.__name__.lower()}")
                except ModuleNotFoundError:
                     # This needs to be in the config.yaml file or some setup file
                    if model.__name__.lower() == 'uirsummary' or model.__name__.lower() == 'resetcount':
                        bcs_oi_api_objects = bcs_oi_api_instance.get_output( model=model )
                    else:
                        bcs_oi_api_objects = bcs_oi_api_instance.get_output(
                            model=model, url_params=endpoint_query.url_params(params={"max": "1000"})
                        )
                else:
                    if model.__name__.lower() == 'uirsummary' or  model.__name__.lower() == 'resetcount':
                        bcs_oi_api_objects = i.get_bcs_oi_api_objects( bcs_oi_api_instance=bcs_oi_api_instance )
                    else:
                        bcs_oi_api_objects = i.get_bcs_oi_api_objects( 
                            bcs_oi_api_instance=bcs_oi_api_instance,
                            url_params=endpoint_query.url_params(params={"max": "1000"})
                        )

                # Adding timestamp down here, otherwise solunk doenst like having every event with teh same timestamp
                timestamp = datetime.datetime.now().strftime(config.get("timeformat", "%Y-%m-%dT%H:%M:%S"))
                base_dict = {"cpyKey": customer.cpy_key, "timestamp": timestamp}

                file_name_addendum=f"{endpoint_query.file_name_addendum}".lower()
                file_name_addendum=file_name_addendum.replace(' ', '_')

                csv_filename=f"{csv_directory}/{customer.cpy_key}-{model.__name__.lower()}{file_name_addendum}.csv"
                json_filename=f"{json_directory}/{model.__name__.lower()}{file_name_addendum}.jsonl"

                # Remove the file once per run and only at the time we are collecting the data - not great and needs to be
                # a save/copy instead of a remove
                # This is so _export cna always append to the file and not have to worry about the addendum component
                if json_filename not in remove_file:
                    _remove_file( json_filename )
                    remove_file[json_filename] = True

                if csv_filename not in remove_file:
                    _remove_file( csv_filename )
                    remove_file[csv_filename] = True
                
                _export(
                    bcs_oi_objects = bcs_oi_api_objects,
                    csv_file_name  = f"{csv_filename}",
                    json_file_name = f"{json_filename}",
                    base_dict      = base_dict,
                    customer_index = customer_index
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to get the output for model {model.__name__.lower()} due to exception {e}")
