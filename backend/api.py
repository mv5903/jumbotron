from flask import Flask
from flask_cors import CORS

ROWS = 48
COLUMNS = 64

app = Flask(__name__)
CORS(app)

@app.route('/jumbotron')
def discover():
    return {
        "isAlive": True,
        "rows": ROWS,
        "columns": COLUMNS,
    }

@app.route('/jumbotron')
def greet():
    return {"message": "Hello, API World!"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')