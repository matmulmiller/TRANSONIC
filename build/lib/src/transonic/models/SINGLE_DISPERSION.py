from src.modules.model_class import Model
import numpy as np


class SINGLE_DISPERSION(Model):
    """
    The single dispersion model assumes the flow through the system follows 
    a single flow path that can be represented by laminar/plug flow overlayed 
    with some dispersion. The concentration curves are then added together to 
    predict the output concentration. 

    Attributes:
    - dt : the amount of time during which the tracer was injected (CFD sim dt)
    - tau : the spacetime of the reactor defined by volume / flow rate
    - bounds : the bounds for the model parameters which are optimized for
    - C0 : initial concnetration CALCULATED BY N0 / TOTAL REACTOR MASS

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
    
    def C_1(self, t: float, Pe: float, tau: float) -> np.array:
        """
        Taylor-Dispersion superimposed on a laminar/plug flow. 

        Parameters:
        - t : time
        - Pe : radial peclet number of the system
        - tau : spacetime of flow path 1

        Returns:
        - np.array that gives concentration predictions for each time stamp
        """

        term_1 = 1 / 2 / np.sqrt(np.pi*(t/tau)/Pe)
        term_2 = np.exp(-1 * (1-(t/tau))**2 * Pe / 4 / (t/tau))        
        return np.where(t==0, 0, self.C0 * term_1 * term_2)

    
    def function(self, x, Pe, tau):
        """
        Sums the concentration profiles for flow path 1 and flow path 2.
        """
        return self.C_1(x, Pe, tau) 
