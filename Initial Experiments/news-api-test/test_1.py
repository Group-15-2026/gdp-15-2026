from newsapi import NewsApiClient
import json

if __name__ == '__main__':
    f = open("newsapi_key.txt", "r")
    API_KEY = f.readline().strip()
    f.close()

    newsapi = NewsApiClient(api_key=API_KEY)

    # grabs the current top headlines, returns python dictionary
    top_headlines = newsapi.get_top_headlines(category='business',
                                              language='en',
                                              country='us')

    # grabs all articles matching query
    # limited to past 28 days on free plan
    # returns python dictionary
    all_articles = newsapi.get_everything(q='apple',
                                          sources='bbc-news,the-verge',
                                          from_param='2026-03-01',
                                          to='2026-03-07',
                                          language='en',
                                          sort_by='relevancy',
                                          page=1)

    top = open("top_headlines.txt","w")
    all = open("all_articles.txt","w")

    # writes to files and converts python dict to JSON
    top.write(json.dumps(top_headlines, indent=4))
    all.write(json.dumps(all_articles, indent=4))

    top.close()
    all.close()
