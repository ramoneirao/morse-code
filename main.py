import sys
import argparse
import sounddevice as sd

from morse_core.text_to_morse import TextToMorse
from morse_core.morse_to_audio import MorseToAudio
from morse_core.audio_to_text import AudioToText


def get_input_devices():
    devices = sd.query_devices()
    result = []
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            result.append((i, dev))
    return result


def get_output_devices():
    devices = sd.query_devices()
    result = []
    for i, dev in enumerate(devices):
        if dev["max_output_channels"] > 0:
            result.append((i, dev))
    return result


def list_devices():
    print("\n=== INPUT DEVICES ===")
    for i, dev in get_input_devices():
        marker = ""
        name = dev["name"].lower()
        if "monitor" in name or "loopback" in name:
            marker = "  <-- provável áudio do sistema"
        print(f"[{i}] {dev['name']}{marker}")

    print("\n=== OUTPUT DEVICES ===")
    for i, dev in get_output_devices():
        print(f"[{i}] {dev['name']}")


def auto_find_system_input():
    """
    Tenta achar automaticamente um dispositivo de entrada que capture
    o áudio do sistema (monitor/loopback).
    """
    candidates = []
    for i, dev in get_input_devices():
        name = dev["name"].lower()
        if "monitor" in name or "loopback" in name:
            candidates.append((i, dev["name"]))

    if not candidates:
        return None

    # pega o primeiro monitor/loopback encontrado
    return candidates[0][0]


def send_text(text: str, wpm: int, freq: int, output_device: int | None):
    tm = TextToMorse()
    morse = tm.convert(text)
    print(f"\nCódigo Morse:\n{morse}")

    ma = MorseToAudio(wpm=wpm, freq=freq, device=output_device)
    print("\nReproduzindo...")
    ma.play(morse)
    print("Concluído.")


def listen_text(wpm: int, input_device: int | None, use_system: bool):
    if use_system and input_device is None:
        input_device = auto_find_system_input()

    if use_system and input_device is None:
        print("Não encontrei automaticamente um dispositivo monitor/loopback.")
        print("Rode primeiro: python main.py list-devices")
        print("Depois use: python main.py listen --device ID")
        sys.exit(1)

    print(f"Dispositivo de entrada selecionado: {input_device}")
    at = AudioToText(wpm=wpm)
    transcription = at.listen_and_decode(device=input_device)
    print(f"\nTexto transcrito: '{transcription}'")


def build_parser():
    parser = argparse.ArgumentParser(description="Código Morse por áudio")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-devices", help="Lista dispositivos de áudio")

    send_parser = sub.add_parser("send", help="Envia texto como áudio Morse")
    send_parser.add_argument("text", help="Texto para converter")
    send_parser.add_argument("--wpm", type=int, default=15, help="Velocidade do Morse")
    send_parser.add_argument("--freq", type=int, default=600, help="Frequência do tom")
    send_parser.add_argument("--output-device", type=int, default=None, help="ID do dispositivo de saída")

    listen_parser = sub.add_parser("listen", help="Escuta áudio Morse e transcreve")
    listen_parser.add_argument("--wpm", type=int, default=15, help="Velocidade esperada do Morse")
    listen_parser.add_argument("--device", type=int, default=None, help="ID do dispositivo de entrada")
    listen_parser.add_argument(
        "--system",
        action="store_true",
        help="Tenta capturar automaticamente do monitor/loopback do sistema"
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-devices":
        list_devices()

    elif args.command == "send":
        send_text(
            text=args.text,
            wpm=args.wpm,
            freq=args.freq,
            output_device=args.output_device,
        )

    elif args.command == "listen":
        listen_text(
            wpm=args.wpm,
            input_device=args.device,
            use_system=args.system,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrompido.")
        sys.exit(0)
