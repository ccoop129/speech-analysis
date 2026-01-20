import pandas as pd
import spacy
from collections import Counter
import json

# Load spaCy model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

# Increase max_length to handle longer texts
nlp.max_length = 2000000

# UK to US spelling mappings
UK_TO_US = {
    'colour': 'color', 'civilization': 'civilization', 'coloured': 'colored', 'colours': 'colors',
    'honour': 'honor', 'honoured': 'honored', 'honours': 'honors',
    'favour': 'favor', 'favoured': 'favored', 'favours': 'favors',
    'labour': 'labor', 'laboured': 'labored', 'labours': 'labors',
    'neighbour': 'neighbor', 'neighbours': 'neighbors',
    'behaviour': 'behavior', 'behaviours': 'behaviors',
    'centre': 'center', 'centred': 'centered', 'centres': 'centers',
    'theatre': 'theater', 'theatres': 'theaters',
    'metre': 'meter', 'metres': 'meters',
    'organisation': 'organization', 'organisations': 'organizations',
    'realise': 'realize', 'realised': 'realized',
    'analyse': 'analyze', 'analysed': 'analyzed',
    'defence': 'defense', 'defence\'s': 'defense\'s',
    'licence': 'license', 'licences': 'licenses',
    'practice': 'practice',  # Both used as noun
    'travelling': 'traveling', 'travelled': 'traveled',
    'cancelled': 'canceled',
    'recognised': 'recognized', 'recognise': 'recognize',
}

# Semantic normalization: map related terms to canonical form
SEMANTIC_MAP = {
    # China
    'china': 'china',
    'chinese': 'china',
    'prc': 'china',
    'beijing': 'china',
    
    # Russia
    'russia': 'russia',
    'russian': 'russia',
    'moscow': 'russia',
    
    # Asia
    'asia': 'asia',
    'asian': 'asia',
    
    # Europe
    'europe': 'europe',
    'european': 'europe',
    
    # Africa
    'africa': 'africa',
    'african': 'africa',

    #India
    'india': 'india',
    'indian': 'india',
    'new_delhi': 'india',
    'new delhi': 'india',

    #Indonesia
    'indonesia': 'indonesia',
    'indonesian': 'indonesia',
    'jakarta': 'indonesia',

    #United Kingdom
    'uk': 'united_kingdom',
    'u.k.': 'united_kingdom',
    'united_kingdom': 'united_kingdom',
    'united kingdom': 'united_kingdom', 
    'britain': 'united_kingdom',
    'british': 'united_kingdom',
    'london': 'united_kingdom',
    'England': 'united_kingdom',
    'english': 'united_kingdom',

    # Australia
    'australia': 'australia',
    'australian': 'australia',
    'canberra': 'australia',

    #Germany
    'germany': 'germany',
    'german': 'germany',
    'berlin': 'germany',

    #France
    'france': 'france',
    'french': 'france',
    'paris': 'france',

    #Japan
    'japan': 'japan',
    'japanese': 'japan',
    'tokyo': 'japan',
    #South Korea
    'south_korea': 'south_korea',
    'south korea': 'south_korea',
    'seoul': 'south_korea',

    #North Korea
    'north_korea': 'north_korea',
    'north korea': 'north_korea',
    'pyongyang': 'north_korea',
    'north_korean': 'north_korea',
    'north koreans': 'north_korea',
    'north korean': 'north_korea',
    'north koreans': 'north_korea',

    #Iran
    'iran': 'iran',
    'iranian': 'iran',
    'tehran': 'iran',

    # Saudi Arabia
    'saudi_arabia': 'saudi_arabia',
    'saudi arabia': 'saudi_arabia',
    'saudi': 'saudi_arabia',
    'riyadh': 'saudi_arabia',
    'saudi_arabian': 'saudi_arabia',
    'saudi arabian': 'saudi_arabia',

    # UAE
    'uae': 'uae',
    'u.a.e.': 'uae',
    'united_arab_emirates': 'uae',
    'united arab emirates': 'uae',
    'abu_dhabi': 'uae',
    'abu dhabi': 'uae',
    'emirati': 'uae',
    'emirates': 'uae',

    #Italy
    'italy': 'italy',
    'italian': 'italy',
    'rome': 'italy',

    #Singapore
    'singapore': 'singapore',
    'singaporean': 'singapore',
    'singaporeans': 'singapore',

  #Palestine
    'palestine': 'palestine',
    'palestinian': 'palestine',
    'ramallah': 'palestine',
    'palestinians': 'palestine',
    'palestinian authority': 'palestine',

# Canada
    'canada': 'canada',
    'canadian': 'canada',
    'ottawa': 'canada',

    #Turkey 
    'turkey': 'turkey',
    'turkish': 'turkey',
    'ankara': 'turkey',
    'turkiye': 'turkey',

    #Taiwan
    'taiwan': 'taiwan',
    'taiwanese': 'taiwan',
    'taipei': 'taiwan',


    
    #Brazil
    'brazil': 'brazil',
    'brazilian': 'brazil',
    'brasil': 'brazil',
    'brasileiro': 'brazil',
    'brasileira': 'brazil',
    'brasilia': 'brazil',

    #Kazakhstan
    'kazakhstan': 'kazakhstan',
    'kazakhstani': 'kazakhstan',
    'nur_sultan': 'kazakhstan',
    'astana': 'kazakhstan',

    #Ukraine
    'ukraine': 'ukraine',
    'ukrainian': 'ukraine',
    'kyiv': 'ukraine',
    'kiev': 'ukraine',

    #Kyrgystan
    'kyrgyzstan': 'kyrgyzstan',
    'kyrgyz': 'kyrgyzstan',
    'bishkek': 'kyrgyzstan',

    #Belarus
    'belarus': 'belarus',
    'belarussian': 'belarus',
    'minsk': 'belarus',

    #Israel
    'israel': 'israel',
    'israeli': 'israel',
    'jerusalem': 'israel',

    #Vietnam
    'vietnam': 'vietnam',
    'vietnamese': 'vietnam',
    'hanoi': 'vietnam',

    #Thailand
    'thailand': 'thailand',
    'thai': 'thailand',
    'bangkok': 'thailand',

    #Tibet
    'tibet': 'tibet',
    'tibetan': 'tibet',
    'lhasa': 'tibet',

    #Hong Kong
    'hong_kong': 'hong_kong',
    'hong kong': 'hong_kong',
    'hk': 'hong_kong',
    'h.k.': 'hong_kong',
    'hongkong': 'hong_kong',
    'hongkongese': 'hong_kong',



    # Middle East
    'middle_east': 'middle_east',
    'middle east': 'middle_east',
    'MENA': 'middle_east',

    #Military
    'military': 'military',
    'militia': 'military',
    'armed_forces': 'military',
    'armed forces': 'military',
    'army': 'military',
    'navy': 'military',
    'air_force': 'military',
    'air force': 'military',

    #civilization
    'civilization': 'civilization',
    'civilisations': 'civilization',
    'civilizations': 'civilization',
    'civilisation': 'civilization',
    
    # Americas
    'america': 'america',
    'american': 'america',
    'usa': 'america',
    'us': 'america',
    'united_states': 'america',
    'united_states_of_america': 'america',
    'united states': 'america',
    'united states of america': 'america',
    
    # United Nations
    'un': 'united_nations',
    'u.n.': 'united_nations',
    
    # Development-related
    'develop': 'develop',
    'developing': 'develop',
    'developed': 'develop',
    'development': 'develop',
    
    # Cooperation
    'cooperate': 'cooperate',
    'cooperation': 'cooperate',
    'cooperative': 'cooperate',
    
    # Partnership
    'partnership': 'partnership',
    'partner': 'partnership',
    'partners': 'partnership',

    #European Union
    'eu': 'european_union',
    'e.u.': 'european_union',
    'european_union': 'european_union',
    'european union': 'european_union',
    'brussels': 'european_union',

    #NATO
    'nato': 'nato',
    'north_atlantic_treaty_organization': 'nato',
    'north atlantic treaty organization': 'nato',
    'brussels': 'nato',

    #ASEAN
    'asean': 'asean',
    'association_of_southeast_asian_nations': 'asean',
    'association of southeast asian nations': 'asean',
    'jakarta': 'asean',
    
    #SCO
    'sco': 'sco',
    'shanghai_cooperation_organization': 'sco',
    'shanghai cooperation organization': 'sco',
    'beijing': 'sco',

    #G7
    'g7': 'g7',
    'group_of_seven': 'g7',
    'group of seven': 'g7',
    'g8': 'g7',
    'group_of_eight': 'g7',
    'group of eight': 'g7',

    
    
    #Pakistan
    'pakistan': 'pakistan',
    'pakistani': 'pakistan',
    'islamabad': 'pakistan',

    #Syria
    'syria': 'syria',
    'syrian': 'syria',
    'damascus': 'syria',



    # Sovereignty/Independence
    'sovereign': 'sovereignty',
    'sovereignty': 'sovereignty',

    #Independence
    'independent': 'independence',
    'independence': 'independence',
    
    # Peace/Peaceful
    'peace': 'peace',
    'peaceful': 'peace',
    
    # Security
    'secure': 'security',
    'security': 'security',
    
    # Trade
    'trade': 'trade',
    'trader': 'trade',
    'commerce': 'trade',
    'commercial': 'trade',
    
    # Agreement/Accord
    'agreement': 'agreement',
    'accord': 'agreement',
    'treaty': 'agreement',
    
    # Dialogue/Discussion
    'dialogue': 'dialogue',
    'discussion': 'dialogue',
    'talk': 'dialogue',
}

def normalize_spelling(word):
    """Convert UK spellings to US spellings."""
    lower_word = word.lower()
    return UK_TO_US.get(lower_word, lower_word)

def apply_semantic_normalization(word):
    """Apply semantic normalization to group related words."""
    # Replace underscores with spaces for multi-word entries
    word_with_underscore = word.replace(' ', '_')
    normalized = SEMANTIC_MAP.get(word_with_underscore, word)
    return normalized.replace('_', ' ')

def process_text(text):
    """Lemmatize, normalize, and filter text. Returns list of processed words."""
    doc = nlp(text.lower())
    processed_words = []
    
    # Keep only meaningful parts of speech
    # NOUN (NN), VERB (VB), ADJ (JJ), ADV (RB)
    keep_pos = {'NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN'}
    
    for token in doc:
        # Skip stop words and punctuation
        if token.is_stop or token.is_punct:
            continue
        
        # Keep only meaningful POS
        if token.pos_ not in keep_pos:
            continue
        
        # Lemmatize
        lemma = token.lemma_.lower()
        
        # Normalize UK/US spelling
        lemma = normalize_spelling(lemma)
        
        # Apply semantic normalization (group related words)
        lemma = apply_semantic_normalization(lemma)
        
        # Skip very short words (likely noise)
        if len(lemma) < 3:
            continue
        
        processed_words.append(lemma)
    
    return processed_words

# Load data
print("Loading China_Russia_Speeches.csv...")
df = pd.read_csv("China_Russia_Speeches.csv", encoding="latin1")

# Process by country
countries = ['China', 'Russia']
results = {}

for country in countries:
    print(f"\nProcessing {country} speeches...")
    
    # Filter by country
    country_df = df[df['country'] == country]
    print(f"  Found {len(country_df)} speeches")
    
    # Process each speech individually to avoid memory issues
    print(f"  Lemmatizing and filtering text...")
    word_counts = Counter()
    
    for idx, content in enumerate(country_df['content'].astype(str).fillna('')):
        if idx % 100 == 0:
            print(f"    Processing speech {idx}/{len(country_df)}...")
        processed_words = process_text(content)
        word_counts.update(processed_words)
    
    # Get top 1000
    top_1000 = word_counts.most_common(1000)
    
    results[country] = top_1000
    
    print(f"  Top 1000 words identified")
    print(f"  Total unique words (top 1000): {len(top_1000)}")
    print(f"  Most common words: {', '.join([w[0] for w in top_1000[:10]])}")

# Save results to JSON files
print("\nSaving results...")
for country in countries:
    filename = f"{country.lower()}_top_1000_words.json"
    data = [
        {'rank': rank, 'word': word, 'frequency': freq}
        for rank, (word, freq) in enumerate(results[country], 1)
    ]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved {filename}")

# Also save combined for TF-IDF analysis later
print("\nSaving combined word data for TF-IDF analysis...")
all_words_data = []
for country in countries:
    for rank, (word, freq) in enumerate(results[country], 1):
        all_words_data.append({
            'country': country,
            'rank': rank,
            'word': word,
            'frequency': freq
        })

combined_df = pd.DataFrame(all_words_data)
combined_df.to_json('top_1000_words_combined.json', orient='records', indent=2)
print("  Saved top_1000_words_combined.json")

# Save processed corpus for TF-IDF analysis
print("\nProcessing full corpus for TF-IDF analysis...")
processed_texts = []
for idx, content in enumerate(df['content'].astype(str).fillna('')):
    if idx % 50 == 0:
        print(f"  Processing speech {idx}/{len(df)}...")
    processed_words = process_text(content)
    processed_texts.append(' '.join(processed_words))

df['processed_text'] = processed_texts
df[['id', 'country', 'title', 'date', 'processed_text']].to_json(
    'CH_RU_processed_lemmatized.json', orient='records', indent=2
)
print("  Saved CH_RU_processed_lemmatized.json (ready for TF-IDF)")

print("\nText analysis complete!")
