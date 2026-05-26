from google import genai
import os
import json
import time


def load_api_key():
    try:
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("ERROR: api_key.txt not found. Are you running this from the root folder?")
        return None


def score_brand(client, brand_name, text):
    """Passes the text to Agent 3 (Scorer) using our locked Rubric."""
    system_prompt = """
    You are an expert Brand Strategist and Quantitative Linguist. Your task is to analyze luxury fragrance brand copy and score it on two strategic axes using a strict linguistic rubric.

    Analyze the provided text and plot it on a 0 to 10 scale for both axes. Use integers or decimals (e.g., 7.5).

    X-AXIS: DOMINANCE (0) vs. VULNERABILITY (10)
    * Closer to 0 (Dominance): Look for imperative verbs, superlatives, establishment markers, third-person authority. The brand speaks as a monument.
    * Closer to 10 (Vulnerability): Look for somatic/fleshy words, direct address (You/I), emotional admissions, exposure of process or imperfection. The brand speaks as a confidant.

    Y-AXIS: COLLECTIVE MYTH (0) vs. PRIVATE TRUTH (10)
    * Closer to 0 (Collective Myth): Look for archetypes, heritage/archive language, shared cultural touchstones, tribal gatekeeping. The brand speaks as a religion.
    * Closer to 10 (Private Truth): Look for stream of consciousness, memory/nostalgia, solitude, hyper-specific odd details. The brand speaks as a diary.

    OUTPUT FORMAT:
    Return ONLY a valid JSON object. No markdown. No extra text.
    {
      "x_score": [Number],
      "x_reasoning": "[One short sentence justifying the X score]",
      "y_score": [Number],
      "y_reasoning": "[One short sentence justifying the Y score]"
    }
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[system_prompt + "\n\nBRAND TEXT:\n" + text]
            )

            # Clean JSON formatting if LLM adds markdown
            raw_output = response.text.strip()
            if raw_output.startswith("```json"):
                raw_output = raw_output[7:-3].strip()
            elif raw_output.startswith("```"):
                raw_output = raw_output[3:-3].strip()

            return json.loads(raw_output)

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "429" in error_msg:
                print(f"  [Server busy. Retrying in 5 seconds...]")
                time.sleep(5)
            else:
                print(f"  [Failed to parse JSON for {brand_name}: {e}]")
                print(f"  [Raw Output]: {raw_output}")
                return None
    return None


def main():
    print("=== STARTING BATCH SCORING ORCHESTRATOR ===\n")

    api_key = load_api_key()
    if not api_key: return
    client = genai.Client(api_key=api_key)

    # 1. Load the Golden Dataset
    try:
        with open("data/knowledge_base/brand_data.json", "r", encoding="utf-8") as f:
            brand_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: data/knowledge_base/brand_data.json not found.")
        return

    all_scores = {}

    # 2. Loop through all 10 brands
    for brand, text in brand_data.items():
        print(f"Scoring: {brand}...")
        scores = score_brand(client, brand, text)

        if scores:
            all_scores[brand] = scores
            print(f"  > Success! Coordinates: X={scores['x_score']}, Y={scores['y_score']}")
        else:
            print(f"  > Failed to score {brand}.")

        # Crucial for avoiding API rate limits during batch processing
        time.sleep(4)

        # 3. Save the final master JSON file
    os.makedirs("data/scores", exist_ok=True)
    master_file = "data/scores/all_brand_scores.json"
    with open(master_file, "w") as f:
        json.dump(all_scores, f, indent=4)

    print(f"\n=== ORCHESTRATION COMPLETE ===")
    print(f"Successfully scored {len(all_scores)}/10 brands.")
    print(f"Master file saved to: {master_file}")


if __name__ == "__main__":
    main()