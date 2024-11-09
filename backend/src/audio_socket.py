import asyncio
import websockets
import json
import os
import time

# Function to continuously send audio files to the server
async def test_audio_stream(user_id, username, latitude, longitude, audio_directory):
    url = f"ws://localhost:8000/ws/audio-stream/{user_id}/{username}/{latitude}/{longitude}"

    async with websockets.connect(url) as websocket:
        print("WebSocket connection established")

        while True:
            # Get the list of audio files in the directory
            audio_files = [f for f in os.listdir(audio_directory) if f.endswith('.wav')]  # You can adjust the file type

            for audio_file_name in audio_files:
                audio_file_path = os.path.join(audio_directory, audio_file_name)
                print(f"Sending audio file: {audio_file_name}")

                try:
                    # Read the audio file and send it to the server
                    with open(audio_file_path, 'rb') as audio_file:
                        audio_data = audio_file.read()
                        await websocket.send(audio_data)
                        print(f"Sent {len(audio_data)} bytes of audio data")

                    print("Audio data sent to server")

                    # Listen for server's response and handle accordingly
                    response = await websocket.recv()
                    data = json.loads(response)
                    print("Response from server:", data)

                    # If SOS is triggered, send confirmation action
                    if data.get("sos_triggered") is None:
                        print("No SOS triggered. Sending confirmation.")
                        await websocket.send(json.dumps({"action": "trigger_sos"}))
                        print("SOS trigger confirmation sent to server")

                    # Optional: Add delay to simulate continuous streaming
                    await asyncio.sleep(1)  # Adjust the sleep time as necessary (to control the frequency of sending files)

                except websockets.exceptions.ConnectionClosed as e:
                    print("WebSocket connection closed:", e)
                    break  # Exit if connection is closed
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break  # Exit on error

# Example call
user_id = "tqpaxLCuYPebJDaqXjxXtMUlg1C3"
username = "Meera"
latitude = 12.59
longitude = 78.89
audio_directory = "../audio"  # Directory containing audio files
asyncio.run(test_audio_stream(user_id, username, latitude, longitude, audio_directory))
