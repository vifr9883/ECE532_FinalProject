#! /usr/bin/env python3

__author__ = "Victor Freire"
__email__ = "freiremelgiz@wisc.edu"

"""
This script solves the Hinge Loss problem to
train a linear classifier.

The problem is solved iteratively via Gradient
Descent for the specified dataset. The Gradient
Descent method is programmed around a save-and-
load architecture so that convergence progress is
saved and each time the script is started, the
algorithm can have a hot-start on the set of weights.

"""

import numpy as np
from IterReg import IterReg
from Dataset import Dataset
from LeastSquares import get_perr
from LeastSquares import classify

DATASET = 1
ALGO = 'GDHL'

""" Helper Functions """
# Compute the loss function value Hinge Loss
def get_loss_HL(X, y, w): # Comp cost fun
    loss = 0
    for i in range(X.shape[0]):
        loss += max(1 - y[i]*np.dot(X[i,:],w),np.zeros(1)[0])
    return loss

# Take a step in GD
def step_GDHL(X, y, w, tau):
    grad = 0 # Init to 0
    for i in range(X.shape[0]):
        grad -= 0.5*y[i]*(1 + np.sign(1 - y[i]*np.dot(X[i,:],w)))*X[i,:]
    w_new = w - tau*grad
    return w_new


if __name__ == "__main__":
    # Initialize a dataset
    num_dataset = DATASET
    data = Dataset(num_dataset) # Retrieve dataset object
    # Initialize IterReg feature
    algo = ALGO
    logger = IterReg(algo,num_dataset) # Init logger GDHL

    # Print Header
    print("-- Using dataset {} | ALGO: {} --".format(num_dataset, algo))

    # Load weights
    try:
        w = logger.load() # Load saved weights
    except FileNotFoundError:
        w = np.zeros(data.X_tr.shape[1]) # Init to zeros
    loss_gd = get_loss_HL(data.X_tr, data.y_tr, w) # Comp cost fun
    print("Hot-start Loss Value: {}".format(loss_gd.round(2)))
    print("Press Ctrl+C to stop and show results")
    print("Iterating...")
    tau = 1/(np.linalg.norm(data.X_tr, 2)**2) # Step size
    descent = 1 # Init
    tol = 1e-6 # Convergence tolerance
    while(abs(descent) > tol): # Converge when within tol
        try:
            w_new = step_GDHL(data.X_tr, data.y_tr, w, tau)
            w = w_new
            # Check convergence
            loss_gd_new = get_loss_HL(data.X_tr, data.y_tr, w)
            descent = loss_gd - loss_gd_new
            loss_gd = loss_gd_new
        except KeyboardInterrupt:
            break
    logger.save(w) # Save progress

    # Compute metrics with new w
    y_hat = classify(data.X,w) # Classify test set
    perr = get_perr(y_hat,data.y) # Get percent error
    loss_gd = get_loss_HL(data.X_tr, data.y_tr, w) # Comp cost fun

    # Output results
    print("\nGradient Descent Hinge Loss classification:")
    print("Percent labels misclassified: {}%".format(perr.round(2)))
    print("Training Loss Value: {}".format(loss_gd.round(2)))
