import http.server
from functools import wraps
import json

# A dictionary to hold routes and their associated handlers
route_registry = {}

# Decorator for registering routes
def route(path, method="GET"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        # Register the function and method with the path
        route_registry[(path, method)] = func
        return wrapper
    return decorator

# Custom HTTP handler to process requests based on the route registry
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _handle_response(self, response):
        """Helper function to handle responses."""
        
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        
        if isinstance(response, dict):
            # Handle dictionary response (send as JSON)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif isinstance(response, str):
            # Handle string response (send as text/html)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))

    def do_GET(self):
        handler = route_registry.get((self.path, "GET"))
        if handler:
            # Call the handler function for the route
            self.send_response(200)
            response = handler()  # Pass the request handler to the function
            self._handle_response(response)
        else:
            # Default behavior for non-registered routes
            super().do_GET()

    def do_POST(self):
        handler = route_registry.get((self.path, "POST"))
        if handler:
            # Call the handler function for the route
            self.send_response(200)
            response = handler()
            self._handle_response(response)
        else:
            # Default behavior for non-registered routes
            super().do_GET()