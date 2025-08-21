import math
from tokenizer import tokenize

class BoW:
    def __init__(self, corpus):
        self.corpus = corpus

        # get tokens for each sentence in corpus
        self.tokens_list = list()
        for sentence in self.corpus:
            self.tokens_list.append(tokenize(sentence))
        
        # get the list of vocabulary for the given list of tokens
        vocab = set()
        for tokens in self.tokens_list:
            vocab.update(tokens)
        self.vocab = list(vocab)
        print("vocab: ", self.vocab)
    
    def get_BoW_matrix(self):
        matrix = []
        for tokens in self.tokens_list:
            vec = [tokens.count(word) for word in self.vocab]
            matrix.append(vec)
        return matrix
    

class TF_IDF:
    def __init__(self, corpus):
        self.corpus = corpus

        # get tokens for each sentence in corpus
        self.tokens_list = list()
        for sentence in self.corpus:
            self.tokens_list.append(tokenize(sentence))

        # construire vocabulaire
        self.vocab = set()
        for tokens in self.tokens_list:
            self.vocab.update(tokens)
        self.vocab = list(self.vocab)
        print("vocab: ", self.vocab)

    def compute_tf(self, tokens):
        """
        TF pour une phrase donnée = fréquence du mot / nombre total de mots
        """
        tf = {}
        total_tokens = len(tokens)
        for word in self.vocab:
            tf[word] = tokens.count(word) / total_tokens if total_tokens > 0 else 0
        return tf

    def compute_idf(self):
        """
        IDF pour chaque mot = log(N / (1 + df))
        - N = nombre total de documents
        - df = nombre de documents contenant ce mot
        """
        N = len(self.tokens_list)
        idf = {}
        for word in self.vocab:
            df = sum(1 for tokens in self.tokens_list if word in tokens)
            idf[word] = math.log(N / (1 + df)) + 1  # +1 pour éviter log(0)
        return idf

    def compute_tf_idf_matrix(self):
        """
        Retourne une matrice TF-IDF (liste de vecteurs)
        """
        idf = self.compute_idf()
        matrix = []
        for tokens in self.tokens_list:
            tf = self.compute_tf(tokens)
            vec = [tf[word] * idf[word] for word in self.vocab]
            matrix.append(vec)
        return matrix


    
def main():
    corpus = ["le chat mange la souris.", "la souris mange le fromage."]
    for sentence in corpus:
        print(sentence)
    corpus = BoW(corpus).get_BoW_matrix()
    print("bow: ", corpus)
    #tf_idf_matrix = TF_IDF(corpus).compute_tf_idf_matrix()
    #print("tf_idf: ", tf_idf_matrix)


if __name__ == "__main__":
    main()