#TODO : Visual of distribution of MAEs
    # - Already have a box and whisker plot set up for RAEs
#TODO : Residual Analysis of somekind
    # - Can't be on a case by case basis because it's just too many
    # - What if I calculated the mean and STD and plotted these versus sim num
#TODO :  Global Model Assessment
    # - Monte Carlo across alpha and beta range 
    # - Sobol indices for characterization
        # - Shelved Sobol indices: parameters must be I.I.D

import numpy as np
from sklearn.metrics import mean_absolute_error
from scipy.stats import shapiro, normaltest, anderson

def MAE_calc(S_true, S_pred):
    '''
    Returns the mean absolute error between a predicted sequence 
    and a ground truth sequence.

    '''

    if len(S_true) != len(S_pred):
        raise ValueError('Cannot perform RAE on sequences of different length.')

    return mean_absolute_error(S_true, S_pred)


def residual_analysis(S_true, S_pred):
    '''
    Calculates the raw residuals of each data point for each experiment. 
    The mean and standard deviation of the residuals are calculated and returned
    to be plotted on a histogram. 
    '''

    residuals = S_true - S_pred
    mu = np.mean(residuals)
    sigma = np.std(residuals)

    return mu, sigma

