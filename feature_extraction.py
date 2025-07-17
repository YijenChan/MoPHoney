import re
import math
import json
from collections import Counter
import openai

# ------------------ GPT API Configuration ------------------
openai.api_key = 'your-api-key-here'  # Replace with your actual key
openai.api_base = "https://your-endpoint.com/v1"  # Replace with your actual endpoint

# ------------------ Structural Feature Extractor ------------------
class PasswordStructuralFeatures:
    def __init__(self):
        self.regex_patterns = {
            'date': r'(19|20)?\d{2}[-/.]?(0?[1-9]|1[0-2])[-/.]?(0?[1-9]|[12][0-9]|3[01])',
            'phone': r'1[3-9]\d{9}',
            'keyboard_walk': r'(qwerty|asdfgh|zxcvbn)',
        }

    def extract(self, password: str) -> dict:
        total_len = len(password)
        if total_len == 0:
            return self._empty_feature()

        features = {
            'digit_ratio': sum(c.isdigit() for c in password) / total_len,
            'lower_ratio': sum(c.islower() for c in password) / total_len,
            'upper_ratio': sum(c.isupper() for c in password) / total_len,
            'symbol_ratio': sum(not c.isalnum() for c in password) / total_len,
            'shannon_entropy': self._calculate_entropy(password),
            'max_digit_run_length': self._max_digit_run(password),
            'bigram_repetition_score': self._repetition_score([password[i:i+2] for i in range(total_len - 1)]),
            'trigram_repetition_score': self._repetition_score([password[i:i+3] for i in range(total_len - 2)]),
        }

        for name, pattern in self.regex_patterns.items():
            features[f'regex_match_{name}'] = 1 if re.search(pattern, password.lower()) else 0

        return features

    def _calculate_entropy(self, password: str) -> float:
        counter = Counter(password)
        total = len(password)
        probs = [freq / total for freq in counter.values()]
        return -sum(p * math.log2(p) for p in probs if p > 0)

    def _max_digit_run(self, password: str) -> int:
        digit_runs = re.findall(r'\d+', password)
        return max((len(run) for run in digit_runs), default=0)

    def _repetition_score(self, ngrams) -> float:
        total = len(ngrams)
        if total == 0:
            return 0.0
        counts = Counter(ngrams)
        repeated = sum(v for v in counts.values() if v > 1)
        return repeated / total

    def _empty_feature(self) -> dict:
        return {
            'digit_ratio': 0.0,
            'lower_ratio': 0.0,
            'upper_ratio': 0.0,
            'symbol_ratio': 0.0,
            'shannon_entropy': 0.0,
            'max_digit_run_length': 0,
            'bigram_repetition_score': 0.0,
            'trigram_repetition_score': 0.0,
            'regex_match_date': 0,
            'regex_match_phone': 0,
            'regex_match_keyboard_walk': 0,
        }

# ------------------ Semantic Feature via GPT ------------------
def extract_semantic_feature(password: str) -> dict:
    prompt = f"""
You are a password security analyst. Assess whether the following password may contain PII (Personally Identifiable Information), such as name, birthday, email, phone, etc.

Output a JSON with two fields:
- "Reason": a brief justification for your assessment
- "Probability": a number between 0 and 1 indicating the likelihood of PII presence

Password: "{password}"

Only return valid JSON format.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=256,
        )
        content = response['choices'][0]['message']['content'].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "Reason": f"Request failed: {str(e)}",
            "Probability": 0.0
        }

# ------------------ Combined Feature Extraction ------------------
def extract_all_features(password: str) -> dict:
    struct_extractor = PasswordStructuralFeatures()
    struct_feats = struct_extractor.extract(password)

    sem_result = extract_semantic_feature(password)
    pii_prob = sem_result.get('Probability', 0.0)
    struct_feats['pii_included_probability'] = pii_prob

    return struct_feats

# ------------------ Sample Execution ------------------
if __name__ == "__main__":
    sample_passwords = [
        "Alice19950608",
        "QwErTy!123",
        "johnsmith@email.com",
        "P@ssw0rd123",
        "LiLei1990",
        "abc123"
    ]

    for pw in sample_passwords:
        print(f"\n🔐 Password: {pw}")
        all_feats = extract_all_features(pw)
        for k, v in all_feats.items():
            print(f"  {k}: {v}")
        print("-" * 60)
