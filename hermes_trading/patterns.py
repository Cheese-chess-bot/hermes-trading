def get_patterns(bars):
    if len(bars) < 5: return []
    p = []
    
    # Extract last 3 candles
    # bars is expected to be a list of dicts: {'open':..., 'close':..., 'high':..., 'low':...}
    c1 = bars[-1] # Latest
    c2 = bars[-2] # 1 ago
    c3 = bars[-3] # 2 ago
    
    # Helper for candle metrics
    def get_metrics(c):
        body = abs(c['close'] - c['open'])
        high_wick = c['high'] - max(c['open'], c['close'])
        low_wick = min(c['open'], c['close']) - c['low']
        range_val = c['high'] - c['low'] if c['high'] - c['low'] > 0 else 0.0001
        is_green = c['close'] > c['open']
        is_red = c['close'] < c['open']
        return body, high_wick, low_wick, range_val, is_green, is_red

    body1, high_wick1, low_wick1, range1, is_green1, is_red1 = get_metrics(c1)
    body2, high_wick2, low_wick2, range2, is_green2, is_red2 = get_metrics(c2)
    body3, high_wick3, low_wick3, range3, is_green3, is_red3 = get_metrics(c3)
    
    # Average body size (last 10)
    bodies = [abs(b['close'] - b['open']) for b in bars[-10:]]
    avg_body = sum(bodies) / len(bodies)
    if avg_body == 0: avg_body = 0.0001

    # 1-CANDLE PATTERNS
    if body1 / range1 < 0.1: p.append("Doji")
    if body1 / range1 < 0.1 and low_wick1 > high_wick1 * 3: p.append("Dragonfly Doji")
    if body1 / range1 < 0.1 and high_wick1 > low_wick1 * 3: p.append("Gravestone Doji")
    if low_wick1 > body1 * 2 and high_wick1 < body1 * 0.2 and is_green1: p.append("Hammer")
    if low_wick1 > body1 * 2 and high_wick1 < body1 * 0.2 and is_red1: p.append("Hanging Man")
    if high_wick1 > body1 * 2 and low_wick1 < body1 * 0.2 and is_green1: p.append("Inverted Hammer")
    if high_wick1 > body1 * 2 and low_wick1 < body1 * 0.2 and is_red1: p.append("Shooting Star")
    if low_wick1 < body1 * 0.1 and high_wick1 < body1 * 0.1 and is_green1 and body1 > avg_body: p.append("Bullish Marubozu")
    if low_wick1 < body1 * 0.1 and high_wick1 < body1 * 0.1 and is_red1 and body1 > avg_body: p.append("Bearish Marubozu")

    # 2-CANDLE PATTERNS
    if is_red2 and is_green1 and c1['close'] > c2['open'] and c1['open'] < c2['close']: p.append("Bullish Engulfing")
    if is_green2 and is_red1 and c1['close'] < c2['open'] and c1['open'] > c2['close']: p.append("Bearish Engulfing")
    if is_red2 and is_green1 and c1['open'] < c2['close'] and c1['close'] > c2['close'] + (body2/2): p.append("Piercing Line")
    if is_green2 and is_red1 and c1['open'] > c2['close'] and c1['close'] < c2['close'] - (body2/2): p.append("Dark Cloud Cover")
    if is_red2 and is_green1 and c1['open'] > c2['close'] and c1['close'] < c2['open']: p.append("Bullish Harami")
    if is_green2 and is_red1 and c1['open'] < c2['close'] and c1['close'] > c2['open']: p.append("Bearish Harami")
    if abs(c1['low'] - c2['low']) < (avg_body * 0.1) and low_wick1 > body1 and low_wick2 > body2: p.append("Tweezer Bottom")
    if abs(c1['high'] - c2['high']) < (avg_body * 0.1) and high_wick1 > body1 and high_wick2 > body2: p.append("Tweezer Top")

    # 3-CANDLE PATTERNS
    if is_red3 and body2 < avg_body * 0.3 and is_green1 and c1['close'] > c3['open'] - (body3/2): p.append("Morning Star")
    if is_green3 and body2 < avg_body * 0.3 and is_red1 and c1['close'] < c3['open'] + (body3/2): p.append("Evening Star")
    if is_green3 and is_green2 and is_green1 and c1['close'] > c2['close'] and c2['close'] > c3['close']: p.append("3 White Soldiers")
    if is_red3 and is_red2 and is_red1 and c1['close'] < c2['close'] and c2['close'] < c3['close']: p.append("3 Black Crows")

    return list(set(p))
