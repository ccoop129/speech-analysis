# speech-analysis

A project scraping, analyzing, and visualizing speeches from the Russian and Chinese foreign ministries by Chris Cooper, Jack Lennon, and Mandy Tao.

# Datasets

<p>Using the china-speech-scraper and russia-speech-scraper, we gathered china_speeches.csv, Lavrov_2026_2014_D4P.csv, and Lavrov_Speeches_D4P.json from <a href="https://mid.ru/en/press_service/announcements/">the Russian</a> and <a href="https://www.fmprc.gov.cn/eng/xw/zyjh/"> Chinese</a> Ministries of Foreign Affairs.</p>
<p>We used keywords.py to make viz_cache.json, which is what generates the interactable chart on the Insights page.</p>
<p>We used R to join the two datasets into China_Russia_Speeches.csv and .json.</p>
<p>We used word_count.py to make CH_RU_processed_lemmatized.json</p>
<p>We used count_noun_chunks_entities.py to make noun_chunks_entities_count.json, top_1000_words_combined.json, china_top_1000_words.json and russia_top_1000_words.json.</p>
<p>We used tfidf_analysis.py to make tfidf_rsults.json, tfidf_results_china_edited.json and tfidif_results_russia_edited.json.</p>
