import asyncio
import websockets
import http.server
import socketserver
import threading

# Custom HTTP handler to define specific routes
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # Serve a simple response on the root path
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Hello World! This is the root path.")
        elif self.path == "/custom":
            # Serve a custom response for the "/custom" path
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Hello from the custom route!")
        else:
            # Default behavior for other paths
            super().do_GET()

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

def run_http_server():
    PORT = 8000
    Handler = CustomHTTPRequestHandler  # Use the custom handler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving HTTP on port", PORT)
        httpd.serve_forever()

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    # Create a thread for the HTTP server
    http_thread = threading.Thread(target=run_http_server)
    http_thread.start()

    # Run the WebSocket server in the main thread
    asyncio.run(main())
