import json
import openai
import time

# ====== GPT API Configuration ======
api_key = 'your-api-key-here'  # Replace with your own key
openai.api_key = api_key
openai.api_base = "https://your-endpoint.com/v1"  # Replace with your own endpoint

# ====== GPT Query with Retry Mechanism ======
def query_threat_llm(real_pw, candidates, max_retries=3):
    prompt = (
        f"You are a simulated attacker trying to guess the real password.\n"
        f"Among the following candidates:\n{', '.join(candidates)}\n"
        f"The real password is: {real_pw}. You must eliminate it.\n"
        f"Now choose the 19 most believable honeywords (excluding the true one).\n"
        f"Only return the honeywords as a list, no explanation."
    )

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a skilled adversary filtering honeywords."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
                n=1,
            )
            text = response.choices[0].message['content']
            return [w.strip(" .,\n\"'") for w in text.strip().splitlines() if w.strip()]
        except Exception as e:
            print(f"[!] GPT API call failed: {e}")
            time.sleep(2)
    return []

# ====== Honeyword Filtering Pipeline ======
def filter_all_honeywords(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list):
        records = [records]

    filtered_records = []

    for entry in records:
        pw = entry.get("password")
        candidates = [h["honeyword"] if isinstance(h, dict) else h for h in entry.get("honeywords", [])]

        if not candidates:
            print(f"[!] Skipping password '{pw}' due to missing candidates.")
            continue

        print(f"\n[>] Processing password: {pw} ({len(candidates)} candidates)")
        filtered = query_threat_llm(pw, candidates)
        print(f"[✓] Retained honeywords: {filtered}")

        filtered_records.append({
            "password": pw,
            "honeywords": filtered
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered_records, f, ensure_ascii=False, indent=2)
    print(f"\n[✔] Filtered results saved to: {output_path}")

# ====== Main Entry ======
if __name__ == "__main__":
    filter_all_honeywords("abc123_honeywords.json", "filtered_honeywords.json")
