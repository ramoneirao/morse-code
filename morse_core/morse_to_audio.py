import numpy as np
import sounddevice as sd
import time


class MorseToAudio:
    def __init__(self, wpm: int = 15, freq: int = 600, device=None):
        self.freq = freq
        self.sample_rate = 44100
        self.device = device

        self.dot_duration = 1.2 / wpm
        self.dash_duration = self.dot_duration * 3
        self.intra_char_space = self.dot_duration
        self.letter_space = self.dot_duration * 3
        self.word_space = self.dot_duration * 7

    def generate_tone(self, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(self.freq * t * 2 * np.pi)

        fade_in = min(int(0.01 * self.sample_rate), len(wave) // 2)
        fade_out = fade_in
        envelope = np.ones(len(wave))

        if fade_in > 0:
            envelope[:fade_in] = np.linspace(0, 1, fade_in)
            envelope[-fade_out:] = np.linspace(1, 0, fade_out)

        return (wave * envelope).astype(np.float32)

    def play(self, morse_code: str):
        i = 0
        while i < len(morse_code):
            char = morse_code[i]

            if char == '.':
                tone = self.generate_tone(self.dot_duration)
                sd.play(tone, self.sample_rate, device=self.device)
                sd.wait()
                time.sleep(self.intra_char_space)

            elif char == '-':
                tone = self.generate_tone(self.dash_duration)
                sd.play(tone, self.sample_rate, device=self.device)
                sd.wait()
                time.sleep(self.intra_char_space)

            elif char == ' ':
                # Detecta 3 espaços consecutivos = separação de palavra
                if morse_code[i:i+3] == '   ':
                    time.sleep(self.word_space - self.intra_char_space)
                    i += 2
                else:
                    time.sleep(self.letter_space - self.intra_char_space)

            i += 1
