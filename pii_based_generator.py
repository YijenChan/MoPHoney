import json
import random
import textwrap
import time
from openai import OpenAI

# Initialize OpenAI client (fill your credentials if needed)
client = OpenAI(
    api_key='',
    base_url=''
)

class PIIGenerator:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.messages = [
            {"role": "system", "content": "You are a Cyberspace Security Expert."},
            {"role": "user", "content": (
                "PII-based password refers to the possibility that users may use their PII information "
                "(such as username, birthday, name, email) to construct their password. "
                "For example, a user with the name Luo Wei may create passwords like luowei123 or lw1234. "
                "I will provide records with passwords and PII. "
                "Recommended strategy: cut the password into substrings, randomly pick a PII item (only use the part before '@' from email), "
                "combine them in different orders, and optionally add 1–2 random characters at the end."
            )}
        ]

    def send_message_to_gpt(self, message, retries=3, delay=2):
        self.messages.append({"role": "user", "content": message})
        for attempt in range(retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.messages,
                    max_tokens=500,
                    temperature=0.6
                )
                reply = response.choices[0].message.content.strip()
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            except Exception as e:
                print(f"[Attempt {attempt + 1}] GPT API error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
        return None

    def generate(self, password, username, birthday, name, email):
        init_instruction = (
            f"Now, I will give you a real instance. Please generate honeywords based on the input "
            f"[({password}, {username}, {birthday}, {name}, {email})]. "
            f"Split the password into segments, choose a PII value (email is before @), and recombine them in diverse ways. "
            f"Keep honeywords between 6–12 characters. Add 1–2 random suffix characters only with low probability."
        )
        self.send_message_to_gpt(init_instruction)

        final_instruction = (
            f"Now, generate 20 honeywords based on the strategy and input above. Make sure:\n"
            f"1. Length is 6–18 characters;\n"
            f"2. Use at least two types among uppercase, lowercase, numbers, or special symbols;\n"
            f"3. Cannot start with special symbol or number.\n"
            f"Return JSON with 'honeywords' and 'explanation' fields ONLY, no extra text or comments."
        )

        response = self.send_message_to_gpt(final_instruction)
        if not response:
            return None

        # Remove markdown wrapping if present
        response = response.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(response)
            honeywords = parsed.get("honeywords", [])
            explanation = parsed.get("explanation", "")

            # Filter by basic constraints
            valid_honeywords = [h for h in honeywords if 6 <= len(h) <= 12]

            if len(set(valid_honeywords)) != len(valid_honeywords):
                print("[Warning] Duplicate honeywords detected.")

            # Supplement if less than 20
            while len(valid_honeywords) < 20:
                modified = self.modify_honeyword(random.choice(valid_honeywords))
                if modified not in valid_honeywords:
                    valid_honeywords.append(modified)

            return {
                "honeywords": valid_honeywords[:20],
                "explanation": "20 unique honeywords based on provided PII and password. Local variations added."
            }

        except json.JSONDecodeError:
            print(f"Invalid JSON returned:\n{response}")
            return None

    def modify_honeyword(self, honeyword):
        honeyword = ''.join(
            c.upper() if random.random() < 0.2 else c.lower() for c in honeyword
        )
        if len(honeyword) < 12 and random.random() < 0.2:
            honeyword += ''.join(
                random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(random.randint(1, 2))
            )
        if len(honeyword) >= 6 and random.random() < 0.2:
            index = random.randint(0, len(honeyword) - 1)
            replacement = random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
            honeyword = honeyword[:index] + replacement + honeyword[index + 1:]
        return honeyword

if __name__ == "__main__":
    generator = PIIGenerator()
    password = "zs123a"
    username = "supercat"
    birthday = "1999-05-02"
    name = "zhangsan"
    email = "hao123@example.com"

    result = generator.generate(password, username, birthday, name, email)

    if result:
        honeywords = result.get("honeywords", [])
        explanation = result.get("explanation", "")
        for i in range(0, len(honeywords), 4):
            print(", ".join(honeywords[i:i + 4]))
        print("\nExplanation:")
        print(textwrap.fill(explanation, width=60))
