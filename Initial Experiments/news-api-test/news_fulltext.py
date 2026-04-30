import newspaper

first_article = newspaper.Article(url="https://www.bbc.co.uk/news/articles/cgqkkxd09e2o", language='en')

first_article.download()
first_article.parse()

print(first_article.title)

print(first_article.text)


article2 = newspaper.Article(url="https://edition.cnn.com/2026/04/30/politics/trump-iran-war-strait-of-hormuz-blockade-analysis", language='en')

article2.download()
article2.parse()

print(article2.title)

print(article2.text)

# Works for BBC, CNN
# Doesn't work for Reuters, WSJ, Bloomberg

# article3 = newspaper.Article(url="https://www.bloomberg.com/news/articles/2026-04-30/alphabet-amazon-outpace-meta-in-ai-during-earnings-bonanza", language='en')

# article3.download()
# article3.parse()

# print(article3.title)

# print(article3.text)

