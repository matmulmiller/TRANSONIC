import numpy as np
import pandas as pd


def type_check(dtype, value) -> bool:
    '''
    Checks if the given dtype is a general match of the dtype for a given value

    Paramters:
    - dtpye : the data type you want to compare to
    - value : the value whose data type you want to check

    Returns:
    - bool_val : A boolean value about whether the data types are generally same

    Notes:
    - Trying to check if two variables, one from numpy/pandas and the other just
      normal python data type, (e.g. int32 vs int) in a general way is like 
      making love to a blender.
    '''

    # Put value in numpy array to make numerica type matching easier
    value_arr = np.array([value])

    if value_arr.dtype.kind == dtype.kind:
        bool_val = True
    elif dtype==pd.StringDtype() and type(value)==str:
        # B/c f*** me, pandas thought it would be cool if they had their own
        # string data type
        bool_val = True
    else:
        bool_val = False

    return bool_val
    


def ID_retieval(df: pd.DataFrame, criteria: dict):
    '''
    Returns the indices of the given DataFrame where a set of criteria is true.

    Parameters:
    - df : This is the design of experiments document where parametrs are kept
    - critiera : a dictionary of the form {'critiera': [value1, value2, ...]}

    Returns:
    - A pd.Series object of the indices/labels where the criteria are met. 
    '''

    # Create a pd.Series w/ same index as df and all TRUE values
    filter_series = pd.Series(True, index=df.index)  

    # Iterate through criteria dictionary
    for column, values in criteria.items():

        # Notify if the user provides a criteria that doesn't exist
        if column not in df.columns:
            raise ValueError(f"{column} is not an existing criteria.")
        
        # Check to see if data type in criteria is same as that in df
        if not type_check(df[column].dtype, values[0]):
            raise ValueError(f"Data types do not match for {column}. "
                            f"{column} data type is: {df[column].dtype}"
                            f" and the entered value is type {type(values[0])}")

        # Update filter by using the &= operatoer (e.g. True &= False -> False)
        filter_series &= df[column].isin(values)

    return df.index[filter_series]


def relative_absolute_error(S_true, S_pred):
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
    

if __name__ == '__main__':
    doe = pd.read_csv("data/CASE_PARAMETERS.csv", 
                      dtype={'VISCOUS_MODEL': 'string'})
    print(doe.dtypes)

    criteria = {'FLOW_RATE': [4.0], 
                'PERC_DS': [50],
                'RAMP_ANGLE': [60],
                'VISCOUS_MODEL': ['TURBULENT']}

    idxs = ID_retieval(doe, criteria)

    print(idxs)
