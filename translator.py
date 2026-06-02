import requests
import time

PART_SIZE = 500  # Smaller chunks are safer and faster for free APIs

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
            # Call the official MyMemory GET API endpoint directly
            url = f"https://api.mymemory.translated.net/get?q={part}&langpair={src}|{dest}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data.get("responseData", {}).get("translatedText", "")
                translated_parts.append(translated_text)
            else:
                translated_parts.append(f"[API Error Status: {response.status_code}]")

        except Exception as e:
            translated_parts.append(f"[Connection Error: {str(e)}]")

        if progress_callback:
            progress_callback(index, total_parts)

        time.sleep(0.5)  # Clean delay to prevent rate limiting

    return " ".join(translated_parts)
