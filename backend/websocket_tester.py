import asyncio
import websockets
import aiofiles

async def send_video_file(user_id, alert_id, file_format, video_path):
    url = f"wss://omnipresence.aryanmehesare.co/ws/stream/{user_id}/{alert_id}/{file_format}"

    try:
        async with websockets.connect(url) as websocket:
            # Open the video file and send its data in chunks
            async with aiofiles.open(video_path, 'rb') as video_file:
                while True:
                    # Read a chunk of the video file (e.g., 1024 bytes at a time)
                    chunk = await video_file.read(1024)
                    if not chunk:
                        break  # End of file

                    # Send the chunk via WebSocket
                    await websocket.send(chunk)

                    # Optionally, you can receive a response after each chunk
                    response = await websocket.recv()
                    print("Server response:", response)

    except Exception as e:
        print(f"Connection failed: {e}")

# Run the test
user_id = "tqpaxLCuYPebJDaqXjxXtMUlg1C3"
alert_id = 48
file_format = "mp4"
video_path = "F:/Sentinel360/test_video.mp4"  # Provide the actual path to the video file

asyncio.run(send_video_file(user_id, alert_id, file_format, video_path))


import asyncio
import websockets
async def test_stream(user_id, alert_id):
    uri = f"ws://localhost:8000/ws/stream/{user_id}/{alert_id}"
    
    try:
        async with websockets.connect(uri, timeout=60) as websocket:  # Increase timeout
            with open("test_video.mp4", "rb") as video_file:  # Replace with a sample video file
                while chunk := video_file.read(1024):  # Read file in chunks
                    await websocket.send(chunk)
            print("Finished sending video data.")
    except Exception as e:
        print(f"Error streaming data: {e}")
user_id = "Z9ZLeZ0DO6Z0qtbIs3Ha6eV4fSV2"
alert_id = 1111
asyncio.run(test_stream(user_id, alert_id))