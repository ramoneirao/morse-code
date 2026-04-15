import numpy as np
import sounddevice as sd
import time

class MorseToAudio:
    def __init__(self, wpm: int = 15, freq: int = 600):
        self.freq = freq
        self.sample_rate = 44100
        
        # No código Morse padrão:
        # Um ponto dura 1 unidade de tempo.
        # Um traço dura 3 unidades de tempo.
        # O espaço entre partes da mesma letra é de 1 unidade de tempo.
        # O espaço entre letras é de 3 unidades de tempo.
        # O espaço entre palavras é de 7 unidades de tempo.
        # Fórmula: unidade de tempo (segundos) = 1.2 / WPM.
        self.dot_duration = 1.2 / wpm
        self.dash_duration = self.dot_duration * 3
        # Espaços
        self.intra_char_space = self.dot_duration
        self.letter_space = self.dot_duration * 3
        self.word_space = self.dot_duration * 7

    def generate_tone(self, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.sin(self.freq * t * 2 * np.pi)
        
        # Aplica um envelope curto para evitar cortes no áudio / 'clicks' nas bordas
        fade_in = min(int(0.01 * self.sample_rate), len(wave) // 2)
        fade_out = fade_in
        envelope = np.ones(len(wave))
        if fade_in > 0:
            envelope[:fade_in] = np.linspace(0, 1, fade_in)
            envelope[-fade_out:] = np.linspace(1, 0, fade_out)
            
        return (wave * envelope).astype(np.float32)

    def play(self, morse_code: str):
        # A string morse foi gerada com um espaço simples entre caracteres e espaço triplo entre palavras
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
                # No TextToMorse, as letras são separadas por ' ' e palavras por '   '
                # Para cada ' ', esperamos 2 durações de ponto adicionais.
                # Como já esperamos 1 duração de ponto após a marca anterior (intra_char_space),
                # esperar mais 2 totaliza 3, que é exatamente o letter_space!
                time.sleep(self.dot_duration * 2)
