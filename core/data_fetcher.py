def get_train_test_data(train_ratio=0.72, period="300d"):
    """Real walk-forward split"""
    data, returns = get_multi_asset_data(period="max")
    split_date = returns.index[int(len(returns)*train_ratio)]
    is_returns = returns.loc[:split_date]
    oos_returns = returns.loc[split_date:]
    return is_returns, oos_returns
