import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['figure.dpi'] = 300
plt.rcParams['figure.figsize'] = (8,6)


class Plotter:


    def __init__(self, t, y_gt, y_pred, y_label='E(t)',time_unit='s',char_title=[]):

        self.t = t
        self.y_gt = y_gt
        self.y_pred = y_pred
        self.y_label=y_label
        self.time_unit=time_unit
        self.plot_parser_dict = {'pred_vs_gt':self.pred_vs_gt}
        self.char_title = char_title

    
    def pred_vs_gt(self,filename='null.png'):
        plt.plot(self.t, self.y_gt, label="Ground-Truth")
        plt.plot(self.t, self.y_pred, label="Predicted")
        plt.xlabel(f"Time ({self.time_unit})")
        plt.ylabel(f"{self.y_label}")
        if self.char_title:
            plt.title(self.char_title)
        plt.legend()
        plt.savefig(filename)
        return 0
