import numpy as np

#-------------------utils-------------------------
# ratio of good predictions
def accuracy(predictions, test_labels):
    return np.mean(predictions == test_labels)

# proportion des vrais positifs prédit parmis les positifs prédit
def precision(predictions, test_labels):
    matrix = confusion_matrix(predictions, test_labels)
    tp = matrix["true_positive"]
    fp = matrix["false_positive"]
    
    return tp / (tp + fp) if tp + fp > 0 else 0

# proportion des vrais positifs prédit parmis les positifs de l'échantillon 
def recall(predictions, test_labels):
    matrix = confusion_matrix(predictions, test_labels)
    tp = matrix["true_positive"]
    fn = matrix["false_negative"]
    
    return tp / (tp + fn) if tp + fn > 0 else 0

# moyenne harmonique de precision et recall
def f1_score(predictions, test_labels):
    p = precision(predictions, test_labels)
    r = recall(predictions, test_labels)
    return 2 * r * p / (p + r) if p + r > 0 else 0


# donne une vue d'ensemble des prédictions
def confusion_matrix(predictions, test_labels):
    tp = 0
    fn = 0
    tn = 0
    fp = 0
    result = {}
    for y_pred, y in zip(predictions, test_labels):
        if y_pred == y == 1 : tp += 1
        elif y_pred == 1 and y == 0: fp += 1
        elif y_pred == 0 and y == 1: fn += 1
        elif y_pred == y == 0: tn += 1
    result["true_positive"] = tp
    result["false_positive"] = fp
    result["true_negative"] = tn
    result["false_negative"] = fn
    return result

