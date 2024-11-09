import asyncio
import websockets
import json

async def test_audio_stream(user_id, username, latitude, longitude, audio_file_path):
    url = f"ws://localhost:8000/ws/audio-stream/{user_id}/{username}/{latitude}/{longitude}"

    async with websockets.connect(url) as websocket:
        print("WebSocket connection established")

        # Read the entire audio file and send to WebSocket
        try:
            with open(audio_file_path, 'rb') as audio_file:
                # Read the entire file into memory
                audio_data = audio_file.read()
                await websocket.send(audio_data)
                print(f"Sent {len(audio_data)} bytes of audio data")

            print("Audio data sent to server")

            # Listening for messages from the server (do not close immediately)
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print("Response from server:", data)

                # If SOS is triggered, send confirmation action
                if data.get("sos_triggered") is None:
                    print("No SOS triggered. Sending confirmation.")
                    await websocket.send(json.dumps({"action": "trigger_sos"}))
                    print("SOS trigger confirmation sent to server")

                # Optional: Close connection after processing is complete (if needed)
                if data.get("sos_triggered") is not None:
                    print("Server has processed the audio and responded. Closing connection.")
                    break  # Exit the loop and close the connection if response is final

        except websockets.exceptions.ConnectionClosed as e:
            print("WebSocket connection closed:", e)
        except Exception as e:
            print(f"Unexpected error: {e}")

# Example call
user_id = "tqpaxLCuYPebJDaqXjxXtMUlg1C3"
username = "Meera"
latitude = 12.59
longitude = 78.89
audio_file_path = "../testaudio.wav"
asyncio.run(test_audio_stream(user_id, username, latitude, longitude, audio_file_path))
