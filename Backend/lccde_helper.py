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
    xgb_params = json_req["model_req"]["XGB"]
    lg_params = json_req["model_req"]["LightGBM"]
    cb_params = json_req["model_req"]["CatBoost"]

    default_fill(json_req, default_params)

    #run model
    result = lccde.run_model('./Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km.csv', xgb_params, lg_params, cb_params)
    #print (result)

    #create json
    result_json = parse_to_json(result)
    #print('results')
    #print(result_json)
    
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

#rerun function
def rerun(json_req):
    #parse json

    #hit the db
    pass

#record in db function?
def record():
    pass

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

#testing json
# json_ex = {
#   "model_req": {
#   "dataset_path": "",
#     "XGB": {
#       "n_estimators": "100",
#       "max_depth": "",
#       "learning_rate": "0.1"
#     },
#     "LightGBM": {
#       "num_iterations": 100,
#       "max_depth": "",
#       "learning_rate": "0.1",
#       "num_leaves": "31",
#       "boosting_type": "gbdt"
#     },
#     "CatBoost": {
#       "n_estimators": 100, 
#       "max_depth": "",
#       "learning_rate": ""
#     }
#  }
# }

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