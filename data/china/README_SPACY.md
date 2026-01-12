Using the spaCy-backed analyzer

1) Create a Python environment and install dependencies (WSL/Ubuntu recommended):

```bash
python -m pip install -r requirements_spacy.txt
python -m textblob.download_corpora
python -m spacy download en_core_web_sm
```

2) Run the analyzer using spaCy NER (preferred):

```bash
python analyze_with_spacy.py china_speeches.csv --ner spacy --spacy-model en_core_web_sm --top 200
```

3) Fallback to TextBlob-only NER (less accurate):

```bash
python analyze_with_spacy.py china_speeches.csv --ner textblob
```

Outputs will be in `outputs_spacy/` next to the input CSV, with `{year}_noun_phrases.csv` and `{year}_entities.csv`.

Notes

- `spaCy` provides robust NER and will greatly reduce garbage tokens like `ssss` or `#NAME?`.
- `TextBlob` entity heuristic remains as a fallback.
- If you want spaCy large models, change `--spacy-model` accordingly.
