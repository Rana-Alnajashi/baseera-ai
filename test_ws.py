import asyncio
import websockets
import json

async def test_baseera_ws():
    uri = "ws://localhost:8000/ws/diligence"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to Baseera WebSocket.")
            
            # Send the initial research payload
            payload = {
                "target_company": "Saudi Telecom Company (STC)",
                "focus_area": "diversification strategy"
            }
            await websocket.send(json.dumps(payload))
            
            # Listen for streaming LangGraph events
            while True:
                response = await websocket.recv()
                event_data = json.loads(response)
                print(f"Event Received: {json.dumps(event_data, indent=2)}")
                
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed by server.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_baseera_ws())