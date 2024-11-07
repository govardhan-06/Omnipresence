import asyncio
import websockets

async def test_stream(user_id, alert_id):
    uri = f"ws://localhost:8000/ws/stream/{user_id}/{alert_id}/{file_format}"
    
    try:
        async with websockets.connect(uri, timeout=60) as websocket:  # Increase timeout
            with open("F:/Sentinel360/test_video.mp4", "rb") as video_file:  # Replace with a sample video file
                while chunk := video_file.read(1024):  # Read file in chunks
                    await websocket.send(chunk)
            print("Finished sending video data.")
    except Exception as e:
        print(f"Error streaming data: {e}")

user_id = "tqpaxLCuYPebJDaqXjxXtMUlg1C3"
alert_id = 7
file_format="mp4"

asyncio.run(test_stream(user_id, alert_id))
