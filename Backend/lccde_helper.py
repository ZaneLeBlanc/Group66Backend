import datetime
import sqlite3
import lccde
import json

default_params = {
    "XGB": {
      "n_estimators": 100,
      "max_depth": 6,
      "learning_rate": 0.3
    },
    "LightGBM": {
      "num_iterations": 100,
      "max_depth": -1,
      "learning_rate": 0.1,
      "num_leaves": 31,
      "boosting_type": "gbdt"
    },
    "CatBoost": {
      "n_estimators": 100, 
      "max_depth": 6,
      "learning_rate": 0.03
    }
}

#regular run function
def run(json_req):
    print (json_req)
    #decode/parse incoming json
    default_fill(json_req, default_params)

    xgb_params = json_req["model_req"]["XGB"]
    lg_params = json_req["model_req"]["LightGBM"]
    cb_params = json_req["model_req"]["CatBoost"]

    path = './Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/'
    dataset_path = str(json_req["model_req"]["dataset_path"])
    dataset = path + dataset_path
    #run model
    result = lccde.run_model(dataset, xgb_params, lg_params, cb_params)

    #create json
    result_json = parse_to_json(result)

    #store results
    record(result, xgb_params, lg_params, cb_params, dataset_path)
    
    return result_json
    #return json result

#fill the json will default parameters if they empty
def default_fill(json_req, default):
    #print(json) #before

    for model, model_params in default.items():
        json_model = json_req["model_req"].get(model, {})
        for param, default_val in model_params.items():
            if isinstance(json_model[param], str):
                if json_model[param].isnumeric():
                    json_model[param] = int(json_model[param])
                if isfloat(json_model[param]):
                    json_model[param] = float(json_model[param])
            if not json_model[param]:
                json_model[param] = default_val
        json_req["model_req"][model] = json_model
    
    print('**Params with defaults**\n' + str(json_req)) #after

def isfloat(str):
    try:
        if float(str).is_integer():
            return False
        return True
    except ValueError:
        return False

#get runs from db function
def get_runs():

    keys = ['id', 'run_date', 'dataset_path', 'execution_time', 'accuracy', 'precision', 'recall', 'f1', 'heatmap']
    XGB_keys = ['n_estimators', 'max_depth', 'learning_rate']
    LG_keys = ['num_iterations', 'max_depth', 'learning_rate', 'num_leaves', 'boosting_type']
    CB_keys = ['n_estimators', 'max_depth', 'learning_rate']

    connection = sqlite3.connect('test_DB.db')
    c = connection.cursor()

    c.execute("SELECT * FROM LCCDE")
    rows = c.fetchall()

    c.close()
    connection.close()
    #parse json
    
    rows_dict = { "rows" : [] }

    for r in rows:
        idx_offset = 0
        row_dict = {}
        for i, key in enumerate(keys):
            row_dict[key] = r[i]
        idx_offset += len(keys) 
        row_dict['XGB'] = {}
        for i, key in enumerate(XGB_keys):
            row_dict['XGB'][key] = r[i + idx_offset]
        idx_offset += len(XGB_keys) 
        row_dict['LightGBM'] = {}
        for i, key in enumerate(LG_keys):
            row_dict['LightGBM'][key] = r[i + idx_offset]
        idx_offset += len(LG_keys)
        row_dict['CatBoost'] = {}
        for i, key in enumerate(CB_keys):
            row_dict['CatBoost'][key] = r[i + idx_offset]
        rows_dict["rows"].append(row_dict)

    #print(rows_dict)
    json_rows = json.dumps(rows_dict)
    return json_rows
 

#record in db function?
def record(result, xgb_params, lg_params, cb_params, dataset_path):

    connection = sqlite3.connect('test_DB.db')
    c = connection.cursor()

    param_lists = [xgb_params, lg_params, cb_params]
    record = list(result)

    for model_params in param_lists:
        for param in model_params:
            record.append(model_params[param])

    record.append(datetime.datetime.now())
    record.append(dataset_path)
    print(record)

    c.execute("INSERT INTO LCCDE (duration, accuracy, prec, recall, f1_score, heatmap_data, xgb_n_estimators, xgb_max_depth, xgb_learning_rate, lg_num_iterations, lg_max_depth, lg_learning_rate, lg_num_leaves, lg_boosting_type, cb_n_estimators, cb_max_depth, cb_learning_rate, run_date, dataset_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (record))
    connection.commit()

    c.close()
    connection.close()

#read from db function? how are we searching
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

#testing json
json_ex = {
   "model_req": {
  "dataset_path": "",
     "XGB": {
       "n_estimators": "100",
       "max_depth": "",
       "learning_rate": "0.1"
     },
     "LightGBM": {
       "num_iterations": 100,
       "max_depth": "",
       "learning_rate": "0.1",
       "num_leaves": "31",
       "boosting_type": "gbdt"
   },
    "CatBoost": {
       "n_estimators": 100, 
       "max_depth": "",
       "learning_rate": ""
     }
  }
 }


#result format
# results = {
#   "model_results": {
#     "accuracy": "",
#     "precision": "",
#     "recall": "",
#     "f1": "",
#     "execution_time": "",
#     "heatmap": "Path to Heatmap Image"
#     }
# }

# running this on front end for lccde test
# {
#                 "model_req": {
#                   "dataset_name": "",
#                   "XGB": {
#                     "n_estimators": "",
#                     "max_depth": "",
#                     "learning_rate": ""
#                   },
#                   "LightGBM": {
#                     "num_iterations": "",
#                     "max_depth": "",
#                     "learning_rate": "",
#                     "num_leaves": "",
#                     "boosting_type": ""
#                   },
#                   "CatBoost": {
#                     "n_estimators": "",
#                     "max_depth": "",
#                     "learning_rate": ""
#                   }
#                 }
#               }
