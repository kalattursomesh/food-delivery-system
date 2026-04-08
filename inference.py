"""
inference.py - Baseline inference script for the Food Delivery OpenEnv.

This script demonstrates how an AI agent interacts with the environment
by calling the /reset and /step API endpoints.
"""

import sys
import os
import requests
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_URL = os.environ.get("OPENENV_URL", "http://localhost:8000")


def run_inference(task_id="easy_1"):
    """Run a single episode of the food delivery environment."""
    # Reset the environment
    reset_resp = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
    reset_data = reset_resp.json()
    episode_id = reset_data["episode_id"]
    obs = reset_data["observation"]

    print(f"[RESET] Episode: {episode_id} | Task: {task_id}")
    print(f"  Orders: {obs['metrics'].get('total_orders', 0)} | "
          f"Drivers: {len(obs.get('drivers', []))}")

    total_reward = 0.0
    step_count = 0

    while not obs.get("done", False):
        # Simple greedy: assign pending orders to nearest idle drivers
        action = {"action_type": "wait"}

        pending = [o for o in obs.get("orders", []) if o["status"] == "pending"]
        idle_drivers = [d for d in obs.get("drivers", []) if d["status"] == "idle"]

        if pending and idle_drivers:
            order = pending[0]
            # Find nearest idle driver
            best_driver = None
            min_dist = float("inf")
            for d in idle_drivers:
                dist = (abs(d["location"]["x"] - order["pickup_location"]["x"])
                        + abs(d["location"]["y"] - order["pickup_location"]["y"]))
                if dist < min_dist:
                    min_dist = dist
                    best_driver = d

            if best_driver:
                action = {
                    "action_type": "assign_order",
                    "order_id": order["id"],
                    "driver_id": best_driver["id"],
                }

        step_resp = requests.post(
            f"{BASE_URL}/step/{episode_id}",
            json={"action": action},
        )
        step_data = step_resp.json()
        obs = step_data["observation"]
        total_reward += obs.get("reward", 0.0)
        step_count += 1

    print(f"[DONE] Steps: {step_count} | Score: {obs.get('score', 0):.4f} | "
          f"Total Reward: {total_reward:.4f}")
    return obs.get("score", 0.0)


def main():
    """Run inference across all task difficulties."""
    from tasks import get_all_task_ids

    print("=" * 60)
    print("Food Delivery OpenEnv - Inference")
    print("=" * 60)

    all_tasks = get_all_task_ids()
    scores = []

    for task_id in all_tasks:
        try:
            score = run_inference(task_id)
            scores.append({"task_id": task_id, "score": score})
        except Exception as e:
            print(f"[ERROR] Task {task_id}: {e}")
            scores.append({"task_id": task_id, "score": 0.0})

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    for s in scores:
        print(f"  {s['task_id']:.<20} {s['score']:.4f}")

    avg = sum(s["score"] for s in scores) / len(scores) if scores else 0
    print(f"\n  Average Score: {avg:.4f}")


if __name__ == "__main__":
    main()
