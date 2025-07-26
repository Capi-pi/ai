import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page, rank in dict(sorted(ranks.items(), key=lambda item : item[1])).items():
        print(f"website = {page}, pageRank = {rank:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print()
    print(f"PageRank Results from Iteration")
    for page, rank in dict(sorted(ranks.items(), key=lambda item : item[1])).items():
        print(f"website = {page}, pageRank = {rank:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages. And return :
    pages = {page1 : {set of pages that are linked to by page1} (...) pageN : {set of pages that are linked to by pageN}}
    """
    pages = dict()                                      

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    """
    transition_proba = {}
    pageNeighbors = corpus[page]
    if pageNeighbors:
        neighborsProba = (damping_factor / len(pageNeighbors)) + (1 - damping_factor) / len(corpus) 
    else:
        neighborsProba = 0
    for p in corpus.keys():
        if p in pageNeighbors:
            transition_proba[p] = neighborsProba
        else:
            transition_proba[p] = (1 - damping_factor) / len(corpus)
    return transition_proba


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    """
    if not corpus or n <= 0:
        raise ValueError("Corpus must be non-empty and n > 0")

    current_page = random.choice(list(corpus.keys()))
    count = {page : 0 for page in corpus.keys()}
    for _ in range(n):
        count[current_page] += 1
        current_sample = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(list(current_sample.keys()), weights=list(current_sample.values()))[0]
    
    total = sum(count.values())
    return {page : pageRank / total for page, pageRank in count.items()}


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    """
    pages_number = len(corpus)
    pageRank = {page : 1 / pages_number for page in corpus.keys()}
    converge, epsilon = False, 0.001
    while not converge:
        new_pageRank = {}
        for page in corpus.keys():
            rank = (1 - damping_factor) / pages_number
            total = 0
            for i in corpus.keys():
                if corpus[i]:
                    if page in corpus[i]:
                        total += pageRank[i] / len(corpus[i])
                else:
                    total += pageRank[i] / pages_number

            rank += damping_factor * total
            new_pageRank[page] = rank

        converge = all(abs(new_pageRank[p] - pageRank[p]) <= epsilon for p in corpus.keys())
        pageRank = new_pageRank.copy()
    return pageRank


if __name__ == "__main__":
    main()
