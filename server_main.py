from concurrent.futures import thread
from flask import Flask , request , jsonify, render_template
from flask_cors import CORS 
import subprocess
import threading



app =  Flask(__name__)

@app.route('/')
def home():
    return render_template("steps.html")

def hosho():
    process = subprocess.Popen(["python" , "hosho.py"],
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE , text=True
    )

    
    # std means standard output
    for line in process.stdout:
        print(f"[output] {line}" , end="")
    for line in process.stderr:
        print(f"[error] {line}" , end="")



def mbira():
    subprocess.run(["python" , "mbira.py"])
 
 
@app.route('/start')  # the front-end is supposed to actuallymake a post request to the /start

def run_script():
    thread = threading.Thread(target=hosho , daemon=True)

    thread.start()
    return jsonify(
        {"status" : "Recording has started"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',
    port=5000)
    
    
    




