from GUI.GraphicScenario import *
from Room import *

def main():
    # Creates a graphic scenario
    graphicScenario = GraphicScenario()
    
    #Updates the room and then the graphic scenario
    while 1:
        graphicScenario.update()

if __name__ == '__main__': main()