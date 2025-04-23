import numpy as np
import sounddevice as sd
from scipy.signal import butter, filtfilt
import os
import keyboard
from datetime import datetime
import wave
import queue

# --- Configuration ---
SAMPLE_RATE = 44100
CHUNK = 2048
CHANNELS = 1
FORMAT = 'int16'
RECORDINGS_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'music_recordings')
os.makedirs(RECORDINGS_DIR, exist_ok=True)


# --- Audio Setup ---
def select_microphone():
    print("\nAvailable Audio Devices:")
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        print(f"{i}: {dev['name']} (Inputs: {dev['max_input_channels']})")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ('mic' in dev['name'].lower() or 'external' in dev['name'].lower()):
            print(f"\nAuto-selected: Device {i} - {dev['name']}")
            return i
    print("\nUsing default input device")
    return None


MIC_INDEX = select_microphone()

# --- Musical Notes ---
MBIRA_NOTES = {
    'B3': 246.94,
    'B2': 123.47,
    'C#3': 138.59,
    'D#3': 155.56,
    'E3': 164.81,
    'F#3': 185.00,
    'G#3': 207.65,
    'A3': 220.00,
    'B3': 246.94,
    'C#4': 277.18,
    'D#4': 311.13,
    'E4': 329.63,
    'F#4': 369.99,
    'G#4': 415.30,
    'A4': 440.00,
    'B4': 493.88,
    'C#5': 554.37,
    'D#5': 622.25,
    'E5': 659.25,
    'F#5': 739.99,
    'G#5': 830.61,
    'A5': 880.00
}

# --- Audio Processing ---
b, a = butter(5, [115 / (0.5 * SAMPLE_RATE), 2000 / (0.5 * SAMPLE_RATE)], btype='band')


def freq_to_note(freq):
    if freq == 0: return None
    closest = min(MBIRA_NOTES.items(), key=lambda x: abs(x[1] - freq))
    return f"{closest[0]} ({round(freq, 1)} Hz)"


def detect_frequency(data):
    if np.max(np.abs(data)) < 1000: return 0
    elif np.max(np.abs(data)) >100 : pass
    else: return 0
    filtered = filtfilt(b, a, data)
    windowed = filtered * np.hanning(len(filtered))
    fft = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(filtered), 1 / SAMPLE_RATE)
    fft[:10] = 0
    peak_idx = np.argmax(fft)
    return freqs[peak_idx] if fft[peak_idx] > 1000 else 0


# --- Recording Implementation ---
class AudioRecorder:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.recording = False
        self.stream = None
        self.current_session_files = None

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")
        if self.recording:
            self.audio_queue.put(indata.copy())
            # Detect notes in real-time
            data = indata[:, 0] * 32767
            if freq := detect_frequency(data):
                note = freq_to_note(freq)
                print(f"Detected: {note}")
                with open(self.current_session_files['notes'], 'a') as f:
                    f.write(f"{note}\n")

    def start_recording(self):
        if self.recording:
            print("Already recording!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_files = {
            'audio': os.path.join(RECORDINGS_DIR, f"recording_{timestamp}.wav"),
            'notes': os.path.join(RECORDINGS_DIR, f"notes_{timestamp}.txt")
        }

        print(f"\nRecording STARTED at {timestamp}")
        print(f"Audio will save to: {self.current_session_files['audio']}")
        print(f"Notes will save to: {self.current_session_files['notes']}")
        print("Press 's' to stop recording\n")

        self.recording = True
        self.stream = sd.InputStream(
            device=MIC_INDEX,
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK,
            channels=CHANNELS,
            dtype=FORMAT,
            callback=self.audio_callback
        )
        self.stream.start()

    def stop_recording(self):
        if not self.recording:
            print("Not currently recording!")
            return

        self.recording = False
        self.stream.stop()
        self.stream.close()

        # Save audio to file
        frames = []
        while not self.audio_queue.empty():
            frames.append(self.audio_queue.get())

        if frames:
            with wave.open(self.current_session_files['audio'], 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(np.concatenate(frames).tobytes())

            print(f"\nRecording saved:")
            print(f"- Audio: {self.current_session_files['audio']}")
            print(f"- Notes: {self.current_session_files['notes']}")
        else:
            print("\nNo audio was recorded")

        # Clear current session
        self.current_session_files = None


# --- Main Program ---
def main():
    print("=== Automatic Music Recorder ===")
    print("Controls:")
    print("  'r' - Start recording & note detection")
    print("  's' - Stop recording & save files")
    print("  'q' - Quit program")
    print(f"\nAll files save to: {RECORDINGS_DIR}\n")

    recorder = AudioRecorder()

    try:
        while True:
            if keyboard.is_pressed('r'):
                recorder.start_recording()
                while not keyboard.is_pressed('s'):
                    sd.sleep(100)
                recorder.stop_recording()
            elif keyboard.is_pressed('q'):
                print("Exiting program...")
                break
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        if recorder.recording:
            recorder.stop_recording()
        sd.stop()


if __name__ == '__main__':
    main()