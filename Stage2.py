import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

class Stage2Controller:
    def __init__(self):
        self.fuzzyLogic()
        # self.displayPlot()

    def fuzzyLogic(self):
        
        self.dist1 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist1')
        self.dist2 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist2')
        self.dist3 = ctrl.Antecedent(np.arange(0, 5000, 1), 'dist3')
        self.speedL = ctrl.Consequent(np.arange(-50, 100, 1), 'speedL')
        self.speedR = ctrl.Consequent(np.arange(-50, 100, 1), 'speedR')

        self.dist1['close'] = fuzz.trapmf(self.dist1.universe, [0, 0, 150, 160])
        self.dist1['ok'] = fuzz.trapmf(self.dist1.universe, [150, 200, 250, 300])
        self.dist1['far'] = fuzz.trapmf(self.dist1.universe, [250, 300, 4900, 5000])

        self.dist2['close'] = fuzz.trapmf(self.dist2.universe, [0, 0, 150, 160])
        self.dist2['ok'] = fuzz.trapmf(self.dist2.universe, [150, 200, 250, 300])
        self.dist2['far'] = fuzz.trapmf(self.dist2.universe, [250, 300, 4900, 5000])

        self.dist3['close'] = fuzz.trapmf(self.dist3.universe, [0, 0, 150, 160])
        self.dist3['ok'] = fuzz.trapmf(self.dist3.universe, [150, 200, 250, 300])
        self.dist3['far'] = fuzz.trapmf(self.dist3.universe, [250, 300, 4900, 5000])

        self.speedL['back'] = fuzz.trapmf(self.speedL.universe, [-20, -10, -5, 0])
        self.speedL['stop'] = fuzz.trapmf(self.speedL.universe, [-5, -2, 2, 5])
        self.speedL['slow'] = fuzz.trapmf(self.speedL.universe, [0, 5, 10, 20])

        self.speedR['back'] = fuzz.trapmf(self.speedR.universe, [-20, -10, -5, 0])
        self.speedR['stop'] = fuzz.trapmf(self.speedR.universe, [-5, -2, 2, 5])
        self.speedR['slow'] = fuzz.trapmf(self.speedR.universe, [0, 5, 10, 20])

        
        rules = [
            ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['ok'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['ok'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['close'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['close'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['ok'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['far'] & self.dist2['far'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),

            ctrl.Rule(self.dist1['ok'] & self.dist2['ok'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['close'] & self.dist2['ok'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['ok'] & self.dist2['far'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),
            ctrl.Rule(self.dist1['close'] & self.dist2['far'] & self.dist3['far'], (self.speedL['stop'], self.speedR['back'])),
    
            
        ]

        self.steering_ctrl = ctrl.ControlSystem(rules)

        self.steering = ctrl.ControlSystemSimulation(self.steering_ctrl)

    def calculateWheelSpeeds(self, d1, d2, d3):
        self.steering.input['dist1'] = d1
        self.steering.input['dist2'] = d2
        self.steering.input['dist3'] = d3
        self.steering.compute()

        return self.steering.output['speedL'], self.steering.output['speedR']
    
    def displayPlot(self):
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(8, 6))


        ax1.plot(self.speedL.universe, self.speedL['back'].mf, 'b', linewidth=1.5, label='Back')
        ax1.plot(self.speedL.universe, self.speedL['stop'].mf, 'g', linewidth=1.5, label='Stop')
        ax1.plot(self.speedL.universe, self.speedL['slow'].mf, 'r', linewidth=1.5, label='Slow')
        ax1.plot(self.speedL.universe, self.speedL['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        ax1.set_title('SpeedL')
        ax1.legend()

        ax2.plot(self.speedR.universe, self.speedR['back'].mf, 'b', linewidth=1.5, label='Back')
        ax2.plot(self.speedR.universe, self.speedR['stop'].mf, 'g', linewidth=1.5, label='Stop')
        ax2.plot(self.speedR.universe, self.speedR['slow'].mf, 'r', linewidth=1.5, label='Slow')
        ax2.plot(self.speedR.universe, self.speedR['fast'].mf, 'orange', linewidth=1.5, label='Fast')
        ax2.set_title('SpeedR')
        ax2.legend()

        for ax in (ax1, ax2):
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()

        plt.tight_layout()
        plt.show()  


