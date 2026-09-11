# camera_api.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import signal
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store running processes
processes = {}

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent

@app.route('/status', methods=['GET'])
def status():
    """Check if camera modules are running"""
    return jsonify({
        'squat_running': 'squat' in processes and processes['squat'].poll() is None,
        'sitting_running': 'sitting' in processes and processes['sitting'].poll() is None
    })

@app.route('/start-squat', methods=['POST'])
def start_squat():
    """Start squat detection module"""
    try:
        # Check if already running
        if 'squat' in processes and processes['squat'].poll() is None:
            return jsonify({
                'success': False,
                'message': 'Squat detection already running'
            })
        
        # Kill any existing process
        if 'squat' in processes:
            processes['squat'].kill()
        
        # Start new process
        script_path = BACKEND_DIR / 'posture' / 'live_posture_detection.py'
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(BACKEND_DIR)
        )
        processes['squat'] = process
        
        return jsonify({
            'success': True,
            'message': 'Squat detection started'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/start-sitting', methods=['POST'])
def start_sitting():
    """Start sitting posture detection module"""
    try:
        # Check if already running
        if 'sitting' in processes and processes['sitting'].poll() is None:
            return jsonify({
                'success': False,
                'message': 'Sitting detection already running'
            })
        
        # Kill any existing process
        if 'sitting' in processes:
            processes['sitting'].kill()
        
        # Start new process
        script_path = BACKEND_DIR / 'sitting_posture_module' / 'live_sitting_posture.py'
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(BACKEND_DIR)
        )
        processes['sitting'] = process
        
        return jsonify({
            'success': True,
            'message': 'Sitting detection started'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/stop-all', methods=['POST'])
def stop_all():
    """Stop all running camera modules"""
    try:
        for key, process in processes.items():
            if process.poll() is None:
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:  # Linux/Mac
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        
        processes.clear()
        return jsonify({
            'success': True,
            'message': 'All modules stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/stop/<module>', methods=['POST'])
def stop_module(module):
    """Stop specific module (squat or sitting)"""
    try:
        if module in processes and processes[module].poll() is None:
            if os.name == 'nt':  # Windows
                processes[module].terminate()
            else:  # Linux/Mac
                os.killpg(os.getpgid(processes[module].pid), signal.SIGTERM)
            del processes[module]
            return jsonify({
                'success': True,
                'message': f'{module} module stopped'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'{module} module not running'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    print("🚀 Camera API Server Starting...")
    print(f"📁 Backend directory: {BACKEND_DIR}")
    print("📍 Available endpoints:")
    print("   POST /start-squat   - Start squat detection")
    print("   POST /start-sitting  - Start sitting detection")
    print("   POST /stop-all       - Stop all modules")
    print("   GET  /status         - Check running modules")
    print("\n🌐 Server running at: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)