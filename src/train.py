import load_data
import learning
import matplotlib.pyplot as plt
import numpy as np
import utils 
import vectorize


#-------------------------------main-----------------------------

def fit_data(filepath=None, train_filepath=None, test_filepath=None, jsonfilepath="vectors.json"):
    
    # import a clean version of the data
    print("Processing the data...")
    #data = load_data.load_clean_data(filepath, train_filepath, test_filepath)

    # split the data
    #vocab, (X_train, y_train), (X_test, y_test) = load_data.split_data(data)
    vocab, (X_train, y_train), (X_test, y_test) = load_data.load_vectors(jsonfilepath)
    
    # fit data to a model
    model = learning.LogisticRegression(learning_rate=0.3, n_iter=10000, verbose=True)
    #model = learning.GaussianNB()
    model.fit(X_train, y_train)
    print("saving...")
    model.save(vocab, "LogisticRegression")
    y_pred = model.predict(X_test)
    probs = model.predict_proba(X_test)
    evaluate(model, y_pred, probs, y_test)


def predict(X, model):
  return model.predict_proba(X)
  


def evaluate(model, y_pred, probaDist, y, X=None):
  # compute the different metrics for the evaluation
  acc = utils.accuracy(y_pred, y)
  prec = utils.precision(y_pred, y)
  rec = utils.recall(y_pred, y)
  f1 = utils.f1_score(y_pred, y)
  cm = utils.confusion_matrix(y_pred, y)

  print("=== Metrics ===")
  print(f"accuracy: {acc:.4f}")
  print(f"precision: {prec:.4f}")
  print(f"recall: {rec:.4f}")
  print(f"f1: {f1:.4f}")
  print("confusion matrix:", cm)


  # plots
  # 1) loss history
  if hasattr(model, "loss_history_"):
    plt.figure()
    plt.plot(model.loss_history_)
    plt.xlabel("Iteration")
    plt.ylabel("Loss (cross-entropy)")
    plt.title("Training(lr=.3) loss history")
    plt.grid(True)
    plt.savefig("loss_history.png")
    plt.show()
  else:
    print("this model is not iterative thus we don't have a loss for each iteration")
    print(f"But here its loss after training: {model.log_loss(X, probaDist, y)}")

  # 2) confusion matrix
  cm_arr = np.array([[cm["true_negative"], cm["false_positive"]],
                      [cm["false_negative"], cm["true_positive"]]])
  plt.figure()
  plt.imshow(cm_arr, interpolation='nearest', aspect='auto')
  plt.title("Confusion matrix")
  plt.ylabel("True label")
  plt.xlabel("Predicted label")
  plt.colorbar()
  for i in range(2):
      for j in range(2):
          plt.text(j, i, int(cm_arr[i, j]), ha="center", va="center")
  plt.savefig("confusion_matrix.png")
  plt.show()


def main():
  # sur drive
  #fit_data(train_filepath="/content/drive/MyDrive/final_project/data/train_df.csv",
  #          test_filepath="/content/drive/MyDrive/final_project/data/test_df.csv")
  
  #fit_data(filepath=r"C:\Users\AlphaAmadouDjouldéDI\Desktop\final_project\data\val_df.csv")
  fit_data(jsonfilepath="vectors.json")


if __name__ == "__main__":
    main()
