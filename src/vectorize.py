from lexer import stem_tokens, remove_stop_words
import math
from tqdm import tqdm
from tokenizer import tokenize, sentences

STOPSWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 
              'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
               'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 
              'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 
              'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

class BoW:
    def __init__(self, corpus, vocabConnu = None):
        #self.corpus = sentences(corpus)    # if corpus is not a list of sentence
        self.corpus = corpus
        self.tokens_list = []
        # get tokens for each sentence in corpus
        print("getting tokens for each sentence in the corpus...")
        for sentence in tqdm(self.corpus):
          sentence_token = tokenize(sentence)
          #print(sentence_token)-----------debug

          # remove stops_words from sentence 
          #sentence_token = remove_stop_words(sentence_token, STOPSWORDS)
          #print(sentence_token)

          # compress each token of sentence_token to its radical
          #sentence_token = stem_tokens(sentence_token)

          self.tokens_list.append(sentence_token)

        #print(self.tokens_list)--------debug
        
        if vocabConnu:
            self.vocab = vocabConnu
        else:
            # get the list of vocabulary for the given list of tokens
            vocab = set()
            print("getting the list of vocabulary...")
            for token in tqdm(self.tokens_list):
                vocab.update(token)
            self.vocab = list(vocab)
            #print("vocab: ", self.vocab)
    
    def get_BoW_matrix(self):
        matrix = []
        print("computing the BoW_matrix...")
        for tokens in tqdm(self.tokens_list):
            vec = [tokens.count(word) for word in self.vocab]
            matrix.append(vec)
        return matrix
    

class TF_IDF:
    def __init__(self, corpus, vocabConnu = None):
        self.corpus = sentences(corpus)    # if sentence is not a list of sentence
        #self.corpus = corpus
        #print(self.corpus)
        self.tokens_list = []
        # get tokens for each sentence in corpus
        print("getting tokens for each sentence in the corpus...")
        for sentence in tqdm(self.corpus):
          sentence_token = tokenize(sentence)

          # remove stops_words from sentence 
          #sentence_token = remove_stop_words(sentence_token, STOPSWORDS)

          # compress each token of sentence_token to its radical
          #sentence_token = stem_tokens(sentence_token)

          self.tokens_list.append(sentence_token)

        #print(self.tokens_list)
        
        if vocabConnu:
            self.vocab = vocabConnu
        else:
            # get the list of vocabulary for the given list of tokens
            print("constructing the list of vocabulary...")
            self.vocab = set()
            for tokens in tqdm(self.tokens_list):
                self.vocab.update(tokens)
            self.vocab = list(self.vocab)
            #print("vocab: ", self.vocab)

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
        - documentFrequency (df) = nombre de documents contenant ce mot
        """
        N = len(self.tokens_list)
        idf = {}
        for word in tqdm(self.vocab):
            df = sum(1 for tokens in self.tokens_list if word in tokens)
            idf[word] = math.log(N / (1 + df)) + 1  # +1 pour éviter log(0)
        return idf

    def compute_tf_idf_matrix(self):
        """
        Retourne une matrice TF-IDF (liste de vecteurs)
        """
        print("computing tf-idf matrix...")
        idf = self.compute_idf()
        print()
        matrix = []
        print("computing tf for each sentence(list of token)...")
        for tokens in tqdm(self.tokens_list):
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