from deep_translator import MyMemoryTranslator
import time

PART_SIZE = 1000  # MyMemory prefers slightly smaller chunk sizes for free tier

def split_text(text, size):
    return [text[i:i + size] for i in range(0, len(text), size)]

def translate_text(text, src, dest, progress_callback=None):
    if not text or not text.strip():
        return ""

    parts = split_text(text, PART_SIZE)
    total_parts = len(parts)
    translated_parts = []

    for index, part in enumerate(parts, start=1):
        try:
            # Swap GoogleTranslator for MyMemoryTranslator
            result = MyMemoryTranslator(source=src, target=dest).translate(part)
            translated_parts.append(result if result else "")

        except Exception as e:
            translated_parts.append(f"[ERROR PART {index}: {str(e)}]")

        if progress_callback:
            progress_callback(index, total_parts)

        time.sleep(0.5)  # Respectful delay between API chunk calls

    return "\n".join(translated_parts)
