#! /usr/bin/env python3

__author__ = "Victor Freire"
__email__ = "freiremelgiz@wisc.edu"

"""
This script performs least squares classification of
the selected dataset solving the problem with the
closed-form solution.

This script also performs a low-rank approximation,
informed by the PCA, and trains classifiers using
Least Squares on the low-rank approximation of the
training data.

This script also solves the Least Squares problem
iteratively via Gradient Descent and the results can
be compared to the closed-form Least Squares solution
"""

DATASET = 1 # Select dataset [1,6]
ALGO = 'GDLS'

from Dataset import Dataset
import numpy as np
import matplotlib.pyplot as plt
from IterReg import IterReg # Iterative register worker

""" Helper Functions """
# Perform data classification with provided weights
def classify(X,w):
    y_hat = np.sign(X@w) # Predict labels
    return y_hat

# Gets the percent error of the predictions
def get_perr(y_hat, y):
    nerr = get_nerr(y_hat,y) # Use other function
    perr = nerr/len(y)*100 # Percent error
    return perr

# Gets the number of misclassifications
def get_nerr(y_hat, y):
    nerr = np.sum(np.abs(y_hat-y)/2) # Number of errors
    return nerr

# Returns the weights using the original LS solution
def trainLSOrig(X, y):
    # Find least squares solution with training data provided
    w = np.linalg.inv(X.T@X)@X.T@y
    return w

# Compute the loss function value Mean Squared Error
def get_loss_MSE(X, y, w): # Compute cost func
    loss = np.linalg.norm(X@w-y,2)**2 # MSE
    return loss

# Take a step in GD
def step_GDLS(X, y, w, tau):
    grad = 2*X.T@(X@w - y) # Compute gradient
    w_new = w - tau*grad
    return w_new

if __name__ == "__main__":
    # Initialize a dataset
    num_dataset = DATASET
    data = Dataset(num_dataset) # Retrieve dataset object

    # Print Header
    print("/// Least Squares Training via Closed Form ///")
    print("-- Using dataset {} | Closed Form Solution --".format(num_dataset))

    # Use helper functions to get percent error
    w = trainLSOrig(data.X_tr, data.y_tr) # Get weights with training set
    y_hat = classify(data.X,w) # Classify test set
    perr = get_perr(y_hat, data.y) # Get percent error
    loss_tr = get_loss_MSE(data.X_tr, data.y_tr, w) # Compute cost func

    # Output results
    print("Percent labels misclassified: {}%".format(perr.round(2)))
    print("Training Loss Value: {}".format(loss_tr.round(2)))


    """ Low rank approximation study """
    # Find skinny SVD of training data
    U, s, VT = np.linalg.svd(data.X_tr, full_matrices=False)
    V = VT.T

    # Find rank-20 or rank-8 approximation to data
    if num_dataset < 4:
        rank = 20
    elif num_dataset == 6:
        rank = 5
    else:
        rank = 8

    # Compute low-rank approximation to X_tr
    X_r = np.zeros(data.X_tr.shape)
    for i in range(rank):
        X_r += s[i]*np.outer(U[:,i],V[:,i])

    # Use helper functions to get percent error
    w = trainLSOrig(X_r, data.y_tr) # Get weights with training set
    y_hat = classify(data.X,w) # Classify test set
    perr = get_perr(y_hat, data.y) # Get percent error
    loss_r = get_loss_MSE(X_r, data.y_tr, w) # Compute cost func

    # Output results
    print("\n/// Least Squares Training via Rank-{} Approximation ///".format(rank))
    print("Percent labels misclassified: {}%".format(perr.round(2)))
    print("Training Loss Value: {}".format(loss_r.round(2)))



    ## Compare Gradient Descent with Closed Form
    # Initialize IterReg feature
    algo = ALGO
    logger = IterReg(algo,num_dataset) # Init logger

    # Print Header
    print("\n /// Least Squares Training with Gradient Descent ///")
    print("-- Using dataset {} | ALGO: {} --".format(num_dataset, algo))

    # Load weights
    try:
        w = logger.load() # Load saved weights
    except FileNotFoundError:
        w = np.zeros(data.X_tr.shape[1]) # Init to zeros
    loss_gd = get_loss_MSE(data.X_tr, data.y_tr, w) # Comp cost fun
    print("Hot-start Loss Value: {}".format(loss_gd.round(2)))
    print("Press Ctrl+C to stop and show results")
    print("Iterating...")
    tau = 1/(np.linalg.norm(data.X_tr,2)**2) # Step size
    while((loss_gd-loss_tr) > 1): # While not converged
        try:
            w_new = step_GDLS(data.X_tr, data.y_tr, w, tau)
            w = w_new
        except KeyboardInterrupt:
            break
    logger.save(w) # Save progress

    # Compute metrics with new w
    y_hat = classify(data.X,w) # Classify test set
    perr = get_perr(y_hat, data.y) # Get percent error
    loss_gd = get_loss_MSE(data.X_tr, data.y_tr, w) # Comp cost fun

    # Output results
    print("\nGradient Descent Least Squares classification:")
    print("Percent labels misclassified: {}%".format(perr.round(2)))
    print("Training Loss Value: {}".format(loss_gd.round(2)))
