import math
from typing import Any, Dict, List
from models import Order, Driver, Location


def manhattan_distance(a: Location, b: Location) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def grade_task(
    task_id: str,
    difficulty: str,
    orders: List[Order],
    drivers: List[Driver],
    success_criteria: Dict[str, Any],
    total_steps: int,
    max_steps: int,
) -> float:
    delivered = [o for o in orders if o.status == "delivered"]
    cancelled = [o for o in orders if o.status == "cancelled"]
    total = len(orders)

    if total == 0:
        return 0.0

    delivered_count = len(delivered)
    on_time = [o for o in delivered if o.elapsed_time <= o.max_delivery_time]
    on_time_rate = len(on_time) / delivered_count if delivered_count > 0 else 0.0

    vip_orders = [o for o in orders if o.priority == "vip"]
    vip_delivered_on_time = [
        o for o in vip_orders
        if o.status == "delivered" and o.elapsed_time <= o.max_delivery_time
    ]

    score = 0.0

    delivery_ratio = delivered_count / total
    score += delivery_ratio * 0.35

    score += on_time_rate * 0.30

    if success_criteria.get("vip_on_time"):
        if len(vip_orders) > 0:
            vip_score = len(vip_delivered_on_time) / len(vip_orders)
            score += vip_score * 0.15
        else:
            score += 0.15
    else:
        score += delivery_ratio * 0.15

    efficiency = max(0.0, 1.0 - (total_steps / max_steps))
    score += efficiency * 0.10

    pending = [o for o in orders if o.status == "pending"]
    unhandled_penalty = len(pending) / total * 0.10
    score -= unhandled_penalty

    score += 0.10

    score = max(0.0, min(1.0, score))

    if difficulty == "easy":
        score = min(1.0, score * 1.1)
    elif difficulty == "hard":
        score = score * 0.95

    return round(score, 4)


def compute_step_reward(
    action_success: bool,
    order_just_delivered: bool,
    order_on_time: bool,
    is_vip: bool,
    steps_taken: int,
    max_steps: int,
) -> float:
    reward = 0.0

    if not action_success:
        reward -= 0.05

    if order_just_delivered:
        reward += 0.3
        if order_on_time:
            reward += 0.2
        else:
            reward -= 0.1
        if is_vip:
            reward += 0.15

    if action_success and not order_just_delivered:
        reward += 0.02

    if steps_taken > max_steps * 0.8:
        reward -= 0.02

    return round(reward, 4)
