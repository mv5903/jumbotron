from flask import Flask
from flask_cors import CORS

from backend.jumbotron import Matrix

ROWS = 48
COLUMNS = 64

MATRIX = [];

app = Flask(__name__)
CORS(app)

@app.route('/jumbotron')
def discover():
    return {
        "isAlive": True,
        "rows": ROWS,
        "columns": COLUMNS,
    }


if __name__ == '__main__':
    # Create empty matrix of pixels
    MATRIX = Matrix()
    app.run(debug=True, host='0.0.0.0')