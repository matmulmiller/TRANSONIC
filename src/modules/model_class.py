import numpy as np 
from scipy.optimize import curve_fit, differential_evolution

class Model:
    def __init__(self, initial_guess=None):
        self.initial_guess = initial_guess


    def fit(self, xdata, ytrue, polish_bool=True):
        '''
        A two-step optimization procedure where differential evolution is 
        applied first and then a polishing step with a gradient based method 
        is used. Fits the model instance to the provided ground truth data.

        Parameters:
        - xdata : np.array
            time sequence to fit over
        - ytrue : np.array
            the ground truth data to fit the model to 
        - polish_bool : bool 
            Bool for whether or not to perform the gradient based optimization step

        Returns: 
        - Nothing, but sets model attribute "params" to optimally found parameters
        '''

        result = differential_evolution(self.objective, 
                                        self.bounds, 
                                        args=(xdata, ytrue),
                                        polish=polish_bool,
                                        seed=69)
        self.params = result.x


    def scipy_curve_fit(self, xdata, ydata, bounds=None):
        try: 
            popt, pcov = curve_fit(self.function, xdata, ydata, 
                                bounds=bounds , p0=self.initial_guess)
            self.params = popt
        except RuntimeError as e:
            print(f"{e}: Couldn't find optimal parameters")
            self.params = [0, 0, 0]
    
    def predict(self, xdata):
        return self.function(xdata, *self.params)
    
    def function(self, x, *params):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def objective(self, params, args):
         raise NotImplementedError("This method should be implemented by subclasses.")
