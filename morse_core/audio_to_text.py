import numpy as np
import sounddevice as sd
import time
import queue

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

    def listen_and_decode(self, device=None) -> str:
        """Grava áudio continuamente e traduz em tempo real até o usuário pressionar Enter."""
        import threading
        
        print("Pressione ENTER a qualquer momento para parar a escuta.")
        print("Iniciando escuta simultânea... (Toque o áudio Morse no outro terminal)")
        print("\nTexto: ", end='', flush=True)
        
        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(indata[:, 0].copy())
            
        state = 'SILENCE'
        state_duration = 0.0
        current_morse = ""
        decoded_text = ""
        running_max = 0.01
        
        stop_event = threading.Event()
        
        def process_audio():
            nonlocal state, state_duration, current_morse, decoded_text, running_max
            window_size = int(self.sample_rate * 0.05)
            kernel = np.ones(window_size) / window_size
            overlap = np.zeros(window_size - 1)
            
            dot_frames = self.dot_duration * self.sample_rate
            letter_space_frames = dot_frames * 2.5
            word_space_frames = dot_frames * 6.0
            
            printed_letter = True
            printed_word = True
            
            while not stop_event.is_set() or not q.empty():
                try:
                    chunk = q.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                envelope = np.abs(chunk)
                chunk_max = np.max(envelope) if len(envelope) > 0 else 0
                if chunk_max > running_max:
                    running_max = chunk_max
                else:
                    running_max = running_max * 0.999
                    
                threshold_real = max(0.02, running_max * 0.3)
                
                combined = np.concatenate((overlap, envelope))
                smoothed = np.convolve(combined, kernel, mode='valid')
                if window_size > 1:
                    overlap = envelope[-(window_size - 1):]
                
                is_on = smoothed > threshold_real
                
                for val in is_on:
                    if val and state == 'SILENCE':
                        state = 'TONE'
                        state_duration = 1
                        printed_letter = False
                        printed_word = False
                    elif not val and state == 'TONE':
                        if state_duration < dot_frames * 2.0:
                            current_morse += "."
                        else:
                            current_morse += "-"
                        state = 'SILENCE'
                        state_duration = 1
                    else:
                        state_duration += 1
                        if state == 'SILENCE':
                            if not printed_letter and state_duration > letter_space_frames:
                                if current_morse:
                                    char = self.REVERSE_DICT.get(current_morse, '?')
                                    print(char, end='', flush=True)
                                    decoded_text += char
                                    current_morse = ""
                                printed_letter = True
                            if not printed_word and state_duration > word_space_frames:
                                print(" ", end='', flush=True)
                                decoded_text += " "
                                printed_word = True
                                
        t = threading.Thread(target=process_audio)
        t.start()
        
        stream = sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32', device=device, blocksize=2048, callback=callback)
        with stream:
            input()
            
        stop_event.set()
        t.join()
        
        print("\n\n[Tradução Finalizada]")
        return decoded_text.strip()

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
