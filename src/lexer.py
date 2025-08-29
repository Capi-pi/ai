from collections import Counter
import re

common_prefixes = {
    "un",  # not, opposite of
    "re",  # again
    "dis", # not, opposite of
    "en",  # cause to
    "in",  # not, in
    "im",  # not, in
    "pre", # before
    "anti",# against
    "over",# over, above
    "under",# under, below
    "mis", # wrongly
    "sub", # under
    "super",# above, beyond
    "trans",# across
    "semi", # half
    "mid",  # middle
    "non",  # not
}

common_suffixes = {
    "s",   # plural, third person singular present
    "ed",  # past tense, past participle
    "ing",  # present participle, gerund
    "er",  # comparative, one who does
    "est",  # superlative
    "ly",  # adverbial
    "tion", # act or process
    "able", # capable of being
    "ment", # state, result, or action
    "ness", # state or quality
    "ful",  # full of
    "less", # without
    "ity",  # state or quality
    "ment", # action or process
    "ous",  # having the quality of
    "al",   # relating to
    "en",   # made of
}

prefix_pattern = r"^(?:" + "|".join(re.escape(p) for p in common_prefixes) + r")"
suffix_pattern = r"(?:" + "|".join(re.escape(s) for s in common_suffixes) + r")$"

def word_frequencies(tokens):
    # retourne une liste de paire (token, frequence)
    return Counter(tokens)

def top_k(tokens, k = 10):
    # retourne les k plus fréquent tokens
    return word_frequencies(tokens).most_common(k)

def remove_stop_words(tokens, stoplist):
    # remove stop_words (Det, Pronoum etc... ) from tokens
    pattern = r"(?:" + "|".join(re.escape(s) for s in stoplist) + r")"
    tokens = re.sub(pattern, "", " ".join(tokens)).split()
    return tokens

def stem(token):
    # réduire un mot à sa racine
    token = re.sub(f"{prefix_pattern}", "", token)
    token = re.sub(f"{suffix_pattern}", "", token)
    return token

def stem_tokens(tokens):
    # réduire une liste de tokens à leurs racines
    return [stem(token) for token in tokens]
