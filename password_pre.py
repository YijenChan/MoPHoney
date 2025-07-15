import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Define LSH hash function class
class LSH:
    def __init__(self, num_hashes, input_dim, seed=42):
        self.num_hashes = num_hashes
        self.input_dim = input_dim
        np.random.seed(seed)
        self.hash_funcs = [self._generate_random_hash(self.input_dim) for _ in range(num_hashes)]

    def _generate_random_hash(self, input_dim):
        return np.random.randn(input_dim)

    def hash_password(self, password_vector):
        return [1 if np.dot(self.hash_funcs[i], password_vector) > 0 else 0 for i in range(self.num_hashes)]

# Process each password and compute hash
def process_password(pwd, hashed_results, num_hashes, seed):
    pwd = str(pwd).strip()
    if len(pwd) == 0:
        return  # Skip empty passwords

    try:
        vectorizer = CountVectorizer(analyzer='char', ngram_range=(1, 3), max_features=15)
        lsh = LSH(num_hashes=num_hashes, input_dim=15, seed=seed)

        vector = vectorizer.fit_transform([pwd]).toarray()[0]
        vector = np.pad(vector, (0, max(0, lsh.input_dim - len(vector))), 'constant')[:lsh.input_dim]

        hashed_password = lsh.hash_password(vector)
        hashed_results.append((pwd, hashed_password))

    except Exception as e:
        print(f"Error processing password '{pwd}': {e}")

# Preprocess and store password hashes
def preprocess_hashes(csv_file, output_file, num_hashes=10, seed=42):
    try:
        df = pd.read_csv(csv_file, usecols=['Password'])
    except Exception as e:
        raise Exception(f"Failed to read CSV file: {str(e)}")

    hashed_results = []
    for pwd in df['Password']:
        process_password(pwd, hashed_results, num_hashes, seed)

    pd.DataFrame(hashed_results, columns=['Password', 'Hash']).to_csv(output_file, index=False)
    print(f"Hashed results saved to {output_file}")

# Example call
if __name__ == "__main__":
    preprocess_hashes('shuffle_samples.csv', 'shuffle_samples_hash.csv')
