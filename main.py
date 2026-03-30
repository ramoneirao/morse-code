import sys
from morse_core.text_to_morse import TextToMorse
from morse_core.morse_to_audio import MorseToAudio
from morse_core.audio_to_text import AudioToText

def main():
    while True:
        print("\n--- Aplicação de Código Morse ---")
        print("1. Texto para Código Morse (tocar áudio)")
        print("2. Ouvir/Receber áudio em Código Morse (transcrever para texto)")
        print("3. Sair")
        
        choice = input("\nEscolha uma opção (1-3): ")

        if choice == '1':
            text = input("Digite o texto para converter: ")
            tm = TextToMorse()
            morse = tm.convert(text)
            print(f"\nCódigo Morse Gerado:\n{morse}")
            
            # WPM (Words Per Minute) afeta a velocidade do som
            ma = MorseToAudio(wpm=15)
            print("Reproduzindo...")
            ma.play(morse)
            print("Concluído.")

        elif choice == '2':
            try:
                duration_str = input("Digite a duração da escuta em segundos (padrão 10): ")
                duration = int(duration_str) if duration_str.strip() else 10
            except ValueError:
                print("Duração inválida, usando 10 segundos.")
                duration = 10
                
            at = AudioToText(wpm=15)
            transcription = at.listen_and_decode(duration)
            print(f"\nTexto Transcrito: '{transcription}'")

        elif choice == '3':
            print("Saindo do programa...")
            sys.exit(0)
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    # Bloco try/except permite encerrar suavemente com Ctrl+C
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário. Saindo...")
        sys.exit(0)
