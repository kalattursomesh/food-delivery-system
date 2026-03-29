import requests
from typing import Optional, Dict, Any


class FoodDeliveryClient:

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.episode_id: Optional[str] = None

    def health(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/health")
        resp.raise_for_status()
        return resp.json()

    def list_tasks(self) -> Dict[str, Any]:
        resp = requests.get(f"{self.base_url}/tasks")
        resp.raise_for_status()
        return resp.json()

    def reset(
        self,
        task_id: str = "easy_1",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"task_id": task_id}
        if seed is not None:
            payload["seed"] = seed
        if episode_id is not None:
            payload["episode_id"] = episode_id

        resp = requests.post(f"{self.base_url}/reset", json=payload)
        resp.raise_for_status()
        data = resp.json()
        self.episode_id = data.get("episode_id")
        return data

    def step(
        self,
        action_type: str,
        order_id: Optional[str] = None,
        driver_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.episode_id:
            raise RuntimeError("No active episode. Call reset() first.")

        action = {"action_type": action_type}
        if order_id:
            action["order_id"] = order_id
        if driver_id:
            action["driver_id"] = driver_id
        if reason:
            action["reason"] = reason

        resp = requests.post(
            f"{self.base_url}/step/{self.episode_id}",
            json={"action": action},
        )
        resp.raise_for_status()
        return resp.json()

    def state(self) -> Dict[str, Any]:
        if not self.episode_id:
            raise RuntimeError("No active episode. Call reset() first.")
        resp = requests.get(f"{self.base_url}/state/{self.episode_id}")
        resp.raise_for_status()
        return resp.json()
