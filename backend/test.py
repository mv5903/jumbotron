from flask import Flask
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import eventlet

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/jumbotron')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(f"Echo: {message}")

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
