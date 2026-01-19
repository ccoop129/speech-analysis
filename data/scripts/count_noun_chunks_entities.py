import pandas as pd
import spacy
from collections import Counter
import json
import os
import warnings

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, '..')

# Load spaCy model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

# Increase max_length to handle longer texts
nlp.max_length = 2000000

# Semantic normalization map for entities
SEMANTIC_MAP = {
    # China
    'china': 'china',
    'chinese': 'china',
    'prc': 'china',
    'beijing': 'china',
    'people\'s republic of china': 'china',
    'the people\'s republic of china': 'china',
    
    # Russia
    'russia': 'russia',
    'russian': 'russia',
    'moscow': 'russia',
    'russian federation': 'russia',
    'the russian federation': 'russia',
    
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
    'delhi': 'india',

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
    'the united kingdom': 'united_kingdom',
    'the uk': 'united_kingdom',
    'the u.k.': 'united_kingdom',

    # Australia
    'australia': 'australia',
    'australian': 'australia',
    'canberra': 'australia',
    'commonwealth of australia': 'australia',
    'the commonwealth of australia': 'australia',

    #Germany
    'germany': 'germany',
    'german': 'germany',
    'berlin': 'germany',
    'the federal republic of germany': 'germany',
    'federal republic of germany': 'germany',

    #France
    'france': 'france',
    'french': 'france',
    'paris': 'france',
    'the french republic': 'france',
    'french republic': 'france',
    'the republic of france': 'france',
    'republic of france': 'france',

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
    'democratic_people\'s_republic_of_korea': 'north_korea',
    'democratic people\'s republic of korea': 'north_korea',
    'dprk': 'north_korea',
    'the democratic people\'s republic of korea': 'north_korea',
    'the dprk': 'north_korea',

    #Iran
    'iran': 'iran',
    'iranian': 'iran',
    'tehran': 'iran',
    'islamic_republic_of_iran': 'iran',
    'islamic republic of iran': 'iran',
    'the islamic republic of iran': 'iran',

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
    'republic_of_singapore': 'singapore',
    'republic of singapore': 'singapore',
    'the republic of singapore': 'singapore',

  #Palestine
    'palestine': 'palestine',
    'palestinian': 'palestine',
    'ramallah': 'palestine',
    'palestinians': 'palestine',
    'palestinian authority': 'palestine',
    'state_of_palestine': 'palestine',
    'state of palestine': 'palestine',
    'the state of palestine': 'palestine',

# Canada
    'canada': 'canada',
    'canadian': 'canada',
    'ottawa': 'canada',

    #Turkey 
    'turkey': 'turkey',
    'turkish': 'turkey',
    'ankara': 'turkey',
    'turkiye': 'turkey',
    'turkiyeli': 'turkey',
    'the republic of turkey': 'turkey',
    'republic of turkey': 'turkey',
    'the turkish republic': 'turkey',
    'turkish republic': 'turkey',
    'Türkiye': 'turkey',

    #Taiwan
    'taiwan': 'taiwan',
    'taiwanese': 'taiwan',
    'taipei': 'taiwan',
    'republic_of_china': 'taiwan',
    'republic of china': 'taiwan',
    'the republic of china': 'taiwan',


    
    #Brazil
    'brazil': 'brazil',
    'brazilian': 'brazil',
    'brasil': 'brazil',
    'brasileiro': 'brazil',
    'brasileira': 'brazil',
    'brasilia': 'brazil',
    'the federative republic of brazil': 'brazil',
    'federative republic of brazil': 'brazil',

    #Kazakhstan
    'kazakhstan': 'kazakhstan',
    'kazakhstani': 'kazakhstan',
    'nur_sultan': 'kazakhstan',
    'astana': 'kazakhstan',
    'kazakh': 'kazakhstan',
    'kazakhs': 'kazakhstan',
    'the republic of kazakhstan': 'kazakhstan',
    'republic of kazakhstan': 'kazakhstan',

    #Ukraine
    'ukraine': 'ukraine',
    'ukrainian': 'ukraine',
    'kyiv': 'ukraine',
    'kiev': 'ukraine',

    #Kyrgystan
    'kyrgyzstan': 'kyrgyzstan',
    'kyrgyz': 'kyrgyzstan',
    'bishkek': 'kyrgyzstan',
    'the kyrgyz republic': 'kyrgyzstan',
    'kyrgyz republic': 'kyrgyzstan',

    #Mongolia
    'mongolia': 'mongolia',
    'mongolian': 'mongolia',
    'ulaanbaatar': 'mongolia',


    #Belarus
    'belarus': 'belarus',
    'belarussian': 'belarus',
    'minsk': 'belarus',
    'the republic of belarus': 'belarus',
    'republic of belarus': 'belarus',

    #Israel
    'israel': 'israel',
    'israeli': 'israel',
    'jerusalem': 'israel',
    'state_of_israel': 'israel',
    'state of israel': 'israel',
    'the state of israel': 'israel',

    #Vietnam
    'vietnam': 'vietnam',
    'vietnamese': 'vietnam',
    'hanoi': 'vietnam',
    'viet nam': 'vietnam',
    'socialist_republic_of_vietnam': 'vietnam',
    'socialist republic of vietnam': 'vietnam',
    'the socialist republic of vietnam': 'vietnam',

    #Thailand
    'thailand': 'thailand',
    'thai': 'thailand',
    'bangkok': 'thailand',
    'kingdom_of_thailand': 'thailand',
    'kingdom of thailand': 'thailand',
    'the kingdom of thailand': 'thailand',

    #Tibet
    'tibet': 'tibet',
    'tibetan': 'tibet',
    'lhasa': 'tibet',
    'tibetan_autonomous_region': 'tibet',
    'tibetan autonomous region': 'tibet',
    'the tibetan autonomous region': 'tibet',

    #Hong Kong
    'hong_kong': 'hong_kong',
    'hong kong': 'hong_kong',
    'hk': 'hong_kong',
    'h.k.': 'hong_kong',
    'hongkong': 'hong_kong',
    'hongkongese': 'hong_kong',
    'Hong Kong Special Administrative Region': 'hong_kong',
    'the hong kong special administrative region': 'hong_kong',



    # Middle East
    'middle_east': 'middle_east',
    'middle east': 'middle_east',
    'MENA': 'middle_east',
    'the middle east': 'middle_east',

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
    'america': 'united states',
    'american': 'united states',
    'usa': 'united states',
    'us': 'united states',
    'united_states': 'united states',
    'united_states_of_america': 'united states',
    'united states': 'united states',
    'united states of america': 'united states',
    'washington': 'united states',
    'the united states': 'united states',
    
    # United Nations
    'un': 'united nations',
    'u.n.': 'united nations',
    'united_nations': 'united nations',
    'the united nations': 'united nations',

    
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
    'the european union': 'european_union',
    'the eu': 'european_union',
    'the e.u.': 'european_union',

    #NATO
    'nato': 'nato',
    'north_atlantic_treaty_organization': 'nato',
    'north atlantic treaty organization': 'nato',
    'brussels': 'nato',
    'the north atlantic treaty organization': 'nato',

    #ASEAN
    'asean': 'asean',
    'association_of_southeast_asian_nations': 'asean',
    'association of southeast asian nations': 'asean',
    'jakarta': 'asean',
    'the association of southeast asian nations': 'asean',
    
    #SCO
    'sco': 'sco',
    'shanghai_cooperation_organization': 'sco',
    'shanghai cooperation organization': 'sco',
    'the shanghai cooperation organization': 'sco',

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
    'syrian arab republic': 'syria',
    'the syrian arab republic': 'syria',



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

def apply_semantic_normalization(text):
    """Apply semantic normalization to map related terms to canonical form."""
    lower_text = text.lower().strip()
    return SEMANTIC_MAP.get(lower_text, lower_text)

def strip_articles(text):
    """Remove leading articles (the, a, an) from text."""
    lower_text = text.lower().strip()
    articles = ['the ', 'a ', 'an ']
    for article in articles:
        if lower_text.startswith(article):
            return lower_text[len(article):].strip()
    return lower_text

# Entities to filter out (temporal, ordinal, etc.)
ENTITIES_TO_SKIP = {
    'today', 'tomorrow', 'yesterday', 'now', 'then', 'here', 'there',
    'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
    'eighth', 'ninth', 'tenth', 'last', 'next', 'previous',
    'january', 'february', 'march', 'april', 'may', 'june', 'july', 
    'august', 'september', 'october', 'november', 'december',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'ladies', 'gentlemen',
    'sergey lavrov', 'lavrov', 'xi jinping', 'xi', 'hu', 'hu jintao', 'putin', 'vladimir putin',
}

# Noun chunks to filter out (non-meaningful)
NOUN_CHUNKS_TO_SKIP = {
    'gentleman', 'lady', 'ladies', 'gentlemen',
    'sergey lavrov', 'president xi jinping', 'xi jinping',
}

def is_numeric(text):
    """Check if text is primarily numeric (numbers, ordinals, etc.)."""
    # Remove common words that might be attached to numbers
    cleaned = text.lower().strip()
    # Check if it's a number word or contains mostly digits
    number_words = {'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 
                    'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 
                    'eighty', 'ninety', 'hundred', 'thousand', 'million', 'billion'}
    
    if cleaned in number_words:
        return True
    
    # Check if it contains mostly digits
    digit_count = sum(1 for c in cleaned if c.isdigit())
    return digit_count > len(cleaned) / 2

# Load data
print("Loading CH_RU_prime.csv...")
print("  (Skipping any rows with encoding issues)...")

# Capture warnings during CSV load
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    df = pd.read_csv(os.path.join(data_dir, "CH_RU_prime.csv"), encoding='latin1', on_bad_lines='skip', engine='python')
    
    # Report any warnings
    for warning in w:
        if 'ParserWarning' in str(warning.category):
            print(f"  WARNING: {warning.message}")

print(f"  Successfully loaded {len(df)} rows")

# Process by country
countries = ['China', 'Russia']
results = {}

for country in countries:
    print(f"\nProcessing {country} speeches...")
    
    # Filter by country
    country_df = df[df['country'] == country]
    print(f"  Found {len(country_df)} speeches")
    
    # Initialize counters
    noun_chunks_counter = Counter()
    entities_counter = Counter()
    total_noun_chunks = 0
    total_entities = 0
    
    # Process each speech
    print(f"  Extracting noun chunks and entities...")
    for idx, content in enumerate(country_df['content'].astype(str).fillna('')):
        if idx % 100 == 0:
            print(f"    Processing speech {idx}/{len(country_df)}...")
        
        # Process text with spaCy
        doc = nlp(content.lower())
        
        # Extract noun chunks
        for chunk in doc.noun_chunks:
            # Skip pronouns and determiners (non-meaningful)
            if chunk.root.pos_ in ['PRON', 'DET'] or all(token.is_stop for token in chunk):
                continue
            lemmatized_chunk = ' '.join([token.lemma_ for token in chunk])
            # Strip leading articles
            cleaned_chunk = strip_articles(lemmatized_chunk)
            
            # Skip non-meaningful noun chunks
            if cleaned_chunk.lower() in NOUN_CHUNKS_TO_SKIP:
                continue
            
            noun_chunks_counter[cleaned_chunk] += 1
            total_noun_chunks += 1
        
        # Extract entities
        for ent in doc.ents:
            lemmatized_entity = ' '.join([token.lemma_ for token in ent])
            # Strip leading articles
            cleaned_entity = strip_articles(lemmatized_entity)
            
            # Skip non-meaningful temporal/ordinal entities
            if cleaned_entity.lower() in ENTITIES_TO_SKIP:
                continue
            
            # Skip numeric entities
            if is_numeric(cleaned_entity):
                continue
            
            normalized_entity = apply_semantic_normalization(cleaned_entity)
            entities_counter[normalized_entity] += 1
            total_entities += 1
    
    # Store results
    results[country] = {
        'total_noun_chunks': total_noun_chunks,
        'unique_noun_chunks': len(noun_chunks_counter),
        'top_noun_chunks': noun_chunks_counter.most_common(50),
        'total_entities': total_entities,
        'unique_entities': len(entities_counter),
        'top_entities': entities_counter.most_common(50),
    }
    
    print(f"  Total noun chunks: {total_noun_chunks}")
    print(f"  Unique noun chunks: {len(noun_chunks_counter)}")
    print(f"  Total entities: {total_entities}")
    print(f"  Unique specific entities: {len(entities_counter)}")
    print(f"  Top 10 noun chunks: {noun_chunks_counter.most_common(10)}")
    print(f"  Top 10 entities: {entities_counter.most_common(10)}")

# Save results to JSON
print("\nSaving results...")
output_data = {}
for country in countries:
    output_data[country] = {
        'total_noun_chunks': results[country]['total_noun_chunks'],
        'unique_noun_chunks': results[country]['unique_noun_chunks'],
        'top_50_noun_chunks': [
            {'rank': rank, 'noun_chunk': chunk, 'frequency': freq}
            for rank, (chunk, freq) in enumerate(results[country]['top_noun_chunks'], 1)
        ],
        'total_entities': results[country]['total_entities'],
        'unique_entities': results[country]['unique_entities'],
        'top_50_entities': [
            {'rank': rank, 'entity': entity, 'frequency': freq}
            for rank, (entity, freq) in enumerate(results[country]['top_entities'], 1)
        ],
    }

with open(os.path.join(data_dir, 'noun_chunks_entities_count.json'), 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)
print("  Saved noun_chunks_entities_count.json")

# Print summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
for country in countries:
    print(f"\n{country}:")
    print(f"  Total Noun Chunks: {results[country]['total_noun_chunks']:,}")
    print(f"  Unique Noun Chunks: {results[country]['unique_noun_chunks']:,}")
    print(f"  Total Entities: {results[country]['total_entities']:,}")
    print(f"  Unique Specific Entities: {results[country]['unique_entities']:,}")

print("\n" + "="*70)
print("Script complete! Results saved to noun_chunks_entities_count.json")
