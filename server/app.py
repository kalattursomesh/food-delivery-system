import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import json
import uvicorn

from server.food_delivery_environment import FoodDeliveryEnvironment
from models import DeliveryAction


app = FastAPI(
    title="Food Delivery Operations Environment",
    description="An OpenEnv environment for AI agents to manage food delivery operations",
    version="1.0.0",
)

environments = {}


class ResetRequest(BaseModel):
    task_id: str = "easy_1"
    seed: Optional[int] = None
    episode_id: Optional[str] = None


class StepRequest(BaseModel):
    action: DeliveryAction


@app.get("/health")
def health():
    return {"status": "healthy", "environment": "food_delivery_env"}


@app.get("/tasks")
def list_tasks():
    from tasks import get_all_task_ids, get_task
    task_ids = get_all_task_ids()
    result = []
    for tid in task_ids:
        t = get_task(tid)
        if t:
            result.append({
                "task_id": t.task_id,
                "difficulty": t.difficulty,
                "description": t.description,
                "max_steps": t.max_steps,
            })
    return {"tasks": result}


@app.post("/reset")
def reset(req: ResetRequest):
    env = FoodDeliveryEnvironment()
    obs = env.reset(task_id=req.task_id, seed=req.seed, episode_id=req.episode_id)
    episode_id = env.state.episode_id
    environments[episode_id] = env
    return {
        "episode_id": episode_id,
        "observation": obs.model_dump(),
    }


@app.post("/step/{episode_id}")
def step(episode_id: str, req: StepRequest):
    env = environments.get(episode_id)
    if not env:
        return {"error": f"No episode found with id {episode_id}. Call /reset first."}

    obs = env.step(req.action)
    if obs.done:
        environments.pop(episode_id, None)

    return {
        "episode_id": episode_id,
        "observation": obs.model_dump(),
    }


@app.get("/state/{episode_id}")
def get_state(episode_id: str):
    env = environments.get(episode_id)
    if not env:
        return {"error": f"No episode found with id {episode_id}."}
    return {"state": env.state.model_dump()}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    env = FoodDeliveryEnvironment()
    episode_id = None

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type", "")

            if msg_type == "reset":
                task_id = msg.get("task_id", "easy_1")
                obs = env.reset(task_id=task_id)
                episode_id = env.state.episode_id
                await ws.send_json({
                    "type": "reset_result",
                    "episode_id": episode_id,
                    "observation": obs.model_dump(),
                })

            elif msg_type == "step":
                action_data = msg.get("action", {})
                action = DeliveryAction(**action_data)
                obs = env.step(action)
                await ws.send_json({
                    "type": "step_result",
                    "observation": obs.model_dump(),
                })

            elif msg_type == "state":
                await ws.send_json({
                    "type": "state_result",
                    "state": env.state.model_dump(),
                })

    except WebSocketDisconnect:
        pass


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
