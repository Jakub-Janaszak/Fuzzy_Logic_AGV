import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class Stage1Controller:
    def __init__(self):
        self.fuzzyLogic()
        self.displayPlot()

    def fuzzyLogic(self):
        # Definiowanie zmiennych rozmytych
        self.dist1 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist1')
        self.dist2 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist2')
        self.dist3 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist3')
        self.ratio = ctrl.Antecedent(np.arange(0, 1000, 1), 'ratio')  
        self.speedL = ctrl.Consequent(np.arange(-50, 100, 1), 'speedL')
        self.speedR = ctrl.Consequent(np.arange(-50, 100, 1), 'speedR')

        # Funkcje przynależności dla dist1
        self.dist1['close'] = fuzz.trapmf(self.dist1.universe, [0, 0, 150, 160])
        self.dist1['ok'] = fuzz.trapmf(self.dist1.universe, [150, 200, 250, 300])
        self.dist1['far'] = fuzz.trapmf(self.dist1.universe, [250, 300, 4900, 5000])

        # Funkcje przynależności dla dist2
        self.dist2['close'] = fuzz.trapmf(self.dist2.universe, [0, 0, 150, 160])
        self.dist2['ok'] = fuzz.trapmf(self.dist2.universe, [150, 200, 250, 300])
        self.dist2['far'] = fuzz.trapmf(self.dist2.universe, [250, 300, 4900, 5000])

        # Funkcje przynależności dla dist3
        self.dist3['close'] = fuzz.trapmf(self.dist3.universe, [0, 0, 150, 160])
        self.dist3['ok'] = fuzz.trapmf(self.dist3.universe, [150, 200, 250, 300])
        self.dist3['far'] = fuzz.trapmf(self.dist3.universe, [250, 300, 4900, 5000])

        # Funkcje przynależności dla kąta
        self.ratio['too_right'] = fuzz.trapmf(self.ratio.universe, [0, 0, 105, 120])
        self.ratio['ok'] = fuzz.trapmf(self.ratio.universe, [105, 120, 125, 140])
        self.ratio['too_left'] = fuzz.trapmf(self.ratio.universe, [125, 140, 1000, 1000])

        # Funkcje przynależności dla prędkości
        self.speedL['back'] = fuzz.trapmf(self.speedL.universe, [-50, -30, -15, 0])
        self.speedL['stop'] = fuzz.trapmf(self.speedL.universe, [-15, -5, 5, 15])
        self.speedL['slow'] = fuzz.trapmf(self.speedL.universe, [0, 10, 20, 30])
        self.speedL['fast'] = fuzz.trapmf(self.speedL.universe, [20, 30, 40, 50])

        self.speedR['back'] = fuzz.trapmf(self.speedR.universe, [-50, -30, -15, 0])
        self.speedR['stop'] = fuzz.trapmf(self.speedR.universe, [-15, -5, 5, 15])
        self.speedR['slow'] = fuzz.trapmf(self.speedR.universe, [0, 10, 20, 30])
        self.speedR['fast'] = fuzz.trapmf(self.speedR.universe, [20, 30, 40, 50])

        # Definiowanie reguł rozmytych
        rules = [
            ctrl.Rule(self.ratio['too_right'], (self.speedL['stop'], self.speedR['slow'])),
            ctrl.Rule(self.ratio['ok'], (self.speedL['slow'], self.speedR['slow'])),
            ctrl.Rule(self.ratio['too_left'], (self.speedL['slow'], self.speedR['stop'])),
            ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['close'], (self.speedL['back'], self.speedR['back'])),
            #ctrl.Rule(self.dist1['close'] & self.dist2['close'] & self.dist3['far'], (self.speedL['slow'], self.speedR['stop'])),
            #ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['far'], (self.speedL['fast'], self.speedR['fast'])),
            
        ]

        # Inicjalizacja systemu kontrolnego z listą reguł
        self.steering_ctrl = ctrl.ControlSystem(rules)
        self.steering = ctrl.ControlSystemSimulation(self.steering_ctrl)

    def calculateWheelSpeeds(self, d1, d2, d3):
        # Ustawianie wartości wejściowych z odczytów czujników
        self.steering.input['dist1'] = d1
        self.steering.input['dist2'] = d2
        self.steering.input['dist3'] = d3

        # Obliczanie kąta jako różnicy odległości
        ratio_value = ((d1-60) / d2)*100 if d2 != 0 else 0  # Uniknięcie dzielenia przez zero
        print(f"Ratio: {ratio_value}")
        self.steering.input['ratio'] = ratio_value

        # Wykonanie obliczeń w systemie kontrolnym
        self.steering.compute()

        # Zwrócenie wyników prędkości lewego i prawego silnika
        return self.steering.output['speedL'], self.steering.output['speedR']
    


    def displayPlot(self):
        # Wizualizacja 
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(8, 8))
    
        # Wykres dla speedL
        ax1.plot(self.speedL.universe, self.speedL['back'].mf, 'b', linewidth=1.5, label='Back')
        ax1.plot(self.speedL.universe, self.speedL['stop'].mf, 'g', linewidth=1.5, label='Stop')
        ax1.plot(self.speedL.universe, self.speedL['slow'].mf, 'r', linewidth=1.5, label='Slow')
        ax1.plot(self.speedL.universe, self.speedL['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        ax1.set_title('SpeedL')
        ax1.legend()
    
        # Ustaw formatowanie dla osi x i y
        ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.1f}'))
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.2f}'))
    
        # Wykres dla speedR
        ax2.plot(self.speedR.universe, self.speedR['back'].mf, 'b', linewidth=1.5, label='Back')
        ax2.plot(self.speedR.universe, self.speedR['stop'].mf, 'g', linewidth=1.5, label='Stop')
        ax2.plot(self.speedR.universe, self.speedR['slow'].mf, 'r', linewidth=1.5, label='Slow')
        ax2.plot(self.speedR.universe, self.speedR['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        ax2.set_title('SpeedR')
        ax2.legend()
    
        # Ustaw formatowanie dla osi x i y
        ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.1f}'))
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.2f}'))
    
        # Wykres dla ratio
        ax3.plot(self.ratio.universe, self.ratio['too_right'].mf, 'b', linewidth=1.5, label='Too Right')
        ax3.plot(self.ratio.universe, self.ratio['ok'].mf, 'g', linewidth=1.5, label='OK')
        ax3.plot(self.ratio.universe, self.ratio['too_left'].mf, 'r', linewidth=1.5, label='Too Left')
        ax3.set_title('Ratio')
        ax3.legend()
    
        # Ustaw formatowanie dla osi x i y
        ax3.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.2f}'))
        ax3.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y:.2f}'))
    
        # Wyłączenie górnych i prawych osi
        for ax in (ax1, ax2, ax3):
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
    
        plt.tight_layout()
        plt.show()  # Wyświetlenie wykresu
    
