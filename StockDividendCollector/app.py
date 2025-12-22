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

# --- NEW EDITOR API ENDPOINTS REMOVED (Replaced by Browser Downloads) ---

if __name__ == '__main__':
    # Get port from environment variable for Cloud Run
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
