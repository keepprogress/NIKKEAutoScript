#!/usr/bin/env python3
"""
Multi-User Launcher for NIKKEAutoScript
Runs two GUI instances side by side in a single browser window
"""

import multiprocessing
import subprocess
import time
import webbrowser
import os
import sys
import signal

def run_gui_for_user(user_num):
    """Run GUI instance for specific user"""
    if user_num == 1:
        cmd = [sys.executable, 'gui_user1.py']
        port = 12271
    else:
        cmd = [sys.executable, 'gui_user2.py']
        port = 12272
    
    print(f"Starting User {user_num} GUI on port {port}...")
    process = subprocess.Popen(cmd)
    return process

def create_dashboard():
    """Create an HTML dashboard showing both GUIs side by side"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>NIKKE Multi-User Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0f0f0f;
            color: #ffffff;
            overflow: hidden;
            height: 100vh;
        }
        
        .header {
            background: linear-gradient(90deg, #4a148c 0%, #7b1fa2 100%);
            padding: 12px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
            position: relative;
            z-index: 100;
        }
        
        .header h1 {
            font-size: 20px;
            font-weight: 600;
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .container {
            display: flex;
            height: calc(100vh - 44px);
            position: relative;
        }
        
        .user-frame {
            flex: 1;
            position: relative;
            background-color: #1a1a1a;
        }
        
        .user-frame:first-child {
            border-right: 2px solid #2a2a2a;
        }
        
        .user-info {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 50;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(10px);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .user-1 .user-info { 
            background: linear-gradient(135deg, rgba(76,175,80,0.9), rgba(67,160,71,0.9)); 
        }
        
        .user-2 .user-info { 
            background: linear-gradient(135deg, rgba(255,152,0,0.9), rgba(251,140,0,0.9)); 
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #00ff00;
            box-shadow: 0 0 10px rgba(0,255,0,0.5);
        }
        
        iframe {
            width: 100%;
            height: 100%;
            border: none;
            background-color: #ffffff;
        }
        
        .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #888;
        }
        
        .spinner {
            border: 3px solid rgba(255,255,255,0.1);
            border-radius: 50%;
            border-top: 3px solid #7b1fa2;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            color: #ff5252;
            padding: 20px;
            text-align: center;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .container { flex-direction: column; }
            .user-frame:first-child { 
                border-right: none; 
                border-bottom: 2px solid #2a2a2a;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎮 NIKKE AutoScript - Multi-User Dashboard</h1>
    </div>
    
    <div class="container">
        <div class="user-frame user-1">
            <div class="user-info">
                <div class="status-dot"></div>
                <span><strong>User 1</strong> • Port 12271 • Schedule: 13:00</span>
            </div>
            <div class="loading" id="loading1">
                <div class="spinner"></div>
                <div>Connecting to User 1...</div>
            </div>
            <iframe 
                id="frame1"
                src="http://localhost:12271" 
                onload="hideLoading(1)"
                onerror="showError(1)"
            ></iframe>
        </div>
        
        <div class="user-frame user-2">
            <div class="user-info">
                <div class="status-dot"></div>
                <span><strong>User 2</strong> • Port 12272 • Schedule: 14:00</span>
            </div>
            <div class="loading" id="loading2">
                <div class="spinner"></div>
                <div>Connecting to User 2...</div>
            </div>
            <iframe 
                id="frame2"
                src="http://localhost:12272" 
                onload="hideLoading(2)"
                onerror="showError(2)"
            ></iframe>
        </div>
    </div>
    
    <script>
        let retryCount = {1: 0, 2: 0};
        const maxRetries = 10;
        
        function hideLoading(user) {
            document.getElementById('loading' + user).style.display = 'none';
        }
        
        function showError(user) {
            const loading = document.getElementById('loading' + user);
            if (retryCount[user] < maxRetries) {
                retryCount[user]++;
                loading.innerHTML = `
                    <div class="spinner"></div>
                    <div>Waiting for User ${user} GUI to start... (${retryCount[user]}/${maxRetries})</div>
                `;
                setTimeout(() => {
                    document.getElementById('frame' + user).src = 
                        document.getElementById('frame' + user).src;
                }, 2000);
            } else {
                loading.innerHTML = `
                    <div class="error">
                        Failed to connect to User ${user} GUI<br>
                        Please check if port ${user === 1 ? '12271' : '12272'} is accessible
                    </div>
                `;
            }
        }
        
        // Initial retry after 3 seconds
        setTimeout(() => {
            if (document.getElementById('loading1').style.display !== 'none') {
                showError(1);
            }
            if (document.getElementById('loading2').style.display !== 'none') {
                showError(2);
            }
        }, 3000);
    </script>
</body>
</html>
"""
    
    filename = 'nikke_multi_user_dashboard.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return os.path.abspath(filename)

def main():
    print("╔════════════════════════════════════════════════╗")
    print("║       NIKKE AutoScript Multi-User Launcher     ║")
    print("╠════════════════════════════════════════════════╣")
    print("║  User 1: localhost:12271 (config/nkas.json)    ║")
    print("║  User 2: localhost:12272 (config/nkas_user2.json) ║")
    print("╚════════════════════════════════════════════════╝\n")
    
    # Store process references
    processes = []
    
    try:
        # Start User 1 GUI
        print("🚀 Starting User 1 GUI on port 12271...")
        p1 = run_gui_for_user(1)
        processes.append(p1)
        
        # Small delay between starts
        time.sleep(2)
        
        # Start User 2 GUI
        print("🚀 Starting User 2 GUI on port 12272...")
        p2 = run_gui_for_user(2)
        processes.append(p2)
        
        # Create and open dashboard
        print("\n📝 Creating multi-user dashboard...")
        dashboard_path = create_dashboard()
        
        # Wait for GUIs to initialize
        print("⏳ Waiting for GUIs to initialize...")
        time.sleep(5)
        
        # Open dashboard
        print(f"\n🌐 Opening dashboard in browser...")
        print(f"   URL: file:///{dashboard_path}")
        webbrowser.open(f'file:///{dashboard_path}')
        
        print("\n✅ Multi-User Dashboard is running!")
        print("\n📌 Instructions:")
        print("   - Each user has their own GUI instance")
        print("   - Configure User 1 in the left panel")
        print("   - Configure User 2 in the right panel")
        print("   - User 2 tasks run 1 hour after User 1")
        print("\n⚠️  Press Ctrl+C to stop all instances\n")
        
        # Wait for processes
        for p in processes:
            p.wait()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        for i, p in enumerate(processes):
            print(f"   Stopping User {i+1} GUI...")
            p.terminate()
            p.wait()
        print("\n✅ All instances stopped successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for p in processes:
            if p.poll() is None:
                p.terminate()

if __name__ == '__main__':
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()