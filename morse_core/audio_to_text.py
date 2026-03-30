import numpy as np
import sounddevice as sd
import time

class AudioToText:
    def __init__(self, wpm: int = 15):
        self.sample_rate = 44100
        # Time unit
        self.dot_duration = 1.2 / wpm
        # Threshold for audio volume (adjust if environment is noisy or mic is quiet)
        self.threshold = 0.05
        
        self.REVERSE_DICT = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
            '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
            '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
            '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
            '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9', '-----': '0'
        }

    def listen_and_decode(self, duration: int = 5) -> str:
        """Records audio for a given duration and attempts to extract Morse code text."""
        print(f"Began listening for {duration} seconds... (Speak/Play Morse audio now)")
        
        # Record microphone input
        recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
        sd.wait()
        print("Processing audio...")
        
        # Calculate amplitude envelope
        envelope = np.abs(recording[:, 0])
        
        # Smooth envelope using a moving average window (50ms)
        window_size = int(self.sample_rate * 0.05)
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(envelope, kernel, mode='same')
        
        # Binarize signal (is the tone on or off?)
        is_on = smoothed > self.threshold
        
        # Find rising and falling edges
        diff = np.diff(is_on.astype(int))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        
        # Handle edge cases where recording starts/ends mid-tone
        if len(starts) == 0 or len(ends) == 0:
            return ""
            
        if ends[0] < starts[0]:
            starts = np.insert(starts, 0, 0)
        if len(starts) > len(ends):
            ends = np.append(ends, len(is_on) - 1)
            
        durations_on = (ends - starts) / self.sample_rate
        
        # Calculate silent durations between tones
        silence_starts = ends[:-1]
        silence_ends = starts[1:]
        durations_off = (silence_ends - silence_starts) / self.sample_rate
        
        morse_code = ""
        for i in range(len(durations_on)):
            # Distinguish dot (1 unit) vs dash (3 units)
            # Threshold at 2 units
            if durations_on[i] < self.dot_duration * 2.0:
                morse_code += "."
            else:
                morse_code += "-"
                
            if i < len(durations_off):
                # Distinguish letter space vs word space vs intra-character space
                if durations_off[i] > self.dot_duration * 4.5:
                    morse_code += "   " # word space
                elif durations_off[i] > self.dot_duration * 2.0:
                    morse_code += " " # letter space
                    
        print(f"Extracted Raw Morse Code: {morse_code}")
        return self._decode_morse_string(morse_code)

    def _decode_morse_string(self, morse_string: str) -> str:
        """Converts raw space-separated morse string back to alphanumeric text."""
        text = ""
        words = morse_string.split("   ")
        for word in words:
            chars = word.split(" ")
            for char in chars:
                if char in self.REVERSE_DICT:
                    text += self.REVERSE_DICT[char]
                elif char:
                    # Unrecognized symbol
                    text += "?"
            text += " "
        return text.strip()
