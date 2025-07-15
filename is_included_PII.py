import json
import re
import textwrap
import time
from openai import OpenAI

# Initialize OpenAI client (add your API key and base_url as needed)
client = OpenAI(
    api_key='',
    base_url=""
)

def extract_json_from_response(response_text):
    """
    Extract the first JSON object from the LLM response using regex.
    """
    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def evaluate_pii_risk(record, retries=3, delay=2):
    """
    Call GPT API to determine if a password uses PII information.
    Returns a dict with 'Brief Reason' and 'Tag': 4 (PII-based), 0 (not PII-based).
    """
    prompt = (
        f"Users may use their PII (Personally Identifiable Information) to construct passwords. "
        f"PII fields include: username, birthday, name, and email. "
        f"Analyze whether the password contains any form of the user's PII, including exact matches, substrings, or modified forms. "
        f"Given this record: {record}, return a JSON with two fields: 'Brief Reason' and 'Tag' (4 if PII is used, 0 if not). "
        f"Do not return anything except the JSON object."
    )

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Cyberspace Security Expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0
            )

            result = response.choices[0].message.content.strip()

            # Clean markdown formatting if present
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()

            json_str = extract_json_from_response(result)
            if json_str:
                return json.loads(json_str)
            else:
                print("[Warning] No valid JSON segment found.")
                return None

        except json.JSONDecodeError as e:
            print(f"[Error] Failed to parse JSON: {str(e)}")
            return None
        except Exception as e:
            print(f"[Error] GPT API call failed (attempt {attempt + 1}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

def print_result(result):
    """
    Pretty-print the result returned by GPT.
    """
    print("\nGPT Password Evaluation Result:")
    brief_reason = result.get("Brief Reason", "")
    tag = result.get("Tag", "")

    wrapped_reason = textwrap.fill(brief_reason, width=100)
    print("Brief Reason:")
    print(wrapped_reason)
    print(f"Tag: {tag}")

if __name__ == "__main__":
    record = ["SsanCat3", "supercat", "1995/05/02", "Zhangsan", "hao123@example.com"]
    result = evaluate_pii_risk(record)
    if result:
        print_result(result)
