"""
inference.py - Baseline inference script for the Food Delivery OpenEnv.

Emits structured [START]/[STEP]/[END] output blocks to stdout
as required by the OpenEnv Phase 2 validator.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.food_delivery_environment import FoodDeliveryEnvironment
from models import DeliveryAction, Location
from tasks import get_all_task_ids, get_task
from grader import manhattan_distance


def find_nearest_idle_driver(drivers, target_location):
    """Find the nearest idle driver to a target location."""
    best = None
    best_dist = float("inf")
    for d in drivers:
        if d.status == "idle":
            dist = manhattan_distance(d.location, target_location)
            if dist < best_dist:
                best_dist = dist
                best = d
    return best


def run_task(env, task_id):
    """Run a single task and emit structured output."""
    obs = env.reset(task_id=task_id)

    # [START] block
    print(f"[START] task={task_id}", flush=True)

    total_reward = 0.0
    step_count = 0

    while not obs.done:
        action = None

        # Prioritise VIP > priority > normal
        pending_orders = [o for o in obs.orders if o.status == "pending"]
        vip_orders = [o for o in pending_orders if o.priority == "vip"]
        priority_orders = [o for o in pending_orders if o.priority == "priority"]
        normal_orders = [o for o in pending_orders if o.priority == "normal"]

        sorted_orders = vip_orders + priority_orders + normal_orders

        assigned = False
        for order in sorted_orders:
            driver = find_nearest_idle_driver(obs.drivers, order.pickup_location)
            if driver:
                action = DeliveryAction(
                    action_type="assign_order",
                    order_id=order.id,
                    driver_id=driver.id,
                )
                assigned = True
                break

        if not assigned:
            action = DeliveryAction(action_type="wait")

        obs = env.step(action)
        total_reward += obs.reward
        step_count += 1

        # [STEP] block
        print(f"[STEP] step={step_count} reward={obs.reward}", flush=True)

    final_score = env.state.current_score

    # [END] block
    print(f"[END] task={task_id} score={final_score} steps={step_count}", flush=True)

    return final_score


def main():
    """Run inference across all tasks with structured output."""
    env = FoodDeliveryEnvironment()
    all_tasks = get_all_task_ids()

    for task_id in all_tasks:
        try:
            run_task(env, task_id)
        except Exception as e:
            # Still emit structured blocks on failure so the validator
            # can parse partial results.
            print(f"[START] task={task_id}", flush=True)
            print(f"[STEP] step=0 reward=0", flush=True)
            print(f"[END] task={task_id} score=0 steps=0", flush=True)
            sys.stderr.write(f"ERROR on {task_id}: {e}\n")


if __name__ == "__main__":
    main()
