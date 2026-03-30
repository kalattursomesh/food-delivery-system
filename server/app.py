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
                --bg: #050505;
                --card-bg: rgba(15, 15, 25, 0.8);
                --text: #ffffff;
                --text-muted: #94a3b8;
                --glass: rgba(255, 255, 255, 0.03);
                --success: #10b981;
                --warning: #f59e0b;
                --error: #ef4444;
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
            }}

            .background {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #050505 100%);
                z-index: -2;
            }}

            .hero-glow {{
                position: absolute;
                top: -10%;
                right: -10%;
                width: 50%;
                height: 50%;
                background: radial-gradient(circle, rgba(138, 43, 226, 0.2) 0%, transparent 70%);
                filter: blur(80px);
                z-index: -1;
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
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 4rem;
            }}

            .logo {{
                font-size: 1.8rem;
                font-weight: 800;
                background: linear-gradient(90deg, var(--accent), var(--primary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -1px;
            }}

            .status-badge {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: var(--card-bg);
                padding: 0.5rem 1rem;
                border-radius: 50px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 0.9rem;
            }}

            .status-dot {{
                width: 8px;
                height: 8px;
                background-color: #00ff88;
                border-radius: 50%;
                box-shadow: 0 0 10px #00ff88;
                animation: pulse 2s infinite;
            }}

            @keyframes pulse {{
                0% {{ opacity: 0.4; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.4; }}
            }}

            .hero-section {{
                display: grid;
                grid-template-columns: 1.2fr 1fr;
                gap: 4rem;
                align-items: center;
                margin-bottom: 6rem;
            }}

            .hero-content h1 {{
                font-size: 4rem;
                line-height: 1.1;
                margin-bottom: 1.5rem;
                font-weight: 800;
            }}

            .hero-content p {{
                font-size: 1.2rem;
                color: var(--text-muted);
                margin-bottom: 2.5rem;
                max-width: 500px;
            }}

            .hero-image-container {{
                position: relative;
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .hero-image {{
                width: 100%;
                display: block;
                transition: transform 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
            }}

            .hero-image-container:hover .hero-image {{
                transform: scale(1.05);
            }}

            .cta-group {{
                display: flex;
                gap: 1.5rem;
            }}

            .btn {{
                padding: 1rem 2rem;
                border-radius: 12px;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }}

            .btn-primary {{
                background: linear-gradient(90deg, var(--primary), var(--secondary));
                color: white;
                box-shadow: 0 10px 20px rgba(138, 43, 226, 0.3);
            }}

            .btn-primary:hover {{
                transform: translateY(-3px);
                box-shadow: 0 15px 30px rgba(138, 43, 226, 0.5);
            }}

            .btn-secondary {{
                background: var(--card-bg);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
            }}

            .btn-secondary:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.3);
            }}

            .tasks-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 2rem;
                margin-bottom: 6rem;
            }}

            .task-card {{
                background: var(--card-bg);
                padding: 2rem;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }}

            .task-card:hover {{
                border-color: var(--primary);
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.08);
            }}

            .difficulty-tag {{
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: 0.3rem 0.8rem;
                border-radius: 4px;
                margin-bottom: 1rem;
                display: inline-block;
            }}

            .easy {{ background: rgba(0, 255, 136, 0.1); color: #00ff88; }}
            .medium {{ background: rgba(255, 187, 0, 0.1); color: #ffbb00; }}
            .hard {{ background: rgba(255, 60, 0, 0.1); color: #ff3c00; }}

            .task-card h3 {{
                font-size: 1.4rem;
                margin-bottom: 0.8rem;
            }}

            .task-card p {{
                color: var(--text-muted);
                font-size: 0.95rem;
            }}

            footer {{
                text-align: center;
                padding: 4rem 0;
                color: var(--text-muted);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}


            /* Dashboard Layout Core */
            .dashboard-container {{
                display: none;
                margin-top: 4rem;
                scroll-margin-top: 2rem;
            }}

            .dashboard-layout {{
                display: grid;
                grid-template-columns: 1fr 350px;
                gap: 1.5rem;
                height: 700px;
                margin-bottom: 2rem;
            }}

            .map-container {{
                background: #0f172a;
                border-radius: 20px;
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            }}

            #city-grid {{
                width: 100%;
                height: 100%;
                display: block;
            }}

            .sidebar {{
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                height: 100%;
            }}

            .sidebar-card {{
                background: var(--card-bg);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
            }}

            .mission-stats-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-top: 1rem;
            }}

            .stat-box {{
                background: rgba(255, 255, 255, 0.03);
                padding: 0.8rem;
                border-radius: 12px;
                text-align: center;
            }}

            .stat-box label {{
                display: block;
                font-size: 0.7rem;
                color: var(--text-muted);
                text-transform: uppercase;
                margin-bottom: 0.2rem;
            }}

            .stat-box span {{
                font-size: 1.1rem;
                font-weight: 800;
                color: var(--accent);
            }}

            .performance-chart-container {{
                margin-top: 1rem;
                width: 100%;
                height: 80px;
                background: rgba(0, 0, 0, 0.4);
                border-radius: 8px;
                padding: 4px;
            }}

            #performance-chart {{
                width: 100%;
                height: 100%;
            }}

            .log-container {{
                flex-grow: 1;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.8rem;
                padding: 1rem;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
                max-height: 480px;
            }}

            .control-bar {{
                display: flex;
                gap: 1rem;
                justify-content: center;
                margin-bottom: 4rem;
            }}

            .map-overlay {{
                position: absolute;
                top: 1rem;
                left: 1rem;
                z-index: 10;
                pointer-events: none;
            }}

            .map-badge {{
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(8px);
                padding: 0.5rem 1rem;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 0.8rem;
                font-weight: 600;
            }}

            .legend-v2 {{
                position: absolute;
                bottom: 1rem;
                right: 1rem;
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(8px);
                padding: 0.8rem;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                font-size: 0.75rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            .legend-item-v2 {{ display: flex; align-items: center; gap: 0.5rem; }}
            .legend-icon {{ width: 12px; height: 12px; border-radius: 3px; }}

            .btn-warning {{
                background: var(--warning);
                color: black;
            }}

            /* Responsive Scaling */
            @media (max-width: 1024px) {{
                .dashboard-layout {{
                    grid-template-columns: 1fr;
                    height: auto;
                }}
                .map-container {{
                    height: 500px;
                }}
            }}

            @media (max-width: 968px) {{
                .hero-section {{ grid-template-columns: 1fr; text-align: center; }}
                .hero-content {{ order: 2; }}
                .hero-image-container {{ order: 1; }}
                .hero-content h1 {{ font-size: 3rem; }}
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
                            <div class="legend-item-v2"><span class="legend-icon" style="background: var(--primary);"></span> Restaurant</div>
                            <div class="legend-item-v2"><span class="legend-icon" style="background: var(--accent);"></span> Delivery Driver</div>
                            <div class="legend-item-v2"><span class="legend-icon" style="background: #fbbf24;"></span> Order Pickup</div>
                            <div class="legend-item-v2"><span class="legend-icon" style="background: var(--success);"></span> Delivery Target</div>
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
            let lastFrameTime = performance.now();
            
            // Ambient Traffic Simulation (Visual Only)
            const ambientTraffic = [];
            const numTrafficCars = 15;
            
            for (let i = 0; i < numTrafficCars; i++) {{
                const isHorizontal = Math.random() > 0.5;
                ambientTraffic.push({{
                    id: `traffic-${{i}}`,
                    horizontal: isHorizontal,
                    pos: Math.random() * gridSize,
                    lane: Math.floor(Math.random() * gridSize),
                    speed: 0.05 + Math.random() * 0.1,
                    color: ['#475569', '#334155', '#1e293b', '#94a3b8'][Math.floor(Math.random() * 4)]
                }});
            }}

            // Reward History for Chart
            let rewardHistory = [];
            const chartCanvas = document.getElementById('performance-chart');
            const chartCtx = chartCanvas ? chartCanvas.getContext('2d') : null;

            const varColors = {{
                primary: '#8a2be2',
                accent: '#00f2ff',
                success: '#10b981',
                bg: '#0f172a'
            }};

            function updatePerformanceChart() {{
                if (!chartCtx || rewardHistory.length < 2) return;
                const w = chartCanvas.width = chartCanvas.offsetWidth;
                const h = chartCanvas.height = chartCanvas.offsetHeight;
                
                chartCtx.clearRect(0, 0, w, h);
                chartCtx.strokeStyle = varColors.accent;
                chartCtx.lineWidth = 2;
                chartCtx.beginPath();
                
                const maxReward = Math.max(...rewardHistory, 0.1);
                const minReward = Math.min(...rewardHistory, -0.1);
                const range = maxReward - minReward;
                
                rewardHistory.forEach((r, i) => {{
                    const x = (i / (rewardHistory.length - 1)) * w;
                    const y = h - ((r - minReward) / range) * h;
                    if (i === 0) chartCtx.moveTo(x, y);
                    else chartCtx.lineTo(x, y);
                }});
                chartCtx.stroke();
                
                // Area fill
                chartCtx.lineTo(w, h);
                chartCtx.lineTo(0, h);
                chartCtx.fillStyle = `${{varColors.accent}}22`;
                chartCtx.fill();
            }}

            function log(msg, color = '#b0b0b0') {{
                const consoleOutput = document.getElementById('log-console');
                const entry = document.createElement('div');
                entry.className = 'log-entry';
                entry.style.color = color;
                entry.textContent = `> ${{msg}}`;
                consoleOutput.appendChild(entry);
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }}

            function updateStats(obs) {{
                document.getElementById('stat-status').textContent = obs.done ? 'Finished' : 'Active';
                document.getElementById('stat-reward').textContent = (obs.reward || 0).toFixed(4);
                document.getElementById('stat-score').textContent = (obs.score || 0).toFixed(2);
                
                const delivered = obs.metrics?.delivered ?? 0;
                const total = obs.metrics?.total_orders ?? 0;
                document.getElementById('stat-delivered').textContent = `${{delivered}}/${{total}}`;
                
                rewardHistory.push(obs.reward || 0);
                if (rewardHistory.length > 50) rewardHistory.shift();
                updatePerformanceChart();

                document.getElementById('time-step-badge').textContent = `TIME STEP: ${{obs.time_step}}`;
                
                if (obs.action_message) log(obs.action_message, '#00f2ff');
                if (obs.hints && obs.hints.length > 0) log(`Hint: ${{obs.hints[0]}}`, '#facc15');
                
                if (obs.done) log('MISSION ACCOMPLISHED.', varColors.success);
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

                    // 1. Cyber-Tactical Background with Depth
                    const cycle = (currentObs.time_step % 100) / 100;
                    const bgGrad = ctx.createRadialGradient(width/2, height/2, 0, width/2, height/2, width);
                    bgGrad.addColorStop(0, '#0f172a');
                    bgGrad.addColorStop(1, '#020617');
                    ctx.fillStyle = bgGrad;
                    ctx.fillRect(0, 0, width, height);

                    // Celestial Particles (Subtle)
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
                    for(let i=0; i<30; i++) {{
                        const sx = (i * 137.5) % width;
                        const sy = (i * 223.1) % height;
                        ctx.beginPath();
                        ctx.arc(sx, sy, 0.5, 0, Math.PI*2);
                        ctx.fill();
                    }}

                    // 2. High-Tech Grid with Glow
                    ctx.strokeStyle = 'rgba(0, 242, 255, 0.08)';
                    ctx.lineWidth = 1;
                    ctx.shadowBlur = 0;
                    for (let i = 0; i <= gridSize; i++) {{
                        ctx.beginPath();
                        ctx.moveTo(i * cellSize, 0); ctx.lineTo(i * cellSize, height);
                        ctx.moveTo(0, i * cellSize); ctx.lineTo(width, i * cellSize);
                        ctx.stroke();
                    }}
                    
                    // Scanline Effect
                    const scanPos = (Date.now() / 20) % height;
                    ctx.fillStyle = 'rgba(0, 242, 255, 0.02)';
                    ctx.fillRect(0, scanPos, width, 2);

                    // 3. Road Network (Dark Matte)
                    ctx.fillStyle = '#1e293b';
                    const roadWidth = cellSize * 0.45;
                    for (let i = 0; i < gridSize; i++) {{
                        ctx.fillRect(i * cellSize + (cellSize - roadWidth)/2, 0, roadWidth, height);
                        ctx.fillRect(0, i * cellSize + (cellSize - roadWidth)/2, width, roadWidth);
                    }}

                    ctx.globalCompositeOperation = 'lighter';
                    
                    // 3. Draw Ambient Traffic (Live Traffic)
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
                        
                        ctx.shadowBlur = 10;
                        ctx.shadowColor = car.color;
                        ctx.fillStyle = car.color;
                        ctx.beginPath();
                        ctx.arc(tx, ty, 3, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // Headlights
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
                        if (car.horizontal) ctx.fillRect(tx + 4, ty - 2, 6, 1);
                        else ctx.fillRect(tx - 1, ty + 4, 1, 6);
                    }});
                    ctx.shadowBlur = 0;

                // 4. Draw Interactive Traffic Zone (High-Congestion Area)
                if (currentObs.metadata && (currentObs.metadata.task_id === 'hard_2' || currentObs.metadata.task_id === 'hard_1')) {{
                    const pulse = (Math.sin(Date.now() / 500) + 1) / 2;
                    ctx.fillStyle = `rgba(239, 68, 68, ${{0.1 + pulse * 0.1}})`;
                    ctx.fillRect(8 * cellSize, 0, 4 * cellSize, height);
                    ctx.strokeStyle = '#ef4444';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([10, 5]);
                    ctx.strokeRect(8 * cellSize, 0, 4 * cellSize, height);
                    ctx.setLineDash([]);
                    
                    ctx.font = 'bold 12px Outfit';
                    ctx.fillStyle = '#ef4444';
                    ctx.textAlign = 'center';
                    ctx.fillText('CRITICAL CONGESTION', 10 * cellSize, 30);
                }}

                // 5. Draw Restaurants (Neon Hubs)
                currentObs.restaurants.forEach(r => {{
                    const x = r.location.x * cellSize + cellSize/2;
                    const y = r.location.y * cellSize + cellSize/2;
                    drawMarker(x, y, '🏪', r.name || r.id, varColors.primary, 24, true);
                }});

                // 6. Draw Delivery Targets (Glowing Endpoints)
                currentObs.orders.forEach(o => {{
                    if (o.status !== 'delivered' && o.status !== 'cancelled') {{
                        const x = o.delivery_location.x * cellSize + cellSize/2;
                        const y = o.delivery_location.y * cellSize + cellSize/2;
                        drawMarker(x, y, '🏠', `TARGET: ${{o.id}}`, '#10b981', 18, true);

                        if (['pending', 'preparing', 'assigned'].includes(o.status)) {{
                            const px = o.pickup_location.x * cellSize + cellSize/2;
                            const py = o.pickup_location.y * cellSize + cellSize/2;
                            drawMarker(px, py, '🍕', `PICKUP`, '#f59e0b', 18, true);
                        }}
                    }}
                }});

                // 6. Draw Drivers with Interpolation
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

                    // Draw Path
                    if (d.status !== 'idle' && d.status !== 'offline') {{
                        const order = currentObs.orders.find(o => o.id === d.current_order_id);
                        if (order) {{
                            const isPickingUp = (d.status.includes('restaurant') || d.status.includes('picking'));
                            const target = isPickingUp ? order.pickup_location : order.delivery_location;
                            const tx = target.x * cellSize + cellSize/2;
                            const ty = target.y * cellSize + cellSize/2;

                            ctx.strokeStyle = isPickingUp ? varColors.accent : varColors.success;
                            ctx.lineWidth = 2;
                            ctx.setLineDash([5, 5]);
                            ctx.beginPath();
                            ctx.moveTo(cx, cy);
                            ctx.lineTo(tx, ty);
                            ctx.stroke();
                            ctx.setLineDash([]);
                        }}
                    }}

                    const icon = d.status === 'offline' ? '💤' : '🛵';
                    drawMarker(cx, cy, icon, d.id, varColors.accent, 26, d.status !== 'idle');
                }});

                    // Advance animation
                    if (transitionFactor < 1.0) {{
                        transitionFactor += 0.05; 
                    }}
                }} catch (e) {{
                    console.error('Render error:', e);
                }}
            }}

            function drawMarker(x, y, icon, label, color, size, pulse = false) {{
                const floatY = Math.sin(Date.now() / 400) * 4;
                const finalY = y + floatY;

                if (pulse) {{
                    const p = (Math.sin(Date.now() / 250) + 1) / 2;
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = color;
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(x, finalY, size * (1 + p * 0.3), 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.shadowBlur = 0;
                }}

                ctx.font = `${{size}}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'white';
                ctx.fillText(icon, x, finalY);

                ctx.font = 'bold 11px Outfit';
                ctx.fillStyle = color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = color;
                ctx.fillText(label, x, finalY + size/1.1);
                ctx.shadowBlur = 0;
            }}

            async function launchTask(taskId) {{
                currentTaskId = taskId;
                rewardHistory = [];
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('dashboard').scrollIntoView({{ behavior: 'smooth' }});
                
                log(`Tactical Link Initiating: ${{taskId}}...`, varColors.primary);
                
                // Use only WebSocket for initialization to prevent double-reset
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
                    log('Intelligent Tracking System Active.', '#10b981');
                    autoInterval = setInterval(() => {{
                        if (socket && socket.readyState === WebSocket.OPEN) {{
                            socket.send(JSON.stringify({{ type: 'auto_step', task_id: currentTaskId }}));
                        }}
                    }}, 250); // Increased speed
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
                    log('System engaging Auto-Pilot.', '#f59e0b');
                    autoInterval = setInterval(() => {{
                        document.getElementById('btn-step').click();
                    }}, 250); // Increased speed
                }}
            }};

            document.getElementById('btn-stop').onclick = () => {{
                if (autoInterval) document.getElementById('btn-auto').click();
            }};

            // Start Animation Loop
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
def reset(req: ResetRequest):
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
