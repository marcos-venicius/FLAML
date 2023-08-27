import requests
import json
import re
import hashlib
import arxiv
import os


def find_papers_pmc(query, size=10):
    """
    Find papers in PubMed Central (PMC) using Europe PMC API.

    Args:
        query (str): The search query to use.
        size (int): The number of results to return (default 10).

    Returns:
        None. Prints the title, url, publication date, and abstract of each paper found.
    """
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}&resulttype=core&pageSize={size}&format=json"

    response = requests.get(url)
    data = json.loads(response.text)

    papers = data["resultList"]["result"]

    for i, paper in enumerate(papers):
        print(f"{i + 1}. {paper['title']}")
        print(f"URL: https://europepmc.org/article/MED/{paper['id']}")
        # print(f"Authors: {paper['authorString']}")
        print(f"Publication Date: {paper['firstPublicationDate']}")
        abstract = paper.get("abstractText", "No abstract available")
        print(f"Abstract: {abstract}\n")


def search_arxiv(query, max_results=10):
    """
    Searches arXiv for the given query and returns the search results.

    Args:
        query (str): The search query.
        max_results (int, optional): The maximum number of search results to return. Defaults to 10.

    Returns:
        jresults (list): A list of dictionaries. Each dictionary contains fields such as 'title', 'authors', 'summary', and 'pdf_url'

    Example:
        >>> results = search_arxiv("attention is all you need")
        >>> print(results)
    """
    cache_dir = "cache"
    # Create the cache if it doesn't exist
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    key = hashlib.md5(("search_arxiv(" + str(max_results) + ")" + query).encode("utf-8")).hexdigest()
    fname = os.path.join(cache_dir, key + ".cache")

    # Cache hit
    if os.path.isfile(fname):
        fh = open(fname, "r")
        data = json.loads(fh.read())
        fh.close()
        return data

    # Normalize the query, removing operator keywords
    query = re.sub(r"[^\s\w]", " ", query.lower())
    query = re.sub(r"\s(and|or|not)\s", " ", " " + query + " ")
    query = re.sub(r"[^\s\w]", " ", query.lower())
    query = re.sub(r"\s+", " ", query).strip()

    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)

    jresults = list()
    for result in search.results():
        r = dict()
        r["entry_id"] = result.entry_id
        r["updated"] = str(result.updated)
        r["published"] = str(result.published)
        r["title"] = result.title
        r["authors"] = [str(a) for a in result.authors]
        r["summary"] = result.summary
        r["comment"] = result.comment
        r["journal_ref"] = result.journal_ref
        r["doi"] = result.doi
        r["primary_category"] = result.primary_category
        r["categories"] = result.categories
        r["links"] = [str(link) for link in result.links]
        r["pdf_url"] = result.pdf_url
        jresults.append(r)

    # Save to cache
    fh = open(fname, "w")
    fh.write(json.dumps(jresults))
    fh.close()
    return jresults
