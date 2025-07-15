from openai import OpenAI
import json
import random
import textwrap
import time
from password_recommender import recommend_similar_passwords_from_csv  # Ensure this module is available

class StrongPasswordGenerator:
    def __init__(self, university_name, test_mode=False):
        self.university_name = university_name
        self.test_mode = test_mode
        self.client = OpenAI(
            api_key='',  # Add your API key here
            base_url=""  # Add your custom base URL here if needed
        )

        self.messages = [
            {"role": "system", "content": f"Honeywords are decoy passwords used to detect unauthorized access. "
                                              f"Please generate honeywords similar to the target password to safeguard the database security."},
            {"role": "user", "content": "Strong password patterns typically include non-repeating characters or complex combinations of letters and numbers."}
        ]

    def generate(self, original_password):
        recommended_passwords = recommend_similar_passwords_from_csv(
            original_password, 'pre_hashed_passwords.csv', num_recommendations=5
        )

        if not recommended_passwords:
            print("Unable to find enough similar passwords.")
            return None

        if self.test_mode:
            print("Seed data from LSH:", [original_password] + recommended_passwords)

        passwords_str = ', '.join([f'({pwd})' for pwd in [original_password] + recommended_passwords])

        final_prompt = (
            f"Here are six passwords, including the original password '{original_password}' "
            f"and five similar passwords: {passwords_str}. "
            "Please break down each password into smaller segments (e.g., substrings, individual characters), "
            "and creatively recombine these segments to form new passwords (honeywords) that look similar to the original. "
            "Ensure each honeyword is unique by varying the order, replacing characters, adding new segments, and avoiding repetitive structures or common prefixes. "
            "Ensure that the newly generated honeywords meet the following conditions: "
            "1. The length is between 6-18 characters; "
            "2. Contains at least two types of characters: uppercase letters, lowercase letters, numbers and special symbols; "
            "3. The password cannot start with a special symbol. "
            "Generate exactly 20 different honeywords with diverse structures. "
            "Present the result **directly** in JSON format, with two fields: 'honeywords' (list of generated passwords) and 'explanation'."
        )

        honeywords_result = self.send_prompt(final_prompt, max_tokens=500)

        if honeywords_result:
            try:
                cleaned_result = honeywords_result.strip().replace("```json", "").replace("```", "")
                result_dict = json.loads(cleaned_result)

                unique_honeywords = []
                seen_honeywords = set()

                for honeyword in result_dict.get("honeywords", []):
                    if honeyword not in seen_honeywords and self.is_valid_honeyword(honeyword):
                        unique_honeywords.append(honeyword)
                        seen_honeywords.add(honeyword)

                if len(set(unique_honeywords)) != len(unique_honeywords):
                    print("[Warning] Duplicate honeywords detected in output.")

                while len(unique_honeywords) < 20:
                    additional = self.generate_additional_honeyword(original_password)
                    if additional not in seen_honeywords and self.is_valid_honeyword(additional):
                        unique_honeywords.append(additional)
                        seen_honeywords.add(additional)

                result_dict["honeywords"] = unique_honeywords[:20]
                return result_dict

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from LLM response: {str(e)}")
                return None

        return None

    def is_valid_honeyword(self, honeyword):
        if not (6 <= len(honeyword) <= 18):
            return False
        has_upper = any(c.isupper() for c in honeyword)
        has_lower = any(c.islower() for c in honeyword)
        has_digit = any(c.isdigit() for c in honeyword)
        return (has_upper + has_lower + has_digit) >= 2 and not honeyword[0] in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?"

    def send_prompt(self, prompt, max_tokens=200, retries=3, delay=2):
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a Cyberspace Security Expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.6
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Retry {attempt + 1}] Error calling GPT API: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
        return None

    def generate_additional_honeyword(self, original_password):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        honeyword = ''.join(random.sample(original_password, min(len(original_password), random.randint(6, 18))))
        while len(honeyword) < 6:
            honeyword += random.choice(chars)
        if honeyword[0] in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?":
            honeyword = random.choice(chars) + honeyword[1:]
        return honeyword[:18]

def print_result(honeywords, explanation):
    print("\nGenerated Honeywords:")
    for i in range(0, len(honeywords), 4):
        print(", ".join(honeywords[i:i + 4]))

    print("\nExplanation:")
    print(textwrap.fill(explanation, width=100))

if __name__ == "__main__":
    generator = StrongPasswordGenerator("Peking University", test_mode=True)
    original_password = "A@Jack135!"
    result = generator.generate(original_password)

    if result:
        print_result(result.get("honeywords", []), result.get("explanation", ""))
