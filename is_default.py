from openai import OpenAI
import json
import textwrap
import time

# Initialize OpenAI client (Ensure your API key is properly set)
client = OpenAI(
    api_key='',
    base_url=""
)

def evaluate_password_strength(password, retries=3, delay=2):
    """
    Call the GPT API to evaluate if the given password is a system default password.
    Returns a JSON result with two fields: 'Brief Reason' and 'Tag' (1 for default, 0 for not default).
    Implements retry logic for robustness.
    """
    prompt = (f"If users do not change the system default password and use it directly, it may cause security incidents."
              f"Evaluate whether the password '{password}' is a system default password. "
              "Return the result in JSON format with two fields: 'Brief Reason' and 'Tag' (1 for default, 0 for not default).")

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Cyberspace Security Expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0
            )

            result = response.choices[0].message.content.strip()

            # Clean and parse JSON response
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "").strip()

            result_dict = json.loads(result)
            return result_dict

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            return None
        except Exception as e:
            print(f"Error calling GPT API (attempt {attempt + 1}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)  # Retry after delay
    return None

def print_result(result):
    """
    Print the LLM's password evaluation result in a readable format.
    """
    print("GPT Password Evaluation Result:")

    brief_reason = result.get("Brief Reason", "")
    tag = result.get("Tag", "")

    # Format and print the brief reason in wrapped lines
    wrapped_reason = textwrap.fill(brief_reason, width=100)

    print("Brief Reason:")
    print(wrapped_reason)
    print(f"Tag: {tag}")

if __name__ == "__main__":
    password = "admin"  # Example password to evaluate
    result = evaluate_password_strength(password)

    if result:
        print_result(result)
