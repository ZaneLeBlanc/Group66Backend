# Zane (3/10)
# this requires:
# 'pip install flask'
# 'pip install flask-cors'

# to start it up you do 
# 'python <filename>.py'

from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/run-python-code', methods=['POST'])
def run_python_code():
    code = request.json.get('code')
    # Execute the Python code
    result = "Python received: [" + (code) + ']'
    return jsonify({'result': result})

@app.route('/lccde', methods=['POST'])
def alg1():
    pass

@app.route('/mth', methods=['POST'])
def alg2():
    pass

@app.route('/tree-based', methods=['POST'])
def alg3():
    pass


if __name__ == '__main__':
    app.run(debug=True)