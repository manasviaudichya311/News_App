# imports
import os
from collections import Counter
from datetime import datetime, timedelta

import pandas
import spacy
from dotenv import load_dotenv
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from summarizer.sbert import SBertSummarizer
from summarizer.bert import BertSummarizer

pandas.set_option("display.max_colwidth", None)
pandas.set_option("display.max_rows", None)
pandas.set_option("display.max_columns", None)
load_dotenv()

def get_named_entities(text, language):
    if language == "de":
        nlp = spacy.load("de_core_news_sm")
    else:
        nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    c = Counter([x.text for x in doc.ents])
    return c.most_common()

def get_summary(text, language):
    if language == "en":
        model = BertSummarizer()
    else:
        model = SBertSummarizer('paraphrase-MiniLM-L6-v2')
    summary = model(text, num_sentences=2)
    return summary

def write_to_csv(headlines, fname=None):
    df = pandas.DataFrame(headlines)
    if fname:
        filename = fname
    else:
        filename = f"query_results_{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nResult written to {filename} file\n")
    return df

def get_articles(query, language):
    newsapi = NewsApiClient(api_key=os.environ["API_KEY"])
    all_articles = []
    # send the first request
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    first_hundred = newsapi.get_everything(
        q=query,
        from_param=thirty_days_ago,
        to=today,
        language=language,
        sort_by="relevancy",
        page=1,
    )
    all_articles.extend(first_hundred["articles"])
    tr = first_hundred["totalResults"]

    # fetch further pages if exists
    if tr > 100:
        for page in range(2, (tr // 100) + 1):
            print(f"Fetching data for page: {page}")
            try:
                next_hundred = newsapi.get_everything(
                    q=query,
                    from_param=thirty_days_ago,
                    to=today,
                    language=language,
                    sort_by="relevancy",
                    page=page,
                )
                all_articles.extend(next_hundred["articles"])
            except NewsAPIException:
                print(f"Failed to fetch data from page {page} due to API LIMIT")
                break
    return all_articles

def extract_details(all_articles):
    headlines = []
    text = ""
    for article in all_articles:
        data = {
            "title": article["title"],
            "url": article["url"],
            "publishedAt": article["publishedAt"],
        }
        headlines.append(data)
        text += article["title"] + " "
    return headlines, text

if __name__ == "__main__":

    while True:
        if input("\nChoose a language, en or de: ") == "de":
            language = "de"
        else:
            language = "en"

        query = input("\nEnter a search query:")

        all_articles = get_articles(query, language)

        # extract headline, url and publication date
        headlines, text = extract_details(all_articles)

        # write to csv
        df = write_to_csv(headlines)
        print(df.head(15))

        text = ' '.join(df.loc[:14, 'title'])

        # Summarize headlines
        print(f"Summary of headlines:\n{get_summary(text, language)}")


        # Count named entities
        print("\nHere are the named entities found in the headlines")
        for each_entity in get_named_entities(text=text, language=language):
            print(each_entity[0], "-", each_entity[1])

        # Keep repeating until user exits
        start = input("\n\nClick enter to continue or type exit to quit: ")
        if start != "exit":
            continue
        else:
            exit(0)
