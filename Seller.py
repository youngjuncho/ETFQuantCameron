import yfinance as yf
import pandas as pd
import pandas_ta as ta

def check_bearish_divergence(df):
    """최근 30일 내 하락 다이버전스 여부 판단"""
    # 1. 고점 비교 (최근 고점 vs 이전 고점)
    current_high = df['High'].iloc[-1]
    prev_high_max = df['High'].iloc[-30:-5].max()

    current_rsi = df['RSI'].iloc[-1]
    prev_rsi_max = df['RSI'].iloc[-30:-5].max()

    # 하락 다이버전스: 가격 고점은 높아졌으나, RSI 고점은 낮아짐 (에너지 고갈)
    if current_high > prev_high_max and current_rsi < prev_rsi_max:
        return True
    return False

def monitor_etf_pro(tickers):
    print(f"📉 [ETF 매도/리스크 정밀 분석] {len(tickers)}개 종목 스캔 중...\n")
    print(f"{'티커':<8} | {'점수':<4} | {'1 2 3 4단계':<12} | {'다이버':<5} | {'RSI'}")
    print("-" * 70)

    for ticker in tickers:
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 지표 계산
            df['RSI'] = ta.rsi(df['Close'], length=14)
            macd = ta.macd(df['Close'])
            df['MACD'] = macd.iloc[:, 0]
            df['MACD_S'] = macd.iloc[:, 2]
            bb = ta.bbands(df['Close'], length=20, std=2)
            df['BBU'] = bb.iloc[:, 2]
            df['MA20'] = ta.sma(df['Close'], length=20)

            curr = df.iloc[-1]
            prev = df.iloc[-2]

            # --- 매도 4단계 체크 ---
            s1 = float(curr['RSI']) > 70                      # 1: 과매수
            s2 = float(curr['High']) >= float(curr['BBU'])    # 2: BB상단 터치
            s3 = prev['MACD'] > prev['MACD_S'] and curr['MACD'] < curr['MACD_S'] # 3: 데드크로스
            s4 = float(curr['Close']) < float(curr['MA20'])   # 4: 20일선 이탈

            # 하락 다이버전스 체크
            has_div = check_bearish_divergence(df)

            score = sum([s1, s2, s3, s4])
            steps_str = "".join(["✅" if s else "❌" for s in [s1, s2, s3, s4]])
            div_str = "⚠️포착" if has_div else "  -  "

            # 특이사항 강조 출력 (다이버전스가 있거나 위험 점수가 높을 때)
            print(f"{ticker:<8} | {score} / 4 | {steps_str:<12} | {div_str:<5} | {round(float(curr['RSI']), 1)}")

        except Exception as e:
            print(f"{ticker:<8} | 분석 에러: {str(e)}")

    print("\n" + "="*70)
    print("📖 [ETF 매도 단계 및 다이버전스 가이드]")
    print("1: 과매수 | 2: BB상단(슈팅) | 3: MACD데드크로스(반전) | 4: 20일선이탈(추세끝)")
    print("⚠️다이버전스: 가격은 오르는데 힘(지표)은 빠짐 -> '폭탄 돌리기' 주의 구간")
    print("="*70)

# 분석할 ETF/주식 티커 (미국/한국 혼합 가능)
my_list = ['IEFA', 'SCHP', 'EMB', 'PDBC', 'BIL', 'GLD', 'IAU', 'SLV', 'IEF', 'QQQ', 'TLT']
monitor_etf_pro(my_list)