import numpy as np
import sounddevice as sd
from nbclient.client import timestamp
from scipy.signal import butter, filtfilt
print ("Notes will be saved as musicbook in your documents folder")
# Audio config
SAMPLE_RATE = 44100
CHUNK = 2048
CHANNELS = 1
FORMAT = 'float32'

# Mbira note frequencies (adju st to match your tuning)
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

# Band-pass filter: keeps 200–1000 Hz
def design_bandpass(lowcut=115, highcut=1200, fs=44100, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    return butter(order, [low, high], btype='band')

b, a = design_bandpass()

#frequency to note
def freq_to_note(freq):
    if freq == 0:
        return None
    closest_note = min(MBIRA_NOTES.items(), key=lambda x: abs(x[1] - freq))
    return f"{closest_note[0]} ({round(freq, 1)} Hz)"

# Frequency detection with noise gate + band-pass
def detect_frequency(data):
    # Noise gate: skip low-volume audio
    if np.max(np.abs(data)) < 1000:  # adjust threshold if needed
        return 0

    filtered = filtfilt(b, a, data)
    windowed = filtered * np.hanning(len(filtered))
    fft = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(filtered), 1.0 / SAMPLE_RATE)

    # Ignore very low frequencies and low energy peaks
    fft[:10] = 0  # remove low-frequency drift
    peak_idx = np.argmax(fft)
    peak_power = fft[peak_idx]
    peak_freq = freqs[peak_idx]

    
    if peak_power < 1000:
        return 0
    return peak_freq

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    data = indata[:, 0] * 32767
    freq = detect_frequency(data)
    note = freq_to_note(freq)
    if note:
        print("Detected:", note)


        with open(r"C:\Users\muket\Documents/musicbook","a") as file:
            file.write(f"{note}-\n")
        print(f"Note was saved as: {note}")


print("Listening for mbira notes with noise filtering...")
with sd.InputStream(
    samplerate=SAMPLE_RATE,
    blocksize=CHUNK,
    dtype=FORMAT,
    channels=CHANNELS,
    callback=audio_callback,
    device=26  
):
    try:
        while True:
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\nStopped.")
