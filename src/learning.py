# Here we can find all the learning models for this project 
# aka logistic regression(binary and multiclass); naives bayes; and a neural networks.
import numpy as np
from tqdm import tqdm

def softmax(z):
    z = np.asarray(z)
    z = z - np.max(z, axis=-1, keepdims=True) 
    exp_z = np.exp(z)
    return exp_z / np.sum(exp_z, axis=-1, keepdims=True)

class LogisticRegression:
    def __init__(self, learning_rate=0.01, n_iter=1000, verbose = False):
        self.learning_rate = learning_rate      # it's just the learning rate lol  
        self.n_iter = n_iter
        self.verbose = verbose

        self.weights = None  # (n_features, n_classes)
        self.bias = None     # (n_classes,)
        self.classes_ = None
        self.class_to_index_ = None
        self.loss_history_ = []
        
    #-------------------------utils_functions-------------------------
    def one_hot(self, class_idx):
        # convert self.y to an (nxk) vector where k is the number of classes 
        Y = np.zeros((self.n_samples, self.k))
        Y[np.arange(self.n_samples), class_idx] = 1.0
        return Y


    def initialize_parameters(self):
        # return random weights and bias
        np.random.seed(0) 
        self.weights = 0.001 * np.random.randn(self.n_features, self.k)
        self.bias = np.zeros(self.k)
        

    def forward_pass(self, X):
        """
            n = n_samples, d = n_features, k = n_classes
            compute y_hat
            X(nxd), W(dxk), bias(kx1)
            linear_pred = X * weights + bias    (nxk)
            y_hat = softmax(linear_pred)    (nxk)
        """
        linear_pred = X @ self.weights + self.bias
        return softmax(linear_pred)
    

    def compute_loss(self, Y_hat, Y_onehot):
        # Cross-entropy moyenne: ce
        epsilon = 1e-12
        ce = -np.sum(Y_onehot * np.log(Y_hat + epsilon)) / Y_hat.shape[0]
        return ce
    

    def backward_pass(self, X, y_onehot, y_hat):
        """
            update the weights and bias

            X(nxd), W(dxk), bias(kx1), y_hat(nxk), y(kx1)
            X.T * (y_hat - y) ---> (dxk)
        """
        diff = y_hat - y_onehot
        dw = (1/self.n_samples) * np.dot(X.T, diff)      # W_gradient
        db = (1/self.n_samples) * np.sum(diff, axis=0)                # bias_gradient
        self.weights -= self.learning_rate * dw
        self.bias -= self.learning_rate * db

    #-------------------------main---------------------------
    def fit(self, X, y):
        # fit the model to the given data points (i.e find goods parameters to make good prediction)
        X = np.array(X)
        y = np.array(y)
        """for x, label in zip(X, y):
            print(f"({x}, {label})")"""             #-----------------------debug--------------

        # map y (the labels) to 0,1...k-1 values
        self.classes = np.unique(y)
        self.class_to_index = {c : i for i, c in enumerate(self.classes)}
        self.class_idx = np.vectorize(self.class_to_index.get)(y)

        self.k = self.classes.size      # number of class
        
        self.n_samples, self.n_features = X.shape     # number of samples and features

        # main loop where we actually find the best parameters
        # but first initialize the weights and bias
        y_one_hot = self.one_hot(self.class_idx)
        self.initialize_parameters()
        for iteration in tqdm(range(self.n_iter)):
            # compute predictions for current parameters
            y_hat = self.forward_pass(X)

            # updates the parameters following gradient descent and repeat
            self.backward_pass(X, y_one_hot, y_hat)

            # monitoring
            if self.verbose or iteration == self.n_iter - 1:
                loss = self.compute_loss(y_hat, y_one_hot)
                self.loss_history_.append(loss)
                if self.verbose and (iteration % max(1, self.n_iter // 10) == 0):
                    print(f"[{iteration:5d}] loss={loss:.4f}")
        if self.verbose:
            print(f"Training finished. final loss={self.loss_history_[-1]:.6f}")


    def predict_proba(self, X):
        X = np.asarray(X, dtype=float)
        return self.forward_pass(X)


    def predict(self, X):
        probs = self.predict_proba(X)    # (n, k)
        # get the index of the class with the highest prob
        idx = np.argmax(probs, axis=1)   # (n,)
        
        # remap indices -> labels d’origine
        inv = np.array(self.classes)
        return inv[idx]


    def accuracy(self, X, y):
        # return the accuracy 
        X = np.asarray(X, dtype=float)
        y_pred = self.predict(X)
        return np.mean(y_pred == y)


class GaussianNB:

    def fit(self, X, y):
        # convert the set of examples to numpy nd arrays
        self.X = np.asarray(X)
        self.y = np.asarray(y)

        # number of samples and features 
        n_samples, n_features = self.X.shape

        # get the different classes in the dataset 
        self.classes_ = np.unique(self.y)
        n_classes = len(self.classes_)
        
        # initialize the mean, var and prior_proba for each class to zero
        self.mean_ = np.zeros((n_classes, n_features), dtype=float)
        self.var_ = np.zeros((n_classes, n_features), dtype=float)
        self.priors_ = np.zeros(n_classes, dtype=float)

        for idx, c in enumerate(self.classes_):
            X_c = self.X[y==c]  # get all the samples where the label is equal to c 

            # compute the mean, var and prior_proba for the class c at index idx
            self.mean_[idx, :] = np.mean(X_c, axis=0)
            self.var_[idx, :] = np.var(X_c, axis=0) + 1e-9
            self.priors_[idx] = X_c.shape[0] / float(n_samples) # it's a simple frequence
        
        # compute the loss
        self.log_loss(self.X, self.y)

    def predict(self, X):
        # take a set of samples as input and output the label predicted for each sample
        y_pred = [self.predict_onesample_(x, label=True) for x in X]
        return np.array(y_pred)
    

    def predict_proba(self, X):
        # take a set of samples as input and output a proaba distribution for each sample
        return np.array([self.predict_onesample_(x, distribution=True) for x in X])
    

    def predict_onesample_(self, x, label=False, distribution=False):
        # take one sample and return the label predicted 
        posteriors = []

        for idx, c in enumerate(self.classes_):
            # compute posterior probability 
            # posterior = prior + P(x|c) 
            prior = np.log(self.priors_[idx])
            posterior = prior + np.sum(self.log_normalPDF_(idx, x))
            posteriors.append(posterior)

        if label:
            # return the class with the highest posterior 
            return self.classes_[np.argmax(posteriors)]         #np.argmax(posteriors) give the idx of the class with the highest posterior
        if distribution:
            # return a probability distribution on the classes
            return softmax(posteriors)


    def log_normalPDF_(self, class_idx, x):
        # use the normal formula on each feature of the sample x to compute its log
        first_part = -(x - self.mean_[class_idx])**2 / (2 * self.var_[class_idx])
        second_part = -1/2 * np.log(2 * np.pi * self.var_[class_idx])
        log_pdf = first_part + second_part
        return log_pdf
    
    def log_loss(self, X, y):
        # compute the log_loss of the model for the sake of comparaison 
        X = np.asarray(X)
        y = np.asarray(y)
        # proba distribution
        probs = self.predict_proba(X)   # 2d array of shape (n_samples, n_classes)
        n_samples = X.shape[0]

        # initialize loss_history
        self.loss_history_ = []
        for i in tqdm(range(n_samples)):
            real_class = y[i]

            # we know that the real_class is mapped to 0, ..., n_classes thuus:
            p = probs[i][real_class]    # the probability of predicting the real_class
            self.loss_history_.append(-np.log(p) / n_samples)
        

    def accuracy(self, X, y):
        # return the accuracy 
        X = np.asarray(X, dtype=float)
        y_pred = self.predict(X)
        return np.mean(y_pred == y)
