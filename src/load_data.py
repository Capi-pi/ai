import pandas as pd
import random
import re
import vectorize

def load_clean_data(filePath):
    # load the cvs file
    data = pd.read_csv(filePath)

    # cleaning
    # remove NaN and dublicate cells
    data.dropna(inplace=True)
    data.drop_duplicates(inplace=True)

    # for this version, let's remove emojiis and special caracter from each text
    # convert data["text"] to lower 
    data["text"] = data["text"].str.lower()
    data["text"] = data["text"].apply(lambda x: re.sub(r"[^a-z\s]", "", x))
    data["text"] = data["text"].apply(lambda x: re.sub(r"\s+", " ", x))
    return data


def quick_explore(data: pd.DataFrame):
    print("Aperçu des données :")
    print(data.head(), "\n")

    print("Dimensions :", data.shape, "\n")

    print("Distribution des labels :")
    print(data["label"].value_counts(), "\n")

    print("Distribution des sentiments :")
    print(data["sentiment"].value_counts(), "\n")

    print("Longueur moyenne des textes :")
    print(data["text"].apply(lambda x: len(x.split())).mean(), "mots en moyenne")


def split_data(dataset: pd.DataFrame):
    """
        this function split the dataset in two list: training and testing 
    """
    # get the labels and evidences
    labels = dataset["label"].to_list()
    evidences = dataset["text"].to_list()

    # vectorize evidences using BoW or TF-IDF
    #evidences = vectorize.TF_IDF(evidences).compute_tf_idf_matrix()
    evidences = vectorize.BoW(evidences).get_BoW_matrix()

    # split dataset into (evidence, label) pairs
    data = [(evidence, label) for evidence, label in zip(evidences, labels)]

    # suffle (evidence, label) pair
    random.shuffle(data)
    shuffled_data = data

    # split the data with 0.8 / 0.2 ratio
    cut_index = int(0.8 * len(shuffled_data))

    # get X_train and y_train
    X_train, label_train = list(), list()
    for x_train, y_train in shuffled_data[: cut_index]:
        X_train.append(x_train)
        label_train.append(y_train)
    
    X_test, label_test = list(), list()
    for x_test, y_test in shuffled_data[cut_index :]:
        X_test.append(x_test)
        label_test.append(y_test)

    return (X_train, label_train), (X_test, label_test)


def main():
    data = load_clean_data("/home/alpha/Desktop/Info/Python/ia/final_project/data/train_df.csv")
    quick_explore(data)

if __name__ == "__main__":
    main()
    