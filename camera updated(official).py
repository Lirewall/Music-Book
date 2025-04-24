import picamera
import time
import subprocess

# Initialize the camera
camera = picamera.PiCamera()

camera.start_preview(fullscreen=False, window=(100, 100, 640, 480))
print("Camera preview started...")
time.sleep(3)

video_filename = None

def start_recording():
    global video_filename
    name = input("Enter name of song: ").strip()
    video_filename = f"{name}.h264"  # Corrected file extension
    camera.start_recording(video_filename)
    print(f"Recording started... Saving video as {video_filename}")

def stop_recording():
    global video_filename
    camera.stop_recording()
    print("Recording stopped.")

    if not video_filename:
        print("No recording found to convert.")
        return

    # Convert the video file using ffmpeg
    output_file = video_filename.replace('.h264', '.mp4')  # Dynamically change extension
    command = [
        "ffmpeg",
        "-probesize", "50M",           # Increase stream analysis for short clips
        "-fflags", "+genpts",          # Add timestamps
        "-i", video_filename,          # Input file
        "-c:v", "copy",                # Copy video codec without re-encoding
        output_file                    # Output file
    ]
    subprocess.run(command)

    print(f"Converted {video_filename} to {output_file} successfully!")

while True:
    command = input("Enter 'start' to begin recording, 'stop' to end recording, or 'exit' to quit: ").strip().lower()

    if command == "start":
        start_recording()
    elif command == "stop":
        stop_recording()
    elif command == "exit":
        break
    else:
        print("Invalid command. Please enter 'start', 'stop', or 'exit'.")

camera.close()
