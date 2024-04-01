import datetime
import sqlite3
import treebased
import json

default_params = {
    "XGB": {
      "n_estimators": 100,
      "max_depth": 6,
      "learning_rate": 0.3
    },
    "DTree": {
      "max_depth": 0.2,
      "min_samples": 7,
      "splitter": "best"
    },
    "RTree": {
      "n_estimators": 100, 
      "max_depth": None,
      "min_samples": 7
    },
    "ETree": { 
      "n_estimators": 100,
      "max_depth": None,
      "min_samples": 7,
      "criterion:": "gini"
    }
}

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

#regular run function
def run(json_req):
    print (json_req)
    #decode/parse incoming json
    xgb_params = json_req["model_req"]["XGB"]
    dtree_params = json_req["model_req"]["DTree"]
    rtree_params = json_req["model_req"]["RTree"]
    etree_params = json_req["model_req"]["ETree"]

    default_fill(json_req, default_params)

    #run model
    result = treebased.run_model('./Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km.csv', xgb_params, lg_params, cb_params)
    #print (result)

    #create json
    result_json = parse_to_json(result)
    #print('results')
    #print(result_json)

    #store results
    record(result, xgb_params, dtree_params, rtree_params, etree_params)
    
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
            if not json_model[param]:
                json_model[param] = default_val
        json_req["model_req"][model] = json_model
    
    #print(json) #after

#get runs from db function
def get_runs():

    keys = ['id', 'execution_time', 'run_date', 'accuracy', 'precision', 'recall', 'f1', 'heatmap']
    XGB_keys = ['n_estimators', 'max_depth', 'learning_rate']
    DT_keys = ['max_depth', 'min_samples', 'splitter']
    RT_keys = ['n_estimators', 'max_depth', 'min_samples']
    ET_keys = ['n_estimators', 'max_depth', 'min_samples', 'criterion']

    connection = sqlite3.connect('test_DB.db')
    c = connection.cursor()

    c.execute("SELECT * FROM TreeBased")
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
        idx_offset += len(keys) - 1   
        row_dict['XGB'] = {}
        for i, key in enumerate(XGB_keys):
            row_dict['XGB'][key] = r[i + idx_offset]
        idx_offset += len(XGB_keys) - 1 
        row_dict['DT_keys'] = {}
        for i, key in enumerate(DT_keys):
            row_dict['DT_keys'][key] = r[i + idx_offset]
        idx_offset += len(DT_keys) - 1 
        for i, key in enumerate(RT_keys):
            row_dict['RT_keys'][key] = r[i + idx_offset]
        idx_offset += len(RT_keys) - 1 
        for i, key in enumerate(ET_keys):
            row_dict['ET_keys'][key] = r[i + idx_offset]
        idx_offset += len(ET_keys) - 1 
        rows_dict["rows"].append(row_dict)

    #print(rows_dict)
    json_rows = json.dumps(rows_dict)
    return json_rows
 

#record in db function?
def record(result, xgb_params, dtree_params, rtree_params, etree_params):

    connection = sqlite3.connect('test_DB.db')
    c = connection.cursor()

    param_lists = [xgb_params, dtree_params, rtree_params, etree_params]
    record = list(result)

    for model_params in param_lists:
        for param in model_params:
            record.append(model_params[param])

    record.append(datetime.datetime.now())
    print(record)

    c.execute("INSERT INTO TreeBased (duration, accuracy, prec, recall, f1_score, heatmap_data, xgb_estimators, xgb_max_depth, xgb_learning_rate, dtree_max_depth, dtree_min_samples, dtree_splitter, rtree_estimators, rtree_max_depth, rtree_min_samples, etree_estimators, etree_max_depth, etree_min_samples, tree_criteion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (record))
    connection.commit()

    c.close()
    connection.close()

#read from db function? how are we searching
def read():
    pass

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

if __name__ == "__main__":
    run(json_ex)




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

#run(json_ex)
#get_runs()