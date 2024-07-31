import pandas as pd
import matplotlib.pyplot as plt
import os.path as path
import numpy as np

from sklearn.metrics import mean_absolute_error
from scipy.stats import shapiro, normaltest, anderson
from src.transonic.modules.utilities import *


def calculate_relative_absolute_error(S_true, S_pred):
    r'''
    Returns the relative absolute error between a predicted sequence and a ground truth sequence.
    .. math::
            \frac{\sum_{i=1}^{N} |(S_{i}^{true} - S_{i}^{pred})|}{\sum_{i=1}^{N} |(S_i^{true} - \overbar{S^{true}})|}

    Parameters:
    - S_true: list type value which contains the true sequence from experiment
    - S_pred: list type value which contains the model predicted values

    Returns:
    - SAE/SSE: relative absolute error between prediction and ground truth for the given inputs
    '''

    if len(S_true) != len(S_pred):
        raise ValueError('Cannot perform RAE on sequences of different length.')

    SAE = sum(np.abs(S_true - S_pred))
    SSE = sum(np.abs(S_true - np.mean(S_true)))
    return SAE/SSE


def calculate_mean_absolute_error(S_true, S_pred):
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


def fit_model(model_class, model_name, system_attr, config):
    attrs = system_attr.X

    if model_name=='TAYLOR_DISPERSION':
        C0=attrs.FLOW_RATE*10**-6 * attrs.TIMESTEP_SIZE / attrs.ARTERIAL_VOLUME
    else:
        C0=1


    model_instance = model_class(
        attrs.TIMESTEP_SIZE, 
        attrs.tau, 
        C0=C0,
        bounds=config['parameter_bounds']
    )

    model_instance.fit(system_attr.C.time, system_attr.C.mass_fraction)
    
    return model_instance


def generate_model_summary(system_attrs):
    
    RAE = calculate_relative_absolute_error(
        system_attrs.C.mass_fraction,
        system_attrs.C_pred.mass_fraction
    )
    

    MAE = calculate_mean_absolute_error(
        system_attrs.C.mass_fraction,
        system_attrs.C_pred.mass_fraction
    )

    mean_residual, std_deviation_of_residuals = residual_analysis(
        system_attrs.C.mass_fraction,
        system_attrs.C_pred.mass_fraction
    )

    return [RAE, MAE, mean_residual, std_deviation_of_residuals]


def append_model_summary(summary_df, id, metrics, model_instance):
    new_row = model_instance.params
    new_row = np.append(new_row, metrics, axis=0)
    summary_df.loc[id] = new_row.tolist()
    return summary_df


def visualize_fit(system_attrs, results_folder):
    # Visualize each fitted line
    plt.figure()
    plt.plot(system_attrs.C.time, system_attrs.C.mass_fraction, label='CFD')
    plt.plot(
            system_attrs.C_pred.time, 
            system_attrs.C_pred.mass_fraction, 
            label='Predicted', 
            linestyle='--'
    )

    title = (f'Q={system_attrs.X.FLOW_RATE} mL/s,'
        + f'%DS={system_attrs.X.PERC_DS},' 
        + f'SRA={system_attrs.X.RAMP_ANGLE}\u00B0'
    )
    
    plt.title(title)
    plt.legend()
    plt.xlabel('Normalized Time')
    plt.ylabel('Normalized E(t)')

    file_name = f'Q{system_attrs.X.FLOW_RATE}_DS{system_attrs.X.PERC_DS}_SRA{system_attrs.X.RAMP_ANGLE}.png'

    plt.savefig(path.join(results_folder, file_name))
    plt.close()





