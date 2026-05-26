from google import genai
import os
import time


def load_api_key():
    """Loads the Gemini API key from the text file."""
    try:
        with open("../api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("ERROR: api_key.txt not found.")
        return None


def clean_brand_text(raw_text):
    """Agent 2: Uses Gemini to strip e-commerce garbage and keep pure brand voice."""
    api_key = load_api_key()
    if not api_key:
        return None

    client = genai.Client(api_key=api_key)

    system_prompt = """
    You are an expert luxury copywriter and brand auditor. 
    Below is raw text scraped from a web search about a luxury fragrance brand. It might contain huge amounts of website garbage (menus, reviews, UI text).

    Your task:
    1. Remove ALL website noise (navigation, user reviews, Fragrantica menus, copyright tags, prices).
    2. Remove pure product specs (bottle size, ingredient lists).
    3. EXTRACT AND KEEP ONLY the sentences that communicate brand identity, heritage, feeling, philosophy, or world-building.

    Return ONLY the cleaned, continuous narrative text. Do not add any introductory or concluding remarks.
    """

    print("Agent 2 (Cleaner) is reading 114,000+ characters and hunting for the narrative...")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[system_prompt + "\n\nRAW TEXT:\n" + raw_text]
            )
            return response.text.strip()

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "429" in error_msg:
                print(f"Server busy (Attempt {attempt + 1}/{max_retries}). Waiting 5 seconds...")
                time.sleep(5)
            else:
                print(f"Fatal Gemini API Error: {e}")
                return None

    print("Agent 2 failed after 3 attempts due to server overload.")
    return None


def main():
    # --- THIS IS WHAT CHANGED ---
    # Pointing exactly at the massive file Tavily just downloaded
    raw_file_path = "../data/raw_text/maison_raw.txt"

    try:
        with open(raw_file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {raw_file_path}.")
        return

    clean_text = clean_brand_text(raw_text)

    if clean_text:
        os.makedirs("../data/clean_text", exist_ok=True)
        # Saving the clean output
        clean_file_path = "../data/clean_text/maison_clean.txt"

        with open(clean_file_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        print("\nSUCCESS! Agent 2 has cleaned the text.")
        print("--- CLEANED TEXT OUTPUT ---")
        print(clean_text)
        print("---------------------------")


if __name__ == "__main__":
    main()