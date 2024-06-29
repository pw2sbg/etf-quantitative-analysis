from abc import ABC
import pandas as pd



class File(ABC):



    def __init__(self, file_name: str):
        
        self.file_name = file_name
        self.dataframe = pd.read_csv(self.file_name)
        self.headers = list(self.dataframe.columns)
        self.rows, self.columns = self.dataframe.shape



    def check_headers(self):
        pass