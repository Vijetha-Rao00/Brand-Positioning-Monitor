from google import genai
import os
import json


def load_api_key():
    try:
        with open("../api_key.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("ERROR: api_key.txt not found.")
        return None


def score_brand_text(clean_text):
    """Agent 3: Scores the text against our strategic rubric."""
    api_key = load_api_key()
    if not api_key: return None

    client = genai.Client(api_key=api_key)

    # THE EXACT RUBRIC WE LOCKED IN EARLIER
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
    You must return ONLY a valid, raw JSON object. Do not use markdown blocks (```json). Do not add any conversational text.
    {
      "x_score": [Number],
      "x_reasoning": "[One short sentence justifying the X score using specific words from the text]",
      "y_score": [Number],
      "y_reasoning": "[One short sentence justifying the Y score using specific words from the text]"
    }
    """

    print("Agent 3 (Scorer) is applying the strategic rubric to Maison Margiela...")

    try:
        # Using the Pro model because scoring requires complex reasoning, not just summarization
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[system_prompt + "\n\nBRAND TEXT:\n" + clean_text]
        )

        # Clean up the output in case the LLM adds markdown formatting
        raw_output = response.text.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:-3].strip()
        elif raw_output.startswith("```"):
            raw_output = raw_output[3:-3].strip()

        return json.loads(raw_output)

    except Exception as e:
        print(f"Agent 3 Failed: {e}")
        return None


def main():
    brand_name = "Maison Margiela"
    # Pointing to the clean file Agent 2 just made
    clean_file_path = "../data/clean_text/maison_clean.txt"

    try:
        with open(clean_file_path, "r", encoding="utf-8") as f:
            clean_text = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {clean_file_path}.")
        return

    # Pass text to Agent 3
    scores = score_brand_text(clean_text)

    if scores:
        print("\n=== STRATEGIC COORDINATES ACQUIRED ===")
        print(f"Brand: {brand_name}")
        print(f"X-Axis (Dominance[0] -> Vulnerability[10]): {scores['x_score']}")
        print(f"Reasoning: {scores['x_reasoning']}")
        print(f"Y-Axis (Myth[0] -> Truth[10]): {scores['y_score']}")
        print(f"Reasoning: {scores['y_reasoning']}")
        print("=====================================\n")

        # Save scores to JSON file so Streamlit can plot it later
        os.makedirs("../data/scores", exist_ok=True)
        score_file = "../data/scores/maison_margiela_score.json"
        with open(score_file, "w") as f:
            json.dump(scores, f, indent=4)
        print(f"Scores successfully saved to {score_file}")


if __name__ == "__main__":
    main()