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
import lccde_helper

@app.route('/run-python-code', methods=['POST'])
def run_python_code():
    code = request.json.get('code')
    # Execute the Python code
    result = "Python received: [" + (code) + ']'
    return jsonify({'result': result})

# fe will hit one of these endpoints with a populated jsonm which will include params and the like
@app.route('/lccde', methods=['POST'])
def alg1():
    params = request.json
    result_json = lccde_helper.run(params)
    return jsonify(result_json)

@app.route('/mth', methods=['POST'])
def alg2():
    pass

@app.route('/tree-based', methods=['POST'])
def alg3():
    pass


if __name__ == '__main__':
    app.run(debug=True)