#!/usr/bin/env python3
"""
TF-IDF Analysis: Identify unique vocabulary for China vs Russia speeches.

This script calculates TF-IDF scores to find words that are distinctive
and unique to each country's diplomatic speeches.

Usage:
  python3 tfidf_analysis.py
"""

import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import string
import re
from nltk.corpus import stopwords
import nltk

# Download stopwords if needed
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

def load_data(filepath):
    """Load processed speeches from JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_text(text):
    """Clean text: remove encoding artifacts and non-alphabetic characters."""
    # Fix encoding artifacts (UTF-8 issues)
    text = text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
    # Remove control characters and other encoding artifacts
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    # Remove common encoding artifacts
    text = re.sub(r'â|é|ñ|ü|ã|ç|ê|î|ï|ó|ô|õ|ú|û|ý|à|á|è|ì|ù', '', text)
    return text

def is_valid_word(word):
    """Filter out invalid words."""
    # Skip if too short
    if len(word) < 3:
        return False
    # Skip if too long (likely encoding artifacts or concatenated words)
    if len(word) > 25:
        return False
    # Skip if contains only digits
    if word.isdigit():
        return False
    # Skip if contains mixed case in unusual patterns (likely acronyms/corrupted)
    if sum(1 for c in word if c.isupper()) > 2 and len(word) < 6:
        return False
    # Skip if contains non-alphabetic characters
    if not all(c.isalpha() or c == '-' for c in word):
        return False
    return True

def main():
    print("=" * 70)
    print("TF-IDF Analysis: Unique Vocabulary by Country")
    print("=" * 70)
    
    # Load data
    print("\nLoading processed speeches...")
    data = load_data('CH_RU_processed_lemmatized.json')
    df = pd.DataFrame(data)
    
    print(f"Total speeches: {len(df)}")
    print(f"China speeches: {len(df[df['country'] == 'China'])}")
    print(f"Russia speeches: {len(df[df['country'] == 'Russia'])}")
    
    # Create document-level corpus (one document per country)
    # Combine all speeches by country into single documents
    print("\nCreating country-level documents...")
    china_text = ' '.join(df[df['country'] == 'China']['processed_text'].astype(str).tolist())
    russia_text = ' '.join(df[df['country'] == 'Russia']['processed_text'].astype(str).tolist())
    
    # Clean the text
    print("Cleaning text...")
    china_text = clean_text(china_text)
    russia_text = clean_text(russia_text)
    
    documents = [china_text, russia_text]
    countries = ['China', 'Russia']
    
    # Build custom stopword list
    stop_words = set(stopwords.words('english'))
    # Add common names, abbreviations, and artifacts that appear in your data
    custom_stops = {
        'said', 'new', 'would', 'also', 'year', 'year', 'country', 'countries',
        'could', 'first', 'way', 'one', 'two', 'three', 'time', 'day', 'come',
        'state', 'make', 'person', 'people', 'government', 'like', 'well',
        'say', 'good', 'man', 'woman', 'well', 'thing', 'hand', 'part'
    }
    stop_words.update(custom_stops)
    
    # Calculate TF-IDF with improved filtering
    print("\nCalculating TF-IDF scores...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        min_df=1,
        max_df=0.95,
        ngram_range=(1, 1),  # Single words only
        stop_words=list(stop_words),
        lowercase=True,
        token_pattern=r'\b[a-z]+\b'  # Only alphabetic words
    )
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Get feature names (words)
    feature_names = np.array(vectorizer.get_feature_names_out())
    
    # Extract top words for each country
    results = {}
    
    for idx, country in enumerate(countries):
        # Get TF-IDF scores for this country
        tfidf_scores = tfidf_matrix[idx].toarray()[0]
        
        # Get indices of non-zero scores, sorted by value descending
        top_indices = np.argsort(tfidf_scores)[::-1][:100]
        
        top_words = []
        for rank, word_idx in enumerate(top_indices, 1):
            word = feature_names[word_idx]
            score = tfidf_scores[word_idx]
            
            # Apply additional filtering
            if not is_valid_word(word):
                continue
            
            top_words.append({
                'rank': rank,
                'word': word,
                'tfidf_score': float(score),
                'country': country
            })
        
        results[country] = top_words
        
        print(f"\n--- Top 20 Distinctive Words for {country} ---")
        for item in top_words[:20]:
            print(f"  {item['rank']:2d}. {item['word']:<20s} (TF-IDF: {item['tfidf_score']:.4f})")
    
    # Save results to JSON
    print("\n\nSaving results...")
    
    # Combined results
    all_results = results['China'] + results['Russia']
    with open('tfidf_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print("  ✓ Saved tfidf_results.json (top 100 words per country)")
    
    # China-specific
    with open('tfidf_results_china.json', 'w', encoding='utf-8') as f:
        json.dump(results['China'], f, indent=2, ensure_ascii=False)
    print("  ✓ Saved tfidf_results_china.json")
    
    # Russia-specific
    with open('tfidf_results_russia.json', 'w', encoding='utf-8') as f:
        json.dump(results['Russia'], f, indent=2, ensure_ascii=False)
    print("  ✓ Saved tfidf_results_russia.json")
    
    # Also save as CSV for easier viewing
    df_results = pd.DataFrame(all_results)
    df_results.to_csv('tfidf_results.csv', index=False)
    print("  ✓ Saved tfidf_results.csv")
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    
    # Additional insights
    print("\n--- Insights ---")
    china_words = set([w['word'] for w in results['China'][:200]])
    russia_words = set([w['word'] for w in results['Russia'][:200]])
    
    unique_to_china = china_words - russia_words
    unique_to_russia = russia_words - china_words
    shared = china_words & russia_words

    print(f"Words unique to China (top 200):   {len(unique_to_china)}")
    print(f"Words unique to Russia (top 200):  {len(unique_to_russia)}")
    print(f"Words in both (top 200):           {len(shared)}")

    if unique_to_china:
        print(f"\nUnique to China: {', '.join(sorted(unique_to_china)[:10])}...")
    if unique_to_russia:
        print(f"Unique to Russia: {', '.join(sorted(unique_to_russia)[:10])}...")

if __name__ == '__main__':
    main()
