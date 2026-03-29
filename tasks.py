from typing import Any, Dict, List, Optional
from models import Location, Restaurant, Driver, Order


class Task:
    def __init__(
        self,
        task_id: str,
        difficulty: str,
        description: str,
        hints: List[str],
        restaurants: List[Restaurant],
        drivers: List[Driver],
        initial_orders: List[Order],
        incoming_orders: List[Dict[str, Any]],
        max_steps: int,
        success_criteria: Dict[str, Any],
    ):
        self.task_id = task_id
        self.difficulty = difficulty
        self.description = description
        self.hints = hints
        self.restaurants = restaurants
        self.drivers = drivers
        self.initial_orders = initial_orders
        self.incoming_orders = incoming_orders
        self.max_steps = max_steps
        self.success_criteria = success_criteria


RESTAURANTS = [
    Restaurant(
        id="rest_1", name="Burger Palace",
        location=Location(x=3, y=5), avg_prep_time_minutes=3, is_open=True,
    ),
    Restaurant(
        id="rest_2", name="Pizza Express",
        location=Location(x=8, y=2), avg_prep_time_minutes=5, is_open=True,
    ),
    Restaurant(
        id="rest_3", name="Sushi World",
        location=Location(x=15, y=10), avg_prep_time_minutes=4, is_open=True,
    ),
    Restaurant(
        id="rest_4", name="Taco Town",
        location=Location(x=6, y=14), avg_prep_time_minutes=2, is_open=True,
    ),
    Restaurant(
        id="rest_5", name="Pasta House",
        location=Location(x=12, y=7), avg_prep_time_minutes=6, is_open=True,
    ),
]


EASY_TASKS = [
    Task(
        task_id="easy_1",
        difficulty="easy",
        description=(
            "A single customer order has come in from Burger Palace. "
            "You have 2 available drivers. Assign the order to the nearest "
            "idle driver and ensure it gets delivered within the time limit. "
            "The goal is to make a successful delivery with minimal wait time."
        ),
        hints=[
            "Check the locations of the drivers and the restaurant to find the nearest one.",
            "Driver D1 is at (2,4), Driver D2 is at (10,10). Burger Palace is at (3,5).",
            "Assign order_1 to driver_1 using action_type='assign_order'.",
        ],
        restaurants=RESTAURANTS[:2],
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=2, y=4),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=10, y=10),
                   status="idle", speed=1.2, rating=4.3),
        ],
        initial_orders=[
            Order(
                id="order_1", customer_name="Sam",
                restaurant_id="rest_1",
                pickup_location=Location(x=3, y=5),
                delivery_location=Location(x=6, y=8),
                status="pending", priority="normal",
                max_delivery_time=20, prep_time_remaining=3,
                items=["Classic Burger", "Fries", "Coke"],
            ),
        ],
        incoming_orders=[],
        max_steps=25,
        success_criteria={
            "all_orders_delivered": True,
            "min_on_time_rate": 1.0,
        },
    ),
    Task(
        task_id="easy_2",
        difficulty="easy",
        description=(
            "Two orders have come in simultaneously — one from Burger Palace "
            "and one from Pizza Express. Assign each to the best available "
            "driver to minimize total delivery time."
        ),
        hints=[
            "Look at which driver is closest to each restaurant.",
            "Driver D1 at (2,4) is near Burger Palace (3,5). Driver D2 at (9,3) is near Pizza Express (8,2).",
            "Assign order_1 to driver_1 and order_2 to driver_2.",
        ],
        restaurants=RESTAURANTS[:2],
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=2, y=4),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=9, y=3),
                   status="idle", speed=1.3, rating=4.5),
        ],
        initial_orders=[
            Order(
                id="order_1", customer_name="Sam",
                restaurant_id="rest_1",
                pickup_location=Location(x=3, y=5),
                delivery_location=Location(x=5, y=9),
                status="pending", priority="normal",
                max_delivery_time=22, prep_time_remaining=3,
                items=["Classic Burger", "Fries"],
            ),
            Order(
                id="order_2", customer_name="Riley",
                restaurant_id="rest_2",
                pickup_location=Location(x=8, y=2),
                delivery_location=Location(x=12, y=5),
                status="pending", priority="normal",
                max_delivery_time=24, prep_time_remaining=5,
                items=["Pepperoni Pizza", "Garlic Bread"],
            ),
        ],
        incoming_orders=[],
        max_steps=30,
        success_criteria={
            "all_orders_delivered": True,
            "min_on_time_rate": 1.0,
        },
    ),
    Task(
        task_id="easy_3",
        difficulty="easy",
        description=(
            "A VIP order has arrived from Sushi World. It must be prioritised "
            "over any other order. Assign the best driver and ensure it is "
            "delivered on time. One other normal order is also pending."
        ),
        hints=[
            "VIP orders should be assigned first — they have shorter deadlines.",
            "Driver D1 at (14,9) is closest to Sushi World (15,10).",
            "Assign order_vip to driver_1 first, then order_2 to driver_2.",
        ],
        restaurants=[RESTAURANTS[2], RESTAURANTS[0]],
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=14, y=9),
                   status="idle", speed=1.5, rating=4.8),
            Driver(id="driver_2", name="Jordan", location=Location(x=4, y=6),
                   status="idle", speed=1.2, rating=4.2),
        ],
        initial_orders=[
            Order(
                id="order_vip", customer_name="VIP Customer",
                restaurant_id="rest_3",
                pickup_location=Location(x=15, y=10),
                delivery_location=Location(x=18, y=13),
                status="pending", priority="vip",
                max_delivery_time=15, prep_time_remaining=4,
                tip_amount=15.0,
                items=["Premium Sushi Platter", "Miso Soup"],
            ),
            Order(
                id="order_normal", customer_name="Casey",
                restaurant_id="rest_1",
                pickup_location=Location(x=3, y=5),
                delivery_location=Location(x=7, y=8),
                status="pending", priority="normal",
                max_delivery_time=25, prep_time_remaining=3,
                items=["Burger Combo"],
            ),
        ],
        incoming_orders=[],
        max_steps=30,
        success_criteria={
            "all_orders_delivered": True,
            "vip_on_time": True,
            "min_on_time_rate": 0.5,
        },
    ),
]


MEDIUM_TASKS = [
    Task(
        task_id="medium_1",
        difficulty="medium",
        description=(
            "Dinner rush! 3 orders are pending and 2 more will arrive soon. "
            "You have 3 drivers. Optimise assignments so all orders are delivered "
            "on time. New orders appear at time-step 5 and 8. Minimise total "
            "delivery time across all orders."
        ),
        hints=[
            "Match each driver to the nearest restaurant for the first 3 orders.",
            "Keep at least one driver free (or almost done) for incoming orders.",
            "At time-step 5 a new order from Taco Town arrives; at 8 from Pasta House.",
        ],
        restaurants=RESTAURANTS,
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=4, y=5),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=9, y=3),
                   status="idle", speed=1.3, rating=4.5),
            Driver(id="driver_3", name="Taylor", location=Location(x=14, y=8),
                   status="idle", speed=1.4, rating=4.6),
        ],
        initial_orders=[
            Order(
                id="order_1", customer_name="Sam",
                restaurant_id="rest_1",
                pickup_location=Location(x=3, y=5),
                delivery_location=Location(x=5, y=9),
                status="pending", priority="normal",
                max_delivery_time=20, prep_time_remaining=3,
                items=["Classic Burger", "Fries"],
            ),
            Order(
                id="order_2", customer_name="Riley",
                restaurant_id="rest_2",
                pickup_location=Location(x=8, y=2),
                delivery_location=Location(x=11, y=6),
                status="pending", priority="normal",
                max_delivery_time=22, prep_time_remaining=5,
                items=["Margherita Pizza"],
            ),
            Order(
                id="order_3", customer_name="Morgan",
                restaurant_id="rest_3",
                pickup_location=Location(x=15, y=10),
                delivery_location=Location(x=18, y=14),
                status="pending", priority="priority",
                max_delivery_time=18, prep_time_remaining=4,
                items=["Sushi Combo"],
            ),
        ],
        incoming_orders=[
            {
                "arrive_at_step": 5,
                "order": {
                    "id": "order_4", "customer_name": "Pat",
                    "restaurant_id": "rest_4",
                    "pickup_location": {"x": 6, "y": 14},
                    "delivery_location": {"x": 3, "y": 18},
                    "status": "pending", "priority": "normal",
                    "max_delivery_time": 25, "prep_time_remaining": 2,
                    "items": ["Taco Platter", "Nachos"],
                },
            },
            {
                "arrive_at_step": 8,
                "order": {
                    "id": "order_5", "customer_name": "Drew",
                    "restaurant_id": "rest_5",
                    "pickup_location": {"x": 12, "y": 7},
                    "delivery_location": {"x": 16, "y": 3},
                    "status": "pending", "priority": "normal",
                    "max_delivery_time": 22, "prep_time_remaining": 6,
                    "items": ["Spaghetti Bolognese", "Tiramisu"],
                },
            },
        ],
        max_steps=40,
        success_criteria={
            "all_orders_delivered": True,
            "min_on_time_rate": 0.8,
        },
    ),
    Task(
        task_id="medium_2",
        difficulty="medium",
        description=(
            "A driver just went offline mid-shift! Driver 2 has become unavailable. "
            "You have 4 pending orders and only 2 remaining drivers. "
            "Some orders may need to be cancelled if they can't be delivered on time. "
            "Maximise the number of successful on-time deliveries."
        ),
        hints=[
            "First, check which orders can realistically be delivered on time with 2 drivers.",
            "Consider cancelling the order with the tightest deadline that is farthest away.",
            "Prioritise VIP/priority orders over normal ones.",
        ],
        restaurants=RESTAURANTS[:4],
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=5, y=5),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=10, y=10),
                   status="offline", speed=1.3, rating=4.5),
            Driver(id="driver_3", name="Taylor", location=Location(x=7, y=12),
                   status="idle", speed=1.4, rating=4.6),
        ],
        initial_orders=[
            Order(
                id="order_1", customer_name="Sam",
                restaurant_id="rest_1",
                pickup_location=Location(x=3, y=5),
                delivery_location=Location(x=1, y=1),
                status="pending", priority="vip",
                max_delivery_time=18, prep_time_remaining=3,
                tip_amount=10.0,
                items=["Premium Burger"],
            ),
            Order(
                id="order_2", customer_name="Riley",
                restaurant_id="rest_2",
                pickup_location=Location(x=8, y=2),
                delivery_location=Location(x=14, y=1),
                status="pending", priority="normal",
                max_delivery_time=16, prep_time_remaining=5,
                items=["Pizza"],
            ),
            Order(
                id="order_3", customer_name="Morgan",
                restaurant_id="rest_3",
                pickup_location=Location(x=15, y=10),
                delivery_location=Location(x=19, y=18),
                status="pending", priority="normal",
                max_delivery_time=14, prep_time_remaining=4,
                items=["Sushi Roll"],
            ),
            Order(
                id="order_4", customer_name="Casey",
                restaurant_id="rest_4",
                pickup_location=Location(x=6, y=14),
                delivery_location=Location(x=8, y=18),
                status="pending", priority="priority",
                max_delivery_time=20, prep_time_remaining=2,
                items=["Taco Box"],
            ),
        ],
        incoming_orders=[],
        max_steps=35,
        success_criteria={
            "min_delivered": 2,
            "min_on_time_rate": 0.75,
            "vip_on_time": True,
        },
    ),
    Task(
        task_id="medium_3",
        difficulty="medium",
        description=(
            "Efficiency challenge! 3 orders are pending from restaurants that are "
            "close together. Try to assign drivers optimally so the total distance "
            "driven is minimised. You get bonus rewards for lower total distance."
        ),
        hints=[
            "Calculate Manhattan distance from each driver to each restaurant.",
            "Driver 1 at (3,4) to rest_1 (3,5) = 1 step, rest_2 (8,2) = 7 steps.",
            "Optimal: Driver 1 to rest_1, Driver 2 to rest_2, Driver 3 to rest_5.",
        ],
        restaurants=[RESTAURANTS[0], RESTAURANTS[1], RESTAURANTS[4]],
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=3, y=4),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=7, y=1),
                   status="idle", speed=1.3, rating=4.5),
            Driver(id="driver_3", name="Taylor", location=Location(x=11, y=8),
                   status="idle", speed=1.4, rating=4.6),
        ],
        initial_orders=[
            Order(
                id="order_1", customer_name="Sam",
                restaurant_id="rest_1",
                pickup_location=Location(x=3, y=5),
                delivery_location=Location(x=6, y=9),
                status="pending", priority="normal",
                max_delivery_time=20, prep_time_remaining=3,
                items=["Burger"],
            ),
            Order(
                id="order_2", customer_name="Riley",
                restaurant_id="rest_2",
                pickup_location=Location(x=8, y=2),
                delivery_location=Location(x=12, y=4),
                status="pending", priority="normal",
                max_delivery_time=20, prep_time_remaining=5,
                items=["Pizza"],
            ),
            Order(
                id="order_3", customer_name="Morgan",
                restaurant_id="rest_5",
                pickup_location=Location(x=12, y=7),
                delivery_location=Location(x=16, y=10),
                status="pending", priority="normal",
                max_delivery_time=20, prep_time_remaining=6,
                items=["Pasta"],
            ),
        ],
        incoming_orders=[],
        max_steps=35,
        success_criteria={
            "all_orders_delivered": True,
            "min_on_time_rate": 1.0,
        },
    ),
]


HARD_TASKS = [
    Task(
        task_id="hard_1",
        difficulty="hard",
        description=(
            "Peak hour chaos! 5 orders are in the queue, 2 more arrive mid-episode. "
            "One restaurant will close at time-step 10 (Sushi World). A driver goes "
            "offline at time-step 7. You have 4 drivers initially. "
            "Maximise deliveries, prioritise VIP orders, and cancel orders that "
            "cannot be fulfilled before their deadline."
        ),
        hints=[
            "Plan ahead: Sushi World closes at step 10, so order_3 (from Sushi World) must be picked up before then.",
            "Driver 4 goes offline at step 7 — don't assign long tasks to them.",
            "VIP order_5 should be prioritised even if it means cancelling a normal order.",
        ],
        restaurants=RESTAURANTS,
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=4, y=5),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=9, y=3),
                   status="idle", speed=1.3, rating=4.5),
            Driver(id="driver_3", name="Taylor", location=Location(x=14, y=8),
                   status="idle", speed=1.4, rating=4.6),
            Driver(id="driver_4", name="Morgan", location=Location(x=7, y=14),
                   status="idle", speed=1.2, rating=4.3),
        ],
        initial_orders=[
            Order(id="order_1", customer_name="Sam", restaurant_id="rest_1",
                  pickup_location=Location(x=3, y=5),
                  delivery_location=Location(x=1, y=9),
                  status="pending", priority="normal",
                  max_delivery_time=20, prep_time_remaining=3,
                  items=["Burger"]),
            Order(id="order_2", customer_name="Riley", restaurant_id="rest_2",
                  pickup_location=Location(x=8, y=2),
                  delivery_location=Location(x=13, y=5),
                  status="pending", priority="priority",
                  max_delivery_time=18, prep_time_remaining=5,
                  items=["Pizza"]),
            Order(id="order_3", customer_name="Morgan", restaurant_id="rest_3",
                  pickup_location=Location(x=15, y=10),
                  delivery_location=Location(x=19, y=15),
                  status="pending", priority="normal",
                  max_delivery_time=22, prep_time_remaining=4,
                  items=["Sushi Platter"]),
            Order(id="order_4", customer_name="Casey", restaurant_id="rest_4",
                  pickup_location=Location(x=6, y=14),
                  delivery_location=Location(x=3, y=18),
                  status="pending", priority="normal",
                  max_delivery_time=25, prep_time_remaining=2,
                  items=["Tacos"]),
            Order(id="order_5", customer_name="VIP Blake", restaurant_id="rest_5",
                  pickup_location=Location(x=12, y=7),
                  delivery_location=Location(x=15, y=4),
                  status="pending", priority="vip",
                  max_delivery_time=16, prep_time_remaining=6,
                  tip_amount=20.0,
                  items=["Premium Pasta"]),
        ],
        incoming_orders=[
            {
                "arrive_at_step": 6,
                "order": {
                    "id": "order_6", "customer_name": "Sky",
                    "restaurant_id": "rest_1",
                    "pickup_location": {"x": 3, "y": 5},
                    "delivery_location": {"x": 7, "y": 2},
                    "status": "pending", "priority": "normal",
                    "max_delivery_time": 20, "prep_time_remaining": 3,
                    "items": ["Cheeseburger"],
                },
            },
            {
                "arrive_at_step": 12,
                "order": {
                    "id": "order_7", "customer_name": "Sage",
                    "restaurant_id": "rest_4",
                    "pickup_location": {"x": 6, "y": 14},
                    "delivery_location": {"x": 2, "y": 12},
                    "status": "pending", "priority": "priority",
                    "max_delivery_time": 18, "prep_time_remaining": 2,
                    "items": ["Taco Feast"],
                },
            },
        ],
        max_steps=45,
        success_criteria={
            "min_delivered": 5,
            "min_on_time_rate": 0.6,
            "vip_on_time": True,
        },
    ),
    Task(
        task_id="hard_2",
        difficulty="hard",
        description=(
            "Surge pricing scenario! 6 orders arrive in waves. You have 3 drivers "
            "but orders keep coming. You must decide which orders to accept and "
            "which to cancel. VIP orders carry double reward. "
            "A traffic jam at grid zone x=8-12; drivers in that zone move at half speed. "
            "Maximise total revenue (tips + on-time bonuses)."
        ),
        hints=[
            "Avoid sending drivers through the traffic zone (x=8-12) when possible.",
            "VIP orders have higher tips — prioritise them for revenue.",
            "It's better to cancel early than to deliver late — late deliveries get 0 reward.",
        ],
        restaurants=RESTAURANTS,
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=4, y=5),
                   status="idle", speed=1.5, rating=4.7),
            Driver(id="driver_2", name="Jordan", location=Location(x=14, y=3),
                   status="idle", speed=1.3, rating=4.5),
            Driver(id="driver_3", name="Taylor", location=Location(x=6, y=15),
                   status="idle", speed=1.4, rating=4.6),
        ],
        initial_orders=[
            Order(id="order_1", customer_name="Sam", restaurant_id="rest_1",
                  pickup_location=Location(x=3, y=5),
                  delivery_location=Location(x=2, y=9),
                  status="pending", priority="normal",
                  max_delivery_time=18, prep_time_remaining=3,
                  items=["Burger"]),
            Order(id="order_2", customer_name="Riley", restaurant_id="rest_3",
                  pickup_location=Location(x=15, y=10),
                  delivery_location=Location(x=18, y=6),
                  status="pending", priority="vip",
                  max_delivery_time=16, prep_time_remaining=4,
                  tip_amount=20.0,
                  items=["Sushi Deluxe"]),
            Order(id="order_3", customer_name="Morgan", restaurant_id="rest_4",
                  pickup_location=Location(x=6, y=14),
                  delivery_location=Location(x=4, y=19),
                  status="pending", priority="normal",
                  max_delivery_time=20, prep_time_remaining=2,
                  items=["Tacos"]),
        ],
        incoming_orders=[
            {
                "arrive_at_step": 4,
                "order": {
                    "id": "order_4", "customer_name": "VIP Dana",
                    "restaurant_id": "rest_5",
                    "pickup_location": {"x": 12, "y": 7},
                    "delivery_location": {"x": 16, "y": 2},
                    "status": "pending", "priority": "vip",
                    "max_delivery_time": 16, "prep_time_remaining": 6,
                    "tip_amount": 25.0,
                    "items": ["Premium Pasta Set"],
                },
            },
            {
                "arrive_at_step": 8,
                "order": {
                    "id": "order_5", "customer_name": "Pat",
                    "restaurant_id": "rest_1",
                    "pickup_location": {"x": 3, "y": 5},
                    "delivery_location": {"x": 7, "y": 1},
                    "status": "pending", "priority": "normal",
                    "max_delivery_time": 22, "prep_time_remaining": 3,
                    "items": ["Fries Combo"],
                },
            },
            {
                "arrive_at_step": 12,
                "order": {
                    "id": "order_6", "customer_name": "Quinn",
                    "restaurant_id": "rest_2",
                    "pickup_location": {"x": 8, "y": 2},
                    "delivery_location": {"x": 5, "y": 4},
                    "status": "pending", "priority": "priority",
                    "max_delivery_time": 18, "prep_time_remaining": 5,
                    "items": ["Family Pizza"],
                },
            },
        ],
        max_steps=45,
        success_criteria={
            "min_delivered": 4,
            "min_on_time_rate": 0.6,
            "vip_on_time": True,
        },
    ),
    Task(
        task_id="hard_3",
        difficulty="hard",
        description=(
            "Full operations management! You're managing the entire evening shift. "
            "Start with 3 orders, and 4 more will arrive over time. One driver "
            "has a low rating and should only get easy deliveries. "
            "A restaurant runs out of ingredients at step 15 (Pizza Express — "
            "any unstarted orders from there must be cancelled). "
            "Maintain a fleet on-time rate above 70%% and deliver all VIP orders."
        ),
        hints=[
            "Driver 3 (rating 3.8) should get short, simple deliveries only.",
            "Pizza Express becomes unavailable at step 15 — plan accordingly.",
            "Balance workload: don't overload one driver while others are idle.",
        ],
        restaurants=RESTAURANTS,
        drivers=[
            Driver(id="driver_1", name="Alex", location=Location(x=5, y=5),
                   status="idle", speed=1.5, rating=4.8),
            Driver(id="driver_2", name="Jordan", location=Location(x=10, y=8),
                   status="idle", speed=1.3, rating=4.5),
            Driver(id="driver_3", name="Taylor", location=Location(x=7, y=3),
                   status="idle", speed=1.0, rating=3.8),
            Driver(id="driver_4", name="Casey", location=Location(x=3, y=12),
                   status="idle", speed=1.4, rating=4.6),
        ],
        initial_orders=[
            Order(id="order_1", customer_name="Sam", restaurant_id="rest_1",
                  pickup_location=Location(x=3, y=5),
                  delivery_location=Location(x=6, y=8),
                  status="pending", priority="normal",
                  max_delivery_time=20, prep_time_remaining=3,
                  items=["Burger"]),
            Order(id="order_2", customer_name="Riley", restaurant_id="rest_2",
                  pickup_location=Location(x=8, y=2),
                  delivery_location=Location(x=13, y=5),
                  status="pending", priority="normal",
                  max_delivery_time=24, prep_time_remaining=5,
                  items=["Pepperoni Pizza"]),
            Order(id="order_3", customer_name="VIP Morgan", restaurant_id="rest_5",
                  pickup_location=Location(x=12, y=7),
                  delivery_location=Location(x=15, y=3),
                  status="pending", priority="vip",
                  max_delivery_time=18, prep_time_remaining=6,
                  tip_amount=18.0,
                  items=["Truffle Pasta"]),
        ],
        incoming_orders=[
            {
                "arrive_at_step": 5,
                "order": {
                    "id": "order_4", "customer_name": "Pat",
                    "restaurant_id": "rest_4",
                    "pickup_location": {"x": 6, "y": 14},
                    "delivery_location": {"x": 2, "y": 17},
                    "status": "pending", "priority": "normal",
                    "max_delivery_time": 22, "prep_time_remaining": 2,
                    "items": ["Taco Box"],
                },
            },
            {
                "arrive_at_step": 8,
                "order": {
                    "id": "order_5", "customer_name": "VIP Drew",
                    "restaurant_id": "rest_3",
                    "pickup_location": {"x": 15, "y": 10},
                    "delivery_location": {"x": 18, "y": 13},
                    "status": "pending", "priority": "vip",
                    "max_delivery_time": 16, "prep_time_remaining": 4,
                    "tip_amount": 22.0,
                    "items": ["Sushi Premium Set"],
                },
            },
            {
                "arrive_at_step": 13,
                "order": {
                    "id": "order_6", "customer_name": "Sage",
                    "restaurant_id": "rest_2",
                    "pickup_location": {"x": 8, "y": 2},
                    "delivery_location": {"x": 5, "y": 5},
                    "status": "pending", "priority": "normal",
                    "max_delivery_time": 20, "prep_time_remaining": 5,
                    "items": ["Margherita Pizza"],
                },
            },
            {
                "arrive_at_step": 18,
                "order": {
                    "id": "order_7", "customer_name": "Robin",
                    "restaurant_id": "rest_1",
                    "pickup_location": {"x": 3, "y": 5},
                    "delivery_location": {"x": 8, "y": 9},
                    "status": "pending", "priority": "priority",
                    "max_delivery_time": 22, "prep_time_remaining": 3,
                    "items": ["Double Burger"],
                },
            },
        ],
        max_steps=50,
        success_criteria={
            "min_delivered": 5,
            "min_on_time_rate": 0.7,
            "vip_on_time": True,
        },
    ),
]


ALL_TASKS = {t.task_id: t for t in EASY_TASKS + MEDIUM_TASKS + HARD_TASKS}


def get_task(task_id: str) -> Optional[Task]:
    return ALL_TASKS.get(task_id)


def get_tasks_by_difficulty(difficulty: str) -> List[Task]:
    return [t for t in ALL_TASKS.values() if t.difficulty == difficulty]


def get_all_task_ids() -> List[str]:
    return list(ALL_TASKS.keys())
