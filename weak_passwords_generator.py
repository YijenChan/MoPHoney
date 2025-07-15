from openai import OpenAI
import json
import time
import textwrap

# Initialize OpenAI client — insert your API info below
client = OpenAI(
    api_key='',
    base_url=''
)

class WeakPasswordGenerator:
    def __init__(self, university):
        self.university = university
        self.messages = [
            {
                "role": "system",
                "content": f"Honeywords are decoy passwords used to detect unauthorized access. "
                           f"Please generate honeywords similar to the target password to safeguard the database security for {university}."
            },
            {
                "role": "user",
                "content": "Common weak password patterns often include repeated characters, sequential numbers, or simple letter-number combinations."
            }
        ]

    def send_message_to_gpt(self, message, retries=3, delay=2):
        self.messages.append({"role": "user", "content": message})
        for attempt in range(retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.messages,
                    max_tokens=300,
                    temperature=0.6
                )
                reply = response.choices[0].message.content.strip()
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            except Exception as e:
                print(f"Error calling GPT API (attempt {attempt + 1}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
        return None

    def generate(self, password):
        init_instruction = (
            f"Generate honeywords that are structurally similar to the password '{password}', which is a weak password. "
            f"These honeywords should follow common weak password patterns, such as simple character and number sequences, and slight rearrangements."
        )
        self.send_message_to_gpt(init_instruction)

        final_instruction = (
            f"Ensure that the newly generated honeywords meet the following conditions:\n"
            f"1. The length is between 6–18 characters;\n"
            f"2. Contains at least two types of characters: uppercase letters, lowercase letters, and numbers;\n"
            f"3. The new password cannot start with a number;\n"
            f"4. Cannot contain special symbols other than letters and numbers.\n\n"
            f"Generate 20 different honeywords from the given content, ensuring they are similar to the target password. "
            f"Present the result directly in JSON format, with two fields: 'honeywords' (list of generated passwords) and 'explanation'."
        )

        response = self.send_message_to_gpt(final_instruction)

        if response:
            response = response.replace("```json", "").replace("```", "").strip()
        else:
            print("No response received from GPT.")
            return None

        try:
            result = json.loads(response)
            honeywords = result.get("honeywords", [])
            if len(set(honeywords)) != len(honeywords):
                print("[Warning] Duplicate honeywords detected in output.")
            return result
        except json.JSONDecodeError:
            print(f"Invalid JSON returned:\n{response}")
            return None


def print_result(result):
    honeywords = result.get("honeywords", [])
    explanation = result.get("explanation", "")

    print("\nHoneywords:")
    for i in range(0, len(honeywords), 5):
        print(", ".join(honeywords[i:i + 5]))

    print("\nExplanation:")
    print(textwrap.fill(explanation, width=60))


if __name__ == "__main__":
    generator = WeakPasswordGenerator("Peking University")
    password = "qwe123"
    result = generator.generate(password)

    if result:
        print_result(result)
