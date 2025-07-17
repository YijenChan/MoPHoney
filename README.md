<img width="916" height="554" alt="{E99FE989-89FB-413B-A37E-10AD5BA46857}" src="https://github.com/user-attachments/assets/b1f8f09d-90b0-413d-8903-ca4641605641" /># MoPHoney: Honeyword Generation via Mixture of Prompts

> 🔐 This repository contains the official implementation of **MoPHoney**, a novel honeyword generation system based on a **Mixture-of-Prompts** strategy and **Adversarial Filtering**, proposed in our paper.

## 📌 Overview

Traditional honeyword schemes often suffer from poor realism, overlap between users, or limited resistance to modern AI-driven guessing attacks. **MoPHoney** addresses these challenges by introducing:

* A **prompt-mixing mechanism** to generate diverse honeywords using LLMs.
* A **LightGBM router** trained on structural and semantic features to guide the generation.
* A **threat-LLM-based adversarial filter** that removes low-quality or unrealistic honeywords.
* A **global shuffle strategy** to obscure per-user honeyword groups and ensure cross-user unlinkability.

![Architecture](<img width="916" height="554" alt="{E99FE989-89FB-413B-A37E-10AD5BA46857}" src="https://github.com/user-attachments/assets/357d8b0e-a9d8-4219-96f7-333ce9fa123e" />
) <!-- Replace with your actual image path -->

---

## 📁 Project Structure

| File / Folder                | Description                                                              |
| ---------------------------- | ------------------------------------------------------------------------ |
| `Mixture_of_prompts.py`      | Main honeyword generation script using prompt mixing and router weights  |
| `MoP_Router.py`              | Loads LightGBM router model for password class probability prediction    |
| `feature_extraction.py`      | Extracts structural + semantic features for password classification      |
| `adversarial_filtering.py`   | Filters generated honeywords using GPT-4o as a simulated adversary       |
| `global_shuffle.py`          | Applies per-user salting + global shuffling, writes HoneyChecker mapping |
| `train_lightgbm.py`          | Trains the LightGBM classification router                                |
| `train_label.py`             | Prepares labeled password features for training                          |
| `password_hash.py`           | Hashes password dataset for LSH-based similarity search                  |
| `similar_password_finder.py` | Recommends similar passwords via LSH and hybrid similarity metrics       |
| `benchmark_dataset.csv`      | Base password dataset                                                    |
| `router_model.txt`           | Pretrained LightGBM routing model                                        |

---

## 🚀 How to Use

### 1. Setup

Ensure your environment supports:

* Python 3.8+
* `openai`, `lightgbm`, `pandas`, `sklearn`, `numpy`, `Levenshtein`, etc.

```bash
pip install -r requirements.txt
```

*(create `requirements.txt` if needed)*

---

### 2. Step-by-Step Pipeline

```bash
# Step 1: Preprocess base password dataset
python password_hash.py

# Step 2: Train the LightGBM router
python train_label.py
python train_lightgbm.py

# Step 3: Generate honeywords using MoPHoney
python Mixture_of_prompts.py

# Step 4: Filter honeywords with adversarial LLM
python adversarial_filtering.py

# Step 5: Apply global shuffle + honeychecker mapping
python global_shuffle.py
```

---

## 🧪 Sample Output

```json
{
  "password": "abc123",
  "honeywords": [
    "abd123", "abc321", "acb123", "abb123", ...
  ]
}
```

---

## 📊 Model Details

* Router Model: LightGBM trained on 4 password classes (weak, strong, PII-style, unknown).
* Semantic signal: Extracted via GPT reasoning over PII presence.
* Filtering agent: GPT-4o adversary eliminates unrealistic honeywords.

---

## 🔐 Security Advantages

* **Realism**: Prompts tailored per password type improve believability.
* **Unlinkability**: Global shuffle prevents structural overlap between users.
* **Adaptive**: Threat-LLM filtering models modern attacker behavior.
* **Extensible**: Prompt templates and routers are modular and configurable.

---

## 📄 Citation

To cite this work:

```bibtex
@article{MoPHoney2024,
  title={MoPHoney: Honeyword Generation via Mixture-of-Prompts and Threat-Guided Filtering},
  author={Chen, Yiren},
  year={2024},
  journal={ArXiv Preprint},
}
```

---

## 📬 Contact

For questions or collaborations, please open an issue or contact \[[chenyiren@iie.ac.cn]].

