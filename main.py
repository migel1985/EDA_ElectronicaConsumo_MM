import numpy as np # type: ignore
from src.Eda import Eda


class Main:
    def __init__(self):
        self.eda = None
        
    def ejecutar(self):
        self.eda = Eda()
        self.eda.programaPrincipal()
        pass
        
    
if __name__ == "__main__":
    main = Main()
    main.ejecutar()
    