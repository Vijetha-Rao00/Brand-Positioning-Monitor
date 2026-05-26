from google import genai
import os
import json
import time


def load_api_key():
    try:
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("ERROR: api_key.txt not found.")
        return None


def analyze_historical_drift(client, brand, text):
    """Runs the historical text through BOTH Agent 3 (Scoring) and Agent 4 (Critique) in one prompt to save rate limits."""

    system_prompt = f"""
    You are an elite Brand Strategist. You are auditing a HISTORICAL (2020) brand manifesto to calculate strategic drift.

    Target Brand: {brand}
    2020 Manifesto Text: "{text}"

    SCORE THIS TEXT ON TWO AXES (0 to 10):

    X-AXIS: DOMINANCE (0) vs. VULNERABILITY (10)
    * Dominance (0-4): Imperatives, superlatives, third-person monument building.
    * Vulnerability (6-10): First-person, somatic intimacy, emotional diary.

    Y-AXIS: COLLECTIVE MYTH (0) vs. PRIVATE TRUTH (10)
    * Collective Myth (0-4): Archetypes, shared culture, global institutions.
    * Private Truth (6-10): Hyper-specific memory, solitude, individual inner experience.

    CRITIQUE REQUIREMENT:
    Do not score safely. Push the scores to the extremes (0-2 or 8-10) if the text justifies it. Be ruthless in your evaluation of the linguistic tone.

    OUTPUT FORMAT: Return ONLY valid JSON.
    {{
      "x_score": [Number],
      "y_score": [Number],
      "drift_log": "[One sentence justifying these historical scores based on the text provided.]"
    }}
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[system_prompt]
            )
            raw = response.text.strip()
            if raw.startswith("```json"):
                raw = raw[7:-3].strip()
            elif raw.startswith("```"):
                raw = raw[3:-3].strip()
            return json.loads(raw)
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                print(f"  [Server busy. Retrying...]")
                time.sleep(5)
            else:
                print(f"  [Error]: {e}")
                return None
    return None


def main():
    print("=== INITIALIZING ACTUAL DRIFT ANALYSIS ENGINE ===\n")

    api_key = load_api_key()
    if not api_key: return
    client = genai.Client(api_key=api_key)

    try:
        with open("data/knowledge_base/historical_brand_data.json", "r", encoding="utf-8") as f:
            hist_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: historical_brand_data.json not found.")
        return

    hist_scores = {}

    for brand, text in hist_data.items():
        print(f"Calculating 2021 Baseline for: {brand}...")
        result = analyze_historical_drift(client, brand, text)

        if result:
            hist_scores[brand] = result
            print(f"  > 2021 Coordinates Locked: X={result['x_score']}, Y={result['y_score']}")

        time.sleep(4)  # Rate limit protection

    os.makedirs("data/scores", exist_ok=True)
    with open("data/scores/historical_scores.json", "w", encoding="utf-8") as f:
        json.dump(hist_scores, f, indent=4)

    print(f"\n=== DRIFT ANALYSIS COMPLETE ===")
    print("Historical coordinates saved. Refresh your Streamlit app to view the authentic drift vectors.")


if __name__ == "__main__":
    main()