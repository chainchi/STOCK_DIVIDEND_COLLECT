from flask import Flask, render_template, request, jsonify
import subprocess
import os
import shlex

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_script():
    try:
        args_str = request.json.get('args', '')
        print(f"DEBUG: Received request with args: {args_str}")
        
        # Base command
        command = ['python', '-u', 'chatgpt_stock_dividend_collect.py'] # -u for unbuffered output
        
        # Use shlex to handle quotes correctly (posix=False preserves backslashes for Windows)
        user_args = shlex.split(args_str, posix=False)
        full_command = command + user_args
        
        cwd = os.getcwd()
        print(f"DEBUG: Running in {cwd}")
        print(f"DEBUG: Full command: {full_command}")

        def generate():
            # Use Popen for streaming
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr into stdout
                cwd=cwd,
                text=False # We handle decoding manually
            )

            # Stream output
            for line in iter(process.stdout.readline, b''):
                try:
                    # Try utf-8 then cp950 (Big5) then replace
                    decoded_line = line.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        decoded_line = line.decode('cp950')
                    except:
                        decoded_line = line.decode('utf-8', errors='replace')
                
                yield decoded_line

            process.stdout.close()
            return_code = process.wait()
            
            if return_code != 0:
                yield f"\n[Process exited with error code {return_code}]"

        return app.response_class(generate(), mimetype='text/plain')

    except Exception as e:
        return jsonify({'output': f"Server Error: {str(e)}", 'status': 'error'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    if file:
        filename = file.filename
        filepath = os.path.join(os.getcwd(), filename)
        file.save(filepath)
        return jsonify({"status": "success", "filepath": os.path.abspath(filepath)})

# --- NEW EDITOR API ENDPOINTS ---

@app.route('/api/list_txt', methods=['POST']) # Changed to POST to receive path
def list_txt_files():
    data = request.json or {}
    path = data.get('path', '.')
    if not path: path = '.'
    
    try:
        if not os.path.exists(path):
            return jsonify({"status": "error", "message": "Path does not exist"}), 404
        
        files = [f for f in os.listdir(path) if f.endswith('.txt')]
        return jsonify({
            "status": "success", 
            "files": sorted(files),
            "abs_path": os.path.abspath(path)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/read_txt', methods=['POST'])
def read_txt_file():
    data = request.json
    filename = data.get('filename')
    path = data.get('path', '.')
    
    if not filename:
        return jsonify({"status": "error", "message": "No filename provided"}), 400
        
    full_path = os.path.join(path, filename)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"status": "success", "content": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/save_txt', methods=['POST'])
def save_txt_file():
    data = request.json
    filename = data.get('filename')
    path = data.get('path', '.')
    content = data.get('content', '')
    
    if not filename:
        return jsonify({"status": "error", "message": "No filename provided"}), 400
        
    try:
        # Ensure we have a clean absolute path
        target_dir = os.path.abspath(path)
        full_path = os.path.join(target_dir, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return jsonify({
            "status": "success", 
            "message": f"Saved successfully!",
            "full_path": os.path.abspath(full_path)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
