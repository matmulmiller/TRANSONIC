from src.transonic.modules.model_class import Model
from scipy.special import expi
import numpy as np
from sklearn.metrics import mean_squared_error
import math


class TANKS_IN_SERIES(Model):
    """
    Tanks in series model assumes the system to be a series of n CSTRs and uses n to approximate the curve

    in general as n -> inf the model approximates plug flow

    Attributes:
    - dt : the amount of time during which the tracer was injected (CFD sim dt)
    - tau : the spacetime of the reactor defined by volume / flow rate
    - bounds : the bounds for the model parameters which are optimized for
    - C0 : initial concnetration CALCULATED BY N0 / TOTAL REACTOR MASS

    """

    def __init__(self, dt, tau, bounds=None, initial_guess=None, C0=1, rho=1045):
        """
        Initializes the model 

        Parameters: 
        - See class level doc string
        """

        super().__init__(initial_guess=initial_guess)
        self.dt = dt
        self.tau = tau
        self.bounds = bounds
        self.C0 = C0
        self.rho = rho
    
    def C_1(self, t: float, n: float) -> np.array:
        """
        Taylor-Dispersion superimposed on a laminar/plug flow. 

        Parameters:
        - t : time
        - Pe : radial peclet number of the system
        - tau : spacetime of flow path 1

        Returns:
        - np.array that gives concentration predictions for each time stamp
        """

        tau_i = self.tau / n       
        return self.dt * self.C0 * (t**(n-1) / (math.gamma(n-1) * tau_i**(n))) * (np.exp(-t/tau_i))

    
    def function(self, t, n):
        """
        Sums the concentration profiles for flow path 1 and flow path 2.
        """
        return self.C_1(t, n) 

    def objective(self, params, tdata, ytrue):

        n = params
        
        y_predicted = self.function(tdata, n)

        return mean_squared_error(ytrue, y_predicted)