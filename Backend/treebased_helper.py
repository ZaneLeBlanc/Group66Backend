from datetime import datetime
import sqlite3
import treebased
import json
import sqlalchemy
from db_session import Session, engine
from data_models import TreeBased, LCCDE
from sqlalchemy import text, select, desc
import numpy as np

default_params = {
    "XGB": {
      "n_estimators": 100,
      "max_depth": 6,
      "learning_rate": 0.3
    },
    "DTree": {
      "max_depth": None,
      "min_samples_split": 2,
      "splitter": "best"
    },
    "RTree": {
      "n_estimators": 100, 
      "max_depth": None,
      "min_samples_split": 2
    },
    "ETree": { 
      "n_estimators": 100,
      "max_depth": None,
      "min_samples_split": 2
    }
}

#regular run function
def run(json_req):
    print (json_req)

    #decode/parse incoming json
    xgb_params = json_req["model_req"]["XGB"]
    dtree_params = json_req["model_req"]["DTree"]
    rtree_params = json_req["model_req"]["RTree"]
    etree_params = json_req["model_req"]["ETree"]

    default_fill(json_req, default_params)
    
    #add functionality for different datasets
    path = './Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/'
    dataset_path = str(json_req["model_req"]["dataset_path"])
    dataset = path + dataset_path

    #run model
    result, cm = treebased.run_model(dataset, xgb_params, dtree_params, rtree_params, etree_params)
    # print(result)

    #create json
    result_json = parse_to_json(result)
    cm_json = ndarray_to_dict(cm)
    # print('results')
    # print(result_json)

    #store results
    record(result, xgb_params, dtree_params, rtree_params, etree_params, dataset_path)
    
    return result_json, cm_json

#fill the json will default parameters if they empty
def default_fill(json_req, default):
    #print(json) #before

    for model, model_params in default.items():
        json_model = json_req["model_req"].get(model, {})
        for param, default_val in model_params.items():
            if isinstance(json_model[param], str):
                if json_model[param].isnumeric():
                    json_model[param] = int(json_model[param])
            if not json_model[param]:
                json_model[param] = default_val
        json_req["model_req"][model] = json_model
    
    #print(json) #after

#get runs from db function
def get_runs():

    keys = ['id', 'run_date', 'dataset_path', 'execution_time', 'accuracy', 'precision', 'recall', 'f1', 'heatmap']
    XGB_keys = ['n_estimators', 'max_depth', 'learning_rate']
    DT_keys = ['max_depth', 'min_samples_split', 'splitter']
    RT_keys = ['n_estimators', 'max_depth', 'min_samples_split']
    ET_keys = ['n_estimators', 'max_depth', 'min_samples_split']

    with Session.begin() as session:
        rows_dict = { "rows" : [] }

        for class_instance in session.query(TreeBased).all():
            # print(vars(class_instance))
            inst = vars(class_instance)
            del inst[list(inst)[0]]
            # print(inst)
            # r = tuple(list(inst.values()))
            # print(r)
    #         idx_offset = 0
            row_dict = {}
            row_dict['id'] = class_instance.run_id
            row_dict['run_date'] = class_instance.run_date
            row_dict['dataset_path'] = class_instance.dataset_path
            row_dict['execution_time'] = class_instance.duration
            row_dict['accuracy'] = class_instance.accuracy
            row_dict['precision'] = class_instance.prec
            row_dict['recall'] = class_instance.recall
            row_dict['f1'] = class_instance.f1_score
            row_dict['heatmap'] = class_instance.heatmap_data

            row_dict['XGB'] = {}
            row_dict['XGB']['n_estimators'] = class_instance.xgb_estimators
            row_dict['XGB']['max_depth'] = class_instance.xgb_max_depth
            row_dict['XGB']['learning_rate'] = class_instance.xgb_learning_rate

            row_dict['DT_keys'] = {}
            row_dict['DT_keys']['max_depth'] = class_instance.dtree_max_depth
            row_dict['DT_keys']['min_samples_split'] = class_instance.dtree_min_samples
            row_dict['DT_keys']['splitter'] = class_instance.dtree_splitter

            row_dict['RT_keys'] = {}
            row_dict['RT_keys']['n_estimators'] = class_instance.rtree_estimators
            row_dict['RT_keys']['max_depth'] = class_instance.rtree_max_depth
            row_dict['RT_keys']['min_samples_split'] = class_instance.rtree_min_samples

            row_dict['ET_keys'] = {}
            row_dict['ET_keys']['n_estimators'] = class_instance.etree_estimators
            row_dict['ET_keys']['max_depth'] = class_instance.etree_max_depth
            row_dict['ET_keys']['min_samples_split'] = class_instance.etree_min_samples
    #         # print(list(enumerate(keys)))
    #         for i, key in enumerate(keys):
    #             row_dict[key] = r[i]
    #         idx_offset += len(keys) - 1 
    #         print(row_dict)  
    #         row_dict['XGB'] = {}
    #         for i, key in enumerate(XGB_keys):
    #             row_dict['XGB'][key] = r[i + idx_offset]
    #         idx_offset += len(XGB_keys) - 1 
    #         print(row_dict) 
    #         row_dict['DT_keys'] = {}
    #         for i, key in enumerate(DT_keys):
    #             row_dict['DT_keys'][key] = r[i + idx_offset]
    #         idx_offset += len(DT_keys) - 1 
    #         print(row_dict) 
    #         # print(list(enumerate(RT_keys)))
    #         row_dict['RT_keys'] = {}
    #         for i, key in enumerate(RT_keys):
    #             print(i, key)
    #             row_dict['RT_keys'][key] = r[i + idx_offset]
    #         idx_offset += len(RT_keys) - 1 
    #         print(row_dict) 
    #         row_dict['ET_keys'] = {}
    #         for i, key in enumerate(ET_keys):
    #             row_dict['ET_keys'][key] = r[i + idx_offset]
    #         idx_offset += len(ET_keys) - 1  
            rows_dict["rows"].append(row_dict)
            # 
        print(rows_dict)
        session.close()

    json_rows = json.dumps(rows_dict)
    return json_rows


#record in db function?
def record(result, xgb_params, dtree_params, rtree_params, etree_params, dataset_path):

    with Session.begin() as session:
        param_lists = [xgb_params, dtree_params, rtree_params, etree_params]
        record = list(result)

        for model_params in param_lists:
            for param in model_params:
                record.append(model_params[param])

        now = datetime.now()
        record.append(str(now.strftime("%Y-%m-%d %H:%M:%S.%f")))
        record.append(dataset_path)
        rec_str = str(record)[1:-1]
        rec_str = rec_str.replace("None", "NULL")

        query = f'INSERT INTO TreeBased (duration, accuracy, prec, recall, f1_score, heatmap_data, xgb_estimators, xgb_max_depth, xgb_learning_rate, dtree_max_depth, dtree_min_samples, dtree_splitter, rtree_estimators, rtree_max_depth, rtree_min_samples, etree_estimators, etree_max_depth, etree_min_samples, run_date, dataset_path) VALUES ({rec_str})'
        print(query)
        session.execute(text(query))

        session.commit()
        session.close()

# #read from db function? how are we searching
# def read():
#     pass

#decode/parse json function?
def parse_to_json(result):
    keys = ['execution_time', 'accuracy', 'precision', 'recall', 'f1', 'heatmap']
    json_result = {"model_results": {}}

    for idx, key in enumerate(keys):
        if idx >= len(result):
            json_result["model_results"][key] = None
        else:
            json_result["model_results"][key] = result[idx]
    
    json_result = json.dumps(json_result)
    return json_result

import numpy as np

def ndarray_to_dict(arr):
    if not isinstance(arr, np.ndarray) or arr.ndim != 2:
        raise ValueError("Input must be a 2D numpy array.")
    
    rows, cols = arr.shape
    result_dict = {}
    
    for i in range(rows):
        for j in range(cols):
            key = f"{i}{j}"
            result_dict[key] = str(arr[i, j])  # Convert the value to string
    
    return result_dict




#result format
# results = {
#   "model_results": {
#     "execution_time": "",
#     "accuracy": "",
#     "precision": "",
#     "recall": "",
#     "f1": "",
#     "heatmap": "Path to Heatmap Image"
#     }
# }

#testing json

# running this on front end for tree based test
# {
#     "model_req": {
#         "dataset_path": "CICIDS2017_sample.csv",
#         "XGB": {
#       "n_estimators": 100,
#       "max_depth": 6,
#       "learning_rate": 0.3
#     },
#     "DTree": {
#       "max_depth": null,
#       "min_samples_split": 2,
#       "splitter": "best"
#     },
#     "RTree": {
#       "n_estimators": 100, 
#       "max_depth": null,
#       "min_samples_split": 2
#     },
#     "ETree": { 
#       "n_estimators": 100,
#       "max_depth": null,
#       "min_samples_split": 2
#     }
#     }
# }