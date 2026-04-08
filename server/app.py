import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json
import uvicorn

from server.food_delivery_environment import FoodDeliveryEnvironment
from models import DeliveryAction


app = FastAPI(
    title="Food Delivery Operations Environment",
    description="An OpenEnv environment for AI agents to manage food delivery operations",
    version="1.0.0",
)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

environments = {}


class ResetRequest(BaseModel):
    task_id: str = "easy_1"
    seed: Optional[int] = None
    episode_id: Optional[str] = None


class StepRequest(BaseModel):
    action: DeliveryAction


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    from tasks import get_all_task_ids, get_task
    task_ids = get_all_task_ids()
    tasks_info = []
    for tid in task_ids:
        t = get_task(tid)
        if t:
            tasks_info.append({
                "id": t.task_id,
                "difficulty": t.difficulty,
                "description": t.description
            })

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Food Delivery Operations | OpenEnv</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #8a2be2;
                --secondary: #4b0082;
                --accent: #00f2ff;
                --bg: #030305;
                --card-bg: rgba(10, 10, 18, 0.9);
                --text: #e2e8f0;
                --text-muted: #64748b;
                --glass: rgba(255, 255, 255, 0.03);
                --success: #10b981;
                --warning: #f59e0b;
                --error: #ef4444;
                --border: rgba(0, 242, 255, 0.15);
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Outfit', sans-serif;
            }}

            body {{
                background-color: var(--bg);
                color: var(--text);
                overflow-x: hidden;
                line-height: 1.6;
                background-image: 
                    radial-gradient(circle at 20% 20%, rgba(138, 43, 226, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 80% 80%, rgba(0, 242, 255, 0.05) 0%, transparent 40%);
            }}

            .background {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #020204;
                z-index: -2;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }}

            header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1.5rem 0;
                border-bottom: 1px solid var(--border);
                margin-bottom: 3rem;
            }}

            .logo {{
                font-size: 1.8rem;
                font-weight: 800;
                background: linear-gradient(90deg, var(--accent), var(--primary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -1px;
                text-transform: uppercase;
            }}

            .status-badge {{
                display: flex;
                align-items: center;
                gap: 0.8rem;
                background: var(--card-bg);
                padding: 0.6rem 1.2rem;
                border-radius: 8px;
                border: 1px solid var(--border);
                font-size: 0.85rem;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);
            }}

            .status-dot {{
                width: 10px;
                height: 10px;
                background-color: var(--accent);
                border-radius: 50%;
                box-shadow: 0 0 12px var(--accent);
                animation: pulse 1.5s infinite;
            }}

            @keyframes pulse {{
                0% {{ opacity: 0.3; transform: scale(0.9); }}
                50% {{ opacity: 1; transform: scale(1.1); }}
                100% {{ opacity: 0.3; transform: scale(0.9); }}
            }}

            .hero-section {{
                display: grid;
                grid-template-columns: 1fr 0.9fr;
                gap: 5rem;
                align-items: center;
                margin-bottom: 8rem;
            }}

            .hero-content h1 {{
                font-size: 4.5rem;
                line-height: 1;
                margin-bottom: 2rem;
                font-weight: 800;
                letter-spacing: -2px;
            }}

            .hero-content p {{
                font-size: 1.25rem;
                color: var(--text-muted);
                margin-bottom: 3rem;
                max-width: 550px;
            }}

            .hero-image-container {{
                position: relative;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 30px 60px rgba(0, 0, 0, 0.8);
                border: 1px solid var(--border);
                background: #000;
            }}

            .hero-image {{
                width: 100%;
                display: block;
                opacity: 0.9;
                transition: transform 1.2s cubic-bezier(0.16, 1, 0.3, 1);
            }}

            .hero-image-container:hover .hero-image {{
                transform: scale(1.08);
                opacity: 1;
            }}

            .cta-group {{
                display: flex;
                gap: 1.5rem;
            }}

            .btn {{
                padding: 1.2rem 2.5rem;
                border-radius: 6px;
                font-weight: 700;
                text-decoration: none;
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                display: inline-flex;
                align-items: center;
                gap: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-size: 0.9rem;
            }}

            .btn-primary {{
                background: var(--accent);
                color: #000;
                box-shadow: 0 0 30px rgba(0, 242, 255, 0.2);
            }}

            .btn-primary:hover {{
                background: #fff;
                transform: translateY(-4px);
                box-shadow: 0 10px 40px rgba(0, 242, 255, 0.4);
            }}

            .btn-secondary {{
                background: transparent;
                color: var(--accent);
                border: 1px solid var(--accent);
            }}

            .btn-secondary:hover {{
                background: rgba(0, 242, 255, 0.15);
                transform: translateY(-4px);
            }}

            .tasks-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 2.5rem;
                margin-bottom: 8rem;
            }}

            .task-card {{
                background: var(--card-bg);
                padding: 2.5rem;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                position: relative;
                overflow: hidden;
            }}

            .task-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--accent), transparent);
                transform: translateX(-100%);
                transition: transform 0.6s ease;
            }}

            .task-card:hover::before {{
                transform: translateX(100%);
            }}

            .task-card:hover {{
                border-color: rgba(0, 242, 255, 0.3);
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            }}

            .difficulty-tag {{
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                padding: 0.4rem 1rem;
                border-radius: 4px;
                margin-bottom: 1.5rem;
                display: inline-block;
                font-weight: 800;
            }}

            .easy {{ background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }}
            .medium {{ background: rgba(245, 158, 11, 0.1); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }}
            .hard {{ background: rgba(239, 68, 68, 0.1); color: var(--error); border: 1px solid rgba(239, 68, 68, 0.2); }}

            .task-card h3 {{
                font-size: 1.6rem;
                margin-bottom: 1rem;
                font-weight: 800;
                color: #fff;
            }}

            .task-card p {{
                color: var(--text-muted);
                font-size: 1rem;
                line-height: 1.6;
            }}

            .btn-launch {{
                background: transparent;
                border: 1px solid var(--accent);
                color: var(--accent);
                padding: 0.5rem 1.2rem;
                border-radius: 4px;
                font-weight: 700;
                font-size: 0.75rem;
                letter-spacing: 1px;
                cursor: pointer;
                transition: all 0.3s;
                text-transform: uppercase;
            }}

            .btn-launch:hover {{
                background: var(--accent);
                color: #000;
            }}

            footer {{
                text-align: center;
                padding: 6rem 0;
                color: var(--text-muted);
                border-top: 1px solid var(--border);
                font-size: 0.9rem;
                letter-spacing: 1px;
            }}

            /* Dashboard Improvements */
            .dashboard-container {{
                display: none;
                margin-top: 4rem;
                scroll-margin-top: 2rem;
            }}

            .dashboard-layout {{
                display: grid;
                grid-template-columns: 1fr 400px;
                gap: 2rem;
                height: 800px;
                margin-bottom: 3rem;
            }}

            .map-container {{
                background: #000;
                border-radius: 12px;
                position: relative;
                overflow: hidden;
                border: 1px solid var(--border);
                box-shadow: inset 0 0 100px rgba(0, 242, 255, 0.05);
            }}

            #city-grid {{
                width: 100%;
                height: 100%;
                display: block;
            }}

            .sidebar {{
                display: flex;
                flex-direction: column;
                gap: 2rem;
                height: 100%;
            }}

            .sidebar-card {{
                background: var(--card-bg);
                border-radius: 12px;
                padding: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
            }}

            .sidebar-card h3 {{
                font-size: 1.1rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 1.5rem;
                color: var(--accent);
                border-left: 3px solid var(--accent);
                padding-left: 1rem;
            }}

            .mission-stats-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.2rem;
            }}

            .stat-box {{
                background: rgba(255, 255, 255, 0.02);
                padding: 1.2rem;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.03);
            }}

            .stat-box label {{
                display: block;
                font-size: 0.65rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 1.5px;
                margin-bottom: 0.5rem;
            }}

            .stat-box span {{
                font-size: 1.4rem;
                font-weight: 800;
                color: #fff;
            }}

            .log-container {{
                flex-grow: 1;
                overflow-y: auto;
                font-family: 'JetBrains Mono', 'Courier New', monospace;
                font-size: 0.8rem;
                padding: 1.2rem;
                background: rgba(0, 0, 0, 0.4);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #a1a1aa;
                line-height: 1.5;
            }}

            .log-entry {{ margin-bottom: 0.5rem; }}

            .control-bar {{
                display: flex;
                gap: 1.5rem;
                justify-content: center;
                margin-bottom: 6rem;
            }}

            .map-badge {{
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(10px);
                padding: 0.8rem 1.5rem;
                border-radius: 4px;
                border: 1px solid var(--accent);
                font-size: 0.8rem;
                font-weight: 800;
                color: var(--accent);
                letter-spacing: 2px;
                box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);
            }}

            .legend-v2 {{
                position: absolute;
                bottom: 1.5rem;
                right: 1.5rem;
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(15px);
                padding: 1rem;
                border-radius: 8px;
                display: flex;
                flex-direction: column;
                gap: 0.8rem;
                font-size: 0.7rem;
                border: 1px solid var(--border);
                text-transform: uppercase;
                letter-spacing: 1px;
            }}

            .legend-item-v2 {{ display: flex; align-items: center; gap: 0.8rem; }}
            .legend-icon {{ width: 14px; height: 14px; border: 1px solid var(--accent); }}

            .btn-warning {{
                background: transparent;
                color: var(--warning);
                border: 1px solid var(--warning);
            }}

            .btn-warning:hover {{
                background: rgba(245, 158, 11, 0.1);
            }}

            /* Responsive Scaling */
            @media (max-width: 1024px) {{
                .dashboard-layout {{
                    grid-template-columns: 1fr;
                    height: auto;
                }}
                .map-container {{
                    height: 600px;
                }}
            }}

            @media (max-width: 968px) {{
                .hero-section {{ grid-template-columns: 1fr; text-align: center; }}
                .hero-content {{ order: 2; }}
                .hero-image-container {{ order: 1; }}
                .hero-content h1 {{ font-size: 3.5rem; }}
                .cta-group {{ justify-content: center; }}
                .tasks-grid {{ grid-template-columns: 1fr; }}
            }}
</style>
    </head>
    <body>
        <div class="background"></div>
        <div class="hero-glow"></div>

        <div class="container">
            <header>
                <div class="logo">FOOD DELIVERY ENV</div>
                <div class="status-badge">
                    <div class="status-dot"></div>
                    System Online
                </div>
            </header>

            <section class="hero-section">
                <div class="hero-content">
                    <h1>Manage the <br><span style="color: var(--accent);">Future</span> of Delivery</h1>
                    <p>An OpenEnv-compatible simulation for AI agents to master restaurant operations, driver routing, and customer satisfaction in a dynamic city environment.</p>
                    <div class="cta-group">
                        <a href="/docs" class="btn btn-primary">Explorer Docs</a>
                        <a href="#tasks" class="btn btn-secondary">View Tasks</a>
                    </div>
                </div>
                <div class="hero-image-container">
                    <img src="/static/hero.png" alt="Environment Dashboard" class="hero-image">
                </div>
            </section>

            <section id="dashboard" class="dashboard-container">
                <div class="dashboard-layout">
                    <div class="map-container">
                        <div class="map-overlay">
                            <div id="time-step-badge" class="map-badge">TS: 0</div>
                        </div>
                        <canvas id="city-grid" width="1000" height="700"></canvas>
                        <div class="legend-v2">
                            <div class="legend-item-v2"><span class="legend-icon" style="background: var(--primary);"></span> HUB</div>
                            <div class="legend-item-v2"><span class="legend-icon" style="background: var(--accent);"></span> UNIT</div>
                            <div class="legend-item-v2"><span class="legend-icon" style="background: #fbbf24;"></span> PICKUP</div>
                            <div class="legend-item-v2"><span class="legend-icon" style="background: var(--success);"></span> TARGET</div>
                        </div>
                    </div>

                    <div class="sidebar">
                        <div class="sidebar-card">
                            <h3>Mission Insights</h3>
                            <div class="mission-stats-grid">
                                <div class="stat-box"><label>Status</label><span id="stat-status">Idle</span></div>
                                <div class="stat-box"><label>Reward</label><span id="stat-reward">0.00</span></div>
                                <div class="stat-box"><label>Live Score</label><span id="stat-score">0.00</span></div>
                                <div class="stat-box"><label>Delivered</label><span id="stat-delivered">0/0</span></div>
                            </div>
                            <div class="performance-chart-container">
                                <label style="font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase;">Reward Analytics</label>
                                <canvas id="performance-chart"></canvas>
                            </div>
                        </div>

                        <div class="sidebar-card" style="flex-grow: 1; display: flex; flex-direction: column;">
                            <h3>Operations Log</h3>
                            <div id="log-console" class="log-container">
                                <div class="log-entry">> Initializing...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="control-bar">
                    <button id="btn-step" class="btn btn-secondary">Next Step</button>
                    <button id="btn-auto-pilot" class="btn btn-warning">Auto-Pilot</button>
                    <button id="btn-auto" class="btn btn-primary">Run Simulation</button>
                    <button id="btn-stop" class="btn btn-secondary">Pause</button>
                </div>
            </section>

            <h2 id="tasks" style="font-size: 2.5rem; margin-bottom: 3rem; text-align: center;">Mission Hub</h2>
            <div class="tasks-grid">
                {"".join([f'''
                <div class="task-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <span class="difficulty-tag {t['difficulty']}">{t['difficulty']}</span>
                        <button onclick="launchTask('{t['id']}')" class="btn-launch">Launch</button>
                    </div>
                    <h3>{t['id'].replace('_', ' ').title()}</h3>
                    <p>{t['description']}</p>
                </div>
                ''' for t in tasks_info])}
            </div>

            <footer>
                <p>&copy; 2026 Food Delivery Operations Engine. OpenEnv Standard Compliance Level 1.</p>
            </footer>
        </div>

        <script>
            let socket = null;
            let currentTaskId = null;
            let currentEpisodeId = null;
            let autoInterval = null;
            const canvas = document.getElementById('city-grid');
            const ctx = canvas.getContext('2d');
            const gridSize = 20;
            
            // Animation State
            let currentObs = null;
            let prevObs = null;
            let transitionFactor = 1.0;
            
            // Ambient Traffic Simulation (Premium)
            const ambientTraffic = [];
            const numTrafficCars = 25; 
            
            for (let i = 0; i < numTrafficCars; i++) {{
                const isHorizontal = Math.random() > 0.5;
                ambientTraffic.push({{
                    id: `traffic-${{i}}`,
                    horizontal: isHorizontal,
                    pos: Math.random() * gridSize,
                    lane: Math.floor(Math.random() * gridSize),
                    speed: 0.03 + Math.random() * 0.08,
                    width: 12 + Math.random() * 8,
                    height: 8,
                    color: ['#334155', '#475569', '#1e293b', '#64748b'][Math.floor(Math.random() * 4)]
                }});
            }}

            const varColors = {{
                primary: '#8a2be2',
                accent: '#00f2ff',
                success: '#10b981',
                bg: '#050505',
                error: '#ef4444',
                warning: '#f59e0b'
            }};

            // Reward History
            let rewardHistory = [];
            const chartCanvas = document.getElementById('performance-chart');
            const chartCtx = chartCanvas ? chartCanvas.getContext('2d') : null;

            function updatePerformanceChart() {{
                if (!chartCtx || rewardHistory.length < 2) return;
                const w = chartCanvas.width = chartCanvas.offsetWidth;
                const h = chartCanvas.height = chartCanvas.offsetHeight;
                chartCtx.clearRect(0, 0, w, h);
                chartCtx.strokeStyle = varColors.accent;
                chartCtx.lineWidth = 2;
                chartCtx.beginPath();
                const max = Math.max(...rewardHistory, 0.1);
                const min = Math.min(...rewardHistory, -0.1);
                const range = max - min;
                rewardHistory.forEach((r, i) => {{
                    const x = (i / (rewardHistory.length - 1)) * w;
                    const y = h - ((r - min) / range) * h;
                    if (i === 0) chartCtx.moveTo(x, y);
                    else chartCtx.lineTo(x, y);
                }});
                chartCtx.stroke();
                chartCtx.lineTo(w, h);
                chartCtx.lineTo(0, h);
                chartCtx.fillStyle = `${{varColors.accent}}22`;
                chartCtx.fill();
            }}

            function log(msg, color = '#64748b') {{
                const consoleOutput = document.getElementById('log-console');
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.style.color = color;
                const now = new Date().toLocaleTimeString([], {{hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit'}});
                entry.innerHTML = `<span style="color: #3f3f46">[${{now}}]</span> <span style="color: ${{color}}">// ${{msg}}</span>`;
                consoleOutput.appendChild(entry);
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }}

            function updateStats(obs) {{
                document.getElementById('stat-status').textContent = obs.done ? 'COMPLETED' : 'ENGAGED';
                document.getElementById('stat-reward').textContent = (obs.reward || 0).toFixed(4);
                document.getElementById('stat-score').textContent = (obs.score || 0).toFixed(2);
                const delivered = obs.metrics?.delivered ?? 0;
                const total = obs.metrics?.total_orders ?? 0;
                document.getElementById('stat-delivered').textContent = `${{delivered}}/${{total}}`;
                rewardHistory.push(obs.reward || 0);
                if (rewardHistory.length > 60) rewardHistory.shift();
                updatePerformanceChart();
                document.getElementById('time-step-badge').textContent = `T-STEP: ${{obs.time_step}}`;
                if (obs.action_message) log(obs.action_message.toUpperCase(), varColors.accent);
                if (obs.done) log('MISSION SUCCESSFUL. ALL SYSTEMS DISENGAGED.', varColors.success);
            }}

            function drawGrid() {{
                requestAnimationFrame(drawGrid);
                if (!currentObs || !ctx) return;
                
                try {{
                    const width = canvas.width;
                    const height = canvas.height;
                    const cellSize = width / gridSize;
                    ctx.globalCompositeOperation = 'source-over';
                    ctx.clearRect(0, 0, width, height);

                    // 1. Base Layer (Tactical Dark)
                    ctx.fillStyle = '#010103';
                    ctx.fillRect(0, 0, width, height);

                    // 2. City Blocks (Buildings)
                    ctx.fillStyle = '#050508';
                    const pad = cellSize * 0.1;
                    const roadWidth = cellSize * 0.4;
                    for (let i = 0; i < gridSize; i++) {{
                        for (let j = 0; j < gridSize; j++) {{
                            const bx = i * cellSize + (cellSize - roadWidth)/2 + roadWidth;
                            const by = j * cellSize + (cellSize - roadWidth)/2 + roadWidth;
                            const bw = cellSize - roadWidth;
                            const bh = cellSize - roadWidth;
                            
                            // Draw block base
                            ctx.fillStyle = 'rgba(10, 10, 20, 0.8)';
                            ctx.fillRect(i * cellSize + pad, j * cellSize + pad, cellSize - pad*2, cellSize - pad*2);
                            
                            // Subtle wireframe on block
                            ctx.strokeStyle = 'rgba(138, 43, 226, 0.03)';
                            ctx.strokeRect(i * cellSize + pad + 2, j * cellSize + pad + 2, cellSize - pad*2 - 4, cellSize - pad*2 - 4);
                        }}
                    }}

                    // 3. Advanced Road Network
                    ctx.fillStyle = '#080812';
                    for (let i = 0; i < gridSize; i++) {{
                        // Horizontal Roads
                        ctx.fillRect(0, i * cellSize + (cellSize - roadWidth)/2, width, roadWidth);
                        // Vertical Roads
                        ctx.fillRect(i * cellSize + (cellSize - roadWidth)/2, 0, roadWidth, height);
                    }}
                    
                    // Road Markings (Neon Centerlines)
                    ctx.strokeStyle = 'rgba(0, 242, 255, 0.08)';
                    ctx.lineWidth = 1;
                    ctx.setLineDash([10, 10]);
                    for (let i = 0; i < gridSize; i++) {{
                        const pos = i * cellSize + cellSize/2;
                        // Horizontal centers
                        ctx.beginPath(); ctx.moveTo(0, pos); ctx.lineTo(width, pos); ctx.stroke();
                        // Vertical centers
                        ctx.beginPath(); ctx.moveTo(pos, 0); ctx.lineTo(pos, height); ctx.stroke();
                    }}
                    ctx.setLineDash([]);

                    // 4. High-Tech Grid Overlay
                    ctx.strokeStyle = 'rgba(0, 242, 255, 0.04)';
                    ctx.lineWidth = 0.5;
                    for (let i = 0; i <= gridSize; i++) {{
                        ctx.beginPath(); ctx.moveTo(i * cellSize, 0); ctx.lineTo(i * cellSize, height); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(0, i * cellSize); ctx.lineTo(width, i * cellSize); ctx.stroke();
                    }}

                    // Major Coordinates
                    ctx.fillStyle = 'rgba(0, 242, 255, 0.2)';
                    ctx.font = '7px JetBrains Mono';
                    for (let i = 0; i < gridSize; i += 2) {{
                        ctx.fillText(String.fromCharCode(65 + i), i * cellSize + 2, 8);
                        ctx.fillText(i + 1, 2, i * cellSize + 10);
                    }}

                    // 5. Traffic Congestion Zone
                    if (currentObs.metadata && (currentObs.metadata.task_id.startsWith('hard'))) {{
                        const pulse = (Math.sin(Date.now() / 300) + 1) / 2;
                        ctx.fillStyle = `rgba(239, 68, 68, ${{0.05 + pulse * 0.05}})`;
                        ctx.fillRect(8 * cellSize, 0, 4 * cellSize, height);
                        ctx.strokeStyle = `rgba(239, 68, 68, ${{0.3 + pulse * 0.2}})`;
                        ctx.lineWidth = 1;
                        ctx.strokeRect(8 * cellSize, 0, 4 * cellSize, height);
                        
                        // Hazard lines
                        ctx.setLineDash([5, 5]);
                        ctx.beginPath();
                        ctx.moveTo(8 * cellSize, 0); ctx.lineTo(12 * cellSize, height);
                        ctx.stroke();
                        ctx.setLineDash([]);
                    }}

                    // 6. Ambient Traffic
                    ctx.globalCompositeOperation = 'lighter';
                    ambientTraffic.forEach(car => {{
                        car.pos = (car.pos + car.speed) % gridSize;
                        let tx, ty;
                        if (car.horizontal) {{
                            tx = car.pos * cellSize;
                            ty = car.lane * cellSize + cellSize/2;
                        }} else {{
                            tx = car.lane * cellSize + cellSize/2;
                            ty = car.pos * cellSize;
                        }}
                        drawTacticalCar(ctx, tx, ty, car.width, car.height, car.color, car.horizontal);
                    }});

                    // 7. Radar Pings from HUBs
                    const now = Date.now();
                    currentObs.restaurants.forEach(r => {{
                        const rx = r.location.x * cellSize + cellSize/2;
                        const ry = r.location.y * cellSize + cellSize/2;
                        const pingSize = (now % 2000) / 2000 * cellSize * 4;
                        const opacity = 1 - (now % 2000) / 2000;
                        ctx.strokeStyle = `rgba(138, 43, 226, ${{opacity * 0.3}})`;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.arc(rx, ry, pingSize, 0, Math.PI * 2);
                        ctx.stroke();
                    }});

                    // 8. HUBs (Restaurants)
                    currentObs.restaurants.forEach(r => {{
                        const x = r.location.x * cellSize + cellSize/2;
                        const y = r.location.y * cellSize + cellSize/2;
                        drawTacticalMarker(x, y, 'HEX', r.name || r.id, varColors.primary, 15);
                    }});

                    // 9. Targets (Orders)
                    currentObs.orders.forEach(o => {{
                        if (o.status !== 'delivered' && o.status !== 'cancelled') {{
                            const dx = o.delivery_location.x * cellSize + cellSize/2;
                            const dy = o.delivery_location.y * cellSize + cellSize/2;
                            
                            // Glowing target pulse
                            const pulse = (Math.sin(now / 200) + 1) / 2;
                            ctx.shadowBlur = 10 + pulse * 10;
                            ctx.shadowColor = varColors.success;
                            drawTacticalMarker(dx, dy, 'CROSS', `TARGET-${{o.id}}`, varColors.success, 10);
                            ctx.shadowBlur = 0;

                            if (['pending', 'preparing', 'assigned'].includes(o.status)) {{
                                const px = o.pickup_location.x * cellSize + cellSize/2;
                                const py = o.pickup_location.y * cellSize + cellSize/2;
                                drawTacticalMarker(px, py, 'DIAMOND', `PICKUP-${{o.id}}`, varColors.warning, 9);
                            }}
                        }}
                    }});

                    // 10. Active Units (Drivers)
                    currentObs.drivers.forEach(d => {{
                        let x = d.location.x;
                        let y = d.location.y;

                        if (prevObs && transitionFactor < 1.0) {{
                            const pd = prevObs.drivers.find(p => p.id === d.id);
                            if (pd) {{
                                x = pd.location.x + (x - pd.location.x) * transitionFactor;
                                y = pd.location.y + (y - pd.location.y) * transitionFactor;
                            }}
                        }}

                        const cx = x * cellSize + cellSize/2;
                        const cy = y * cellSize + cellSize/2;

                        // Mission Path Visualization
                        if (d.status !== 'idle' && d.status !== 'offline') {{
                            const order = currentObs.orders.find(o => o.id === d.current_order_id);
                            if (order) {{
                                const isPickingUp = (d.status.includes('restaurant') || d.status.includes('picking'));
                                const target = isPickingUp ? order.pickup_location : order.delivery_location;
                                const tx = target.x * cellSize + cellSize/2;
                                const ty = target.y * cellSize + cellSize/2;

                                // Path glow
                                ctx.strokeStyle = isPickingUp ? varColors.accent : varColors.success;
                                ctx.lineWidth = 2;
                                ctx.shadowBlur = 8;
                                ctx.shadowColor = ctx.strokeStyle;
                                ctx.setLineDash([5, 5]);
                                ctx.beginPath();
                                ctx.moveTo(cx, cy);
                                ctx.lineTo(tx, ty);
                                ctx.stroke();
                                ctx.setLineDash([]);
                                ctx.shadowBlur = 0;
                            }}
                        }}

                        drawTacticalMarker(cx, cy, 'UNIT', d.id, varColors.accent, 12, d.status !== 'idle');
                    }});

                    // 11. Scanline Overlay Effect
                    ctx.globalCompositeOperation = 'source-over';
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                    for (let i = 0; i < height; i += 4) {{
                        ctx.fillRect(0, i, width, 1);
                    }}

                    if (transitionFactor < 1.0) transitionFactor += 0.08;
                }} catch (e) {{
                    console.error('Tactical Render Failure:', e);
                }}
            }}

            function drawTacticalCar(ctx, x, y, w, h, color, horizontal) {{
                ctx.save();
                ctx.translate(x, y);
                if (!horizontal) ctx.rotate(Math.PI / 2);
                
                // Shadow
                ctx.fillStyle = 'rgba(0,0,0,0.5)';
                ctx.fillRect(-w/2 + 2, -h/2 + 2, w, h);

                // Body
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.roundRect(-w/2, -h/2, w, h, 2);
                ctx.fill();
                
                // Lights glow
                ctx.shadowBlur = 5;
                ctx.shadowColor = '#fff';
                ctx.fillStyle = '#fff';
                ctx.fillRect(w/2 - 2, -h/2, 2, 2);
                ctx.fillRect(w/2 - 2, h/2 - 2, 2, 2);
                
                ctx.shadowColor = '#f00';
                ctx.fillStyle = '#f00';
                ctx.fillRect(-w/2, -h/2, 1, 2);
                ctx.fillRect(-w/2, h/2 - 2, 1, 2);
                
                ctx.restore();
            }}

            function drawTacticalMarker(x, y, type, label, color, size, active = false) {{
                const now = Date.now();
                const floatY = active ? Math.sin(now / 300) * 4 : 0;
                const ty = y + floatY;

                ctx.save();
                ctx.translate(x, ty);
                
                // Outer Glow
                ctx.shadowBlur = 15;
                ctx.shadowColor = color;
                ctx.strokeStyle = color;
                ctx.lineWidth = 2.5;

                if (type === 'HEX') {{
                    ctx.beginPath();
                    for (let i = 0; i < 6; i++) {{
                        const angle = i * Math.PI / 3;
                        ctx.lineTo(size * Math.cos(angle), size * Math.sin(angle));
                    }}
                    ctx.closePath();
                    ctx.fillStyle = color + '11';
                    ctx.fill();
                    ctx.stroke();
                    
                    // Inner accent
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.arc(0, 0, size * 0.4, 0, Math.PI*2);
                    ctx.stroke();
                }} else if (type === 'CROSS') {{
                    ctx.beginPath();
                    ctx.moveTo(-size, 0); ctx.lineTo(size, 0);
                    ctx.moveTo(0, -size); ctx.lineTo(0, size);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(0, 0, size * 0.7, 0, Math.PI * 2);
                    ctx.stroke();
                }} else if (type === 'DIAMOND') {{
                    ctx.beginPath();
                    ctx.moveTo(0, -size); ctx.lineTo(size, 0);
                    ctx.lineTo(0, size); ctx.lineTo(-size, 0);
                    ctx.closePath();
                    ctx.stroke();
                    ctx.fillStyle = color + '22';
                    ctx.fill();
                }} else if (type === 'UNIT') {{
                    // Circle background
                    ctx.beginPath();
                    ctx.arc(0, 0, size, 0, Math.PI * 2);
                    ctx.stroke();
                    
                    // Directional arrow
                    ctx.fillStyle = color;
                    ctx.beginPath();
                    ctx.moveTo(0, -size - 5);
                    ctx.lineTo(5, -size + 1);
                    ctx.lineTo(-5, -size + 1);
                    ctx.closePath();
                    ctx.fill();

                    if (active) {{
                        const pulse = (Math.sin(now/150) + 1) / 2;
                        ctx.beginPath();
                        ctx.arc(0, 0, size * (1.2 + pulse * 0.2), 0, Math.PI * 2);
                        ctx.strokeStyle = color + '66';
                        ctx.stroke();
                    }}
                }}

                // Digital Label
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#fff';
                ctx.font = '800 10px JetBrains Mono, monospace';
                ctx.textAlign = 'center';
                const text = label.toUpperCase();
                ctx.fillText(text, 0, size + 14);
                
                // Small ID tag
                ctx.font = '500 8px JetBrains Mono';
                ctx.fillStyle = color;
                ctx.fillText("» ACTIVE", 0, -size - 8);

                ctx.restore();
            }}

            async function launchTask(taskId) {{
                currentTaskId = taskId;
                rewardHistory = [];
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('dashboard').scrollIntoView({{ behavior: 'smooth' }});
                
                log(`Tactical Link Initiating: ${{taskId}}...`, varColors.primary);
                initWebSocket();
            }}

            function initWebSocket() {{
                if (socket) socket.close();
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                socket = new WebSocket(`${{protocol}}//${{window.location.host}}/ws`);
                
                socket.onopen = () => {{
                    log('Control Link Established.', varColors.success);
                    socket.send(JSON.stringify({{ type: 'reset', task_id: currentTaskId }}));
                }};
                
                socket.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    if (data.type === 'step_result' || data.type === 'reset_result') {{
                        prevObs = currentObs;
                        currentObs = data.observation;
                        transitionFactor = 0;
                        updateStats(currentObs);
                        
                        if (currentObs.done) {{
                             if (autoInterval) {{
                                 clearInterval(autoInterval);
                                 autoInterval = null;
                                 document.getElementById('btn-auto').textContent = 'Run Simulation';
                                 document.getElementById('btn-auto').classList.remove('btn-success', 'btn-warning');
                                 document.getElementById('btn-auto').classList.add('btn-primary');
                                 document.getElementById('btn-auto-pilot').textContent = 'Auto-Pilot';
                                 document.getElementById('btn-auto-pilot').classList.remove('btn-success');
                                 document.getElementById('btn-auto-pilot').classList.add('btn-warning');
                             }}
                             log('Mission Accomplished. Final stats locked.', varColors.success);
                        }}
                    }}
                }};
            }}

            document.getElementById('btn-step').onclick = () => {{
                if (socket && socket.readyState === WebSocket.OPEN) {{
                    socket.send(JSON.stringify({{ type: 'step', action: {{ action_type: 'wait' }} }}));
                }}
            }};

            document.getElementById('btn-auto-pilot').onclick = () => {{
                const btn = document.getElementById('btn-auto-pilot');
                if (autoInterval) {{
                    clearInterval(autoInterval);
                    autoInterval = null;
                    btn.textContent = 'Auto-Pilot';
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-warning');
                    log('Auto-Pilot Disengaged.');
                }} else {{
                    btn.textContent = 'Active...';
                    btn.classList.remove('btn-warning');
                    btn.classList.add('btn-success');
                    log('Intelligent Tracking System Active.', varColors.success);
                    autoInterval = setInterval(() => {{
                        if (socket && socket.readyState === WebSocket.OPEN) {{
                            socket.send(JSON.stringify({{ type: 'auto_step', task_id: currentTaskId }}));
                        }}
                    }}, 250); 
                }}
            }};

            document.getElementById('btn-auto').onclick = () => {{
                const btn = document.getElementById('btn-auto');
                if (autoInterval) {{
                    clearInterval(autoInterval);
                    autoInterval = null;
                    btn.textContent = 'Run Simulation';
                    btn.classList.remove('btn-warning');
                    btn.classList.add('btn-primary');
                    log('System Paused.');
                }} else {{
                    btn.textContent = 'Running...';
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-warning');
                    log('System engaging Auto-Pilot.', varColors.warning);
                    autoInterval = setInterval(() => {{
                        document.getElementById('btn-step').click();
                    }}, 250);
                }}
            }};

            document.getElementById('btn-stop').onclick = () => {{
                if (autoInterval) document.getElementById('btn-auto').click();
            }};

            drawGrid();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
def health():
    return {"status": "healthy", "environment": "food_delivery_env"}


@app.get("/tasks")
def list_tasks():
    from tasks import get_all_task_ids, get_task
    task_ids = get_all_task_ids()
    result = []
    for tid in task_ids:
        t = get_task(tid)
        if t:
            result.append({
                "task_id": t.task_id,
                "difficulty": t.difficulty,
                "description": t.description,
                "max_steps": t.max_steps,
            })
    return {"tasks": result}


@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    if req is None:
        req = ResetRequest()
    env = FoodDeliveryEnvironment()
    obs = env.reset(task_id=req.task_id, seed=req.seed, episode_id=req.episode_id)
    episode_id = env.state.episode_id
    environments[episode_id] = env
    return {
        "episode_id": episode_id,
        "observation": obs.model_dump(),
    }


@app.post("/step/{episode_id}")
def step(episode_id: str, req: StepRequest):
    env = environments.get(episode_id)
    if not env:
        return {"error": f"No episode found with id {episode_id}. Call /reset first."}

    obs = env.step(req.action)
    if obs.done:
        environments.pop(episode_id, None)

    return {
        "episode_id": episode_id,
        "observation": obs.model_dump(),
    }


@app.get("/state/{episode_id}")
def get_state(episode_id: str):
    env = environments.get(episode_id)
    if not env:
        return {"error": f"No episode found with id {episode_id}."}
    return {"state": env.state.model_dump()}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    env = FoodDeliveryEnvironment()
    episode_id = None

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type", "")

            if msg_type == "reset":
                task_id = msg.get("task_id", "easy_1")
                obs = env.reset(task_id=task_id)
                episode_id = env.state.episode_id
                await ws.send_json({
                    "type": "reset_result",
                    "episode_id": episode_id,
                    "observation": obs.model_dump(),
                })

            elif msg_type == "auto_step":
                current_obs = env.reset(task_id=msg.get("task_id", "easy_1")) if not env._task else env._build_observation(True, "", 0)
                
                # Simple Greedy Assignment
                pending_orders = [o for o in current_obs.orders if o.status == "pending"]
                idle_drivers = [d for d in current_obs.drivers if d.status == "idle"]
                
                if pending_orders and idle_drivers:
                    # Pick first pending order and nearest idle driver
                    order = pending_orders[0]
                    best_driver = None
                    min_dist = float('inf')
                    
                    for d in idle_drivers:
                        dist = abs(d.location.x - order.pickup_location.x) + abs(d.location.y - order.pickup_location.y)
                        if dist < min_dist:
                            min_dist = dist
                            best_driver = d
                    
                    if best_driver:
                        action = DeliveryAction(
                            action_type="assign_order",
                            order_id=order.id,
                            driver_id=best_driver.id
                        )
                        obs = env.step(action)
                    else:
                        obs = env.step(DeliveryAction(action_type="wait"))
                else:
                    obs = env.step(DeliveryAction(action_type="wait"))

                await ws.send_json({
                    "type": "step_result",
                    "observation": obs.model_dump(),
                })

            elif msg_type == "state":
                await ws.send_json({
                    "type": "state_result",
                    "state": env.state.model_dump(),
                })

    except WebSocketDisconnect:
        pass


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
