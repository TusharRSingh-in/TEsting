mport translators as ts
import time

PART_SIZE = 1000

def split_text(text, size):
    return [text[i:i + size] for i in range(0, len(text), size)]

def translate_text(text, src, dest, progress_callback=None):
    if not text or not text.strip():
        return ""

    # Convert regional tags back to short codes if necessary
    src_code = src.split('-')[0]
    dest_code = dest.split('-')[0]

    parts = split_text(text, PART_SIZE)
    total_parts = len(parts)
    translated_parts = []

    for index, part in enumerate(parts, start=1):
        try:
            # Uses an alternative engine tier that handles proxy/DNS limits better
            result = ts.translate_text(part, from_language=src_code, to_language=dest_code, translator='bing')
            translated_parts.append(result if result else "")

        except Exception as e:
            try:
                # Backup engine if the first choice fails a network call
                result = ts.translate_text(part, from_language=src_code, to_language=dest_code, translator='alibaba')
                translated_parts.append(result if result else "")
            except Exception as secondary_error:
                translated_parts.append(f"[Server Connection Issue: Please try again in a moment]")

        if progress_callback:
            progress_callback(index, total_parts)

        time.sleep(0.4)

    return "\n".join(translated_parts)
