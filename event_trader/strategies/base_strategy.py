import os
import pandas as pd

class BaseStrategy:
    def __init__(self, stock_data, sub_path):
        self.stock_data = stock_data
        self.params_path = os.path.join('params', sub_path, f'{self.stock_data.code}.csv')
        self.parameters = {}

    def load_parameters(self, default_params):
        """
        Load parameters from a CSV file. If the file does not exist, use the default parameters provided.

        :param default_params: A dictionary where keys are parameter names and values are their default values.
        """
        if os.path.isfile(self.params_path):
            df = pd.read_csv(self.params_path)
            for name in default_params.keys():
                self.parameters[name] = df[name].iloc[0]
        else:
            self.parameters.update(default_params)

    def save_parameters(self):
        os.makedirs(os.path.dirname(self.params_path), exist_ok=True)
        df = pd.DataFrame({name: [value] for name, value in self.parameters.items()})
        df.to_csv(self.params_path, index=False)

    def notify(self, message: str):
        print(f"Notification: {message}")
        
    def __getitem__(self, key: str):
        if (key in self.parameters):
            return self.parameters[key]
        else:
            raise KeyError(f"Key '{key}' not found in { self.__class__.__name__}") 
        
    def __getattr__(self, key: str):
        if (key in self.parameters):
            return self.parameters[key]
        else:
            raise KeyError(f"Key '{key}' not found in  { self.__class__.__name__}") 
