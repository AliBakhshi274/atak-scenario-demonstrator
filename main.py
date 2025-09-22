from view.SimulationGUI import SimulationGUI
import time

def main():
    app = SimulationGUI()
    app.mainloop()
        
if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Program terminated.")
