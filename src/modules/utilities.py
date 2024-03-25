import numpy as np
import pandas as pd


def type_check(value1, value2):
    '''
    Checks if two values are of the same type and returns the truth value

    Paramters:
    - value1 : the base value to be compared against
    - value2 : the given value to compare against value1

    Notes:
    - We first check to see if the first value has the '.item()' attribute to
      handle values taken from pandas dataframes or numpy arrays.
    '''

    if hasattr(value1, 'item'):
        status = isinstance(value2, type(value1.item()))
    else:
        status = isinstance(value2, type(value1))
    return status


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
        if not type_check(df[column][0], values[0]):
            raise ValueError(f"Data types do not match for {column}. "
                            f"{column} data type is: {type(df[column][0])}"
                            f"and the entered value is type {type(values[0])}")

        # Update filter by using the &= operatoer (e.g. True &= False -> False)
        filter_series &= df[column].isin(values)

    return df.index[filter_series]
    

if __name__ == '__main__':
    doe = pd.read_csv("data/CASE_PARAMETERS.csv")

    criteria = {'FLOW_RATE': [1.75, 4.0], 
                'PERC_DS': [20, 50]}

    idxs = ID_retieval(doe, criteria)

    print(idxs)