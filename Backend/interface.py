# Zane (3/10)
# this requires:
# 'pip install flask'
# 'pip install flask-cors'

# Aaron (3/23)
# This file will serve as a medium for requests to travel from fe -> be/db
# modifying currently called functions should be done with care

# Amy (3/29)
# to initialize the db:
# 'python local_db_setup.py'

# to start it up you do 
# 'python <filename>.py'

# TO RUN:
# navigate to Backend folder
# run: python interface.py

from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import mth_helper
import treebased_helper
import lccde_helper
import json

@app.route('/run-python-code', methods=['POST'])
def run_python_code():
    code = request.json.get('code')
    # Execute the Python code
    result = "Python received: [" + (code) + ']'
    return jsonify({'result': result})

# fe will hit one of these endpoints with a populated jsonm which will include params and the like
@app.route('/runLccde', methods=['PUT'])
def alg1():
    #in postman del .get('code')
    params = request.json.get('code')
    #jsonify incoming
    params = json.loads(params)
    result_json = lccde_helper.run(params)

    return jsonify(result_json)

@app.route('/retrieveLccde', methods=['GET'])
def alg2():
    result_json = lccde_helper.get_runs()
    return jsonify(result_json)

@app.route('/runMth', methods=['PUT'])
def alg3():
    params = request.json.get('code')
    params = json.loads(params)
    result_json = mth_helper.run(params)

    return jsonify(result_json)

@app.route('/retrieveMth', methods=['GET'])
def alg4():
    result_json = mth_helper.get_runs()
    return jsonify(result_json)

@app.route('/runTree', methods=['PUT'])
def alg5():
    params = request.json.get('code')
    params = json.loads(params)
    result_json, cm_json = treebased_helper.run(params)
    print(result_json)
    print(cm_json)
    print(jsonify(cm_json))
    return jsonify(result_json), jsonify(cm_json)
    # pass

@app.route('/retrieveTree', methods=['GET'])
def alg6():
    result_json = treebased_helper.get_runs()
    # print(result_json)
    return jsonify(result_json)
    # pass

if __name__ == '__main__':
    app.run(debug=True)

