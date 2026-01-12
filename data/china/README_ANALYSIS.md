Usage

1. Install dependencies (in WSL/Ubuntu):

```bash
python -m pip install -r requirements.txt
python -m textblob.download_corpora
```

2. Run the analyzer (defaults detect `content` and `date` columns):

```bash
python analyze_yearly_textblob.py china_speeches.csv --top 200
```

3. Output CSVs will be in `outputs_textblob/` with `{year}_noun_phrases.csv` and `{year}_entities.csv`.

Notes

- `TextBlob` noun phrase extraction uses the `pattern` library; installing corpora with `textblob.download_corpora` improves results.
- Entity extraction here is a simple proper-noun heuristic using POS tags (NNP/NNPS). For robust NER prefer spaCy or flair.
