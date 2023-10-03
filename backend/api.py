from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/helloworld')
def greet():
    return {"message": "Hello, API World!"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')