import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def mc_sim_plot(output: Path, airport: str, mc: pd.DataFrame, horizon: int=6) -> None:
    q25 = mc.iloc[:,-(horizon):].quantile(0.25,axis=1)
    med = mc.iloc[:,-(horizon):].quantile(0.50,axis=1)
    q75 = mc.iloc[:,-(horizon):].quantile(0.75,axis=1)

    fig, ax = plt.subplots(figsize=(30,20))
    fig.suptitle(f"Monte Carlo Simulation: {airport} Passenger Volume",fontsize=48)
    ax.plot(mc, color='grey', alpha=0.3,linewidth=3.0)
    ax.plot(q25.iloc[-(horizon+1):],color = 'y',linewidth=3.0, label='25th Percentile')
    ax.plot(q75.iloc[-(horizon+1):],color='r',linewidth=3.0, label='75th Percentile')
    ax.plot(med.iloc[-(horizon+1):], color='b',linewidth=3.0, label='Median')
    ax.set_xlabel('Month',fontsize=24)
    ax.set_ylabel('Passenger Volume',fontsize=24)
    ax.tick_params(axis='both',labelsize=24)
    ax.legend(loc='upper left', fontsize=24)

    airport_dir = output/ airport
    airport_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(airport_dir/ f"{airport}_monte_carlo_sim.svg",dpi=150)
    fig.savefig(airport_dir / f"{airport}_monte_carlo_sim.jpg",dpi=150)
    plt.close(fig)