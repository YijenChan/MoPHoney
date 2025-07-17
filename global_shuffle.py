import json
import hashlib
import random
import uuid

# ========== Salt and Hash ========== #
def salted_hash(salt: str, word: str) -> str:
    combined = salt + word
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

# ========== Global Shuffle Main Function ========== #
def global_shuffle(input_json: str, output_json: str, checker_json: str):
    with open(input_json, "r", encoding="utf-8") as f:
        records = json.load(f)

    global_entries = []
    honeychecker = []

    for user_id, record in enumerate(records):
        real_pw = record["password"]

        # Parse honeywords (single string to list)
        honeywords_line = record.get("honeywords", [""])[0]
        honeywords = [w.strip() for w in honeywords_line.split(",") if w.strip()]

        # Combine real password and honeywords
        full_list = [real_pw] + honeywords

        # Generate a unique salt per user
        user_salt = uuid.uuid4().hex  # alternatively: hashlib.sha256(str(user_id).encode()).hexdigest()

        # Salt-hash all entries
        user_entries = []
        for local_idx, word in enumerate(full_list):
            hashed = salted_hash(user_salt, word)
            user_entries.append({
                "user_id": user_id,
                "local_index": local_idx,
                "is_real": local_idx == 0,  # first one is the real password
                "salt": user_salt,
                "word": word,
                "hash": hashed
            })

        global_entries.extend(user_entries)

    # Shuffle the entire password list globally
    random.shuffle(global_entries)

    # Build honeychecker mapping table
    final_output = []
    for idx, entry in enumerate(global_entries):
        if entry["is_real"]:
            honeychecker.append({
                "user_id": entry["user_id"],
                "real_index": idx,
                "hash": entry["hash"]
            })

        # Output only the hash (omit user info)
        final_output.append({
            "hash": entry["hash"]
        })

    # Write the global shuffled password file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

    # Write honeychecker file
    with open(checker_json, "w", encoding="utf-8") as f:
        json.dump(honeychecker, f, ensure_ascii=False, indent=2)

    print(f"✅ Global password table saved to: {output_json}")
    print(f"✅ HoneyChecker mapping saved to: {checker_json}")
    print(f"🔢 Total entries: {len(global_entries)}, Users: {len(records)}")

# ========== Entry Point ========== #
if __name__ == "__main__":
    global_shuffle(
        input_json="filtered_honeywords.json",
        output_json="global_shuffled_passwords.json",
        checker_json="honeychecker.json"
    )
