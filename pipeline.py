import sys
import pandas as pd
from pathlib import Path
from src.forecast_building import run_forecast
from src.plotting_func import mc_sim_plot


ROOT = Path.cwd()
OUTPUT = ROOT / "outputs"
PROCESSED = ROOT / "data" / "processed" / "passenger_volume"

def main():
    if len(sys.argv) < 4:
        print("Error: insufficient amount of arguments passed\n Usage: pipeline.py <Number of Simulations> <Forecast Horizon> <Airport Code>")
    elif len(sys.argv) == 4:
        fc = run_forecast(OUTPUT, PROCESSED, sys.argv[3].upper(), int(sys.argv[2]), int(sys.argv[1]))
        mc_sim_plot(OUTPUT, sys.argv[3].upper(), fc, int(sys.argv[2]))
    else:
        for arg in sys.argv[3:]:
            fc = run_forecast(OUTPUT, PROCESSED, arg.upper(), int(sys.argv[2]), int(sys.argv[1]))
            mc_sim_plot(OUTPUT, arg.upper(), fc, int(sys.argv[2]))


if __name__ == "__main__":
    main()