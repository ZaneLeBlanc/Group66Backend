# Zane (3/10)
# this requires:
# 'pip install flask'
# 'pip install flask-cors'

# Aaron (3/23)
# This file will serve as a medium for requests to travel from fe -> be/db
# modifying currently called functions should be done with care

# to start it up you do 
# 'python <filename>.py'

from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
import lccde

@app.route('/run-python-code', methods=['POST'])
def run_python_code():
    code = request.json.get('code')
    # Execute the Python code
    result = "Python received: [" + (code) + ']'
    return jsonify({'result': result})

# fe will hit one of these endpoints with a populated jsonm which will include params and the like
@app.route('/lccde', methods=['POST'])
def alg1():
    params = code = request.json.get('code')
    path = ''
    if params == 'cicds2017_sample_km':
        path = './Intrusion-Detection-System-Using-Machine-Learning-main/data/CICIDS2017_sample_km.csv'
    results = lccde.run_model(path)
    return jsonify({'result': results})

@app.route('/mth', methods=['POST'])
def alg2():
    pass

@app.route('/tree-based', methods=['POST'])
def alg3():
    pass


if __name__ == '__main__':
    app.run(debug=True)