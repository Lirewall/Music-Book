from concurrent.futures import thread
from fileinput import filename
from flask import Flask , request , jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS 

import subprocess
import threading

# libs for file detection
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app =  Flask(__name__)

USB_path = 'files_sent'

class USBHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"New file detected: {event.src_path}")

observer = Observer()
observer.schedule(USBHandler(), path=USB_path, recursive=False)
observer.start()

@app.route('/')
def home():
    return render_template("web.html")

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
 

@app.route('/steps')
def steps():
    return render_template("steps.html")
    
@app.route('/vedios')
def videos():
    return render_template("vedio.html")
 
@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(USB_path , filename)

    return send_file(filepath)


@app.route('/start')  # the front-end is supposed to actuallymake a post request to the /start

def run_script():
    thread = threading.Thread(target=hosho , daemon=True)

    thread.start()
    return jsonify(
        {"status" : "Recording has started"}), 200


if __name__ == '__main__':
    try: 
        app.run(host='0.0.0.0',
        port=5000)
    finally:
        observer.stop()
        observer.join()
    
    




