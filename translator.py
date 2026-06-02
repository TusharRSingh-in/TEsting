from translate import Translator
import time

PART_SIZE = 500  # Safe chunk size for local text processing

def split_text(text, size):
    return [text[i:i + size] for i in range(0, len(text), size)]

def translate_text(text, src, dest, progress_callback=None):
    if not text or not text.strip():
        return ""

    # Clean the language tags (e.g., convert 'en-GB' back to 'en' if needed)
    src_code = src.split('-')[0]
    dest_code = dest.split('-')[0]

    parts = split_text(text, PART_SIZE)
    total_parts = len(parts)
    translated_parts = []

    try:
        # Initialize the offline-capable translator engine
        translator = Translator(from_lang=src_code, to_lang=dest_code)
        
        for index, part in enumerate(parts, start=1):
            try:
                result = translator.translate(part)
                translated_parts.append(result if result else "")
            except Exception as chunk_err:
                translated_parts.append(f"[Chunk Error: {str(chunk_err)}]")
            
            if progress_callback:
                progress_callback(index, total_parts)
                
            time.sleep(0.1)  # Lightning fast since it doesn't need the internet!

    except Exception as e:
        return f"[Translation Engine Error: {str(e)}]"

    return " ".join(translated_parts)
