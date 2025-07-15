from openai import OpenAI
import json
import textwrap
import time

# Initialize OpenAI client
client = OpenAI(
    api_key='',
    base_url="https://apix.ai-gaochao.cn/v1"
)

def evaluate_password_strength(password, retries=3, delay=2):
    """
    Call GPT API to evaluate whether the given password is weak or strong.
    Returns a JSON with 'Brief Reason' and 'Tag': 2 for weak, 3 for strong.
    """

    prompt = (f"Evaluate the password '{password}' for weakness. "
              f"Recommended criteria: "
              "1) Weak if it contains fewer than 8 characters, "
              "2) Weak if it only contains letters, "
              "3) Strong if it includes uppercase, lowercase, digits, and special characters. "
              "Feel free to use your own judgment as well. "
              "Return the result in JSON format with two fields: 'Brief Reason' and 'Tag' "
              "(2 for weak, 3 for strong).")

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Cyberspace Security Expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=120,
                temperature=0
            )

            result = response.choices[0].message.content.strip()

            # Clean Markdown formatting
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()

            result_dict = json.loads(result)
            return result_dict

        except json.JSONDecodeError as e:
            print(f"[Error] Failed to decode GPT JSON: {str(e)}")
            return None
        except Exception as e:
            print(f"[Error] GPT API call failed (attempt {attempt + 1}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

def print_result(result):
    """
    Print GPT's evaluation result in readable format.
    """
    print("GPT Password Evaluation Result:")
    brief_reason = result.get("Brief Reason", "")
    tag = result.get("Tag", "")

    wrapped_reason = textwrap.fill(brief_reason, width=100)
    print("Brief Reason:")
    print(wrapped_reason)
    print(f"Tag: {tag}")

if __name__ == "__main__":
    password = "qwe123"  # Example test password
    result = evaluate_password_strength(password)
    if result:
        print_result(result)
