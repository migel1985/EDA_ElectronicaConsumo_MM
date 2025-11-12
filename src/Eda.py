import numpy as np # type: ignore
import pandas as pd # type: ignore
from src.utils.Graficos import Graficos



class Eda:
    dataSet1 = None
    def __init__(self):
        print("paso por init")
        self.dataSet1 = pd.read_csv("src/data/Electronic_sales_Setp2023_sept2024.csv", sep=",", index_col=0)

    def programaPrincipal(self):
        print("programaPrincipal")
        self.graficohp1 = Graficos()
        self.graficohp1.hipotesis1(self.dataSet1)
        self.graficohp1.hipotesis2(self.dataSet1)
        self.graficohp1.hipotesis3(self.dataSet1)
        self.graficohp1.hipotesis4(self.dataSet1)
        self.graficohp1.hipotesis5(self.dataSet1)
        self.graficohp1.hipotesis6(self.dataSet1)
        self.graficohp1.hipotesis7(self.dataSet1)
        self.graficohp1.hipotesis8(self.dataSet1)


    