# Zane (3/10)
# this requires:
# 'pip install flask'
# 'pip install flask-cors'

# to start it up you do 
# 'python test.py'

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

if __name__ == '__main__':
    app.run(debug=True)