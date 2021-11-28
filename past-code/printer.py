print("Import Strategy and Model")
from strategy import Strategy
from model import Model

print("Init strats")
strats = [
    Strategy("ARDRUSDT", "LSKUSDT", 4, -0.1, 6100, 0.7),
    Strategy("NKNUSDT", "WINUSDT", 4.3, -0.6, 5500, 0.5),
    Strategy("FUNUSDT", "ZRXUSDT", 4.3, -0.4, 4200, 0.5), 
    Strategy("CELRUSDT", "ONGUSDT", 4.3, -0.2, 4200, 0.4), 
    Strategy("CHZUSDT", "ENJUSDT", 4.3, -0.5, 4500, 0.4)
]

print("Turn printer on")
printer = Model(strats)
printer.turn_on()