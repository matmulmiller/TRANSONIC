import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QShortcut, QAction
from PyQt5.uic import loadUi
from PyQt5.QtGui import  QKeySequence
import os
import subprocess

default_params ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- \'n\''
}

default_bounds ={
    'LFR_DZ_CSTR': '\n- [0.01, 0.99]\n- [0.01, 0.99]',
    'TANKS_IN_SERIES': '\n- [1, \'105\']'
}

tmp_dir = 'tmp'
tmp_config_file = 'tmp/config.yaml'

class ConfigSettings(QWidget):
    def __init__(self):
        super().__init__()
        
        #Initialize
        loadUi("./src/transonic/Windows/ConfigSettings.ui", self)
        self.setWindowTitle("Config Settings")
        self.cwd_label.setText(f"CWD: {os.getcwd()}")
        self.cwd_label.adjustSize()

        #Buttons
        self.make_config.clicked.connect(self.create_config_file)
        
        #Actions

    
    def create_config_file(self):
        model = self.model_select.currentIndex()
        if model == 0:
            model = 'LFR_DZ_CSTR'
        elif model == 1:
            model = 'TANKS_IN_SERIES'
         
        doe_path  = self.doe_path.displayText()
        work_dir = self.work_dir.displayText()
        input_path = self.input_path.displayText()

        if self.default_parameters.isChecked() == True:
            parameters = default_params[model]
            
        if self.default_bounds.isChecked() == True: 
            param_bounds = default_bounds[model]

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        try:
            with open(tmp_config_file,"w") as f:
                f.write(f"model: \'{model}\'\n\ndoe: \'{doe_path}\'\n\nwd: \'{work_dir}\'\n\ninput: \'{input_path}\'\n\nparameters:{parameters}\n\nparameter_bounds: {param_bounds}")
        except:
            print("Failure! Something went wrong trying to generate the file")
        print("Success! Config file generated")

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        #initialize
        loadUi("./src/transonic/Windows/App.ui", self)
        self.setWindowTitle("TRANSONIC")
        self.completion_label.setText(" ")

        #Actions
        close_app = QAction("Exit", self)
        close_app.setShortcut(QKeySequence.Quit)
        close_app.triggered.connect(self.close)
        self.addAction(close_app)
        
        # Keyboard shortcuts
        close_app_keybinding = QShortcut(QKeySequence("Ctrl+W"), self)
        close_app_keybinding.activated.connect(self.close)

        #Buttons
        self.config_button.clicked.connect(self.create_config)
        self.run_button.clicked.connect(self.run_main)


    def create_config(self):
        print("Creating config file...")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        self.config_settings = ConfigSettings()
        self.config_settings.show()
            
    def run_main(self):
        print("Attempting to run model based on setup...")
        self.completion_label.setText("Model running...")
        self.completion_label.adjustSize()
        QApplication.processEvents()
        
        try:
            main_path = 'src/transonic/main.py'
            flag = '-c'
            if os.path.exists(tmp_config_file):
                subprocess.run(['python3',main_path, flag, tmp_config_file])
                print("Main.py successfully ran")
                self.completion_label.setText("Complete")
                self.completion_label.adjustSize()
            else:
                print("No config file")
                self.completion_label.setText("Model did not run.")
                self.completion_label.adjustSize()

            if self.del_after_run.isChecked() == True:
                try:
                    os.remove(tmp_config_file)
                    os.rmdir(tmp_dir)
                except:
                    print("\nError in deleting tmp folder\n")
        except Exception as e:
            print(f"Error in running main")
                  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

