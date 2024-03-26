from src.modules.model_class import Model
from scipy.special import expi
import numpy as np


class LFR_CSTR_WITH_BYPASS(Model):
    """
    LFR_CSTR_WITH_BYPASS model represents a where all flow first enters a 
    laminar flow reactor (LFR). The outlet of the LFR is split into 2 streams:
        - One stream enters into a CSTR
        - One stream bypasses the CSTR and goes to the mixing point 

    Attributes:
    - dt : the amount of time during which the tracer was injected (CFD sim dt)
    - tau : the spacetime of the reactor defined by volume / flow rate
    - bounds : the bounds for the model parameters which are optimized for
    """

    def __init__(self, dt, tau, bounds=None, initial_guess=None):
        """
        Initializes the model 

        Parameters: 
        - See class level doc string
        """
        super().__init__(initial_guess=initial_guess)
        self.dt = dt
        self.tau = tau
        self.bounds = bounds

    def C1_func(self, t, beta):
        """
        This funciton gives the concentration leaving the LFR at some time, t

        Parameters:
        - beta : the fraction of the system volume that is described by the CSTR
        - t : the time or time range to predict over

        Returns:
        - The calculated concentration leaving the LFR at time t
        """
        return (1-beta)**2 * self.tau**2 * self.dt / 2 / t**3

    def exp_term(self, t, a):
        """
        This is a necessary term for calculating the outlet of the CSTR
        """
        return np.exp(a*t)*(a*t + 1)/t**2

    def expi_term(self, t, a):
        """
        This is a necessary term for calculating the outlet of the CSTR
        """
        return a**2 * expi(a*t)

    def C2_func(self, t, alpha, beta):
        """
        Calculates the concentration leaving the CSTR for some time, t

        Parameters:
        - alpha : the fraction of fluid which enters the CSTR
        - beta : the fraction of the system volume that is described by the CSTR

        Returns:
        - The concentration leaving the CSTR at time t

        """

        a = alpha / beta / self.tau
        b = alpha * (1-beta)**2 * self.dt * self.tau / 2 / beta
        tau1 = (1-beta)*self.tau
        C_0 = b*0.5*(self.exp_term(tau1/2, a) - self.expi_term(tau1/2, a))
        C2 = (C_0 - 0.5*b*(self.exp_term(t, a) - self.expi_term(t, a)))/np.exp(a*t)
        return C2
    
    def Cout_func(self, t_range, alpha, beta):
        """
        Outputs the concentration of the whole model weighted by the fraction of
        fluid which bypasses vs the fraction of fluid that enters the CSTR. 

        """

        condition = (1-beta)*self.tau/2
        Cout = np.where(t_range < condition, 
                        0, 
                        (1-alpha)*self.C1_func(t_range, beta) + \
                        alpha*self.C2_func(t_range, alpha, beta))
        return Cout
    
    def function(self, x, a, b):
        self.params = [a, b]
        return self.Cout_func(x, a, b)

