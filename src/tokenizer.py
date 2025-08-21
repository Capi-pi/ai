import re
import unicodedata

# Liste minimale d'abréviations pour éviter les faux split de phrases
ABBREVIATIONS = {
    "m.", "mr.", "mrs.", "ms.", "dr.", "prof.", "st.", "etc.", "vs."
}

def normalize(text: str, lowercase: bool = True, strip_accents: bool = True) -> str:
    """
    Nettoie le texte : normalisation Unicode, minuscules, accents.
    """
    # Normalisation unicode
    text = unicodedata.normalize("NFKD", text)

    # Retirer accents
    if strip_accents:
        text = "".join(ch for ch in text if not unicodedata.combining(ch))

    # Minuscule
    if lowercase:
        text = text.lower()

    # Retirer espaces multiples
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text: str, keep_punct: bool = False, keep_case: bool = False, strip_accents: bool = True) -> list[str]:
    """
    Découpe un texte en tokens.
    - keep_punct : garde ponctuation comme tokens
    - keep_case : conserve la casse
    - strip_accents : enlève accents
    """
    if not keep_case or strip_accents:
        text = normalize(text, lowercase=not keep_case, strip_accents=strip_accents)

    if keep_punct:
        # Mot, nombre, ou ponctuation
        pattern = r"\w+(?:'\w+)?|[^\w\s]"
    else:
        # Mot ou nombre seulement
        pattern = r"\w+(?:'\w+)?"

    return re.findall(pattern, text)


def sentences(text: str) -> list[str]:
    """
    Découpe un texte en phrases en tenant compte des abréviations simples.
    """
    # Normalisation légère pour uniformiser espaces
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Découpe sur ponctuation terminale
    sentence_endings = re.finditer(r"([.!?])\s+", text)
    start = 0
    sentences_list = []

    for match in sentence_endings:
        end = match.end()
        part = text[start:end].strip()

        # Vérifie si ça finit par une abréviation connue
        if part.lower().split()[-1] in ABBREVIATIONS:
            continue

        sentences_list.append(part)
        start = end

    # Ajouter dernier segment
    if start < len(text):
        sentences_list.append(text[start:].strip())

    return sentences_list

