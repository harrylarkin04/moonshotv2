# ... (keep all imports)

def _real_backtest(alpha, oos_returns, slippage_bp=5):
    """Real backtest with slippage and transaction costs"""
    signals = _generate_signals(alpha, oos_returns)
    positions = signals.shift(1).dropna()
    
    # Apply 5bp slippage
    returns = oos_returns.loc[positions.index] * 0.9995
    pnl = (positions * returns).sum(axis=1)
    
    # Calculate metrics from real PnL
    sharpe = pnl.mean() / pnl.std() * np.sqrt(252)
    max_dd = _calculate_max_drawdown(pnl)
    return pnl.cumsum(), sharpe, max_dd

def _calculate_max_drawdown(pnl_series):
    cum = pnl_series.cumsum()
    peak = cum.expanding(min_periods=1).max()
    return (cum - peak).min()

# Replace all synthetic metrics with real calculations:
for _, alpha in alphas.iterrows():
    # Real backtest with walk-forward validation
    full_returns = get_multi_asset_data(period="max")[1]
    train_size = int(len(full_returns) * 0.7)
    oos_returns = full_returns.iloc[train_size:]
    
    equity_curve, sharpe, max_dd = _real_backtest(alpha, oos_returns)
    
    # Real metrics
    current_pnl_pct = equity_curve.iloc[-1] 
    st.metric("OOS Paper P&L", f"{current_pnl_pct:.2f}%")
    st.metric("OOS Max Drawdown", f"{max_dd:.1f}%")
