import numpy as np
import sounddevice as sd
import time

class AudioToText:
    def __init__(self, wpm: int = 15):
        self.sample_rate = 44100
        # Unidade de tempo
        self.dot_duration = 1.2 / wpm
        # Limiar para o volume do áudio (ajuste se o ambiente estiver barulhento ou o microfone estiver baixo)
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
        """Grava áudio por uma duração específica e tenta extrair o texto do código Morse."""
        print(f"Iniciando escuta por {duration} segundos... (Fale/Toque o áudio Morse agora)")
        
        # Grava a entrada do microfone
        recording = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
        sd.wait()
        print("Processando áudio...")
        
        # Calcula o envelope de amplitude
        envelope = np.abs(recording[:, 0])
        
        # Suaviza o envelope usando uma janela de média móvel (50ms)
        window_size = int(self.sample_rate * 0.05)
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(envelope, kernel, mode='same')
        
        # Binariza o sinal (o tom está ligado ou desligado?)
        is_on = smoothed > self.threshold
        
        # Encontra as bordas de subida e descida
        diff = np.diff(is_on.astype(int))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]
        
        # Trata casos extremos onde a gravação começa/termina no meio de um tom
        if len(starts) == 0 or len(ends) == 0:
            return ""
            
        if ends[0] < starts[0]:
            starts = np.insert(starts, 0, 0)
        if len(starts) > len(ends):
            ends = np.append(ends, len(is_on) - 1)
            
        durations_on = (ends - starts) / self.sample_rate
        
        # Calcula durações de silêncio entre tons
        silence_starts = ends[:-1]
        silence_ends = starts[1:]
        durations_off = (silence_ends - silence_starts) / self.sample_rate
        
        morse_code = ""
        for i in range(len(durations_on)):
            # Distingue ponto (1 unidade) vs traço (3 unidades)
            # Limiar em 2 unidades
            if durations_on[i] < self.dot_duration * 2.0:
                morse_code += "."
            else:
                morse_code += "-"
                
            if i < len(durations_off):
                # Distingue espaço entre letras vs espaço entre palavras vs espaço entre caracteres
                if durations_off[i] > self.dot_duration * 4.5:
                    morse_code += "   " # espaço entre palavras
                elif durations_off[i] > self.dot_duration * 2.0:
                    morse_code += " " # espaço entre letras
                    
        print(f"Código Morse Bruto Extraído: {morse_code}")
        return self._decode_morse_string(morse_code)

    def _decode_morse_string(self, morse_string: str) -> str:
        """Converte a string morse bruta separada por espaços de volta para texto alfanumérico."""
        text = ""
        words = morse_string.split("   ")
        for word in words:
            chars = word.split(" ")
            for char in chars:
                if char in self.REVERSE_DICT:
                    text += self.REVERSE_DICT[char]
                elif char:
                    # Símbolo não reconhecido
                    text += "?"
            text += " "
        return text.strip()
