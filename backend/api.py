# pip imports
import json
import os
import socketserver
import subprocess
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from threading import Event
import time
import eventlet
from PIL import Image
from io import BytesIO
import cv2
import websockets
from werkzeug.utils import secure_filename
from flask_sockets import Sockets
import asyncio

# local imports
from utils.jumbotron import Jumbotron
from utils.config import Config
from utils.httpDecorator import CustomHTTPRequestHandler, route 

try:
    # Setup
    temp_filename = None
    thread_started = False
    thread_stop_event = Event()
    video_is_playing = True
    app = Flask(__name__)
    CORS(app)
    sockets = Sockets(app)
    clients = set()
    jumbotron_updater_thread = None

    # region Helper Methods
    def save_state(state):
        with open(Config.STATE_FILE, 'w') as file:
            json.dump(state, file)

    def load_state():
        if os.path.exists(Config.STATE_FILE):
            with open(Config.STATE_FILE, 'r') as file:
                return json.load(file)
        return None

    def convert_matrix_to_image(matrix):
        image = Image.new("RGB", (Config.COLUMNS, Config.ROWS))
        for row in range(Config.ROWS):
            for column in range(Config.COLUMNS):
                pixel = matrix[row][column]
                r, g, b = pixel['r'], pixel['g'], pixel['b']
                image.putpixel((column, row), (r, g, b))
        return image

    async def jumbotron_updater(websocket):
        Config.LOGGER.info("Client connected")
        while not thread_stop_event.is_set():
            if (Config.MATRIX is not None):
                try:
                    message = json.dumps({
                        'data': Config.MATRIX.get2DArrayRepresentation(),
                        'timestamp': time.time_ns()
                    })
                    await websocket.send(message)
                except Exception as e:
                    await websocket.close() 
                    Config.LOGGER.info("Client disconnected")
                    break
                await asyncio.sleep(1/Config.UPDATES_PER_SECOND) 

    def video_playback_thread():
        try:
            video = cv2.VideoCapture(temp_filename)

            if not video.isOpened():
                Config.LOGGER.warning("Could not open video")
                return

            start_time = time.time()
            frames_processed = 0

            while video_is_playing:
                ret, frame = video.read()
                if not ret:
                    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    start_time = time.time()
                    frames_processed = 0
                    continue

                expected_time = start_time + (frames_processed / Config.UPDATES_PER_SECOND)
                current_time = time.time()
                if current_time < expected_time:
                    time.sleep(expected_time - current_time)
                elif current_time > expected_time + (1 / Config.UPDATES_PER_SECOND):
                    frames_processed += 1
                    continue

                # Get the current brightness setting
                current_brightness = Config.MATRIX.getBrightness()

                # Convert the frame to an image and adjust brightness
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                matrix_representation = Jumbotron.convert_image_to_matrix(image, current_brightness)

                # Update the matrix with the new frame
                Config.MATRIX.update_from_matrix_array(matrix_representation)
                frames_processed += 1

            video.release()
        except Exception as e:
            Config.LOGGER.error("Error in video playback thread: %s", str(e))
            
    #endregion
    def json_response(data, status=200):
        return json.dumps(data), status

    def send_file(file_stream, mime_type='application/octet-stream', status=200):
        return file_stream.read(), status, mime_type
    
    @route('/')
    def hello():
        return json_response({ "hi": "there" })

    @route('/jumbotron', method='GET')
    def discover():
        Config.LOGGER.info("Client discovered Jumbotron API")
        return json_response({
            "isAlive": True,
            "rows": Config.ROWS,
            "columns": Config.COLUMNS,
        })

    @route('/jumbotron/pixel/<int:row>/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>', method='GET')
    def update_pixel(row, column, r, g, b, brightness):
        Config.LOGGER.info(
            "Updating pixel at row: %d, column: %d to r: %d, g: %d, b: %d, brightness: %d",
            row, column, r, g, b, brightness
        )
        Config.MATRIX.updatePixel(int(row), int(column), int(r), int(g), int(b), int(brightness))
        return json_response({"success": True})

    @route('/jumbotron/row/<int:row>/<int:r>/<int:g>/<int:b>/<int:brightness>', method='GET')
    def update_row(row, r, g, b, brightness):
        Config.LOGGER.info(
            "Updating row: %d to r: %d, g: %d, b: %d, brightness: %d",
            row, r, g, b, brightness
        )
        Config.MATRIX.updateRow(int(row), int(r), int(g), int(b), int(brightness))
        return json_response({"success": True})

    @route('/jumbotron/column/<int:column>/<int:r>/<int:g>/<int:b>/<int:brightness>', method='GET')
    def update_column(column, r, g, b, brightness):
        Config.LOGGER.info(
            "Updating column: %d to r: %d, g: %d, b: %d, brightness: %d",
            column, r, g, b, brightness
        )
        Config.MATRIX.updateColumn(int(column), int(r), int(g), int(b), int(brightness))
        return json_response({"success": True})

    @route('/jumbotron/all/<int:r>/<int:g>/<int:b>/<int:brightness>', method='GET')
    def update_all(r, g, b, brightness):
        Config.LOGGER.info(
            "Updating all pixels to r: %d, g: %d, b: %d, brightness: %d",
            r, g, b, brightness
        )
        Config.MATRIX.updateAll(int(r), int(g), int(b), int(brightness))
        return json_response({"success": True})

    @route('/jumbotron/reset', method='GET')
    def reset():
        global video_is_playing
        Config.LOGGER.info("Resetting all pixels")
        video_is_playing = False
        time.sleep(1 / Config.UPDATES_PER_SECOND)
        Config.MATRIX.reset()
        return json_response({"success": True})

    @route('/jumbotron/upload/<int:brightness>', method='POST')
    def upload_image(post_data, form, brightness):
        global video_is_playing
        Config.LOGGER.info("Uploading image")
        if 'file' not in form:
            Config.LOGGER.warning("No file part in the request")
            return json_response({'error': 'No file part in the request.'}, status=400)

        file_field = form['file']
        if not file_field.filename:
            Config.LOGGER.info("No file selected for uploading")
            return json_response({'error': 'No file selected for uploading.'}, status=400)

        video_is_playing = False
        time.sleep(1 / Config.UPDATES_PER_SECOND)
        file_data = file_field.file.read()
        image = Image.open(BytesIO(file_data))
        matrix_representation = Jumbotron.convert_image_to_matrix(image, int(brightness))
        Config.MATRIX.update_from_matrix_array(matrix_representation)
        Config.LOGGER.info("Image uploaded successfully")
        save_state({'type': 'image', 'content': matrix_representation})
        return json_response(matrix_representation)

    @route('/jumbotron/brightness/<int:brightness>', method='POST')
    def brightness_update(post_data, brightness):
        brightness = int(brightness)
        Config.LOGGER.info("Updating brightness to %d", brightness)
        Config.MATRIX.updateBrightness(brightness)
        return json_response({"success": True})

    @route('/jumbotron/brightness', method='GET')
    def get_brightness():
        Config.LOGGER.info("Getting brightness")
        brightness = Config.MATRIX.getBrightness()
        return json_response({"brightness": brightness})

    @route('/jumbotron/save_current_matrix/<string:matrixname>', method='POST')
    def save_current_matrix(post_data, matrixname):
        global video_is_playing, temp_filename
        Config.LOGGER.info("Saving current content to file: %s", matrixname)
        if not os.path.exists(Config.SAVES_DIR):
            Config.LOGGER.info("Creating saves directory")
            os.makedirs(Config.SAVES_DIR)

        save_data = {}
        if video_is_playing:
            Config.LOGGER.info("Video is currently playing - saving the video file")
            try:
                current_video_filepath = temp_filename
                save_data['type'] = 'video'
                save_data['content'] = current_video_filepath  # Save the path
            except Exception as e:
                Config.LOGGER.error(f"Error saving video: {str(e)}")
                return json_response({"success": False, "error": str(e)}, status=500)
        else:
            Config.LOGGER.info("Saving current matrix as a still frame")
            current_matrix_state = Config.MATRIX.get2DArrayRepresentation()
            save_data['type'] = 'image'
            save_data['content'] = current_matrix_state

        filename = f"{matrixname}.json"
        filepath = os.path.join(Config.SAVES_DIR, filename)
        try:
            with open(filepath, 'w') as file:
                json.dump(save_data, file)
            Config.LOGGER.info("Current content saved successfully")
            return json_response({"success": True, "filename": filename})
        except Exception as e:
            Config.LOGGER.error(f"Error saving content: {str(e)}")
            return json_response({"success": False, "error": str(e)}, status=500)

    @route('/jumbotron/get_saved_matrices', method='GET')
    def get_saved_matrices():
        Config.LOGGER.info("Getting saved matrices")
        if not os.path.exists(Config.SAVES_DIR):
            os.makedirs(Config.SAVES_DIR)

        files = [
            f for f in os.listdir(Config.SAVES_DIR)
            if os.path.isfile(os.path.join(Config.SAVES_DIR, f)) and f.endswith(".json")
        ]

        data = [{"filename": f, "image": f"/jumbotron/get_saved_matrix_image/{f}"} for f in files]

        Config.LOGGER.info("Saved matrices retrieved successfully")
        return json_response(data)

    @route('/jumbotron/play_saved_matrix/<string:filename>', method='GET')
    def play_saved_matrix(filename):
        Config.LOGGER.info("Playing saved matrix: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        try:
            with open(filepath, 'r') as file:
                saved_content = json.load(file)

            if saved_content['type'] == 'image':
                Config.MATRIX.update_from_matrix_array(saved_content['content'])
                Config.LOGGER.info("Saved matrix played successfully")
                return json_response({"success": True})
            else:
                Config.LOGGER.error("Cannot play non-image content with this endpoint")
                return json_response({"success": False, "error": "Cannot play non-image content with this endpoint"}, status=400)
        except FileNotFoundError:
            Config.LOGGER.error("Saved matrix file not found: %s", filename)
            return json_response({"success": False, "error": "File does not exist."}, status=404)
        except Exception as e:
            Config.LOGGER.error(f"Error playing saved matrix: {str(e)}")
            return json_response({"success": False, "error": str(e)}, status=500)

    @route('/jumbotron/delete_saved_matrix/<string:filename>', method='DELETE')
    def delete_saved_matrix(filename):
        Config.LOGGER.info("Deleting saved matrix: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as file:
                    saved_content = json.load(file)
                    if saved_content['type'] == 'video':
                        video_path = saved_content['content']
                        if os.path.exists(video_path):
                            os.remove(video_path)
                            Config.LOGGER.info("Video file deleted successfully")
                        else:
                            Config.LOGGER.warning("Video file does not exist")
                os.remove(filepath)
                Config.LOGGER.info("Saved matrix deleted successfully")
                return json_response({"success": True})
            except Exception as e:
                Config.LOGGER.error(f"Error deleting matrix: {str(e)}")
                return json_response({"success": False, "error": str(e)}, status=500)
        else:
            Config.LOGGER.warning("File does not exist")
            return json_response({"success": False, "error": "File does not exist."}, status=404)

    @route('/jumbotron/activate_saved_matrix/<string:filename>', method='POST')
    def activate_saved_matrix(post_data, filename):
        global temp_filename, video_is_playing
        Config.LOGGER.info("Activating saved matrix: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        try:
            with open(filepath, 'r') as file:
                saved_content = json.load(file)

            if not isinstance(saved_content, dict):
                Config.LOGGER.error("Invalid content format in file: %s", filename)
                return json_response({"success": False, "error": "Invalid content format."}, status=400)

            if 'type' not in saved_content or 'content' not in saved_content:
                Config.LOGGER.error("Missing required keys in saved content: %s", filename)
                return json_response({"success": False, "error": "Invalid content format."}, status=400)

            video_is_playing = False
            time.sleep(1 / Config.UPDATES_PER_SECOND)

            if saved_content['type'] == 'video':
                video_path = saved_content['content']
                if os.path.exists(video_path):
                    video_is_playing = True
                    temp_filename = video_path
                    save_state({'type': 'video', 'filename': filename, 'brightness': 40})
                    eventlet.spawn(video_playback_thread)
                else:
                    Config.LOGGER.error("Video file not found: %s", video_path)
                    return json_response({"success": False, "error": "Video file not found."}, status=404)
            elif saved_content['type'] == 'image':
                Config.MATRIX.update_from_matrix_array(saved_content['content'])
                video_is_playing = False
                save_state({'type': 'image', 'content': saved_content['content']})
            else:
                Config.LOGGER.error("Unknown content type: %s", saved_content['type'])
                return json_response({"success": False, "error": "Unknown content type."}, status=400)

            Config.LOGGER.info("Saved content activated successfully")
            return json_response({"success": True})

        except FileNotFoundError:
            Config.LOGGER.error("Saved content file not found: %s", filename)
            return json_response({"success": False, "error": "File does not exist."}, status=404)
        except json.JSONDecodeError:
            Config.LOGGER.error("Invalid JSON format in file: %s", filename)
            return json_response({"success": False, "error": "Invalid JSON format."}, status=400)
        except Exception as e:
            Config.LOGGER.error(f"Error activating saved content: {str(e)}")
            return json_response({"success": False, "error": str(e)}, status=500)

    @route('/jumbotron/get_saved_matrix_image/<string:filename>', method='GET')
    def get_saved_matrix_image(filename):
        Config.LOGGER.info("Getting preview for saved content: %s", filename)
        filepath = os.path.join(Config.SAVES_DIR, filename)

        try:
            with open(filepath, 'r') as file:
                saved_content = json.load(file)

            if saved_content['type'] == 'video':
                video_path = saved_content['content']
                if not os.path.exists(video_path):
                    Config.LOGGER.error("Video file not found: %s", video_path)
                    return json_response({"success": False, "error": "Video file not found."}, status=404)

                cap = cv2.VideoCapture(video_path)
                success, frame = cap.read()
                cap.release()
                if not success:
                    Config.LOGGER.error("Failed to capture frame from video: %s", video_path)
                    return json_response({"success": False, "error": "Failed to capture frame from video."}, status=500)

                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            elif saved_content['type'] == 'image':
                image = convert_matrix_to_image(saved_content['content'])
            else:
                Config.LOGGER.error("Unknown content type: %s", saved_content['type'])
                return json_response({"success": False, "error": "Unknown content type."}, status=400)

            byte_io = BytesIO()
            image.save(byte_io, 'PNG')
            byte_io.seek(0)
            return send_file(byte_io, mime_type='image/png')
        except FileNotFoundError:
            Config.LOGGER.error("Content file not found: %s", filename)
            return json_response({"success": False, "error": "File does not exist."}, status=404)
        except Exception as e:
            Config.LOGGER.error(f"Error getting saved content image: {str(e)}")
            return json_response({"success": False, "error": str(e)}, status=500)

    @route('/jumbotron/playvideo/<int:brightness>', method='POST')
    def play_video(post_data, form, brightness):
        global temp_filename, video_is_playing
        Config.LOGGER.info("Playing video")
        if 'file' not in form:
            Config.LOGGER.warning("No file part in the request")
            return json_response({'error': 'No file part in the request.'}, status=400)

        file_field = form['file']
        if not file_field.filename:
            Config.LOGGER.info("No file selected for uploading")
            return json_response({'error': 'No file selected for uploading.'}, status=400)

        video_is_playing = False
        time.sleep(1 / Config.UPDATES_PER_SECOND)

        filename = os.path.basename(file_field.filename)
        permanent_file_path = os.path.join(Config.SAVES_DIR, filename)
        with open(permanent_file_path, 'wb') as f:
            f.write(file_field.file.read())
        temp_filename = permanent_file_path

        try:
            video_is_playing = True
            save_state({'type': 'video', 'filename': permanent_file_path, 'brightness': brightness})
            eventlet.spawn(video_playback_thread)
            return json_response({'success': True})
        except Exception as e:
            Config.LOGGER.error("Error playing video: %s", str(e))
            return json_response({'error': 'Error playing video.'}, status=500)

    #endregion
    
    # HTTP server thread
    def run_http_server():
        Handler = CustomHTTPRequestHandler
        
        # Kill old server if it exists
        old_server = subprocess.run(["lsof", "-t", "-i:5000"], stdout=subprocess.PIPE)
        if old_server.stdout:
            subprocess.run(["kill", "-9", old_server.stdout])
        
        with socketserver.TCPServer(("", Config.HTTP_PORT), Handler) as httpd:
            Config.LOGGER.info(f"Serving HTTP on port {Config.HTTP_PORT}")
            httpd.serve_forever()
    
    async def main():
        # Create empty matrix of pixels
        Config.LOGGER.info("Creating matrix of pixels %d x %d on GPIO PIN %d", Config.ROWS, Config.COLUMNS, Config.PIN)
        Config.MATRIX = Jumbotron(Config.ROWS, Config.COLUMNS, Config.PIN)
        Config.LOGGER.info("Matrix created successfully")
        Config.LOGGER.info("Loading last state")
        last_state = load_state()
        if last_state:
            if last_state['type'] == 'video':
                video_path = Config.SAVES_DIR + "/" + last_state.get('filename')
                
                # Retrieve the content
                with open(video_path, 'r') as file:
                    video_path = json.load(file)['content']
                
                if os.path.exists(video_path):
                    # Play the video
                    video_is_playing = True
                    temp_filename = video_path  # Update the global variable
                    eventlet.spawn(video_playback_thread)
                else:
                    Config.LOGGER.error("Video file not found at startup: %s", video_path)
            elif last_state['type'] == 'image':
                # Display the image
                Config.MATRIX.update_from_matrix_array(last_state['content'])
        Config.LOGGER.info("Last state loaded successfully")
        Config.LOGGER.info("Starting Jumbotron API")
        Config.LOGGER.info("Jumbotron API started successfully")
        async with websockets.serve(jumbotron_updater, "0.0.0.0", Config.WS_PORT):
            Config.LOGGER.info(f"WebSocket server started on ws://localhost:{Config.WS_PORT}")
            await asyncio.Future() 

            
except KeyboardInterrupt as e:
    Config.LOGGER.info("Keyboard interrupt received")
    thread_stop_event.set()
    Config.LOGGER.info("Stopping Jumbotron API")
    Config.LOGGER.info("Jumbotron API stopped successfully")
    Config.LOGGER.info("Exiting")
    exit(0)
    
if __name__ == '__main__':
    try:
        http_thread = threading.Thread(target=run_http_server)
        http_thread.start()

        asyncio.run(main())

    except KeyboardInterrupt as e:
        Config.LOGGER.info("Keyboard interrupt received")
        thread_stop_event.set()
        Config.LOGGER.info("Stopping Jumbotron API")
        Config.LOGGER.info("Jumbotron API stopped successfully")
        Config.LOGGER.info("Exiting")
        exit(0)