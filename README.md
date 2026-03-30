---
title: Food Delivery System
emoji: 🍕
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 8000
---

# 🍕 Food Delivery Operations Environment

[![System Status](https://img.shields.io/badge/Status-Online-brightgreen)](#)
[![OpenEnv Compliance](https://img.shields.io/badge/Compliance-OpenEnv_v1.0-blue)](#)

A premium, high-fidelity Simulation Environment designed for training and benchmarking AI agents in complex, multi-objective logistical operations.

> **Explore the Interactive Dashboard:** Once running, visit the root URL at `http://localhost:8000/` to see the live management console.

## 🏙️ Environment Overview

The environment simulates a food delivery operations center. The agent receives incoming customer orders from multiple restaurants and must assign them to available delivery drivers, optimising for on-time delivery, customer satisfaction (VIP priority), and fleet efficiency.

### Key Features

- **Real-world simulation**: City grid with restaurants, drivers, and customers
- **Dynamic events**: New orders arrive mid-episode, restaurants close, drivers go offline, traffic jams
- **Multi-objective optimisation**: Balance on-time delivery, VIP priority, driver workload, and efficiency
- **9 graded tasks** across 3 difficulty levels (easy/medium/hard)
- **Partial reward signals**: Step-by-step feedback, not just end-of-episode scoring

## Action Space

| Action Type | Required Fields | Description |
|---|---|---|
| `assign_order` | `order_id`, `driver_id` | Assign a pending order to an idle driver |
| `reassign_order` | `order_id`, `driver_id` | Reassign an in-progress order to a different driver |
| `cancel_order` | `order_id` | Cancel an undeliverable order |
| `set_driver_offline` | `driver_id` | Take a driver offline |
| `set_driver_online` | `driver_id` | Bring a driver back online |
| `wait` | — | Do nothing, let simulation advance one time-step |

## Observation Space

Each observation includes:

- **restaurants**: List of restaurants with location, prep time, open/closed status
- **drivers**: List of drivers with location, status, current assignment, speed, rating
- **orders**: List of orders with pickup/delivery locations, status, priority, elapsed time
- **metrics**: Aggregated stats (delivered count, on-time rate, idle drivers, etc.)
- **reward**: Step reward based on action quality
- **hints**: Progressive hints for the current task
- **done**: Whether the episode has ended

## Tasks

### Easy (3 tasks)
- **easy_1**: Assign a single order to the nearest driver
- **easy_2**: Assign two simultaneous orders optimally
- **easy_3**: Prioritise a VIP order over a normal order

### Medium (3 tasks)
- **medium_1**: Dinner rush — 5 orders with dynamic arrivals, 3 drivers
- **medium_2**: Driver offline — handle reduced capacity and triage orders
- **medium_3**: Efficiency challenge — minimise total distance driven

### Hard (3 tasks)
- **hard_1**: Peak chaos — restaurant closure, driver outage, 7 orders, 4 drivers
- **hard_2**: Traffic jam zone — surge pricing, route optimisation around congestion
- **hard_3**: Full shift management — ingredient shortage, 7 orders in waves, mixed driver quality

## Reward Function

Step rewards (per action):
- Successful delivery: +0.30
- On-time bonus: +0.20
- VIP on-time bonus: +0.15
- Valid action: +0.02
- Invalid action: -0.05
- Late delivery: -0.10

Final score (0.0–1.0) composed of:
- Delivery ratio: 35%
- On-time rate: 30%
- VIP handling: 15%
- Step efficiency: 10%
- Unhandled penalty: -10%

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r server/requirements.txt
```

### 2. Run the Server Locally

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### 3. Run Baseline Agent

```bash
python baseline.py
```

### 4. Docker

```bash
docker build -t food-delivery-env .
docker run -p 8000:8000 food-delivery-env
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/tasks` | List all available tasks |
| POST | `/reset` | Start a new episode (body: `{"task_id": "easy_1"}`) |
| POST | `/step/{episode_id}` | Execute an action |
| GET | `/state/{episode_id}` | Get episode state |
| WS | `/ws` | WebSocket interface |

## Example Usage

```python
from client import FoodDeliveryClient

client = FoodDeliveryClient("http://localhost:8000")
data = client.reset(task_id="easy_1")
episode_id = data["episode_id"]

result = client.step(
    action_type="assign_order",
    order_id="order_1",
    driver_id="driver_1",
)

print(result["observation"]["reward"])
print(result["observation"]["metrics"])
```

## Project Structure

```
food_delivery_env/
├── __init__.py
├── models.py
├── tasks.py
├── grader.py
├── client.py
├── baseline.py
├── openenv.yaml
├── pyproject.toml
├── Dockerfile
├── .dockerignore
├── README.md
└── server/
    ├── __init__.py
    ├── food_delivery_environment.py
    ├── app.py
    └── requirements.txt
```

## Deployment

### Hugging Face Spaces

This environment is deployed as a Docker Space on Hugging Face:

1. Create a new Space with Docker SDK
2. Upload all project files
3. The Dockerfile handles the rest

### GitHub

The full source code is available on GitHub with CI/CD for automated testing.

## License

BSD 3-Clause License
