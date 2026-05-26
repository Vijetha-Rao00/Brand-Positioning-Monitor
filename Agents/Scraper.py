import asyncio
import os
import json
import time
import pathlib
from crawl4ai import AsyncWebCrawler
from google import genai


def load_api_key():
    # Dynamically search the current folder and parent folders for the key
    current = pathlib.Path(__file__).parent
    for folder in [current, current.parent, current.parent.parent]:
        key_file = folder / "api_key.txt"
        if key_file.exists():
            return key_file.read_text().strip()
    print("ERROR: api_key.txt not found. Please ensure it's in your project root.")
    return None


# --- THE AUTHENTICITY BOUNCER (AGENT 2) ---
def clean_and_verify_text(client, brand, raw_text):
    system_prompt = f"""
    You are the Authenticity Bouncer for a luxury brand strategy firm.
    I am giving you raw scraped text from {brand}'s official website.

    Your job is to extract ONLY the authentic brand manifesto, emotional copy, and tone-of-voice sentences.

    CRITICAL RULES:
    1. Strip all website UI, cookie notices, product specs, and pricing.
    2. DELETE any text that reads like a Wikipedia article, historical timeline, or third-person journalism (e.g., "{brand} was founded in 1988...").
    3. KEEP ONLY text that uses first/second person ("We", "You", "I"), poetic language, commands, or deep brand philosophy.

    If the text contains NO authentic philosophical brand voice, return exactly the word "INSUFFICIENT_DATA".
    Otherwise, return ONLY the concentrated brand narrative. Do not add intro/outro chat text.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.0-flash',
                contents=[system_prompt + "\n\nRAW TEXT:\n" + raw_text]
            )
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "429" in error_msg:
                print(f"    [Agent 2] API limit hit. Cooling down for 15s...")
                time.sleep(15)
            else:
                print(f"    [Agent 2] Fatal API error: {e}")
                return "INSUFFICIENT_DATA"
    return "INSUFFICIENT_DATA"


# --- THE AUTONOMOUS CRAWLER (AGENT 1) ---
async def scrape_official_sites():
    print("=== DEPLOYING AUTONOMOUS PRIMARY-SOURCE PIPELINE ===\n")

    api_key = load_api_key()
    if not api_key: return
    client = genai.Client(api_key=api_key)

    # Targeting the exact pages where brands hide their philosophy
    official_urls = {
        "Chanel": "https://www.chanel.com/us/about-chanel/the-history/",
        "Hermes": "https://www.hermes.com/us/en/story/192611-terre-d-hermes-creation/",
        "YSL": "https://www.yslbeautyus.com/fragrance-1",
        "Maison Margiela": "https://www.maisonmargiela-fragrances.us/about-us.html",
        "Jean Paul Gaultier": "https://www.jeanpaulgaultier.com/us/en/fragrances/le-male",
        "Viktor & Rolf": "https://www.viktor-rolf.com/en/fashion-house/",
        "Mancera": "https://manceraparfums.com/en/content/6-our-story",
        "Creed": "https://creedboutique.com/pages/our-heritage",
        "Byredo": "https://www.byredo.com/us_en/about-byredo/"
    }

    # VARO is a concept, so we dynamically inject its manifesto directly into the dataset
    varo_manifesto = "For the person you are when no one is watching. The scent of a secret you almost forgot. VARŌ doesn’t announce you to the room; it whispers to your own skin. Raw, unfiltered, and intimately yours. It is the smell of a rain-soaked street corner that only you remember. A confession wrapped in amber glass."

    knowledge_base = {"VARO": varo_manifesto}

    async with AsyncWebCrawler() as crawler:
        for brand, url in official_urls.items():
            print(f"Breaching firewall: {brand}...")
            try:
                # Agent 1 extracts the raw DOM
                result = await crawler.arun(url=url)
                raw_markdown = result.markdown

                if raw_markdown and len(raw_markdown) > 50:
                    print(f"  > Success! Extracted {len(raw_markdown)} raw chars. Passing to Agent 2...")
                    # Agent 2 filters for authenticity
                    clean_text = clean_and_verify_text(client, brand, raw_markdown)

                    if clean_text != "INSUFFICIENT_DATA" and len(clean_text) > 20:
                        print(f"  > ✅ Agent 2 verified authentic voice. Saved {len(clean_text)} chars.")
                        knowledge_base[brand] = clean_text
                    else:
                        print(f"  > ⚠️ Agent 2 rejected the text (Too corporate / SEO garbage).")
                else:
                    print(f"  > ❌ Failed: WAF Blocked or Empty Page.")

            except Exception as e:
                print(f"  > ❌ Crawler Error: {e}")

            time.sleep(3)  # Be polite to their servers

    # Dynamically find the correct save path (Brand Project/data/knowledge_base/)
    base_dir = pathlib.Path(__file__).parent.parent
    kb_dir = base_dir / "data" / "knowledge_base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "brand_data.json"

    # Save the dynamically generated Golden Dataset
    with open(kb_file, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=4)

    print(f"\n=== PIPELINE COMPLETE ===")
    print(f"Successfully autonomously generated Knowledge Base for {len(knowledge_base)}/10 brands.")
    print(f"Saved to: {kb_file}")


if __name__ == "__main__":
    asyncio.run(scrape_official_sites())