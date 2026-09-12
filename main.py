import traceback
import warnings
from fastapi import FastAPI, WebSocket
from langgraph.types import Command
from src.baseera.graph import baseera_app

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

app = FastAPI(title="Baseera AI Due Diligence API")

@app.websocket("/ws/diligence")
async def diligence_stream(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    
    action = data.get("action", "start")
    thread_id = data.get("thread_id")
    thread_config = {"configurable": {"thread_id": thread_id}}
    
    try:
        if action == "start":
            initial_state = {
                "company_name": data.get("company_name", ""),
                "research_goal": data.get("research_goal", "")
            }
            stream = baseera_app.stream(initial_state, config=thread_config, stream_mode="updates")
        else:
            # Resume graph with approved/edited plan
            resume_payload = {"edited_plan": data.get("edited_plan", {})}
            stream = baseera_app.stream(Command(resume=resume_payload), config=thread_config, stream_mode="updates")

        for event in stream:
            for node_name, state_update in event.items():
                if node_name == "__interrupt__":
                    # LangGraph interrupt returns a tuple of Interrupt objects
                    interrupt_val = state_update[0].value if isinstance(state_update, (list, tuple)) else state_update.value
                    await websocket.send_json({
                        "status": "paused_for_review",
                        "framework": interrupt_val.get("framework"),
                        "plan": interrupt_val.get("plan")
                    })
                    return

                await websocket.send_json({
                    "status": "processing",
                    "node": node_name,
                    "state_update": state_update 
                })
                    
    except Exception as e:
        print(f"❌ Backend Execution Error on thread {thread_id}:")
        traceback.print_exc()
        await websocket.send_json({"status": "error", "error": str(e)})