from geo_agent.Entities.Article import Article, Source

from datetime import datetime
#import pytest

if __name__ == "__main__":
    source = Source(
        source_name="BBC News"
    )
    article = Article(
        article_title="Ex-FBI director James Comey surrenders over charge of threatening Trump's life in Instagram post",
        publication_time=datetime.fromisoformat("2026-04-29 17:52:20.120370"),
        source=source,
    )
    print(article.get_text_body())