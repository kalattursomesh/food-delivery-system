import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.food_delivery_environment import FoodDeliveryEnvironment
from models import DeliveryAction, Location
from tasks import get_all_task_ids, get_task
from grader import manhattan_distance


def find_nearest_idle_driver(drivers, target_location):
    best = None
    best_dist = float("inf")
    for d in drivers:
        if d.status == "idle":
            dist = manhattan_distance(d.location, target_location)
            if dist < best_dist:
                best_dist = dist
                best = d
    return best


def heuristic_agent(env, task_id):
    obs = env.reset(task_id=task_id)

    total_reward = 0.0
    step_count = 0

    while not obs.done:
        action = None

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

    return {
        "task_id": task_id,
        "difficulty": env.state.task_difficulty,
        "final_score": env.state.current_score,
        "total_reward": round(total_reward, 4),
        "steps": step_count,
    }


def main():
    print("=" * 60)
    print("Food Delivery Environment - Baseline Evaluation")
    print("=" * 60)
    print()

    env = FoodDeliveryEnvironment()
    all_tasks = get_all_task_ids()
    results = []

    for task_id in all_tasks:
        task = get_task(task_id)
        print(f"Running task: {task_id} ({task.difficulty})...")
        result = heuristic_agent(env, task_id)
        results.append(result)
        print(f"  Score: {result['final_score']:.4f} | "
              f"Reward: {result['total_reward']:.4f} | "
              f"Steps: {result['steps']}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Task':<12} {'Difficulty':<10} {'Score':<10} {'Reward':<10} {'Steps':<6}")
    print("-" * 48)

    for r in results:
        print(f"{r['task_id']:<12} {r['difficulty']:<10} "
              f"{r['final_score']:<10.4f} {r['total_reward']:<10.4f} {r['steps']:<6}")

    easy_scores = [r["final_score"] for r in results if r["difficulty"] == "easy"]
    medium_scores = [r["final_score"] for r in results if r["difficulty"] == "medium"]
    hard_scores = [r["final_score"] for r in results if r["difficulty"] == "hard"]

    print()
    print(f"Easy   avg: {sum(easy_scores)/len(easy_scores):.4f}")
    print(f"Medium avg: {sum(medium_scores)/len(medium_scores):.4f}")
    print(f"Hard   avg: {sum(hard_scores)/len(hard_scores):.4f}")
    print(f"Overall avg: {sum(r['final_score'] for r in results)/len(results):.4f}")


if __name__ == "__main__":
    main()
