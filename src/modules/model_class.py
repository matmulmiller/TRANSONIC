import numpy as np 
from scipy.optimize import curve_fit

class Model:
    def __init__(self, initial_guess=None):
        self.initial_guess = initial_guess

    def fit(self, xdata, ydata):
        popt, pcov = curve_fit(self.function, xdata, ydata, 
                               bounds=self.bounds, p0=self.initial_guess)
        self.params = popt
    
    def predict(self, x):
        return self.function(x, *self.params)
    
    def function(self, x, *params):
        raise NotImplementedError("This method should be implemented by subclasses.")