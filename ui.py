from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloudflare Bypass Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e4e4e7;
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto;
        }
        header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 { 
            color: #f4f4f5;
            font-size: 28px;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .subtitle {
            color: #a1a1aa;
            font-size: 14px;
            margin-top: 5px;
        }
        .card {
            background: #0f172a;
            padding: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 16px;
            color: #3b82f6;
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #a1a1aa;
            font-size: 13px;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            padding: 12px 16px;
            background: #1e293b;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: #e4e4e7;
            font-size: 14px;
            transition: all 0.2s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        button {
            padding: 12px 24px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
        }
        button:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .result {
            background: #1e293b;
            padding: 16px;
            border-radius: 6px;
            margin-top: 16px;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #10b981;
        }
        .error {
            color: #ef4444;
        }
        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #0f172a;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px 6px 0 0;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab.active {
            background: #1e293b;
            border-bottom: 2px solid #3b82f6;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .info-box {
            background: rgba(59, 130, 246, 0.1);
            border-left: 3px solid #3b82f6;
            padding: 12px;
            margin-bottom: 16px;
            border-radius: 4px;
            font-size: 13px;
            color: #94a3b8;
        }
        .spinner {
            border: 2px solid rgba(59, 130, 246, 0.3);
            border-top: 2px solid #3b82f6;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 8px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>☁️ Cloudflare Bypass Tool</h1>
            <div class="subtitle">Bypass Cloudflare protection and extract cookies, HTML content, or mirror requests</div>
        </header>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('cookies')">Get Cookies</div>
            <div class="tab" onclick="switchTab('html')">Get HTML</div>
            <div class="tab" onclick="switchTab('mirror')">Mirror Request</div>
        </div>

        <!-- Cookies Tab -->
        <div id="cookies-tab" class="tab-content active">
            <div class="card">
                <h2>Extract Cloudflare Cookies</h2>
                <div class="info-box">
                    This endpoint extracts Cloudflare clearance cookies from a protected URL.
                </div>
                <form id="cookies-form">
                    <div class="form-group">
                        <label>Target URL</label>
                        <input type="url" id="cookies-url" placeholder="https://example.com" required>
                    </div>
                    <button type="submit" id="cookies-btn">
                        <span>Get Cookies</span>
                    </button>
                </form>
                <div id="cookies-result" class="result"></div>
            </div>
        </div>

        <!-- HTML Tab -->
        <div id="html-tab" class="tab-content">
            <div class="card">
                <h2>Extract HTML Content</h2>
                <div class="info-box">
                    This endpoint returns the full HTML content after bypassing Cloudflare protection.
                </div>
                <form id="html-form">
                    <div class="form-group">
                        <label>Target URL</label>
                        <input type="url" id="html-url" placeholder="https://example.com" required>
                    </div>
                    <button type="submit" id="html-btn">
                        <span>Get HTML</span>
                    </button>
                </form>
                <div id="html-result" class="result"></div>
            </div>
        </div>

        <!-- Mirror Tab -->
        <div id="mirror-tab" class="tab-content">
            <div class="card">
                <h2>Mirror HTTP Request</h2>
                <div class="info-box">
                    Mirror any HTTP request through the bypass server. The server will handle Cloudflare automatically.
                </div>
                <form id="mirror-form">
                    <div class="form-group">
                        <label>HTTP Method</label>
                        <select id="mirror-method">
                            <option value="GET">GET</option>
                            <option value="POST">POST</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                            <option value="PATCH">PATCH</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Target Hostname</label>
                        <input type="text" id="mirror-hostname" placeholder="example.com" required>
                    </div>
                    <div class="form-group">
                        <label>API Path</label>
                        <input type="text" id="mirror-path" placeholder="/api/data" required>
                    </div>
                    <div class="form-group">
                        <label>Request Body (JSON, optional)</label>
                        <input type="text" id="mirror-body" placeholder='{"key": "value"}'>
                    </div>
                    <div class="form-group">
                        <label>Proxy URL (optional)</label>
                        <input type="text" id="mirror-proxy" placeholder="http://user:pass@proxy:port">
                    </div>
                    <button type="submit" id="mirror-btn">
                        <span>Send Request</span>
                    </button>
                </form>
                <div id="mirror-result" class="result"></div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }

        // Cookies Form
        document.getElementById('cookies-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('cookies-btn');
            const result = document.getElementById('cookies-result');
            const url = document.getElementById('cookies-url').value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Processing...';
            result.classList.remove('show');
            
            try {
                const response = await fetch(`/api/cookies?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                
                result.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                result.classList.add('show');
            } catch (error) {
                result.innerHTML = '<pre class="error">Error: ' + error.message + '</pre>';
                result.classList.add('show');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>Get Cookies</span>';
            }
        });

        // HTML Form
        document.getElementById('html-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('html-btn');
            const result = document.getElementById('html-result');
            const url = document.getElementById('html-url').value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Processing...';
            result.classList.remove('show');
            
            try {
                const response = await fetch(`/api/html?url=${encodeURIComponent(url)}`);
                const text = await response.text();
                
                result.innerHTML = '<pre>' + text.substring(0, 2000) + (text.length > 2000 ? '\\n\\n... (truncated)' : '') + '</pre>';
                result.classList.add('show');
            } catch (error) {
                result.innerHTML = '<pre class="error">Error: ' + error.message + '</pre>';
                result.classList.add('show');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>Get HTML</span>';
            }
        });

        // Mirror Form
        document.getElementById('mirror-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('mirror-btn');
            const result = document.getElementById('mirror-result');
            
            const method = document.getElementById('mirror-method').value;
            const hostname = document.getElementById('mirror-hostname').value;
            const path = document.getElementById('mirror-path').value;
            const body = document.getElementById('mirror-body').value;
            const proxy = document.getElementById('mirror-proxy').value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Processing...';
            result.classList.remove('show');
            
            try {
                const headers = {
                    'x-hostname': hostname
                };
                if (proxy) headers['x-proxy'] = proxy;
                
                const options = {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        method,
                        path,
                        headers,
                        body: body ? JSON.parse(body) : null
                    })
                };
                
                const response = await fetch('/api/mirror', options);
                const data = await response.json();
                
                result.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                result.classList.add('show');
            } catch (error) {
                result.innerHTML = '<pre class="error">Error: ' + error.message + '</pre>';
                result.classList.add('show');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>Send Request</span>';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/cookies')
def get_cookies():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        response = requests.get(f'http://localhost:8000/cookies?url={url}')
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/html')
def get_html():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        response = requests.get(f'http://localhost:8000/html?url={url}')
        return response.text, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return str(e), 500

@app.route('/api/mirror', methods=['POST'])
def mirror_request():
    data = request.json
    method = data.get('method', 'GET')
    path = data.get('path', '/')
    headers = data.get('headers', {})
    body = data.get('body')
    
    try:
        url = f'http://localhost:8000{path}'
        response = requests.request(method, url, headers=headers, json=body)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
