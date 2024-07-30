from src.modules.model_class import Model
from scipy.special import expi
import numpy as np


class LFR_CSTR_PFR_PARALLEL(Model):
    """
    LFR_CSTR_PFR_PARALLEL model represents a where all flow first enters a 
    laminar flow reactor (LFR). The outlet of the LFR is split into 2 streams:
        - One stream enters into a CSTR
        - One stream enters into a PFR 

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
    
    def C_PFR(self, t, a, b, c):
        tau_LFR = (1-a)*self.tau
        tau_PFR = a * (1 - b) * self.tau / (1 - c)
        C_PFR1 = 0
        C_PFR2 = (1-a)**2 * self.tau**2 * self.C0 * self.dt / 2 / (t - tau_PFR)**3
        C_PFR_out = np.where(t < (tau_LFR/2 + tau_PFR), C_PFR1, C_PFR2)
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
    
    def function(self, x, a, b, c):
        return c * self.C_CSTR(x, a, b, c) + (1 - c) * self.C_PFR(x, a, b, c)
