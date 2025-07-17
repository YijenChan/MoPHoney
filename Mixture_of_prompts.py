import json
import random
import time
from typing import List, Dict, Any
from MoP_Router import get_password_class_prob
from similar_password_finder import recommend_similar_passwords_from_csv
from feature_extraction import extract_semantic_feature
import openai
import numpy as np

# ========== OpenAI API Configuration ==========
openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual key
openai.api_base = "https://your-api-endpoint.com/v1"  # Optional custom base URL

# ========== Prompt Templates ==========
PROMPT_TEMPLATES = {
    0: "You are a honeyword generator. Based on the following weak password examples: {examples}, generate ONE realistic weak honeyword similar to the target password: {password}. Only output the honeyword, without any explanation.",
    1: "You are a honeyword generator. Based on the following strong password examples: {examples}, generate ONE realistic strong-style honeyword similar to: {password}. Only output the honeyword, without any explanation.",
    2: "You are a honeyword generator. Based on these PII-based passwords: {examples}, generate ONE realistic PII-style honeyword for the anonymized password: {password}. Only output the honeyword, without any explanation.",
    3: "You are a honeyword generator. Given the password: {password}, generate ONE realistic honeyword of similar style. Only output the honeyword, without any explanation."
}

# ========== PII Masking ==========
def mask_sensitive_segments(password: str) -> str:
    result = extract_semantic_feature(password)
    reason = result.get("Reason", "")
    for pii_term in ["name", "email", "birthday", "phone", "ID"]:
        if pii_term in reason.lower():
            return "[MASK]"
    return password

# ========== Prompt Construction ==========
def build_prompts(password: str, neighbors: List[str], weights: List[float], total_count: int) -> List[tuple]:
    weights = list(weights)
    type_counts = [round(w * total_count) for w in weights]
    total = sum(type_counts)
    while total < total_count:
        type_counts[np.argmax(weights)] += 1
        total += 1
    while total > total_count:
        type_counts[np.argmax(type_counts)] -= 1
        total -= 1

    print(f"🧩 Prompt distribution by type: {type_counts}")
    prompts = []
    for k in range(4):
        for _ in range(type_counts[k] * 4):  # Oversample for retry flexibility
            examples = random.sample(neighbors, min(5, len(neighbors)))
            masked_pw = mask_sensitive_segments(password) if k == 2 else password
            prompt = PROMPT_TEMPLATES[k].format(examples=", ".join(examples), password=masked_pw)
            prompts.append((k, prompt))
    random.shuffle(prompts)
    return prompts

# ========== GPT Query with Retry ==========
def query_gpt(prompt: str, max_retries: int = 3, retry_delay: float = 2.0) -> str:
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic honeywords."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=16,
                n=1,
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"⚠️ GPT call failed (attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    return ""

# ========== Main Generation Function ==========
def generate_honeywords(password: str, total_count: int = 30, save_path: str = None) -> Dict[str, Any]:
    print(f"\n🔐 Generating honeywords for: {password}")
    weights = get_password_class_prob(password)
    print(f"📊 Class probabilities: {weights}")
    neighbors = recommend_similar_passwords_from_csv(password, "benchmark_dataset_hash.csv", num_recommendations=10)
    print(f"🔍 Similar passwords: {neighbors}")

    prompt_pool = build_prompts(password, neighbors, weights, total_count)
    honeyword_set = set()
    result = []
    prompt_idx = 0

    print(f"\n🚀 Generating {total_count} honeywords...")
    while len(honeyword_set) < total_count and prompt_idx < len(prompt_pool):
        k, base_prompt = prompt_pool[prompt_idx]
        prompt_idx += 1

        exclusions = list(honeyword_set)
        full_prompt = base_prompt
        if exclusions:
            full_prompt += f" Avoid generating these: {', '.join(exclusions)}."

        print(f"🔄 Generating entry {len(honeyword_set)+1}...")
        honeyword = query_gpt(full_prompt)
        clean = honeyword.strip().split()[0].strip(".,:\"'")

        if clean and clean.lower() != password.lower() and clean not in honeyword_set:
            honeyword_set.add(clean)
            result.append({"type": k, "honeyword": clean})
            print(f"[{len(honeyword_set):02d}/{total_count}] ✅ type-{k} → {clean}")
        else:
            print(f"[{len(honeyword_set):02d}/{total_count}] ⚠️ type-{k} → duplicate or invalid")

    if len(honeyword_set) < total_count:
        print("❌ Failed to generate enough honeywords. Consider increasing prompt volume or refining templates.")

    print("\n🎉 Final honeywords:")
    for i, item in enumerate(result, 1):
        print(f"{i:02d}. (type-{item['type']}) {item['honeyword']}")

    output = {
        "password": password,
        "weights": [float(w) for w in weights],
        "neighbors": neighbors,
        "honeywords": result
    }

    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to: {save_path}")

    return output

# ========== CLI Test Entry ==========
if __name__ == "__main__":
    test_password = "abc123"
    generate_honeywords(test_password, save_path="abc123_honeywords.json")
