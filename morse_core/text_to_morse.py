class TextToMorse:
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----', ', ': '--..--', '.': '.-.-.-', '?': '..--..',
        '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-'
    }

    def convert(self, text: str) -> str:
        """
        Converts a normal text string into Morse code.
        Words are separated by '   ' (3 spaces).
        Letters are separated by ' ' (1 space).
        """
        morse_words = []
        for word in text.strip().upper().split():
            morse_chars = [self.MORSE_CODE_DICT[char] for char in word if char in self.MORSE_CODE_DICT]
            if morse_chars:
                morse_words.append(' '.join(morse_chars))
        return '   '.join(morse_words)
