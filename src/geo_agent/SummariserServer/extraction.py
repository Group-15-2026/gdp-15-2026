from ..Entities.Article import Article

from collections import Counter
import spacy

# SpaCy NLP Setup
nlp = None
relevant_entity_labels = {"GPE", "LAW", "NORP", "ORG", "PERSON"}

# XX merge labels for duplicated actors (preferring anything other than 'other')

def extract_actors(articles: list[Article]) -> list[tuple[Article, Counter[str], dict[str, str]]]:
    global nlp
    
    # Extract Actors
    # XX extract article_texts using SQL DB
    # XX for now, the MVP adds an extra field to address this
    article_texts = [article.text_body for article in articles]
    
    # avoid memory intensive load unless necessary
    if nlp is None:
        nlp = spacy.load(
            "en_core_web_trf",
            disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]   # remove memory/compute intensive, unused parts  
        )
    
    actors: list[tuple[Article, Counter[str], dict[str, str]]] = [] # (source_article_id, actor_counter) members

    # avoid leaking/storing new vocab between batches
    with nlp.memory_zone():
        for doc, article in zip(nlp.pipe(article_texts, batch_size=50), articles):
            doc_actors = Counter[str]()
            doc_actor_clss: dict[str, str] = {}
            for ent in doc.ents:
                if ent.label_ in relevant_entity_labels:
                    doc_actors[ent.text] += 1
                    if ent.text not in doc_actor_clss:
                        doc_actor_clss[ent.text] = ent.label_
                    # we will assume that different occurrences of the same actor in an article get the same spacy class (and so use first one as canonical)
            actors.append((article, doc_actors, doc_actor_clss))

    return actors

# XX add code to extract events / claims too