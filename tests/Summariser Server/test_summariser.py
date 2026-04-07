from geo_agent.Entities.Article import Article, _Source
from geo_agent.SummariserServer.summariser import extract_act_eve

from datetime import datetime
#import pytest

# XX TODO: add unit tests. Currently just seeing if the code runs

def main():
    article1 = Article(
        article_id = "",
        article_title = "",
        publication_time = datetime.now(),
        source = _Source(
            source_id = "",
            source_name = "Bob's Newsagents"
        ),

        text_body = "Today my friend Bob started a new job at Apple! He's also moving from the United Kingdom to the UK"
    )

    articles = [article1]

    article, actors, events = extract_act_eve(articles)

    for actor in actors:
        print(actor.name, actor.actor_type)

if __name__ == "__main__":
    main()