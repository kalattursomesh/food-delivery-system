from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class Location(BaseModel):
    x: int = Field(..., ge=0, le=20)
    y: int = Field(..., ge=0, le=20)


class Restaurant(BaseModel):
    id: str
    name: str
    location: Location
    avg_prep_time_minutes: int
    is_open: bool = True


class Driver(BaseModel):
    id: str
    name: str
    location: Location
    status: Literal["idle", "en_route_to_restaurant", "picking_up",
                     "delivering", "offline"] = "idle"
    current_order_id: Optional[str] = None
    speed: float = 1.0
    rating: float = Field(default=4.5, ge=1.0, le=5.0)
    total_deliveries: int = 0


class Order(BaseModel):
    id: str
    customer_name: str
    restaurant_id: str
    pickup_location: Location
    delivery_location: Location
    status: Literal["pending", "assigned", "preparing", "picked_up",
                     "in_transit", "delivered", "cancelled"] = "pending"
    assigned_driver_id: Optional[str] = None
    prep_time_remaining: int = 0
    priority: Literal["normal", "priority", "vip"] = "normal"
    max_delivery_time: int = 30
    elapsed_time: int = 0
    tip_amount: float = 0.0
    items: List[str] = Field(default_factory=list)


class DeliveryAction(BaseModel):
    action_type: Literal[
        "assign_order",
        "reassign_order",
        "cancel_order",
        "set_driver_offline",
        "set_driver_online",
        "wait",
    ]
    order_id: Optional[str] = None
    driver_id: Optional[str] = None
    reason: Optional[str] = None


class DeliveryObservation(BaseModel):
    restaurants: List[Restaurant] = Field(default_factory=list)
    drivers: List[Driver] = Field(default_factory=list)
    orders: List[Order] = Field(default_factory=list)
    action_success: bool = True
    action_message: str = ""
    reward: float = 0.0
    done: bool = False
    task_description: str = ""
    task_difficulty: str = "easy"
    score: float = 0.0
    steps_taken: int = 0
    max_steps: int = 30
    time_step: int = 0
    hints: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeliveryState(BaseModel):
    episode_id: str
    step_count: int = 0
    task_id: str = ""
    task_difficulty: str = "easy"
    current_score: float = 0.0
    is_done: bool = False
    time_step: int = 0
