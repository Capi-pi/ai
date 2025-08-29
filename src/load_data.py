import json
import pandas as pd
import random
import re
import vectorize





def load_clean_data(filePath=None, train_filepath=None, test_filepath=None):
    def stratified_sample_dataframe(df, samples_per_class, label_column='label'):
      """
      Samples a DataFrame to get an equal number of samples for each class.
      Returns:
          pd.DataFrame: A new DataFrame containing the stratified sample.
      """
      sampled_df = pd.DataFrame()
      for label in df[label_column].unique():
          class_df = df[df[label_column] == label]
          sampled_class = class_df.sample(n=samples_per_class, random_state=42, replace=False) # Use random_state for reproducibility
          sampled_df = pd.concat([sampled_df, sampled_class])

      # Shuffle the sampled DataFrame to mix the classes
      sampled_df = sampled_df.sample(frac=1, random_state=42).reset_index(drop=True)
      return sampled_df

    # load the csv file
    if filePath:
      data = pd.read_csv(filePath)
    else:
      train = pd.read_csv(train_filepath)
      test = pd.read_csv(test_filepath)
      data = pd.concat([train, test])

    # cleaning
    # remove NaN and dublicate cells
    data.dropna(inplace=True)
    data.drop_duplicates(inplace=True)

    # for this version, let's remove emojiis and special caracter from each text
    # convert data["text"] to lower 
    data["text"] = data["text"].str.lower()
    data["text"] = data["text"].apply(lambda x: re.sub(r"[^a-z\s]", "", x))
    data["text"] = data["text"].apply(lambda x: re.sub(r"\s+", " ", x))
    #quick_explore(data)
    return stratified_sample_dataframe(data, 6000)   # for the french dataSet


def quick_explore(data: pd.DataFrame):
    print("Aperçu des données :")
    print(data.head(), "\n")

    print("Dimensions :", data.shape, "\n")

    print("Distribution des labels :")
    print(data["label"].value_counts(), "\n")

    print("Distribution des sentiments :")
    #print(data["sentiment"].value_counts(), "\n")

    print("Longueur moyenne des textes :")
    print(data["text"].apply(lambda x: len(x.split())).mean(), "mots en moyenne")


def split_data(dataset: pd.DataFrame, filename=None):
    """
        this function split the dataset in two list: training and testing 
    """
    # get the labels and evidences
    labels = dataset["label"].to_list()
    evidences = dataset["text"].to_list()

    # vectorize evidences using BoW or TF-IDF
    evidences = vectorize.TF_IDF(evidences)
    #evidences = vectorize.BoW(evidences)
    vocab = evidences.vocab
    evidences = evidences.compute_tf_idf_matrix()
    #evidences = evidences.get_BoW_matrix()

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
    
    if not filename:
      return vocab, (X_train, label_train), (X_test, label_test)
    else:
      vectors = {
        "X_train": X_train,
        "X_test": X_test,
        "label_train": label_train,
        "label_test": label_test,
        "vocab": vocab
      }

      # save to a json file 
      with open("{}.json".format(filename), "w") as f:
        json.dump(vectors, f)

def load_vectors(filepath):
  with open(filepath, "r") as f:
    vectors = json.load(f)
  return vectors["vocab"], (vectors["X_train"], vectors["label_train"]), (vectors["X_test"], vectors["label_test"])


def main():
    data = load_clean_data("/content/drive/MyDrive/final_project/data/french_tweets.csv")
    #quick_explore(data)
    split_data(data, "vectors")

if __name__ == "__main__":
    main()
    