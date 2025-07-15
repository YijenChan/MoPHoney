from openai import OpenAI
import json
import textwrap
import time

# Initialize OpenAI client，add your API here
client = OpenAI(
    api_key='',
    base_url=""
)

class DefaultPasswordHoneywordGenerator:
    def __init__(self, university):
        self.university = university
        self.messages = [
            {
                "role": "system",
                "content": f"You are a cybersecurity expert helping {university} protect its systems using honeywords."
            },
            {
                "role": "user",
                "content": "Default passwords are commonly used in systems before users change them. "
                           "To protect a system default password, we need to disguise it among commonly known weak default passwords."
            }
        ]

    def send_message_to_gpt(self, message, retries=3, delay=2):
        self.messages.append({"role": "user", "content": message})
        for attempt in range(retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.messages,
                    max_tokens=400,
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
            f"The password '{password}' is a system default password. "
            f"To prevent attackers from guessing it easily, we should NOT generate honeywords similar to '{password}'.\n\n"
            f"Instead, generate honeywords using **commonly known weak default passwords** as camouflage, "
            f"such as '123456', 'qwerty', 'password', 'guest123', 'testuser', 'changeme', 'welcome1', etc.\n"
            f"Mix '{password}' into the list without making it obvious or repeated. "
            f"This helps obscure the target among other plausible weak defaults."
        )
        self.send_message_to_gpt(init_instruction)

        final_instruction = (
            f"Now generate 20 honeywords according to the following rules:\n"
            f"1. Length between 6–18 characters;\n"
            f"2. At least two types of characters (upper/lowercase letters and digits);\n"
            f"3. No special characters, no passwords starting with numbers;\n"
            f"4. Do NOT include direct or modified variants of '{password}' (like Admin123, admin321, etc);\n"
            f"5. Use simple and real-world default-style passwords.\n\n"
            f"Return a JSON object with:\n"
            f" - 'honeywords': list of 20 strings\n"
            f" - 'explanation': a short paragraph why these honeywords help hide the real one."
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
        print(", ".join(honeywords[i:i+5]))

    print("\nExplanation:")
    wrapped = textwrap.fill(explanation, width=60)
    print(wrapped)

if __name__ == "__main__":
    generator = DefaultPasswordHoneywordGenerator("Peking University")
    password = "admin"
    result = generator.generate(password)

    if result:
        print_result(result)
