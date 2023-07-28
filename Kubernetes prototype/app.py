from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def delete_job():
    cmd = ['kubectl', 'delete', 'job', 'cracking-job']
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

@app.route('/crack_bcrypt', methods=['POST'])
def crack_bcrypt():
    target_hash = request.form.get('targetHash')
    num_processes_threads = request.form.get('numProcessesThreads')
    mode = request.form.get('mode')
    wordlist_filename = request.form.get('wordlistFilename', '')  # Default value is an empty string
    cpu = request.form.get('cpu')
    memory = request.form.get('memory')
    parallelism = request.form.get('parallelism', '2')  # Default value is '2'

    if not target_hash or not mode:
        return "Error: Please fill in all the required fields.", 400

    cmd = [
        './deploy.sh',
        '-H', target_hash,
        '-N', num_processes_threads,
        '-M', mode,
    ]

    # Add optional arguments if provided
    if wordlist_filename:
        cmd.extend(['--wordlist', wordlist_filename])
    if cpu:
        cmd.extend(['--cpu', cpu])
    if memory:
        cmd.extend(['--memory', memory])
    if parallelism:
        cmd.extend(['-P', parallelism])

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            output = f"Error: {stderr}"
        else:
            output = stdout
    except Exception as e:
        output = f"Error: {e}"

    delete_job()  # Delete the job after the result is displayed

    return output

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

