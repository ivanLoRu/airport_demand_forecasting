import numpy as np
import pandas as pd
from pathlib import Path
from statsmodels.tsa.api import SARIMAX, adfuller

def adf_test(series: pd.Series, name: str = ""):
    result = adfuller(series.dropna(), autolag="AIC")

    output = {
        "test_statistic": result[0],
        "p_value": result[1],
        "n_lags": result[2],
        "n_obs": result[3],
        "critical_values": result[4],
    }

    print(f"\nADF Test: {name}")
    print(f"Test Statistic: {output['test_statistic']:.3f}")
    print(f"P-value: {output['p_value']:.4f}")
    print("Critical Values:")
    for k, v in output["critical_values"].items():
        print(f"  {k}: {v:.3f}")

    return output

def make_monthly(y: pd.Series)->pd.Series:
    y = y.copy()
    y.index = pd.to_datetime(y.index)
    y = y.sort_index(ascending=True)

    if y.isna().any():
        y = y.interpolate(limit_direction="both")
    return y


def wape(y_true: np.array, y_pred: np.array)-> float:
    abs_error = np.sum(np.abs(y_true - y_pred))
    sum_actual = np.sum(np.abs(y_true))
    if sum_actual == 0:
        return 0.0
    return abs_error/sum_actual

def mae(y_true: np.array, y_pred: np.array)-> float:
    return np.mean(np.abs(y_true - y_pred))

#repeat last 12 months forward
def naive_forecast(y: pd.Series, horizon: int=6, season_len = 12) -> pd.Series:
    y= make_monthly(y)
    last = y.iloc[-season_len:]
    reps = int(np.ceil(horizon/season_len))
    forecast = pd.concat([last]*reps).iloc[:horizon]

    future_idx = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    forecast.index = future_idx
    return forecast

def fit_sarima(y: pd.Series, order = (1,1,1), seasonal_order=(1,1,1,12)):
    y= make_monthly(y)
    model = SARIMAX(y, order = order, seasonal_order=seasonal_order, trend="n",
                     enforce_stationarity=False, enforce_invertibility= False)
    res = model.fit(disp=False)
    return res

def sarima_forecast(res, horizon: int=6) -> pd.DataFrame:
    prediction = res.get_forecast(steps=horizon)
    mean = prediction.predicted_mean
    ci = prediction.conf_int(alpha=0.05)

    out = pd.DataFrame({
        "p05":ci.iloc[:,0],
        "p50":mean,
        "p95":ci.iloc[:,1]
    })
    return out

def bootstrap(y: pd.Series, horizon: int=6, n: int=1000, seed: int=43,
              order=(1,1,1), seasonal_order=(1,1,1,12)) ->pd.DataFrame:
    y = make_monthly(y).astype(float)
    eps = 1.0
    y_log = np.log(y+eps)
    rng = np.random.default_rng(seed)

    model = fit_sarima(y_log, order=order, seasonal_order=seasonal_order)
    pred = model.get_forecast(steps=horizon)
    mu = pred.predicted_mean.values
    sigma = pred.se_mean.values

    sims_log = mu[:, None] + rng.normal(0.0, sigma[:, None], size=(horizon,n))
    sims = (np.exp(sims_log))-eps
    sims = np.clip(sims,0, None)
    
    future_idx = pd.date_range(
        y.index[-1]+pd.offsets.MonthBegin(1),
        periods = horizon,
        freq="MS"
    )
    
    return pd.DataFrame(sims,index=future_idx)

def run_forecast(output_dir: Path, data_dir: Path, airport:str, horizon: int=6, num: int=2500 )->pd.DataFrame:
    ##set up data into single df
    data_path = data_dir / "db28_general.csv"
    db28 = pd.read_csv(data_path, parse_dates=["Datetime"])

    ##get airport specific data (arrivals + dep)
    monthly_arr = db28[db28['Destination Airport']==airport].groupby(['Datetime'],as_index=False).agg(
    Passengers = ('Passengers','sum')).set_index("Datetime").sort_index(ascending=True)
    monthly_dep = db28[db28['Origin Airport']==airport].groupby(['Datetime'],as_index=False).agg(
    Passengers = ('Passengers','sum')).set_index("Datetime").sort_index(ascending=True)

    monthly_total = monthly_arr['Passengers'].add(monthly_dep["Passengers"], fill_value=0)
    start = monthly_total.index.min().strftime("%Y-%m")
    end = monthly_total.index.max().strftime("%Y-%m")

    #save data used for forecast
    save_path = data_dir / f"{airport}_{start}_{end}.csv"
    monthly_total.to_csv(save_path, header=False)

    monthly_series = monthly_total.asfreq("MS").interpolate(limit_direction="both")

    #write sarima vs naive results to file
    train = monthly_series.iloc[:-horizon]
    test = monthly_series.iloc[-horizon:]
    naive = naive_forecast(train, horizon)
    res = fit_sarima(train)
    sarima_test = res.get_forecast(steps=horizon).predicted_mean

    fc_mae = mae(test, sarima_test)
    fc_wape = wape(test, sarima_test)
    naive_mae = mae(test, naive)
    naive_wape = wape(test, naive)
    test_results = output_dir / f"{airport}" / "test_results.txt"
    test_results.parent.mkdir(parents=True, exist_ok=True)
    test_results.write_text(
        f"SARIMA Forecast Mean Absolute Error: {fc_mae:.4f}\n"
        f"SARIMA Forecast Weighted Absolute Percentage Error: {fc_wape:.4%}\n"
        f"Naive Forecast Mean Absolute Error: {naive_mae:.4f}\n"
        f"Naive Forecast Weighted Absolute Percentage Error: {naive_wape:.4%}\n"
        )
    
    #monte carlo sim
    sims = bootstrap(monthly_series,horizon,num)
    n_airport = pd.concat([monthly_series]*num,axis=1)
    sims.columns = n_airport.columns
    mc_result = pd.concat([n_airport,sims], axis=0)
    return mc_result
