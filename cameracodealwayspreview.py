import picamera
import time

# Initialize the camera
camera = picamera.PiCamera()

camera.start_preview(fullscreen=False,window=(100,100,640,480))
print("Camera preview started...")
time.sleep(3)
    
def start_recording():
    name = input("Enter name of song")
    video_filename=f"{name}.h246"
    camera.start_recording("{video_filename}")
    print(f"Recording started...Saving video as{video_filename}")

def stop_recording():
    camera.stop_recording()
    print("Recording stopped.")

# Example usage
while True:
    command = input("Enter 'start' to begin recording, 'stop' to end recording, or 'exit' to quit: ").strip().lower()
    
    if command == "start":
        start_recording()
    elif command == "stop":
        stop_recording()
    elif command == "exit":
        break
    else:
        print("Invalid command. Please enter 'preview', 'stop_preview', 'start', 'stop', or 'exit'.")

camera.close()

