import load_data
import learning
import matplotlib.pyplot as plt
import numpy as np
import utils 
import vectorize



#-------------------------------main-----------------------------

def fit_data(filepath):
    
    # import a clean version of the data
    data = load_data.load_clean_data(filepath)

    # split the data
    (X_train, y_train), (X_test, y_test) = load_data.split_data(data)

    # fit data to a model
    model = learning.LogisticRegression(learning_rate=0.3, n_iter=4000, verbose=True)
    #model = learning.GaussianNB
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    evaluate(model, y_pred, y_test)



def evaluate(model: learning.GaussianNB, y_pred, y):
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
        plt.figure()
        plt.plot(model.loss_history_)
        plt.xlabel("Iteration")
        plt.ylabel("Loss (cross-entropy)")
        plt.title("Training(lr=.4) loss history")
        plt.grid(True)
        plt.show()

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
        plt.show()


def main():
    fit_data("/home/alpha/Desktop/Info/Python/ia/final_project/data/val_df.csv")


if __name__ == "__main__":
    main()
