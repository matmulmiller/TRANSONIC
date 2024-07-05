from src.modules.model_class import Model
from scipy.special import expi
import numpy as np
from sklearn.metrics import mean_squared_error


class LFR_CSTR_DZ_BYPASS(Model):
    """
    LFR_CSTR_DZ_BYPASS model represents a where all flow first enters a 
    laminar flow reactor (LFR). The outlet of the LFR is split into 2 streams:
        - One stream enters into a CSTR
            - The CSTR contains a deadzone within it
        - One stream bypasses the CSTR and goes straight to the exit

    Attributes:
    - dt : the amount of time during which the tracer was injected (CFD sim dt)
    - tau : the spacetime of the reactor defined by volume / flow rate
    - bounds : the bounds for the model parameters which are optimized for
    - C0 : initial concnetration injected in pulse experiment
    """

    def __init__(self, dt, tau, bounds=None, initial_guess=None, C0=1):
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
    
    def C_LFR(self, t, a):
        """
        Given the time and LFR volume parameter, a, this function outputs the 
        concentration leaving the LFR and bypassing the CSTR at some time, t. 

        Parameters:
        """

        tau_LFR = (1-a)*self.tau
        C_LFR1 = 0
        C_LFR2 = (1-a)**2 * self.tau**2 * self.C0 * self.dt / 2 / t**3
        C_PFR_out = np.where(t < (tau_LFR/2), C_LFR1, C_LFR2)
        return C_PFR_out
    
    def exp_term(self, t, m):
        """
        This is a necessary term for calculating the outlet of the CSTR
        """

        return np.exp(m*t)*(m*t + 1)/t**2

    def expi_term(self, t, m):
        """
        This is a necessary term for calculating the outlet of the CSTR
        """

        return m**2 * expi(m*t)

    def C_CSTR(self, t, a, b, c):
        """
        Calculates the concentration leaving the CSTR for some time, t

        Parameters:
        - alpha : the fraction of fluid which enters the CSTR
        - beta : the fraction of the system volume that is described by the CSTR

        Returns:
        - The concentration leaving the CSTR at time t

        """

        m = c / (a * b * self.tau)
        n = c * (1 - a)**2 * self.tau * self.dt * self.C0 / a / b
        tau_LFR = (1 - a)*self.tau
        C_0 = 0
        C_IC = n*0.5*(self.exp_term(tau_LFR/2, m) - self.expi_term(tau_LFR/2, m))
        C_1 = (C_IC - 0.5*n*(self.exp_term(t, m) - self.expi_term(t, m)))/np.exp(m*t)
        C_CSTR_out = np.where(t < tau_LFR/2, C_0, C_1)
        return C_CSTR_out
    
    def function(self, xdata, a, b, c):
        return c * self.C_CSTR(xdata, a, b, c) + (1 - c) * self.C_LFR(xdata, a)

    def objective(self, params, xdata, ytrue):
        a, b, c = params
        y_predicted = self.function(xdata, a, b, c)
        return mean_squared_error(ytrue, y_predicted)