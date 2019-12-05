from django.contrib.postgres.search import SearchQuery


class WebSearchQuery(SearchQuery):
    SEARCH_TYPES = {
        "plain": "plainto_tsquery",
        "phrase": "phraseto_tsquery",
        "raw": "to_tsquery",
        "web": "websearch_to_tsquery",
    }
