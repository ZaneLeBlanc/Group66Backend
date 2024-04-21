import datetime
import sqlite3
import mth
import json

default_params = {
    "training_allocation" : 0.8,
    "max_features" : 20,
    "hpo_max_evals" : 20
}

#regular run function
def run(json_req):
    print (json_req)
    #decode/parse incoming json
    default_fill(json_req, default_params)

    train_split = json_req["model_req"]["training_allocation"]
    max_features = json_req["model_req"]["max_features"]
    hpo_max_evals = json_req["model_req"]["hpo_max_evals"]

    path = './Backend/Intrusion-Detection-System-Using-Machine-Learning-main/data/'
    dataset_path = str(json_req["model_req"]["dataset_path"])
    dataset = path + dataset_path
    #run model
    result = mth.run_model(dataset, train_split, max_features, hpo_max_evals)
    #print (result)

    #create json
    result_json = parse_to_json(result)
    #print('results')
    #print(result_json)

    #store results
    record(result, train_split, max_features, hpo_max_evals, dataset_path)
    
    return result_json
    #return json result

#fill the json will default parameters if they empty
def default_fill(json_req, default):
    print(json_req) #before
    for param, value in default.items():
        if isinstance(json_req["model_req"][param], str):
                if json_req["model_req"][param].isnumeric():
                    json_req["model_req"][param] = int(json_req["model_req"][param])
        if not json_req["model_req"][param]:
            json_req["model_req"][param] = value

    print(json_req) #after

#get runs from db function
def get_runs():

    keys = ['id', 'run_date', 'dataset_path', 'execution_time', 'accuracy', 'precision', 'recall', 'f1', 'heatmap', 'training_allocation', 'max_features', 'hpo_max_evals']

    connection = sqlite3.connect('test_DB.db')
    c = connection.cursor()

    c.execute("SELECT * FROM mth")
    rows = c.fetchall()
    print(rows)
    c.close()
    connection.close()
    #parse json
    
    rows_dict = { "rows" : [] }

    for r in rows:
        row_dict = {}
        for i, key in enumerate(keys):
            row_dict[key] = r[i]
        rows_dict["rows"].append(row_dict)

    print(rows_dict)
    json_rows = json.dumps(rows_dict)
    return json_rows
 

#record in db function?
def record(result, train_split, max_features, hpo_max_evals, dataset_path):

    connection = sqlite3.connect('test_DB.db')
    c = connection.cursor()

    param_lists = [train_split, max_features, hpo_max_evals]
    record = list(result)

    for param in param_lists:
        record.append(param)

    record.append(datetime.datetime.now())
    record.append(dataset_path)

    c.execute("INSERT INTO mth (duration, accuracy, prec, recall, f1_score, heatmap_data, train_split, max_features, hpo_max_evals, run_date, dataset_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (record))
    connection.commit()

    c.close()
    connection.close()

#read from db function? how are we searching
# def read():
#     pass

#parse json result
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
        "training_allocation" : "",
        "max_features" : "",
        "hpo_max_evals" : ""
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

 #running this on front end for lccde test
test = {
    "model_req": {
        "dataset_path": "CICIDS2017_sample_km.csv",
        "training_allocation" : "",
        "max_features" : "",
        "hpo_max_evals" : ""
    }
}

#print(run(test))