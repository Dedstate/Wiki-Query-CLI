# Wiki Query CLI ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Transform natural‑language requests into concise Wikipedia summaries, powered by a free neural model.**

---

> **Wiki Query CLI** provides a straightforward command‑line interface to:
> 1. Reformulate your question into an optimal Wikipedia search query using a lightweight instruction‑tuned T5 model.  
> 2. Fetch and display a clean summary of the top matching article, with interactive disambiguation when needed.

---

## 🌟 Features

- **Smart Query Rewrite**  
  Uses a free, open‑source HF model (default `google/flan‑t5‑base`) to turn any user prompt into an effective Wikipedia search term.

- **Interactive Disambiguation**  
  If multiple articles match, you’ll see the top 5 titles and can choose which one to fetch.

- **Robust Error Handling**  
  - Cleans up stray hyphens and special characters.  
  - Falls back to auto‑suggest if a page title lookup fails.  
  - Gracefully handles pages not found or disambiguation loops.

- **Sentence‑Limit Control**  
  Use `--sentences` to specify how many sentences of the summary you need.

- **Lightweight & Local**  
  Runs entirely on your machine (CPU or GPU). No external API calls or paid subscriptions required.

- **Version Flag**  
  Quickly check your installed version with `--version`.

---

## 🚀 Quickstart

> **Requirements:**  
> - Python 3.10+  
> - Git  
> - Poetry (recommended)

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your‑org/wiki‑query‑cli.git
   cd wiki‑query‑cli
   ```

2. **Install dependencies**  
   ```bash
   poetry install
   ```

3. **Run the CLI**  
   - **Ask a single question**  
     ```bash
     poetry run python wiki_query_cli.py ask "Who is Ada Lovelace?"
     ```
   - **Limit output to 2 sentences**  
     ```bash
     poetry run python wiki_query_cli.py ask "Tell me about Python programming language" --sentences 2
     ```
   - **Use a different HF model**  
     ```bash
     poetry run python wiki_query_cli.py ask "What is quantum entanglement?" --model google/flan‑t5‑small
     ```

4. **Check version**  
   ```bash
   poetry run python wiki_query_cli.py --version
   ```

---

## ⚙️ Configuration

You can customize where Hugging Face caches model weights:

1. **Set `TRANSFORMERS_CACHE`**  
   ```bash
   export TRANSFORMERS_CACHE=/path/to/your/cache
   ```
2. **Or use the `--cache-dir` option**  
   ```bash
   poetry run python wiki_query_cli.py ask "Your question" --cache-dir /path/to/dir
   ```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request on GitHub.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
