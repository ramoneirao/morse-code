import numpy as np
import sounddevice as sd
import time

class MorseToAudio:
    def __init__(self, wpm: int = 15, freq: int = 600):
        self.freq = freq
        self.sample_rate = 44100
        
        # In standard Morse code:
        # A dot is 1 time unit long.
        # A dash is 3 time units long.
        # Space between parts of the same letter is 1 time unit.
        # Space between letters is 3 time units.
        # Space between words is 7 time units.
        # Formula: time unit (seconds) = 1.2 / WPM.
        self.dot_duration = 1.2 / wpm
        self.dash_duration = self.dot_duration * 3
        # Spaces
        self.intra_char_space = self.dot_duration
        self.letter_space = self.dot_duration * 3
        self.word_space = self.dot_duration * 7

    def generate_tone(self, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(self.freq * t * 2 * np.pi)
        
        # Apply a short envelope to avoid audio clipping / 'clicks' at the edges
        fade_in = min(int(0.01 * self.sample_rate), len(wave) // 2)
        fade_out = fade_in
        envelope = np.ones(len(wave))
        if fade_in > 0:
            envelope[:fade_in] = np.linspace(0, 1, fade_in)
            envelope[-fade_out:] = np.linspace(1, 0, fade_out)
            
        return (wave * envelope).astype(np.float32)

    def play(self, morse_code: str):
        # We generated the morse string with single space between chars and triple space between words
        for char in morse_code:
            if char == '.':
                tone = self.generate_tone(self.dot_duration)
                sd.play(tone, self.sample_rate)
                sd.wait()
                time.sleep(self.intra_char_space)
            elif char == '-':
                tone = self.generate_tone(self.dash_duration)
                sd.play(tone, self.sample_rate)
                sd.wait()
                time.sleep(self.intra_char_space)
            elif char == ' ':
                # In TextToMorse, letters are separated by ' ' and words by '   '
                # For each ' ', we wait an additional 2 dot durations.
                # Since we already waited 1 dot duration after the previous mark (intra_char_space),
                # waiting 2 more gives us 3 total, which is exactly letter_space!
                time.sleep(self.dot_duration * 2)
