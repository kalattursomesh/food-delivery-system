import copy
import math
from typing import Any, Dict, List, Optional
from uuid import uuid4

from models import (
    Location, Restaurant, Driver, Order,
    DeliveryAction, DeliveryObservation, DeliveryState,
)
from tasks import Task, get_task, get_all_task_ids
from grader import grade_task, compute_step_reward, manhattan_distance


class FoodDeliveryEnvironment:

    def __init__(self):
        self._state = DeliveryState(episode_id=str(uuid4()))
        self._restaurants: List[Restaurant] = []
        self._drivers: List[Driver] = []
        self._orders: List[Order] = []
        self._task: Optional[Task] = None
        self._incoming_orders: List[Dict[str, Any]] = []
        self._events_log: List[str] = []
        self._delivered_times: Dict[str, bool] = {}
        self._traffic_zone: Optional[Dict[str, int]] = None

    def reset(
        self,
        task_id: str = "easy_1",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs,
    ) -> DeliveryObservation:
        task = get_task(task_id)
        if task is None:
            return DeliveryObservation(
                action_success=False,
                action_message=f"Unknown task_id: {task_id}. Available: {get_all_task_ids()}",
                done=True,
            )

        self._task = task
        self._state = DeliveryState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_id=task_id,
            task_difficulty=task.difficulty,
            current_score=0.0,
            is_done=False,
            time_step=0,
        )

        self._restaurants = [r.model_copy(deep=True) for r in task.restaurants]
        self._drivers = [d.model_copy(deep=True) for d in task.drivers]
        self._orders = [o.model_copy(deep=True) for o in task.initial_orders]
        self._incoming_orders = copy.deepcopy(task.incoming_orders)
        self._events_log = []
        self._delivered_times = {}

        if task_id == "hard_2":
            self._traffic_zone = {"x_min": 8, "x_max": 12}
        else:
            self._traffic_zone = None

        return self._build_observation(
            action_success=True,
            action_message="Environment reset. Ready for actions.",
            reward=0.0,
        )

    def step(self, action: DeliveryAction, **kwargs) -> DeliveryObservation:
        if self._task is None or self._state.is_done:
            return DeliveryObservation(
                action_success=False,
                action_message="Episode is done or not started. Call reset() first.",
                done=True,
            )

        self._state.step_count += 1
        self._state.time_step += 1

        self._spawn_incoming_orders()
        self._handle_task_events()

        action_success = True
        action_message = ""
        order_just_delivered = False
        delivered_on_time = False
        is_vip_delivery = False

        if action.action_type == "assign_order":
            action_success, action_message = self._assign_order(
                action.order_id, action.driver_id
            )
        elif action.action_type == "reassign_order":
            action_success, action_message = self._reassign_order(
                action.order_id, action.driver_id
            )
        elif action.action_type == "cancel_order":
            action_success, action_message = self._cancel_order(action.order_id)
        elif action.action_type == "set_driver_offline":
            action_success, action_message = self._set_driver_status(
                action.driver_id, "offline"
            )
        elif action.action_type == "set_driver_online":
            action_success, action_message = self._set_driver_status(
                action.driver_id, "idle"
            )
        elif action.action_type == "wait":
            action_success = True
            action_message = "Waited one time-step."
        else:
            action_success = False
            action_message = f"Unknown action_type: {action.action_type}"

        delivery_results = self._simulate_time_step()
        for result in delivery_results:
            order_just_delivered = True
            delivered_on_time = result["on_time"]
            is_vip_delivery = result["is_vip"]

        reward = compute_step_reward(
            action_success=action_success,
            order_just_delivered=order_just_delivered,
            order_on_time=delivered_on_time,
            is_vip=is_vip_delivery,
            steps_taken=self._state.step_count,
            max_steps=self._task.max_steps,
        )

        done = self._check_done()
        self._state.is_done = done

        if done:
            final_score = grade_task(
                task_id=self._task.task_id,
                difficulty=self._task.difficulty,
                orders=self._orders,
                drivers=self._drivers,
                success_criteria=self._task.success_criteria,
                total_steps=self._state.step_count,
                max_steps=self._task.max_steps,
            )
            self._state.current_score = final_score
            reward += final_score * 0.5

        return self._build_observation(
            action_success=action_success,
            action_message=action_message,
            reward=round(reward, 4),
        )

    @property
    def state(self) -> DeliveryState:
        return self._state

    def _assign_order(self, order_id, driver_id):
        if not order_id or not driver_id:
            return False, "order_id and driver_id are required for assign_order."

        order = self._get_order(order_id)
        if not order:
            return False, f"Order {order_id} not found."
        if order.status != "pending":
            return False, f"Order {order_id} is not pending (status: {order.status})."

        driver = self._get_driver(driver_id)
        if not driver:
            return False, f"Driver {driver_id} not found."
        if driver.status != "idle":
            return False, f"Driver {driver_id} is not idle (status: {driver.status})."

        order.status = "assigned"
        order.assigned_driver_id = driver_id
        driver.status = "en_route_to_restaurant"
        driver.current_order_id = order_id

        return True, f"Order {order_id} assigned to driver {driver_id}."

    def _reassign_order(self, order_id, driver_id):
        if not order_id or not driver_id:
            return False, "order_id and driver_id are required for reassign_order."

        order = self._get_order(order_id)
        if not order:
            return False, f"Order {order_id} not found."
        if order.status not in ("assigned", "preparing"):
            return False, f"Order {order_id} cannot be reassigned (status: {order.status})."

        new_driver = self._get_driver(driver_id)
        if not new_driver:
            return False, f"Driver {driver_id} not found."
        if new_driver.status != "idle":
            return False, f"Driver {driver_id} is not idle."

        if order.assigned_driver_id:
            old_driver = self._get_driver(order.assigned_driver_id)
            if old_driver:
                old_driver.status = "idle"
                old_driver.current_order_id = None

        order.assigned_driver_id = driver_id
        new_driver.status = "en_route_to_restaurant"
        new_driver.current_order_id = order_id

        return True, f"Order {order_id} reassigned to driver {driver_id}."

    def _cancel_order(self, order_id):
        if not order_id:
            return False, "order_id is required for cancel_order."

        order = self._get_order(order_id)
        if not order:
            return False, f"Order {order_id} not found."
        if order.status in ("delivered", "cancelled"):
            return False, f"Order {order_id} is already {order.status}."

        if order.assigned_driver_id:
            driver = self._get_driver(order.assigned_driver_id)
            if driver:
                driver.status = "idle"
                driver.current_order_id = None

        order.status = "cancelled"
        order.assigned_driver_id = None
        return True, f"Order {order_id} cancelled."

    def _set_driver_status(self, driver_id, new_status):
        if not driver_id:
            return False, "driver_id is required."

        driver = self._get_driver(driver_id)
        if not driver:
            return False, f"Driver {driver_id} not found."

        if new_status == "offline" and driver.status not in ("idle", "offline"):
            return False, f"Driver {driver_id} is busy ({driver.status}), cannot go offline."

        driver.status = new_status
        return True, f"Driver {driver_id} is now {new_status}."

    def _simulate_time_step(self):
        delivery_results = []

        for order in self._orders:
            if order.status in ("delivered", "cancelled", "pending"):
                continue
            order.elapsed_time += 1

        for order in self._orders:
            if order.status == "assigned" and order.prep_time_remaining > 0:
                order.prep_time_remaining -= 1
                if order.prep_time_remaining <= 0:
                    order.status = "preparing"

        for order in self._orders:
            if order.status == "preparing":
                driver = self._get_driver(order.assigned_driver_id)
                if driver:
                    dist = manhattan_distance(driver.location, order.pickup_location)
                    effective_speed = self._get_effective_speed(driver)
                    if dist <= effective_speed:
                        driver.location = order.pickup_location.model_copy()
                        order.status = "picked_up"
                        driver.status = "picking_up"
                    else:
                        self._move_driver_toward(driver, order.pickup_location)

        for order in self._orders:
            if order.status == "picked_up":
                order.status = "in_transit"
                driver = self._get_driver(order.assigned_driver_id)
                if driver:
                    driver.status = "delivering"

        for order in self._orders:
            if order.status == "in_transit":
                driver = self._get_driver(order.assigned_driver_id)
                if driver:
                    dist = manhattan_distance(driver.location, order.delivery_location)
                    effective_speed = self._get_effective_speed(driver)
                    if dist <= effective_speed:
                        driver.location = order.delivery_location.model_copy()
                        order.status = "delivered"
                        driver.status = "idle"
                        driver.current_order_id = None
                        driver.total_deliveries += 1
                        on_time = order.elapsed_time <= order.max_delivery_time
                        self._delivered_times[order.id] = on_time
                        delivery_results.append({
                            "order_id": order.id,
                            "on_time": on_time,
                            "is_vip": order.priority == "vip",
                        })
                    else:
                        self._move_driver_toward(driver, order.delivery_location)

        return delivery_results

    def _move_driver_toward(self, driver, target):
        effective_speed = self._get_effective_speed(driver)
        steps_remaining = math.floor(effective_speed)
        dx = target.x - driver.location.x
        dy = target.y - driver.location.y

        move_x = min(abs(dx), steps_remaining)
        if dx > 0:
            driver.location.x += move_x
        elif dx < 0:
            driver.location.x -= move_x
        steps_remaining -= move_x

        if steps_remaining > 0:
            move_y = min(abs(dy), steps_remaining)
            if dy > 0:
                driver.location.y += move_y
            elif dy < 0:
                driver.location.y -= move_y

    def _get_effective_speed(self, driver):
        if self._traffic_zone:
            x_min = self._traffic_zone["x_min"]
            x_max = self._traffic_zone["x_max"]
            if x_min <= driver.location.x <= x_max:
                return driver.speed * 0.5
        return driver.speed

    def _spawn_incoming_orders(self):
        remaining = []
        for entry in self._incoming_orders:
            if entry["arrive_at_step"] <= self._state.time_step:
                order_data = entry["order"]
                if "pickup_location" in order_data and isinstance(order_data["pickup_location"], dict):
                    order_data["pickup_location"] = Location(**order_data["pickup_location"])
                if "delivery_location" in order_data and isinstance(order_data["delivery_location"], dict):
                    order_data["delivery_location"] = Location(**order_data["delivery_location"])
                new_order = Order(**order_data)
                self._orders.append(new_order)
            else:
                remaining.append(entry)
        self._incoming_orders = remaining

    def _handle_task_events(self):
        if not self._task:
            return

        if self._task.task_id == "hard_1":
            if self._state.time_step == 7:
                driver = self._get_driver("driver_4")
                if driver and driver.status == "idle":
                    driver.status = "offline"
            if self._state.time_step == 10:
                for r in self._restaurants:
                    if r.id == "rest_3":
                        r.is_open = False
                for order in self._orders:
                    if (order.restaurant_id == "rest_3"
                            and order.status == "pending"):
                        order.status = "cancelled"

        if self._task.task_id == "hard_3":
            if self._state.time_step == 15:
                for r in self._restaurants:
                    if r.id == "rest_2":
                        r.is_open = False
                for order in self._orders:
                    if (order.restaurant_id == "rest_2"
                            and order.status == "pending"):
                        order.status = "cancelled"

    def _check_done(self):
        if self._state.step_count >= self._task.max_steps:
            return True

        active = [
            o for o in self._orders
            if o.status not in ("delivered", "cancelled")
        ]
        if len(active) == 0 and len(self._incoming_orders) == 0:
            return True

        return False

    def _get_order(self, order_id):
        if not order_id:
            return None
        for o in self._orders:
            if o.id == order_id:
                return o
        return None

    def _get_driver(self, driver_id):
        if not driver_id:
            return None
        for d in self._drivers:
            if d.id == driver_id:
                return d
        return None

    def _build_observation(self, action_success, action_message, reward):
        hints = []
        if self._task and self._state.step_count < len(self._task.hints):
            hints = [self._task.hints[self._state.step_count]]

        delivered = [o for o in self._orders if o.status == "delivered"]
        on_time = [o for o in delivered if o.elapsed_time <= o.max_delivery_time]
        pending = [o for o in self._orders if o.status == "pending"]

        metrics = {
            "total_orders": len(self._orders),
            "delivered": len(delivered),
            "on_time_deliveries": len(on_time),
            "pending": len(pending),
            "cancelled": len([o for o in self._orders if o.status == "cancelled"]),
            "in_progress": len([o for o in self._orders if o.status in ("assigned", "preparing", "picked_up", "in_transit")]),
            "on_time_rate": round(len(on_time) / len(delivered), 4) if delivered else 0.0,
            "idle_drivers": len([d for d in self._drivers if d.status == "idle"]),
        }

        return DeliveryObservation(
            restaurants=self._restaurants,
            drivers=self._drivers,
            orders=self._orders,
            action_success=action_success,
            action_message=action_message,
            reward=reward,
            done=self._state.is_done,
            task_description=self._task.description if self._task else "",
            task_difficulty=self._task.difficulty if self._task else "easy",
            score=self._state.current_score,
            steps_taken=self._state.step_count,
            max_steps=self._task.max_steps if self._task else 30,
            time_step=self._state.time_step,
            hints=hints,
            metrics=metrics,
        )
