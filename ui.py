from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloudflare Bypasser UI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { 
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #eee;
        }
        .tab {
            padding: 12px 24px;
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.2s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            font-family: 'Monaco', 'Menlo', monospace;
            resize: vertical;
            min-height: 100px;
        }
        button {
            padding: 14px 28px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .result h3 {
            margin-bottom: 10px;
            color: #333;
            font-size: 16px;
        }
        pre {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            color: #e74c3c;
            background: #fee;
            padding: 12px;
            border-radius: 6px;
            margin-top: 10px;
        }
        .header-input {
            display: grid;
            grid-template-columns: 1fr 2fr auto;
            gap: 10px;
            margin-bottom: 10px;
        }
        .add-header {
            background: #10b981;
            padding: 8px 16px;
            font-size: 14px;
        }
        .remove-header {
            background: #ef4444;
            padding: 8px 12px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>☁️ Cloudflare Bypasser</h1>
        <div class="subtitle">Bypass Cloudflare protection with ease</div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('cookies')">Get Cookies</button>
            <button class="tab" onclick="switchTab('html')">Get HTML</button>
            <button class="tab" onclick="switchTab('mirror')">Mirror Request</button>
        </div>
        
        <!-- Cookies Tab -->
        <div id="cookies-tab" class="tab-content active">
            <div class="form-group">
                <label>Target URL</label>
                <input type="url" id="cookies-url" placeholder="https://example.com" required>
            </div>
            <div class="form-group">
                <label>Proxy (Optional)</label>
                <input type="text" id="cookies-proxy" placeholder="http://user:pass@proxy:port">
            </div>
            <button onclick="getCookies()">Get Cookies <span id="cookies-loading" class="loading" style="display:none"></span></button>
            <div id="cookies-result"></div>
        </div>
        
        <!-- HTML Tab -->
        <div id="html-tab" class="tab-content">
            <div class="form-group">
                <label>Target URL</label>
                <input type="url" id="html-url" placeholder="https://example.com" required>
            </div>
            <div class="form-group">
                <label>Proxy (Optional)</label>
                <input type="text" id="html-proxy" placeholder="http://user:pass@proxy:port">
            </div>
            <button onclick="getHTML()">Get HTML <span id="html-loading" class="loading" style="display:none"></span></button>
            <div id="html-result"></div>
        </div>
        
        <!-- Mirror Tab -->
        <div id="mirror-tab" class="tab-content">
            <div class="form-group">
                <label>Endpoint Path</label>
                <input type="text" id="mirror-path" placeholder="/api/data" required>
            </div>
            <div class="form-group">
                <label>HTTP Method</label>
                <select id="mirror-method">
                    <option>GET</option>
                    <option>POST</option>
                    <option>PUT</option>
                    <option>DELETE</option>
                    <option>PATCH</option>
                </select>
            </div>
            <div class="form-group">
                <label>Target Hostname</label>
                <input type="text" id="mirror-hostname" placeholder="example.com" required>
            </div>
            <div class="form-group">
                <label>Headers</label>
                <div id="headers-container">
                    <div class="header-input">
                        <input type="text" placeholder="Header name" class="header-name">
                        <input type="text" placeholder="Header value" class="header-value">
                        <button class="remove-header" onclick="removeHeader(this)" style="display:none">×</button>
                    </div>
                </div>
                <button class="add-header" onclick="addHeader()">+ Add Header</button>
            </div>
            <div class="form-group">
                <label>Request Body (JSON, optional)</label>
                <textarea id="mirror-body" placeholder='{"key": "value"}'></textarea>
            </div>
            <button onclick="mirrorRequest()">Send Request <span id="mirror-loading" class="loading" style="display:none"></span></button>
            <div id="mirror-result"></div>
        </div>
    </div>
    
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }
        
        function addHeader() {
            const container = document.getElementById('headers-container');
            const div = document.createElement('div');
            div.className = 'header-input';
            div.innerHTML = `
                <input type="text" placeholder="Header name" class="header-name">
                <input type="text" placeholder="Header value" class="header-value">
                <button class="remove-header" onclick="removeHeader(this)">×</button>
            `;
            container.appendChild(div);
        }
        
        function removeHeader(btn) {
            btn.parentElement.remove();
        }
        
        async function getCookies() {
            const url = document.getElementById('cookies-url').value;
            const proxy = document.getElementById('cookies-proxy').value;
            const loading = document.getElementById('cookies-loading');
            const result = document.getElementById('cookies-result');
            
            if (!url) {
                result.innerHTML = '<div class="error">Please enter a URL</div>';
                return;
            }
            
            loading.style.display = 'inline-block';
            result.innerHTML = '';
            
            try {
                let endpoint = `/cookies?url=${encodeURIComponent(url)}`;
                if (proxy) endpoint += `&proxy=${encodeURIComponent(proxy)}`;
                
                const response = await fetch(endpoint);
                const data = await response.json();
                
                result.innerHTML = `
                    <div class="result">
                        <h3>✓ Cookies Retrieved</h3>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            } catch (error) {
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            } finally {
                loading.style.display = 'none';
            }
        }
        
        async function getHTML() {
            const url = document.getElementById('html-url').value;
            const proxy = document.getElementById('html-proxy').value;
            const loading = document.getElementById('html-loading');
            const result = document.getElementById('html-result');
            
            if (!url) {
                result.innerHTML = '<div class="error">Please enter a URL</div>';
                return;
            }
            
            loading.style.display = 'inline-block';
            result.innerHTML = '';
            
            try {
                let endpoint = `/html?url=${encodeURIComponent(url)}`;
                if (proxy) endpoint += `&proxy=${encodeURIComponent(proxy)}`;
                
                const response = await fetch(endpoint);
                const html = await response.text();
                
                result.innerHTML = `
                    <div class="result">
                        <h3>✓ HTML Retrieved (${html.length} characters)</h3>
                        <pre>${html.substring(0, 1000)}...</pre>
                    </div>
                `;
            } catch (error) {
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            } finally {
                loading.style.display = 'none';
            }
        }
        
        async function mirrorRequest() {
            const path = document.getElementById('mirror-path').value;
            const method = document.getElementById('mirror-method').value;
            const hostname = document.getElementById('mirror-hostname').value;
            const body = document.getElementById('mirror-body').value;
            const loading = document.getElementById('mirror-loading');
            const result = document.getElementById('mirror-result');
            
            if (!path || !hostname) {
                result.innerHTML = '<div class="error">Please enter path and hostname</div>';
                return;
            }
            
            loading.style.display = 'inline-block';
            result.innerHTML = '';
            
            try {
                const headers = {'x-hostname': hostname};
                
                // Collect custom headers
                document.querySelectorAll('.header-input').forEach(div => {
                    const name = div.querySelector('.header-name').value.trim();
                    const value = div.querySelector('.header-value').value.trim();
                    if (name && value) headers[name] = value;
                });
                
                const options = {
                    method: method,
                    headers: headers
                };
                
                if (body && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
                    options.headers['Content-Type'] = 'application/json';
                    options.body = body;
                }
                
                const response = await fetch(path, options);
                const data = await response.text();
                
                result.innerHTML = `
                    <div class="result">
                        <h3>✓ Response (${response.status} ${response.statusText})</h3>
                        <pre>${data.substring(0, 2000)}${data.length > 2000 ? '...' : ''}</pre>
                    </div>
                `;
            } catch (error) {
                result.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            } finally {
                loading.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Proxy all other requests to the main server
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    url = f
