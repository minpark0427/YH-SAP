import requests
import os
import dotenv

dotenv.load_dotenv()

class auto_code_api:
    def __init__(self, token=None, dev=False):
        # Determine the URL
        self.api_url = "http://127.0.0.1:8000/api/" if dev else "https://www.statsplan.com/api/"
        
        # 1. Use the passed token 
        # 2. If None, fall back to the correct environment variable
        if token:
            self.TOKEN = token
        else:
            env_key = "AUTOCODE_API_TOKEN_DEV" if dev else "AUTOCODE_API_TOKEN_PROD"
            self.TOKEN = os.getenv(env_key)

        # Throw a clear error if no token was found anywhere
        if not self.TOKEN:
            raise ValueError(f"API Token not found. Please provide it or set {env_key}")

        self.headers = {
            "Authorization": f"Token {self.TOKEN}",
            "Content-Type": "application/json"
        }

        self.variable_types = [
            "Time to event",
            "Count",
            "Continuous",
            "Binary",
            "Categorical",
         ]

    def post_(self, data, endpoint: str):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status() 

        return response.json()


    def get_(self, endpoint: str, params: dict = None):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def patch_(self, endpoint: str, data: dict):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}" +"/"
        response = requests.patch(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def put_(self, endpoint: str, data: dict):
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}" +"/"
        response = requests.put(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def clear_trial(self, endpoint: str, trial_id: int):

        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}clear-trial/?trial_id={trial_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.status_code
    
   
    def get_methods(self):
        response = self.get_("method/")
        return response
    
    def get_variable_type_id(self, title):
        variable_types = self.get_("variable_type/")
        for vt in variable_types:
            if vt['title'] == title:
                return vt['id']
        raise LookupErrorError(f"Variable type with title '{title}' not found.")


class trial_creator:
    def __init__(self, api_instance, acronym: str, title: str = ""):
        self.api = api_instance
        trial_data = self.api.get_("trial/", params = {"acronym": acronym, "title": title})
 

        trial_id = trial_data[0]['id'] if trial_data != [] else None
        if trial_id == None:
            print("Creating new trial...")
            trial_data = self.api.post_(
                data = {
                    "acronym": acronym,
                    "title": title
                },
                endpoint = "trial/"
            )
            self.trial_id = trial_data['id']
        else:
            print("Using existing trial...")
            self.trial_id = trial_id
    
        
    def patch_trial(self, new_data):
        response = self.api.patch_(endpoint = f"trial/{self.trial_id}", data =   new_data)
        return response


    def update_timepoints(self, timepoint_list):
        timepoint_ids = []
        for tp in timepoint_list:
            response = self.api.post_(endpoint = "timepoint/", data = tp)
            timepoint_ids.append(response['id'])
        self.timepoint_ids = timepoint_ids

        self.patch_trial(new_data = { "timepoints": self.timepoint_ids})


        return timepoint_ids
    
    def add_measure(self, variable_data, value_labels = None):
        if value_labels is not None:
            value_label_ids = []
            for label in value_labels:
                value_label =self.api.post_(endpoint = "value_label/", data = label)
                value_label_ids.append(value_label['id'])
            variable_data['value_labels'] = value_label_ids


        variable_type_id = self.api.get_variable_type_id(variable_data['variable_type'])
        variable_data['variable_type'] = variable_type_id

        measure = self.api.post_(endpoint = "measure/", data = variable_data)
        
        return measure

    def update_timevar(self, variable_data, value_labels):
        timevar = self.add_measure(variable_data, value_labels)
        self.time_variable_id = timevar['id']
        new_data = {
            "time_variable": self.time_variable_id,
        }
        self.patch_trial(new_data = new_data)
        return timevar
    
    def update_allocation_variable(self, variable_data, value_labels):
        allocation_var = "Method not yet implemented"
        print("Allocation variable update not yet implemented.")
        
        # allocation_var = self.add_measure(variable_data, value_labels)
        # self.allocation_variable_id = allocation_var['id']
        # new_data = {
        #     "allocation_variable": self.allocation_variable_id,
        # }
        # self.patch_trial(new_data = new_data)
        return allocation_var

    def update_allocation_groups(self, allocation_group_list):
        allocation_group_ids = []
        for ag in allocation_group_list:
            response = self.api.post_(endpoint = "allocation_group/", data = ag)
            allocation_group_ids.append(response['id'])
        self.allocation_group_ids = allocation_group_ids

        new_data = {
            "allocation_groups": self.allocation_group_ids,
        }
        self.patch_trial(new_data = new_data)

        return allocation_group_ids

  


    def get_timepoints(self):
        # Fetch the single trial object
        trial_data = self.api.get_(endpoint = f"trial/{self.trial_id}")
        timepoint_ids = trial_data.get('timepoints', [])
        tp_data_list = []
        for tp_id in timepoint_ids:
            tp_data = self.api.get_(endpoint = f"timepoint/{tp_id}")
            tp_data_list.append(tp_data)
        return tp_data_list
    
    def get_outcome_variables(self):
        outcome_vars = self.api.get_("outcome_variable/", params = {"trial": self.trial_id})
        return outcome_vars
    
    def get_measures(self):
        # Fetch the single trial object
        trial_data = self.api.get_(endpoint = f"trial/{self.trial_id}")
        return trial_data[0].get('measures', [])

    #outcomes list is a list of dicts with keys: label, variable, variable_type, timepoints


    def add_outcomes(self, outcome_list):
        outcome_ids = []
        for outcome in outcome_list:
            measure_data = {
                "label": outcome['label'],
                "variable": outcome['variable'],
                "variable_type": outcome['variable_type']
            }
            value_labels = outcome.get('value_labels', None)

            measure_response = self.add_measure(measure_data, value_labels)
            measure_id = measure_response['id']
            timepoint_list = self.get_timepoints()
        
            for tp in outcome['timepoints']:
     
                tp_dict = next((item for item in timepoint_list if item.get('label') == tp), None)
                tp_id = tp_dict['id']
                outcome_variable_data = {
                    "outcome": measure_id,
                    "timepoint": tp_id,
                    "trial": self.trial_id
                }

                response = self.api.post_(endpoint = "outcome_variable/", data = outcome_variable_data)
            outcome_ids.append(response['id'])
        self.outcome_ids = outcome_ids
        return outcome_ids
    
    def update_outcomes(self, outcome_list):
        self.api.clear_trial(endpoint=f"outcome_variable/", trial_id=self.trial_id)
        outcome_ids = self.add_outcomes(outcome_list)
        return outcome_ids
    
    def get_outcome_variable_id_from_outcome_label_timepoint(self, analysis, measures_list, timepoint_list, outcome_variable_list):
        outcome_label = analysis['outcome_label']
        timepoint_label = analysis['timepoint']

        measure = next((item for item in measures_list if item.get('label') == outcome_label), None)
        if measure is None:
            raise LookupError("Cannot find measure with label:", outcome_label)
        measure_id = measure['id']
        
        tp_dict = next((item for item in timepoint_list if item.get('label') == timepoint_label), None)
        if tp_dict is None:
            raise LookupError("Cannot find timepoint with label:", timepoint_label)
        tp_id = tp_dict['id']


        outcome_variable = next((item for item in outcome_variable_list if item.get('outcome') == measure_id and item.get('timepoint') == tp_id), None)
        if outcome_variable is None:
            raise LookupError(f"Cannot find outcome variable for {outcome_label} at {timepoint_label}. Check that this outcome is measured a the specified timepoint.")
        outcome_variable_id = outcome_variable['id']
        
        return {'outcome_variable_id': outcome_variable_id, 'measure_id': measure_id, 'timepoint_id': tp_id}

    
    def add_analyses(self, analysis_list):
        analysis_ids = []
        timepoint_list = self.get_timepoints()
        measures_list = self.api.get_(endpoint = "measure/")
        outcome_variable_list = self.get_outcome_variables()

        order = 0
        for analysis in analysis_list:
            order += 1
            ids = self.get_outcome_variable_id_from_outcome_label_timepoint(analysis, measures_list, timepoint_list, outcome_variable_list)
            analysis_data = {
                "trial": self.trial_id,
                "outcome": ids['measure_id'],
                "timepoint": ids['timepoint_id'],
                "method": analysis['method'],
                "order": order,
            }
            print("\n\nPosting analysis data:", analysis_data)
            response = self.api.post_(endpoint = "analysis/", data = analysis_data)
            analysis_ids.append(response['id'])
        self.analysis_ids = analysis_ids
        return analysis_ids
    
    def get_trial_details(self):
        trial_data = self.api.get_(endpoint = f"trial/{self.trial_id}", params = {"expand": "true"})
        return trial_data
    

    

        
