from src.modules.model_class import Model
import numpy as np


class DOUBLE_DISPERSION(Model):
    """
    The double dispersion model assumes the flow through the system follows 
    two paths both of which can be represented by laminar/plug flow overlayed 
    with some dispersion. The concentration curves are then added together to 
    predict the output concentration. 

    Attributes:
    - dt : the amount of time during which the tracer was injected (CFD sim dt)
    - tau : the spacetime of the reactor defined by volume / flow rate
    - bounds : the bounds for the model parameters which are optimized for
    - C0 : initial concnetration CALCULATED BY N0 / TOTAL REACTOR MASS

    Notes:
    - Idea for double taylor-diffusion flows from Lambe, 2011. 
    - The formulation used here is for an open-open vessel boundary conditions.

    References:
     - Lambe, A. T., Ahern, A. T., Williams, L. R., Slowik, J. G., Wong, J. P. S.,
        Abbatt, J. P. D., Brune, W. H., Ng, N. L., Wright, J. P., Croasdale, D. R.,
        Worsnop, D. R., Davidovits, P., & Onasch, T. B.. (2011). Characterization of
        aerosol photooxidation flow reactors: heterogeneous oxidation, secondary 
        organic aerosol formation and cloud condensation nuclei activity measurements.
        Atmospheric Measurement Techniques, 4(3), 445–461. https://doi.org/10.5194/amt-4-445-2011
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
    
    def C_1(self, t: float, Pe1: float, tau1: float) -> np.array:
        """
        Taylor-Dispersion superimposed on flow path 1. 

        Parameters:
        - t : time
        - Pe1 : radial peclet number of the system
        - tau1 : spacetime of flow path 1

        Returns:
        - np.array that gives concentration predictions for each time stamp
        """

        term_1 = 1 / 2 / np.sqrt(np.pi*(t/tau1)/Pe1)
        term_2 = np.exp(-1 * (1-(t/tau1))**2 * Pe1 / 4 / (t/tau1))        
        return np.where(t==0, 0, self.C0 * term_1 * term_2)

    def C_2(self, t: float, Pe2: float, tau2: float) -> np.array:
        """
        Taylor-Dispersion superimposed on flow path 2. 

        Parameters:
        - t : time
        - Pe2 : radial peclet number of the system
        - tau2 : spacetime of flow path 2

        Returns:
        - np.array that gives concentration predictions for each time stamp
        """

        term_1 = 1 / 2 / np.sqrt(np.pi*(t/tau2)/Pe2)
        term_2 = np.exp(-1 * (1-(t/tau2))**2 * Pe2 / 4 / (t/tau2))        
        return np.where(t==0, 0, self.C0 * term_1 * term_2)
    
    def function(self, x, Pe1, Pe2, tau1, tau2):
        """
        Sums the concentration profiles for flow path 1 and flow path 2.
        """
        return self.C_1(x, Pe1, tau1) + self.C_2(x, Pe2, tau2)
