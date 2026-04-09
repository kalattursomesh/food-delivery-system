"""
inference.py - LLM-powered inference script for the Food Delivery OpenEnv.

Uses the OpenAI-compatible LiteLLM proxy (API_BASE_URL / API_KEY env vars)
to decide actions, and emits structured [START]/[STEP]/[END] output blocks
required by the Phase 2 validator.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from server.food_delivery_environment import FoodDeliveryEnvironment
from models import DeliveryAction
from tasks import get_all_task_ids
from grader import manhattan_distance

# ── LLM client using injected env vars ──────────────────────────────
client = OpenAI(
    base_url=os.environ.get("API_BASE_URL", "http://localhost:8000/v1"),
    api_key=os.environ.get("API_KEY", "dummy"),
)

MODEL = os.environ.get("MODEL_ID", "gpt-4o-mini")


# ── Helpers ─────────────────────────────────────────────────────────

def _obs_to_summary(obs) -> str:
    """Compact text summary of the observation for the LLM prompt."""
    lines = []
    lines.append(f"Task: {obs.metadata.get('task_id','')} | Difficulty: {obs.task_difficulty}")
    lines.append(f"Step: {obs.steps_taken}/{obs.max_steps} | Score: {obs.score:.4f}")
    lines.append(f"Description: {obs.task_description}")

    if obs.hints:
        lines.append(f"Hints: {'; '.join(obs.hints)}")

    lines.append("\n-- Drivers --")
    for d in obs.drivers:
        lines.append(
            f"  {d.id} ({d.name}): status={d.status}, loc=({d.location.x},{d.location.y}), "
            f"speed={d.speed}, order={d.current_order_id or 'none'}"
        )

    lines.append("\n-- Orders --")
    for o in obs.orders:
        lines.append(
            f"  {o.id}: status={o.status}, priority={o.priority}, "
            f"pickup=({o.pickup_location.x},{o.pickup_location.y}), "
            f"delivery=({o.delivery_location.x},{o.delivery_location.y}), "
            f"prep_remaining={o.prep_time_remaining}, elapsed={o.elapsed_time}/{o.max_delivery_time}, "
            f"assigned_to={o.assigned_driver_id or 'none'}"
        )

    lines.append("\n-- Restaurants --")
    for r in obs.restaurants:
        lines.append(f"  {r.id} ({r.name}): loc=({r.location.x},{r.location.y}), open={r.is_open}")

    m = obs.metrics
    lines.append(
        f"\n-- Metrics -- delivered={m.get('delivered',0)}/{m.get('total_orders',0)}, "
        f"on_time_rate={m.get('on_time_rate',0)}, pending={m.get('pending',0)}, "
        f"idle_drivers={m.get('idle_drivers',0)}"
    )
    return "\n".join(lines)


SYSTEM_PROMPT = """\
You are an expert food-delivery dispatcher AI. You control drivers to deliver orders.

Available action types (return ONE JSON object per turn):
1. {"action_type":"assign_order","order_id":"...","driver_id":"..."} – assign a pending order to an idle driver.
2. {"action_type":"cancel_order","order_id":"..."} – cancel an order that cannot be delivered on time.
3. {"action_type":"wait"} – do nothing this step.

Rules:
- Prioritise VIP > priority > normal orders.
- Assign the nearest idle driver to each order (use Manhattan distance).
- Cancel orders that clearly cannot be delivered within their max_delivery_time.
- Only assign to drivers whose status is "idle".
- Only assign orders whose status is "pending".
- Return ONLY valid JSON, no markdown fences, no commentary.
"""


def _ask_llm(obs) -> dict:
    """Ask the LLM for the next action given the current observation."""
    summary = _obs_to_summary(obs)

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": summary},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        raw = resp.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        action = json.loads(raw)
        return action

    except Exception as e:
        sys.stderr.write(f"LLM error: {e}\n")
        return _fallback_action(obs)


def _fallback_action(obs) -> dict:
    """Simple greedy fallback if the LLM call fails."""
    pending = [o for o in obs.orders if o.status == "pending"]
    idle = [d for d in obs.drivers if d.status == "idle"]

    # Sort: VIP first, then priority, then normal
    priority_map = {"vip": 0, "priority": 1, "normal": 2}
    pending.sort(key=lambda o: priority_map.get(o.priority, 2))

    for order in pending:
        best_driver = None
        best_dist = float("inf")
        for d in idle:
            dist = manhattan_distance(d.location, order.pickup_location)
            if dist < best_dist:
                best_dist = dist
                best_driver = d
        if best_driver:
            return {
                "action_type": "assign_order",
                "order_id": order.id,
                "driver_id": best_driver.id,
            }

    return {"action_type": "wait"}


# ── Main Loop ───────────────────────────────────────────────────────

def run_task(env, task_id):
    """Run a single task, emit structured output, return final score."""
    obs = env.reset(task_id=task_id)
    print(f"[START] task={task_id}", flush=True)

    total_reward = 0.0
    step_count = 0

    while not obs.done:
        action_dict = _ask_llm(obs)

        # Build validated action
        try:
            action = DeliveryAction(**action_dict)
        except Exception:
            action = DeliveryAction(action_type="wait")

        obs = env.step(action)
        total_reward += obs.reward
        step_count += 1
        print(f"[STEP] step={step_count} reward={obs.reward}", flush=True)

    final_score = env.state.current_score
    print(f"[END] task={task_id} score={final_score} steps={step_count}", flush=True)
    return final_score


def main():
    env = FoodDeliveryEnvironment()
    all_tasks = get_all_task_ids()

    for task_id in all_tasks:
        try:
            run_task(env, task_id)
        except Exception as e:
            print(f"[START] task={task_id}", flush=True)
            print(f"[STEP] step=0 reward=0", flush=True)
            print(f"[END] task={task_id} score=0 steps=0", flush=True)
            sys.stderr.write(f"ERROR on {task_id}: {e}\n")


if __name__ == "__main__":
    main()
