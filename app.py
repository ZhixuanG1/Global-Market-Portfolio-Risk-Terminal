import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from math import erfc, log, sqrt
from statistics import NormalDist
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


TRADING_DAYS = 252
FACTOR_PROXY_TICKERS = ["SPY", "IWM", "IVE", "IVW", "MTUM", "TLT", "SHY"]
CREDIT_PROXY_TICKERS = ["HYG", "LQD", "SHY"]
APP_NAME = "Global Market & Portfolio Risk Terminal"
BENCHMARK_OPTIONS = {
    "S&P 500 ETF": "SPY",
    "Nasdaq 100 ETF": "QQQ",
    "Russell 2000 ETF": "IWM",
    "US Aggregate Bonds": "AGG",
    "US Treasury 20Y+": "TLT",
    "Financials Sector": "XLF",
    "DAX Germany": "^GDAXI",
    "Euro Stoxx 50": "^STOXX50E",
    "MSCI EAFE ETF": "EFA",
    "Emerging Markets ETF": "EEM",
}
SECTOR_PROXY_TICKERS = {
    "Technology": "XLK",
    "Financial Services": "XLF",
    "Healthcare": "XLV",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Basic Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communication Services": "XLC",
}
FRED_RATE_SERIES = {
    "SOFR": "SOFR",
    "Fed Funds": "DFF",
    "3M Treasury": "DGS3MO",
    "2Y Treasury": "DGS2",
    "10Y Treasury": "DGS10",
    "30Y Treasury": "DGS30",
    "30Y Mortgage": "MORTGAGE30US",
}
LIVE_RATE_TICKERS = {
    "13W T-Bill": "^IRX",
    "5Y Treasury": "^FVX",
    "10Y Treasury": "^TNX",
    "30Y Treasury": "^TYX",
}
GLOBAL_MARKET_TICKERS = {
    "United States": "^GSPC",
    "Germany": "^GDAXI",
    "Eurozone": "^STOXX50E",
    "United Kingdom": "^FTSE",
    "France": "^FCHI",
    "Japan": "^N225",
    "Hong Kong": "^HSI",
    "China": "000001.SS",
    "India": "^NSEI",
    "Australia": "^AXJO",
    "Canada": "^GSPTSE",
    "Brazil": "^BVSP",
}
GLOBAL_MARKET_INDEX_DETAILS = {
    "United States": {
        "Index Name": "S&P 500 Index",
        "Ticker": "^GSPC",
        "Provider": "S&P Dow Jones Indices",
        "Description": "Large-cap U.S. equity benchmark covering 500 leading listed companies.",
    },
    "Germany": {
        "Index Name": "DAX Performance Index",
        "Ticker": "^GDAXI",
        "Provider": "STOXX / Deutsche Boerse",
        "Description": "Blue-chip German equity index of major Frankfurt-listed companies.",
    },
    "Eurozone": {
        "Index Name": "EURO STOXX 50 Index",
        "Ticker": "^STOXX50E",
        "Provider": "STOXX",
        "Description": "Blue-chip Eurozone equity benchmark across leading sector leaders.",
    },
    "United Kingdom": {
        "Index Name": "FTSE 100 Index",
        "Ticker": "^FTSE",
        "Provider": "FTSE Russell",
        "Description": "Large-cap U.K. equity benchmark of companies listed on the London Stock Exchange.",
    },
    "France": {
        "Index Name": "CAC 40 Index",
        "Ticker": "^FCHI",
        "Provider": "Euronext",
        "Description": "Major French equity benchmark of 40 large Paris-listed companies.",
    },
    "Japan": {
        "Index Name": "Nikkei 225 Index",
        "Ticker": "^N225",
        "Provider": "Nikkei",
        "Description": "Price-weighted benchmark of 225 leading Tokyo-listed Japanese companies.",
    },
    "Hong Kong": {
        "Index Name": "Hang Seng Index",
        "Ticker": "^HSI",
        "Provider": "Hang Seng Indexes",
        "Description": "Hong Kong blue-chip equity benchmark.",
    },
    "China": {
        "Index Name": "SSE Composite Index",
        "Ticker": "000001.SS",
        "Provider": "Shanghai Stock Exchange",
        "Description": "Broad Shanghai-listed A-share and B-share equity benchmark.",
    },
    "India": {
        "Index Name": "NIFTY 50 Index",
        "Ticker": "^NSEI",
        "Provider": "NSE Indices",
        "Description": "Large-cap Indian equity benchmark of 50 National Stock Exchange companies.",
    },
    "Australia": {
        "Index Name": "S&P/ASX 200 Index",
        "Ticker": "^AXJO",
        "Provider": "S&P Dow Jones Indices / ASX",
        "Description": "Australian equity benchmark covering the largest ASX-listed companies.",
    },
    "Canada": {
        "Index Name": "S&P/TSX Composite Index",
        "Ticker": "^GSPTSE",
        "Provider": "S&P Dow Jones Indices / TMX",
        "Description": "Broad Canadian equity benchmark for Toronto-listed companies.",
    },
    "Brazil": {
        "Index Name": "Ibovespa Index",
        "Ticker": "^BVSP",
        "Provider": "B3",
        "Description": "Primary Brazilian equity benchmark for B3-listed stocks.",
    },
}
GLOBAL_FX_TICKERS = {
    "DXY": "DX-Y.NYB",
    "EUR/USD": "EURUSD=X",
    "USD/JPY": "JPY=X",
    "GBP/USD": "GBPUSD=X",
    "USD/CNY": "CNY=X",
    "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "EUR/GBP": "EURGBP=X",
}
GLOBAL_CURRENCIES = [
    "USD",
    "EUR",
    "JPY",
    "GBP",
    "CNY",
    "CHF",
    "AUD",
    "CAD",
    "HKD",
    "SGD",
    "KRW",
    "INR",
    "BRL",
    "MXN",
    "ZAR",
    "SEK",
    "NOK",
    "DKK",
]
GERMAN_EQUITY_FALLBACK = [
    {"Ticker": "ADS.DE", "Company": "Adidas AG", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "ALV.DE", "Company": "Allianz SE", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "BAS.DE", "Company": "BASF SE", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "BAYN.DE", "Company": "Bayer AG", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "BMW.DE", "Company": "BMW AG", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "DTE.DE", "Company": "Deutsche Telekom AG", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "MBG.DE", "Company": "Mercedes-Benz Group AG", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "SAP.DE", "Company": "SAP SE", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "SIE.DE", "Company": "Siemens AG", "Exchange": "Xetra", "Region": "Germany"},
    {"Ticker": "VOW3.DE", "Company": "Volkswagen AG Pref", "Exchange": "Xetra", "Region": "Germany"},
]
FIXED_INCOME_PRODUCTS = [
    {"Ticker": "BIL", "Company": "SPDR Bloomberg 1-3 Month T-Bill ETF", "Region": "US", "Category": "Treasury Bills", "Duration Bucket": "Ultra Short", "Currency": "USD"},
    {"Ticker": "SHY", "Company": "iShares 1-3 Year Treasury Bond ETF", "Region": "US", "Category": "Government Bonds", "Duration Bucket": "Short", "Currency": "USD"},
    {"Ticker": "IEF", "Company": "iShares 7-10 Year Treasury Bond ETF", "Region": "US", "Category": "Government Bonds", "Duration Bucket": "Intermediate", "Currency": "USD"},
    {"Ticker": "TLT", "Company": "iShares 20+ Year Treasury Bond ETF", "Region": "US", "Category": "Government Bonds", "Duration Bucket": "Long", "Currency": "USD"},
    {"Ticker": "TIP", "Company": "iShares TIPS Bond ETF", "Region": "US", "Category": "Inflation Linked", "Duration Bucket": "Intermediate", "Currency": "USD"},
    {"Ticker": "AGG", "Company": "iShares Core U.S. Aggregate Bond ETF", "Region": "US", "Category": "Aggregate Bonds", "Duration Bucket": "Intermediate", "Currency": "USD"},
    {"Ticker": "LQD", "Company": "iShares iBoxx Investment Grade Corporate Bond ETF", "Region": "US", "Category": "Investment Grade Credit", "Duration Bucket": "Intermediate", "Currency": "USD"},
    {"Ticker": "HYG", "Company": "iShares iBoxx High Yield Corporate Bond ETF", "Region": "US", "Category": "High Yield Credit", "Duration Bucket": "Short", "Currency": "USD"},
    {"Ticker": "MBB", "Company": "iShares MBS ETF", "Region": "US", "Category": "Securitized Credit", "Duration Bucket": "Intermediate", "Currency": "USD"},
    {"Ticker": "EMB", "Company": "iShares J.P. Morgan USD Emerging Markets Bond ETF", "Region": "Global", "Category": "Emerging Market Debt", "Duration Bucket": "Intermediate", "Currency": "USD"},
    {"Ticker": "EXX6.DE", "Company": "iShares eb.rexx Government Germany 1.5-2.5yr UCITS ETF", "Region": "Germany", "Category": "German Government Bonds", "Duration Bucket": "Short", "Currency": "EUR"},
    {"Ticker": "EXX7.DE", "Company": "iShares eb.rexx Government Germany 2.5-5.5yr UCITS ETF", "Region": "Germany", "Category": "German Government Bonds", "Duration Bucket": "Intermediate", "Currency": "EUR"},
    {"Ticker": "EXX8.DE", "Company": "iShares eb.rexx Government Germany 5.5-10.5yr UCITS ETF", "Region": "Germany", "Category": "German Government Bonds", "Duration Bucket": "Long", "Currency": "EUR"},
    {"Ticker": "EUN5.DE", "Company": "iShares Core Euro Government Bond UCITS ETF", "Region": "Germany", "Category": "Euro Government Bonds", "Duration Bucket": "Intermediate", "Currency": "EUR"},
    {"Ticker": "IBCX.DE", "Company": "iShares Euro Corporate Bond Large Cap UCITS ETF", "Region": "Germany", "Category": "Euro Investment Grade Credit", "Duration Bucket": "Intermediate", "Currency": "EUR"},
]


st.set_page_config(page_title=APP_NAME, layout="wide")
st.markdown(
    """
    <style>
    :root {
        --bg: #1B1931;
        --panel: #241b37;
        --panel-2: #2c1b3a;
        --line: rgba(233, 188, 185, 0.16);
        --text: #f8ece8;
        --muted: #caa6ad;
        --accent: #ED9E59;
        --accent-2: #A34054;
        --good: #E9BCB9;
        --warn: #ED9E59;
        --bad: #ff6f7e;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(102, 34, 73, 0.32), transparent 34rem),
            linear-gradient(135deg, #1B1931 0%, #241633 48%, #44174E 100%);
        color: var(--text);
    }

    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: transparent;
        height: 2.15rem;
        pointer-events: auto;
    }

    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu {
        display: none;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
        color: #ED9E59 !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 9999 !important;
    }

    [data-testid="stToolbar"] button {
        background: #241b37 !important;
        border: 1px solid rgba(237, 158, 89, 0.34) !important;
        color: #ED9E59 !important;
        box-shadow: none !important;
    }

    [data-testid="stToolbar"] svg {
        color: #ED9E59 !important;
        fill: #ED9E59 !important;
    }

    .block-container {
        padding-top: 0;
        padding-left: 1.15rem;
        padding-right: 1.15rem;
        padding-bottom: 1.2rem;
        max-width: 96vw;
    }

    [data-testid="stSidebar"] {
        background: #171529;
        border-right: 1px solid var(--line);
        width: 19.5rem !important;
        min-width: 0 !important;
        max-width: 19.5rem !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"][aria-hidden="true"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        border-right: 0 !important;
    }

    [data-testid="stAppViewContainer"] > .main,
    section.main {
        width: 100% !important;
    }

    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    button[aria-label*="sidebar" i],
    button[title*="sidebar" i] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 9999 !important;
        pointer-events: auto !important;
    }

    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    button[aria-label*="sidebar" i],
    button[title*="sidebar" i] {
        background: #241b37 !important;
        border: 1px solid rgba(237, 158, 89, 0.42) !important;
        color: #ED9E59 !important;
        box-shadow: none !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    button[aria-label*="sidebar" i] svg,
    button[title*="sidebar" i] svg {
        color: #ED9E59 !important;
        fill: #ED9E59 !important;
    }

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--text);
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-top: 0.75rem;
    }

    h1, h2, h3 {
        color: var(--text);
        letter-spacing: 0;
    }

    h2 {
        font-size: 0.98rem !important;
        margin-top: 0.8rem !important;
        padding-top: 0.2rem;
        border-top: 0;
    }

    .terminal-header {
        border: 1px solid var(--line);
        background:
            linear-gradient(135deg, rgba(68, 23, 78, 0.92), rgba(27, 25, 49, 0.92)),
            linear-gradient(90deg, rgba(237, 158, 89, 0.14), rgba(163, 64, 84, 0.06));
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.7rem;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.22);
    }

    .terminal-title {
        color: var(--text);
        font-size: 1.22rem;
        font-weight: 720;
        margin: 0;
    }

    .terminal-subtitle {
        color: var(--muted);
        font-size: 0.78rem;
        margin-top: 0.18rem;
    }

    .context-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.38rem;
        margin-top: 0.58rem;
    }

    .context-pill {
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        color: var(--muted);
        background: rgba(27, 25, 49, 0.64);
        font-size: 0.72rem;
        font-weight: 600;
    }

    .status-pass {
        color: var(--good);
        border-color: rgba(233, 188, 185, 0.28);
        background: rgba(233, 188, 185, 0.08);
    }

    .status-review {
        color: var(--bad);
        border-color: rgba(255, 111, 126, 0.28);
        background: rgba(255, 111, 126, 0.1);
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        width: fit-content;
        min-width: 4.2rem;
        justify-content: center;
        border-radius: 999px;
        padding: 0.16rem 0.52rem;
        font-size: 0.72rem;
        font-weight: 820;
        border: 1px solid transparent;
    }

    .status-badge.green,
    .status-badge.pass {
        color: #72f0a2;
        background: rgba(47, 158, 88, 0.18);
        border-color: rgba(114, 240, 162, 0.34);
    }

    .status-badge.yellow,
    .status-badge.review {
        color: #ED9E59;
        background: rgba(237, 158, 89, 0.18);
        border-color: rgba(237, 158, 89, 0.34);
    }

    .status-badge.red,
    .status-badge.fail {
        color: #ff6f7e;
        background: rgba(255, 111, 126, 0.18);
        border-color: rgba(255, 111, 126, 0.34);
    }

    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.62rem 0.72rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 10px 24px rgba(0, 0, 0, 0.14);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-size: 0.7rem;
    }

    [data-testid="stMetricValue"] {
        color: var(--text);
        font-size: 1.08rem;
        font-weight: 720;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.68rem;
    }

    .metric-card {
        min-height: 4.42rem;
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.62rem 0.72rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 10px 24px rgba(0, 0, 0, 0.14);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.7rem;
        font-weight: 700;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.16rem;
        border-bottom: 1px solid var(--line);
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        height: 2rem;
        border-radius: 6px 6px 0 0;
        padding: 0.28rem 0.58rem;
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 650;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent);
        background: rgba(237, 158, 89, 0.12);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.7rem;
    }

    .stSelectbox, .stMultiSelect, .stTextInput, .stNumberInput, .stSlider {
        font-size: 0.78rem;
    }

    div[data-baseweb="select"],
    div[data-baseweb="input"] {
        background: transparent;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background-color: #241b37 !important;
        border-color: var(--line) !important;
        color: var(--text) !important;
        caret-color: #ED9E59 !important;
        border-radius: 7px !important;
        min-height: 2rem;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
    [data-testid="stSidebar"] [data-testid="stNumberInput"] input:focus {
        caret-color: #ED9E59 !important;
        border-color: #ED9E59 !important;
        box-shadow: 0 0 0 1px rgba(237, 158, 89, 0.42) !important;
        outline: none !important;
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] svg,
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        color: var(--text) !important;
        caret-color: #ED9E59 !important;
        fill: var(--muted) !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #241b37 !important;
        color: var(--text) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
    }

    [role="listbox"],
    [role="option"] {
        background: #241b37 !important;
        color: var(--text) !important;
    }

    [role="option"]:hover,
    [aria-selected="true"] {
        background: rgba(237, 158, 89, 0.16) !important;
        color: var(--accent) !important;
    }

    div[data-testid="stSegmentedControl"] {
        margin-bottom: 0.35rem;
    }

    div[data-testid="stSegmentedControl"] > label,
    div[data-testid="stSegmentedControl"] [data-testid="stWidgetLabel"] {
        display: block;
        color: var(--muted) !important;
        font-weight: 700;
        font-size: 0.78rem !important;
        margin-bottom: 0.25rem;
    }

    div[data-testid="stSegmentedControl"] div[role="radiogroup"],
    div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] {
        background: #141226 !important;
        border: 1px solid rgba(237, 158, 89, 0.32) !important;
        border-radius: 8px !important;
        padding: 0.1rem !important;
        width: fit-content;
        overflow: hidden;
    }

    div[data-testid="stSegmentedControl"] div[role="radiogroup"] *,
    div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] *,
    div[data-testid="stSegmentedControl"] div[role="radiogroup"] > *,
    div[data-testid="stSegmentedControl"] [data-baseweb="button-group"] > * {
        background-color: #241b37 !important;
        color: #f4d7cd !important;
        border-color: rgba(237, 158, 89, 0.18) !important;
        box-shadow: none !important;
    }

    div[data-testid="stSegmentedControl"] button,
    div[data-testid="stSegmentedControl"] [role="radio"],
    div[data-testid="stSegmentedControl"] label {
        background: #241b37 !important;
        color: #f4d7cd !important;
        border-color: rgba(237, 158, 89, 0.18) !important;
        min-height: 2rem;
        font-size: 0.82rem;
        font-weight: 700;
        box-shadow: none !important;
    }

    div[data-testid="stSegmentedControl"] button *,
    div[data-testid="stSegmentedControl"] [role="radio"] *,
    div[data-testid="stSegmentedControl"] label * {
        color: inherit !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-testid="stSegmentedControl"] [aria-selected="true"] {
        background: #662249 !important;
        color: #ED9E59 !important;
        border: 1px solid #ED9E59 !important;
        border-radius: 7px !important;
    }

    div[data-testid="stSegmentedControl"] button[aria-checked="true"] *,
    div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] *,
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
    div[data-testid="stSegmentedControl"] [aria-selected="true"] * {
        background-color: transparent !important;
        color: #ED9E59 !important;
    }

    div[data-testid="stSegmentedControl"] div,
    div[data-testid="stSegmentedControl"] span {
        border-color: rgba(237, 158, 89, 0.18) !important;
    }

    div[data-testid="stSegmentedControl"] div:not([data-testid="stWidgetLabel"]) {
        background-color: #241b37 !important;
    }

    div[data-testid="stSegmentedControl"] [data-baseweb="radio"],
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"] > div,
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"] > div > div,
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"] span,
    div[data-testid="stSegmentedControl"] [data-baseweb="button"],
    div[data-testid="stSegmentedControl"] [data-baseweb="button"] > div,
    div[data-testid="stSegmentedControl"] button > div,
    div[data-testid="stSegmentedControl"] button span {
        background-color: #241b37 !important;
        color: #e9bcb9 !important;
        box-shadow: none !important;
    }

    div[data-testid="stSegmentedControl"] label:has(input:checked),
    div[data-testid="stSegmentedControl"] label:has(input:checked) > div,
    div[data-testid="stSegmentedControl"] label:has(input:checked) > div > div,
    div[data-testid="stSegmentedControl"] label:has(input:checked) span,
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"]:has(input:checked),
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"]:has(input:checked) > div,
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"]:has(input:checked) span {
        background-color: #662249 !important;
        color: #ed9e59 !important;
    }

    div[data-testid="stSegmentedControl"] label:has(input:checked),
    div[data-testid="stSegmentedControl"] [data-baseweb="radio"]:has(input:checked) {
        border: 1px solid #ed9e59 !important;
        border-radius: 8px !important;
    }

    label, [data-testid="stWidgetLabel"] {
        color: var(--muted) !important;
        font-size: 0.73rem !important;
    }

    .section-kicker {
        color: var(--accent);
        font-size: 0.9rem;
        font-weight: 760;
        letter-spacing: 0;
        text-transform: uppercase;
        margin: 1.2rem 0 0.55rem;
    }

    .section-kicker.tight {
        margin-top: 0.35rem;
    }

    .desk-panel {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(36, 27, 55, 0.72);
        padding: 0.65rem 0.75rem;
    }

    .module-caption {
        color: var(--muted);
        font-size: 0.74rem;
        margin-top: -0.25rem;
        margin-bottom: 0.45rem;
    }

    .dark-table-wrap {
        max-height: 286px;
        overflow: auto;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(27, 25, 49, 0.58);
    }

    .dark-table {
        width: 100%;
        border-collapse: collapse;
        color: var(--text);
        font-size: 0.76rem;
    }

    .dark-table thead th {
        position: sticky;
        top: 0;
        z-index: 3;
        background: #241b37;
        color: #E9BCB9;
        font-weight: 700;
        text-align: left;
        border-bottom: 1px solid var(--line);
        padding: 0.42rem 0.5rem;
    }

    .dark-table tbody th,
    .dark-table tbody td {
        background: rgba(36, 27, 55, 0.82);
        border-bottom: 1px solid rgba(233, 188, 185, 0.08);
        border-right: 1px solid rgba(233, 188, 185, 0.06);
        padding: 0.38rem 0.5rem;
    }

    .dark-table tbody tr:nth-child(even) th,
    .dark-table tbody tr:nth-child(even) td {
        background: rgba(68, 23, 78, 0.28);
    }

    .dark-table tbody tr:hover th,
    .dark-table tbody tr:hover td {
        background: rgba(163, 64, 84, 0.28);
    }

    [data-testid="stVegaLiteChart"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(36, 27, 55, 0.62);
        padding: 0.55rem 0.65rem 0.75rem;
        box-sizing: border-box;
        width: 100% !important;
        max-width: 100%;
        overflow: visible;
    }

    [data-testid="stVegaLiteChart"] > div,
    [data-testid="stVegaLiteChart"] > div > div {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box;
        overflow: visible !important;
    }

    [data-testid="stVegaLiteChart"] canvas,
    [data-testid="stVegaLiteChart"] svg {
        max-width: 100% !important;
        box-sizing: border-box;
        overflow: visible !important;
    }

    [data-testid="stAlert"] {
        background: rgba(68, 23, 78, 0.54);
        color: var(--text);
        border: 1px solid var(--line);
        border-radius: 8px;
    }

    [data-testid="stAlert"] svg {
        fill: var(--accent);
    }

    .stSlider {
        padding-top: 0.08rem !important;
        padding-bottom: 0.22rem !important;
        margin-bottom: 0.22rem !important;
    }

    .stSlider [data-testid="stTickBar"],
    .stSlider [data-testid="stThumbValue"] {
        font-size: 0.68rem !important;
        line-height: 1 !important;
    }

    .stSlider label {
        margin-bottom: 0.62rem !important;
        padding-bottom: 0 !important;
        line-height: 1.15 !important;
        display: block !important;
    }

    .stSlider [data-baseweb="slider"] {
        margin-top: 0.06rem !important;
    }

    .stSlider [data-testid="stThumbValue"] {
        transform: translateY(0.18rem);
        color: #ff4d57 !important;
        font-weight: 720 !important;
        white-space: nowrap !important;
    }

    [data-testid="stSidebar"] .stSlider {
        margin-bottom: 0.36rem !important;
    }

    [data-testid="stSidebar"] .stSlider label {
        margin-bottom: 0.72rem !important;
    }

    .workspace-label {
        color: #E9BCB9;
        font-size: 0.82rem;
        font-weight: 740;
        margin: 0.7rem 0 0.42rem;
    }

    .workspace-button-row {
        max-width: 980px;
        margin-bottom: 0.72rem;
    }

    .app-topbar {
        position: sticky;
        top: 0;
        z-index: 900;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin: 0 0 0.78rem;
        padding: 0.62rem 0.82rem;
        border: 1px solid rgba(237, 158, 89, 0.22);
        border-radius: 8px;
        background:
            linear-gradient(135deg, rgba(27, 25, 49, 0.98), rgba(68, 23, 78, 0.96));
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24);
        backdrop-filter: blur(10px);
    }

    .app-topbar-title {
        color: #fff7f0;
        font-size: 1.02rem;
        font-weight: 820;
        line-height: 1.1;
    }

    .terminal-credit {
        color: rgba(233, 188, 185, 0.88);
        font-size: 0.78rem;
        font-weight: 680;
        line-height: 1.2;
        white-space: nowrap;
    }

    .terminal-credit a {
        color: #ED9E59;
        text-decoration: none;
    }

    .terminal-credit a:hover {
        text-decoration: underline;
    }

    @media (max-width: 760px) {
        .app-topbar {
            align-items: flex-start;
            flex-direction: column;
            gap: 0.28rem;
        }

        .terminal-credit {
            white-space: normal;
        }
    }

    .workspace-button-row [data-testid="stButton"] button {
        width: 100%;
        background: #241b37 !important;
        color: #E9BCB9 !important;
        border: 1px solid rgba(237, 158, 89, 0.2) !important;
        border-radius: 8px !important;
        font-size: 0.84rem;
        font-weight: 760;
        min-height: 2.35rem;
        box-shadow: none !important;
    }

    .workspace-button-row [data-testid="stButton"] button:hover {
        background: #44174E !important;
        color: #ED9E59 !important;
        border-color: #ED9E59 !important;
    }

    .workspace-button-row [data-testid="stButton"] button[kind="primary"] {
        background: #662249 !important;
        color: #ED9E59 !important;
        border-color: #ED9E59 !important;
    }

    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-secondary"] *,
    button[data-testid="stBaseButton-secondary"] {
        background: #241b37 !important;
        background-color: #241b37 !important;
        color: #E9BCB9 !important;
        border-color: rgba(237, 158, 89, 0.24) !important;
        box-shadow: none !important;
    }

    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-primary"] *,
    button[data-testid="stBaseButton-primary"] {
        background: #662249 !important;
        background-color: #662249 !important;
        color: #ED9E59 !important;
        border-color: #ED9E59 !important;
        box-shadow: none !important;
    }

    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-secondary"]:hover * {
        background: #44174E !important;
        background-color: #44174E !important;
        color: #ED9E59 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

workspace_options = ["Portfolio Dashboard", "Market Monitor", "Global Markets"]
query_workspace = st.query_params.get("workspace", "Portfolio Dashboard")
page = query_workspace if query_workspace in workspace_options else "Portfolio Dashboard"

st.markdown(
    f"""
    <div class="app-topbar">
        <div class="app-topbar-title">{APP_NAME}</div>
        <div class="terminal-credit">
            Built by Zhixuan Gao · <a href="mailto:zhixuangao716@gmail.com">zhixuangao716@gmail.com</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workspace-label">Workspace</div>
    """,
    unsafe_allow_html=True,
)
st.markdown('<div class="workspace-button-row">', unsafe_allow_html=True)
workspace_cols = st.columns(3, gap="small")
for column, workspace in zip(workspace_cols, workspace_options):
    with column:
        if st.button(
            workspace,
            key=f"workspace_nav_{workspace}",
            type="primary" if workspace == page else "secondary",
            width="stretch",
        ):
            st.query_params["workspace"] = workspace
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

if page == "Portfolio Dashboard":
    st.sidebar.header("Portfolio Inputs")

    tickers_input = st.sidebar.text_input(
        "Tickers",
        value="AAPL, MSFT, JPM, TLT",
        help="Enter comma-separated Yahoo Finance tickers.",
    )

    weights_input = st.sidebar.text_input(
        "Weights",
        value="0.25, 0.25, 0.25, 0.25",
        help="Enter comma-separated weights. They can sum to 1 or 100.",
    )

    period = st.sidebar.selectbox(
        "Historical period",
        options=["6mo", "1y", "2y", "3y", "5y", "10y"],
        index=2,
    )

    risk_free_rate = st.sidebar.number_input(
        "Risk-free rate",
        min_value=0.0,
        max_value=0.20,
        value=0.03,
        step=0.005,
        format="%.3f",
    )

    confidence_level = st.sidebar.selectbox(
        "VaR confidence level",
        options=[0.90, 0.95, 0.99],
        index=1,
        format_func=lambda x: f"{x:.0%}",
    )

    st.sidebar.header("Stress Test")
    default_shock = st.sidebar.slider(
        "Default asset shock",
        min_value=-60,
        max_value=20,
        value=-20,
        step=1,
        format="%d%%",
    )

    scenario_preset = st.sidebar.selectbox(
        "Scenario preset",
        options=[
            "Custom",
            "Equity Selloff",
            "Banking Crisis",
            "Rate Shock",
            "Risk-Off Flight to Quality",
        ],
    )

    st.sidebar.header("Advanced Analytics")
    monte_carlo_paths = st.sidebar.slider(
        "Monte Carlo paths",
        min_value=500,
        max_value=10000,
        value=3000,
        step=500,
    )

    forecast_horizon = st.sidebar.slider(
        "Forecast horizon (trading days)",
        min_value=21,
        max_value=252,
        value=126,
        step=21,
    )

    frontier_portfolios = st.sidebar.slider(
        "Random portfolios",
        min_value=1000,
        max_value=20000,
        value=5000,
        step=1000,
    )

    st.sidebar.header("Risk Limits")
    max_vol_limit = st.sidebar.slider(
        "Max annualized volatility",
        min_value=5,
        max_value=80,
        value=25,
        step=1,
        format="%d%%",
    )
    max_drawdown_limit = st.sidebar.slider(
        "Max drawdown loss",
        min_value=5,
        max_value=80,
        value=25,
        step=1,
        format="%d%%",
    )
    max_var_limit = st.sidebar.slider(
        "Max daily VaR loss",
        min_value=1,
        max_value=15,
        value=3,
        step=1,
        format="%d%%",
    )
    min_sharpe_limit = st.sidebar.slider(
        "Min Sharpe ratio",
        min_value=-1.0,
        max_value=3.0,
        value=0.5,
        step=0.1,
    )
    max_weight_limit = st.sidebar.slider(
        "Max single-name weight",
        min_value=10,
        max_value=100,
        value=40,
        step=5,
        format="%d%%",
    )

    rate_shock_bps = st.sidebar.slider(
        "Rate shock",
        min_value=-300,
        max_value=300,
        value=100,
        step=25,
        format="%d bps",
    )

elif page == "Market Monitor":
    st.sidebar.header("Market Monitor")
    rate_history_years = st.sidebar.slider(
        "Rate history",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        format="%dY",
    )
    news_tickers_input = st.sidebar.text_input(
        "News tickers",
        value="AAPL, MSFT, JPM, TLT",
        help="Comma-separated company tickers for the News Desk and equity universe.",
    )
    news_items_per_ticker = st.sidebar.slider(
        "News per ticker",
        min_value=3,
        max_value=15,
        value=6,
        step=1,
    )
    region_filter = st.sidebar.selectbox(
        "Market region",
        options=["US", "Germany", "Global"],
        index=2,
    )
    asset_class_filter = st.sidebar.selectbox(
        "Asset class",
        options=["Equity", "Fixed Income", "All"],
        index=2,
    )
    universe_search = st.sidebar.text_input(
        "Universe search",
        value="",
        help="Search listed equities and fixed income products by ticker, company name, category or region.",
    )
    max_universe_rows = st.sidebar.slider(
        "Max screener rows",
        min_value=50,
        max_value=5000,
        value=1000,
        step=100,
    )
    classification_view = st.sidebar.selectbox(
        "Classification view",
        options=["Sector", "Industry", "Sector + Industry", "Asset Class + Region"],
    )
else:
    st.sidebar.header("Global Markets")
    global_period = st.sidebar.selectbox(
        "Market history",
        options=["5d", "1mo", "3mo", "6mo", "1y"],
        index=2,
    )
    selected_countries = st.sidebar.multiselect(
        "Countries / regions",
        options=list(GLOBAL_MARKET_TICKERS.keys()),
        default=["United States", "Germany", "Eurozone", "Japan", "China", "India"],
    )
    selected_fx_pairs = st.sidebar.multiselect(
        "FX pairs",
        options=list(GLOBAL_FX_TICKERS.keys()),
        default=["DXY", "EUR/USD", "USD/JPY", "GBP/USD", "USD/CNY"],
    )
    global_news_items = st.sidebar.slider(
        "News per country",
        min_value=2,
        max_value=10,
        value=4,
        step=1,
    )
    global_rate_history_years = st.sidebar.slider(
        "Rate history",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        format="%dY",
    )


def parse_list(raw_text):
    return [item.strip().upper() for item in raw_text.split(",") if item.strip()]


def parse_weights(raw_text, expected_count):
    try:
        weights = np.array(
            [float(item.strip()) for item in raw_text.split(",") if item.strip()],
            dtype=float,
        )
    except ValueError:
        return None, "Weights must be numeric."

    if len(weights) != expected_count:
        return None, "The number of weights must match the number of tickers."

    if np.any(weights < 0):
        return None, "Weights must be non-negative."

    if weights.sum() == 0:
        return None, "Weights cannot sum to zero."

    if weights.sum() > 1.5:
        weights = weights / 100

    weights = weights / weights.sum()
    return weights, None


@st.cache_data(ttl=3600)
def download_prices(tickers, benchmark_tickers, selected_period, extra_tickers=None):
    extra_tickers = extra_tickers or []
    benchmark_tickers = (
        benchmark_tickers
        if isinstance(benchmark_tickers, list)
        else [benchmark_tickers]
    )
    all_tickers = list(dict.fromkeys(tickers + benchmark_tickers + extra_tickers))
    raw = yf.download(
        all_tickers,
        period=selected_period,
        auto_adjust=True,
        progress=False,
    )

    if raw.empty:
        return pd.DataFrame(), pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            prices = raw["Close"]
            volume = raw["Volume"] if "Volume" in raw.columns.get_level_values(0) else pd.DataFrame()
        else:
            prices = raw.xs("Close", axis=1, level=1)
            volume = raw.xs("Volume", axis=1, level=1) if "Volume" in raw.columns.get_level_values(1) else pd.DataFrame()
    else:
        prices = raw[["Close"]].rename(columns={"Close": all_tickers[0]})
        volume = raw[["Volume"]].rename(columns={"Volume": all_tickers[0]}) if "Volume" in raw.columns else pd.DataFrame()

    if isinstance(prices, pd.Series):
        prices = prices.to_frame(all_tickers[0])
    if isinstance(volume, pd.Series):
        volume = volume.to_frame(all_tickers[0])

    return prices.dropna(how="all"), volume.dropna(how="all")


@st.cache_data(ttl=90)
def download_ohlc(ticker, selected_period, interval):
    raw = yf.download(
        ticker,
        period=selected_period,
        interval=interval,
        auto_adjust=False,
        prepost=False,
        progress=False,
    )

    if raw.empty:
        return pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        if "Open" in raw.columns.get_level_values(0):
            raw = raw.droplevel(1, axis=1)
        elif "Open" in raw.columns.get_level_values(1):
            raw = raw.xs(ticker, axis=1, level=0, drop_level=True)

    required = ["Open", "High", "Low", "Close", "Volume"]
    available = [column for column in required if column in raw.columns]
    if not {"Open", "High", "Low", "Close"}.issubset(available):
        return pd.DataFrame()

    ohlc = raw[available].dropna(subset=["Open", "High", "Low", "Close"])
    ohlc.index.name = "Date"
    return ohlc


def annualized_return(returns):
    total_return = (1 + returns).prod() - 1
    years = len(returns) / TRADING_DAYS
    if years <= 0:
        return np.nan
    return (1 + total_return) ** (1 / years) - 1


def max_drawdown(returns):
    cumulative = (1 + returns).cumprod()
    running_peak = cumulative.cummax()
    drawdown = cumulative / running_peak - 1
    return drawdown.min(), drawdown


def value_at_risk(returns, confidence):
    return -np.percentile(returns.dropna(), (1 - confidence) * 100)


def conditional_value_at_risk(returns, confidence):
    var_threshold = np.percentile(returns.dropna(), (1 - confidence) * 100)
    tail_losses = returns[returns <= var_threshold]
    return -tail_losses.mean()


def parametric_var(returns, confidence):
    clean_returns = returns.dropna()
    z_score = NormalDist().inv_cdf(confidence)
    return max(0, -(clean_returns.mean() - z_score * clean_returns.std()))


def cornish_fisher_var(returns, confidence):
    clean_returns = returns.dropna()
    if len(clean_returns) < 30 or clean_returns.std() == 0:
        return np.nan

    z_score = NormalDist().inv_cdf(confidence)
    skewness = clean_returns.skew()
    excess_kurtosis = clean_returns.kurtosis()
    adjusted_z = (
        z_score
        + ((z_score**2 - 1) * skewness / 6)
        + ((z_score**3 - 3 * z_score) * excess_kurtosis / 24)
        - ((2 * z_score**3 - 5 * z_score) * skewness**2 / 36)
    )

    return max(0, -(clean_returns.mean() - adjusted_z * clean_returns.std()))


def kupiec_test(returns, var_level, confidence):
    clean_returns = returns.dropna()
    observations = len(clean_returns)
    breaches = int((clean_returns < -var_level).sum())
    expected_probability = 1 - confidence

    if observations == 0:
        return {"Breaches": 0, "Expected Breaches": 0, "LR": np.nan, "P-Value": np.nan}

    observed_probability = breaches / observations
    expected_breaches = observations * expected_probability

    if breaches == 0 or breaches == observations:
        lr_stat = np.nan
        p_value = np.nan
    else:
        restricted = (
            (observations - breaches) * log(1 - expected_probability)
            + breaches * log(expected_probability)
        )
        unrestricted = (
            (observations - breaches) * log(1 - observed_probability)
            + breaches * log(observed_probability)
        )
        lr_stat = max(0, -2 * (restricted - unrestricted))
        p_value = erfc(sqrt(lr_stat / 2))

    return {
        "Breaches": breaches,
        "Expected Breaches": expected_breaches,
        "LR": lr_stat,
        "P-Value": p_value,
        "Observed Breach Rate": observed_probability,
    }


def basel_traffic_light(observations, breaches, confidence):
    if observations == 0:
        return "N/A"

    scaled_breaches = breaches * 250 / observations
    if confidence >= 0.99:
        if scaled_breaches <= 4:
            return "Green"
        if scaled_breaches <= 9:
            return "Yellow"
        return "Red"

    expected = observations * (1 - confidence)
    if breaches <= expected * 1.5:
        return "Green"
    if breaches <= expected * 2.5:
        return "Yellow"
    return "Red"


def portfolio_metrics(portfolio_returns, benchmark_returns, risk_free):
    active_returns = portfolio_returns - benchmark_returns
    excess_returns = portfolio_returns - risk_free / TRADING_DAYS

    ann_return = annualized_return(portfolio_returns)
    ann_vol = portfolio_returns.std() * np.sqrt(TRADING_DAYS)
    downside = portfolio_returns[portfolio_returns < 0].std() * np.sqrt(TRADING_DAYS)

    sharpe = np.nan if ann_vol == 0 else excess_returns.mean() * TRADING_DAYS / ann_vol
    sortino = np.nan if downside == 0 else excess_returns.mean() * TRADING_DAYS / downside

    mdd, drawdown = max_drawdown(portfolio_returns)

    covariance = portfolio_returns.cov(benchmark_returns)
    benchmark_variance = benchmark_returns.var()
    beta = np.nan if benchmark_variance == 0 else covariance / benchmark_variance

    tracking_error = active_returns.std() * np.sqrt(TRADING_DAYS)
    information_ratio = (
        np.nan
        if tracking_error == 0
        else active_returns.mean() * TRADING_DAYS / tracking_error
    )

    return {
        "Annualized Return": ann_return,
        "Annualized Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Max Drawdown": mdd,
        "Beta vs Benchmark": beta,
        "Tracking Error": tracking_error,
        "Information Ratio": information_ratio,
        "Daily VaR": value_at_risk(portfolio_returns, confidence_level),
        "Daily CVaR": conditional_value_at_risk(portfolio_returns, confidence_level),
        "Parametric VaR": parametric_var(portfolio_returns, confidence_level),
        "Cornish-Fisher VaR": cornish_fisher_var(portfolio_returns, confidence_level),
    }, drawdown


def format_percent(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2%}"


def format_number(value):
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}"


def data_timestamp():
    return pd.Timestamp.now(tz="Europe/Berlin").strftime("%Y-%m-%d %H:%M %Z")


def section_title(title, tight=False):
    class_name = "section-kicker tight" if tight else "section-kicker"
    st.markdown(f'<div class="{class_name}">{title}</div>', unsafe_allow_html=True)


def render_dark_table(dataframe, height=286, escape=True):
    display_frame = dataframe.copy()
    if not isinstance(display_frame.index, pd.RangeIndex):
        index_name = display_frame.index.name or "Name"
        display_frame = display_frame.reset_index().rename(columns={"index": index_name})
    html = display_frame.to_html(
        classes="dark-table",
        border=0,
        escape=escape,
        index=False,
    )
    st.markdown(
        f'<div class="dark-table-wrap" style="max-height:{height}px">{html}</div>',
        unsafe_allow_html=True,
    )


def status_badge(value):
    normalized = str(value).strip().lower()
    status_class = {
        "green": "green",
        "pass": "pass",
        "ok": "green",
        "yellow": "yellow",
        "review": "review",
        "red": "red",
        "fail": "fail",
    }.get(normalized, "yellow")
    return f'<span class="status-badge {status_class}">{value}</span>'


def render_status_metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div style="margin-top:0.42rem">{status_badge(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tab_safely(label, render_fn):
    try:
        render_fn()
    except Exception as error:
        st.error(f"{label} is temporarily unavailable: {error}")


CHART_LEGEND = {
    "labelColor": "#caa6ad",
    "title": None,
    "orient": "bottom",
    "direction": "horizontal",
    "columns": 4,
    "labelLimit": 0,
    "symbolLimit": 500,
    "rowPadding": 4,
    "columnPadding": 14,
}

CHART_PADDING = {"left": 10, "right": 34, "top": 10, "bottom": 44}
CHART_COLORS = ["#ED9E59", "#E9BCB9", "#A34054", "#ff6f7e", "#7fc7ff", "#c48cff", "#80d39b"]


def chart_x_scale(x_type):
    if x_type == "temporal":
        return {"nice": False, "padding": 14}
    return {"paddingInner": 0.08, "paddingOuter": 0.2}


def temporal_zoom_params(x_type):
    if x_type != "temporal":
        return []
    return [
        {
            "name": "chart_zoom",
            "select": {"type": "interval"},
            "bind": "scales",
        }
    ]


def render_dark_line_chart(dataframe, height=280):
    chart_frame = dataframe.copy()
    if isinstance(chart_frame, pd.Series):
        chart_frame = chart_frame.to_frame(chart_frame.name or "Value")
    chart_frame = chart_frame.reset_index()
    index_name = chart_frame.columns[0]
    x_type = "temporal" if pd.api.types.is_datetime64_any_dtype(chart_frame[index_name]) else "nominal"
    x_field = "Date" if x_type == "temporal" else "Category"
    chart_frame = chart_frame.rename(columns={index_name: x_field})
    long_frame = chart_frame.melt(x_field, var_name="Series", value_name="Value").dropna()

    spec = {
        "autosize": {"type": "fit", "contains": "padding"},
        "params": temporal_zoom_params(x_type),
        "mark": {"type": "line", "strokeWidth": 2},
        "encoding": {
            "x": {
                "field": x_field,
                "type": x_type,
                "title": None,
                "scale": chart_x_scale(x_type),
                "axis": {
                    "labelColor": "#caa6ad",
                    "gridColor": "rgba(233,188,185,0.08)",
                    "labelAngle": -45 if x_type == "nominal" else 0,
                    "labelFlush": False,
                    "labelOverlap": "parity" if x_type == "temporal" else True,
                },
            },
            "y": {
                "field": "Value",
                "type": "quantitative",
                "title": None,
                "axis": {"labelColor": "#caa6ad", "gridColor": "rgba(233,188,185,0.08)"},
            },
            "color": {
                "field": "Series",
                "type": "nominal",
                "scale": {"range": CHART_COLORS},
                "legend": CHART_LEGEND,
            },
            "tooltip": [
                {"field": x_field, "type": x_type},
                {"field": "Series", "type": "nominal"},
                {"field": "Value", "type": "quantitative", "format": ".4f"},
            ],
        },
        "width": "container",
        "height": height,
        "padding": CHART_PADDING,
        "background": "transparent",
        "view": {"stroke": "rgba(233,188,185,0.14)"},
    }
    st.vega_lite_chart(long_frame, spec, width="stretch", theme=None)


def render_dark_bar_chart(series, height=220, compact=False):
    chart_frame = series.rename("Value").reset_index()
    chart_frame.columns = ["Name", "Value"]
    padding = (
        {"left": 8, "right": 18, "top": 8, "bottom": 28}
        if compact
        else {"left": 10, "right": 34, "top": 12, "bottom": 42}
    )
    mark = {
        "type": "bar",
        "cornerRadiusTopLeft": 3,
        "cornerRadiusTopRight": 3,
        "color": "#ED9E59",
    }
    if compact:
        mark["size"] = 34
    spec = {
        "autosize": {"type": "fit", "contains": "padding"},
        "mark": mark,
        "encoding": {
            "x": {
                "field": "Name",
                "type": "nominal",
                "title": None,
                "scale": chart_x_scale("nominal"),
                "axis": {
                    "labelColor": "#caa6ad",
                    "labelAngle": 0,
                    "labelFlush": False,
                    "labelOverlap": False,
                },
            },
            "y": {
                "field": "Value",
                "type": "quantitative",
                "title": None,
                "axis": {"labelColor": "#caa6ad", "gridColor": "rgba(233,188,185,0.08)"},
            },
            "tooltip": [
                {"field": "Name", "type": "nominal"},
                {"field": "Value", "type": "quantitative", "format": ".4f"},
            ],
        },
        "width": "container",
        "height": height,
        "padding": padding,
        "background": "transparent",
        "view": {"stroke": "rgba(233,188,185,0.14)"},
    }
    st.vega_lite_chart(chart_frame, spec, width="stretch", theme=None)


def render_dark_grouped_bar_chart(dataframe, height=220, compact=False):
    chart_frame = dataframe.copy().reset_index()
    index_name = chart_frame.columns[0]
    chart_frame = chart_frame.rename(columns={index_name: "Name"})
    long_frame = chart_frame.melt("Name", var_name="Series", value_name="Value").dropna()

    if compact:
        max_abs = float(long_frame["Value"].abs().max()) if not long_frame.empty else 0.1
        max_abs = max(max_abs * 1.18, 0.04)
        st.markdown(
            """
            <div style="display:flex;gap:0.75rem;align-items:center;margin:0.1rem 0 0.35rem;color:#caa6ad;font-size:0.68rem;font-weight:700;">
                <span><span style="display:inline-block;width:0.55rem;height:0.55rem;background:#ED9E59;margin-right:0.28rem;"></span>Allocation</span>
                <span><span style="display:inline-block;width:0.55rem;height:0.55rem;background:#A34054;margin-right:0.28rem;"></span>Selection</span>
                <span><span style="display:inline-block;width:0.55rem;height:0.55rem;background:#E9BCB9;margin-right:0.28rem;"></span>Interaction</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        spec = {
            "autosize": {"type": "fit", "contains": "padding"},
            "mark": {"type": "bar", "cornerRadiusEnd": 3, "size": 8},
            "encoding": {
                "y": {
                    "field": "Name",
                    "type": "nominal",
                    "title": None,
                    "scale": {"paddingInner": 0.24, "paddingOuter": 0.16},
                    "axis": {
                        "labelColor": "#caa6ad",
                        "labelLimit": 86,
                        "labelPadding": 5,
                    },
                },
                "yOffset": {"field": "Series", "type": "nominal"},
                "x": {
                    "field": "Value",
                    "type": "quantitative",
                    "title": None,
                    "scale": {"zero": True, "domain": [-max_abs, max_abs]},
                    "axis": {
                        "labelColor": "#caa6ad",
                        "gridColor": "rgba(233,188,185,0.08)",
                        "format": ".0%",
                    },
                },
                "color": {
                    "field": "Series",
                    "type": "nominal",
                    "scale": {"range": ["#ED9E59", "#A34054", "#E9BCB9"]},
                    "legend": None,
                },
                "tooltip": [
                    {"field": "Name", "type": "nominal"},
                    {"field": "Series", "type": "nominal"},
                    {"field": "Value", "type": "quantitative", "format": ".2%"},
                ],
            },
            "width": "container",
            "height": height,
            "padding": {"left": 88, "right": 14, "top": 8, "bottom": 34},
            "background": "transparent",
            "view": {"stroke": "rgba(233,188,185,0.14)"},
        }
        st.vega_lite_chart(long_frame, spec, width="stretch", theme=None)
        return

    legend = (
        {
            **CHART_LEGEND,
            "columns": 1,
            "labelLimit": 0,
            "rowPadding": 4,
            "columnPadding": 10,
        }
        if compact
        else CHART_LEGEND
    )
    padding = (
        {"left": 8, "right": 16, "top": 8, "bottom": 72}
        if compact
        else CHART_PADDING
    )
    mark = {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3}
    if compact:
        mark["size"] = 14
    spec = {
        "autosize": {"type": "fit", "contains": "padding"},
        "mark": mark,
        "encoding": {
            "x": {
                "field": "Name",
                "type": "nominal",
                "title": None,
                "scale": chart_x_scale("nominal"),
                "axis": {
                    "labelColor": "#caa6ad",
                    "labelAngle": -32 if compact else 0,
                    "labelFlush": False,
                    "labelOverlap": False,
                    "labelLimit": 105 if compact else 0,
                },
            },
            "xOffset": {"field": "Series", "type": "nominal"},
            "y": {
                "field": "Value",
                "type": "quantitative",
                "title": None,
                "axis": {"labelColor": "#caa6ad", "gridColor": "rgba(233,188,185,0.08)"},
            },
            "color": {
                "field": "Series",
                "type": "nominal",
                "scale": {"range": CHART_COLORS},
                "legend": legend,
            },
            "tooltip": [
                {"field": "Name", "type": "nominal"},
                {"field": "Series", "type": "nominal"},
                {"field": "Value", "type": "quantitative", "format": ".4f"},
            ],
        },
        "width": "container",
        "height": height,
        "padding": padding,
        "background": "transparent",
        "view": {"stroke": "rgba(233,188,185,0.14)"},
    }
    st.vega_lite_chart(long_frame, spec, width="stretch", theme=None)


def render_dark_scatter_chart(dataframe, x_column, y_column, color_column, height=300):
    spec = {
        "autosize": {"type": "fit", "contains": "padding"},
        "mark": {"type": "circle", "size": 42, "opacity": 0.72},
        "encoding": {
            "x": {
                "field": x_column,
                "type": "quantitative",
                "title": x_column,
                "scale": {"zero": False, "nice": True, "padding": 12},
                "axis": {"labelColor": "#caa6ad", "titleColor": "#E9BCB9", "gridColor": "rgba(233,188,185,0.08)", "labelFlush": False},
            },
            "y": {
                "field": y_column,
                "type": "quantitative",
                "title": y_column,
                "axis": {"labelColor": "#caa6ad", "titleColor": "#E9BCB9", "gridColor": "rgba(233,188,185,0.08)"},
            },
            "color": {
                "field": color_column,
                "type": "quantitative",
                "scale": {"range": ["#662249", "#A34054", "#ED9E59", "#E9BCB9"]},
                "legend": {"labelColor": "#caa6ad", "titleColor": "#E9BCB9", "labelLimit": 0},
            },
            "tooltip": [
                {"field": "Portfolio", "type": "nominal"},
                {"field": x_column, "type": "quantitative", "format": ".2%"},
                {"field": y_column, "type": "quantitative", "format": ".2%"},
                {"field": color_column, "type": "quantitative", "format": ".2f"},
            ],
        },
        "width": "container",
        "height": height,
        "padding": {"left": 10, "right": 52, "top": 12, "bottom": 48},
        "background": "transparent",
        "view": {"stroke": "rgba(233,188,185,0.14)"},
    }
    st.vega_lite_chart(dataframe, spec, width="stretch", theme=None)


def add_technical_indicators(ohlc):
    indicators = ohlc.copy()
    indicators["SMA 20"] = indicators["Close"].rolling(20).mean()
    indicators["SMA 50"] = indicators["Close"].rolling(50).mean()
    indicators["EMA 12"] = indicators["Close"].ewm(span=12, adjust=False).mean()
    indicators["EMA 26"] = indicators["Close"].ewm(span=26, adjust=False).mean()

    rolling_mean = indicators["Close"].rolling(20).mean()
    rolling_std = indicators["Close"].rolling(20).std()
    indicators["BB Upper"] = rolling_mean + 2 * rolling_std
    indicators["BB Lower"] = rolling_mean - 2 * rolling_std

    if "Volume" in indicators.columns and indicators["Volume"].notna().any():
        typical_price = (indicators["High"] + indicators["Low"] + indicators["Close"]) / 3
        volume = indicators["Volume"].fillna(0)
        cumulative_volume = volume.cumsum()
        indicators["VWAP"] = (typical_price * volume).cumsum() / cumulative_volume.replace(0, np.nan)

    return indicators


def render_dark_candlestick_chart(ohlc, selected_indicators=None, height=420):
    selected_indicators = selected_indicators or []
    chart_frame = ohlc.copy()
    if not isinstance(chart_frame.index, pd.DatetimeIndex):
        chart_frame.index = pd.to_datetime(chart_frame.index, errors="coerce")
    chart_frame = chart_frame.dropna(subset=["Open", "High", "Low", "Close"]).sort_index()
    for column in ["Open", "High", "Low", "Close"]:
        chart_frame[column] = pd.to_numeric(chart_frame[column], errors="coerce")
    chart_frame = chart_frame.dropna(subset=["Open", "High", "Low", "Close"])
    if chart_frame.empty:
        st.warning("No valid OHLC rows are available for the selected K-line view.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=chart_frame.index,
            open=chart_frame["Open"],
            high=chart_frame["High"],
            low=chart_frame["Low"],
            close=chart_frame["Close"],
            name="OHLC",
            increasing_line_color="#E9BCB9",
            increasing_fillcolor="rgba(233,188,185,0.64)",
            decreasing_line_color="#ff6f7e",
            decreasing_fillcolor="rgba(255,111,126,0.56)",
        )
    )

    overlay_colors = {
        "SMA 20": "#ED9E59",
        "SMA 50": "#E9BCB9",
        "EMA 12": "#A34054",
        "EMA 26": "#ff6f7e",
        "BB Upper": "#7fc7ff",
        "BB Lower": "#7fc7ff",
        "VWAP": "#c48cff",
    }
    for indicator in selected_indicators:
        if indicator in chart_frame.columns:
            fig.add_trace(
                go.Scatter(
                    x=chart_frame.index,
                    y=chart_frame[indicator],
                    mode="lines",
                    name=indicator,
                    line={"color": overlay_colors.get(indicator, "#ED9E59"), "width": 1.4},
                    opacity=0.9,
                )
            )

    fig.update_layout(
        height=height,
        margin={"l": 44, "r": 24, "t": 8, "b": 42},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(36,27,55,0.62)",
        font={"color": "#caa6ad"},
        hovermode="x unified",
        dragmode="zoom",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.24,
            "xanchor": "left",
            "x": 0,
            "font": {"color": "#E9BCB9", "size": 12},
            "bgcolor": "rgba(27,25,49,0.0)",
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(233,188,185,0.08)",
            "rangeslider": {"visible": False},
            "color": "#caa6ad",
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(233,188,185,0.08)",
            "color": "#caa6ad",
            "fixedrange": False,
        },
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "scrollZoom": True,
            "responsive": True,
        },
    )


def scenario_shock_for_ticker(ticker, preset, fallback_shock):
    equity_indices = {"SPY", "QQQ", "IWM", "DIA", "VOO", "VTI", "IVV"}
    bond_like = {"TLT", "IEF", "SHY", "BND", "AGG", "LQD", "HYG"}
    bank_like = {"JPM", "BAC", "C", "WFC", "GS", "MS", "DB", "UBS", "HSBC", "XLF", "KBE"}

    if preset == "Custom":
        return fallback_shock

    if preset == "Equity Selloff":
        return -0.30 if ticker not in bond_like else 0.06

    if preset == "Banking Crisis":
        if ticker in bank_like:
            return -0.35
        if ticker in bond_like:
            return 0.08
        return -0.20

    if preset == "Rate Shock":
        if ticker in {"TLT", "IEF", "BND", "AGG", "LQD"}:
            return -0.12
        if ticker in {"SHY"}:
            return -0.03
        if ticker in bank_like:
            return -0.08
        return -0.10

    if preset == "Risk-Off Flight to Quality":
        if ticker in {"TLT", "IEF", "BND", "AGG"}:
            return 0.10
        if ticker in {"SHY"}:
            return 0.02
        if ticker in bank_like:
            return -0.25
        if ticker in equity_indices:
            return -0.22
        return -0.18

    return fallback_shock


def run_monte_carlo(returns, horizon, paths, seed=7):
    rng = np.random.default_rng(seed)
    daily_mean = returns.mean()
    daily_volatility = returns.std()

    simulated_returns = rng.normal(
        loc=daily_mean,
        scale=daily_volatility,
        size=(horizon, paths),
    )
    simulated_paths = pd.DataFrame((1 + simulated_returns).cumprod(axis=0))

    percentiles = pd.DataFrame(
        {
            "P5": simulated_paths.quantile(0.05, axis=1),
            "P25": simulated_paths.quantile(0.25, axis=1),
            "Median": simulated_paths.quantile(0.50, axis=1),
            "P75": simulated_paths.quantile(0.75, axis=1),
            "P95": simulated_paths.quantile(0.95, axis=1),
        }
    )
    percentiles.index = np.arange(1, horizon + 1)
    terminal_returns = simulated_paths.iloc[-1] - 1

    return percentiles, terminal_returns


def random_portfolio_frontier(returns, risk_free, number_of_portfolios, seed=11):
    rng = np.random.default_rng(seed)
    expected_returns = returns.mean() * TRADING_DAYS
    covariance = returns.cov() * TRADING_DAYS
    random_weights = rng.dirichlet(np.ones(len(returns.columns)), number_of_portfolios)

    portfolio_returns_sample = random_weights @ expected_returns.values
    portfolio_volatility_sample = np.sqrt(
        np.einsum("ij,jk,ik->i", random_weights, covariance.values, random_weights)
    )
    sharpe_sample = np.where(
        portfolio_volatility_sample == 0,
        np.nan,
        (portfolio_returns_sample - risk_free) / portfolio_volatility_sample,
    )

    frontier = pd.DataFrame(
        {
            "Annualized Return": portfolio_returns_sample,
            "Annualized Volatility": portfolio_volatility_sample,
            "Sharpe Ratio": sharpe_sample,
        }
    )

    best_sharpe_index = frontier["Sharpe Ratio"].idxmax()
    min_vol_index = frontier["Annualized Volatility"].idxmin()

    best_sharpe_weights = pd.Series(random_weights[best_sharpe_index], index=returns.columns)
    min_vol_weights = pd.Series(random_weights[min_vol_index], index=returns.columns)

    return frontier, best_sharpe_weights, min_vol_weights


def build_factor_returns(all_returns):
    required = set(FACTOR_PROXY_TICKERS)
    if not required.issubset(all_returns.columns):
        return pd.DataFrame()

    factors = pd.DataFrame(index=all_returns.index)
    factors["Market"] = all_returns["SPY"] - risk_free_rate / TRADING_DAYS
    factors["Size"] = all_returns["IWM"] - all_returns["SPY"]
    factors["Value"] = all_returns["IVE"] - all_returns["IVW"]
    factors["Momentum"] = all_returns["MTUM"] - all_returns["SPY"]
    factors["Duration"] = all_returns["TLT"] - all_returns["SHY"]

    return factors.dropna()


def factor_regression(target_returns, factor_returns):
    aligned = pd.concat(
        [target_returns.rename("Portfolio"), factor_returns],
        axis=1,
    ).dropna()

    if aligned.shape[0] <= len(factor_returns.columns) + 5:
        return None, None

    y = aligned["Portfolio"].values - risk_free_rate / TRADING_DAYS
    x = aligned[factor_returns.columns].values
    x = np.column_stack([np.ones(len(x)), x])

    coefficients, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    fitted = x @ coefficients
    residuals = y - fitted

    total_sum_squares = np.sum((y - y.mean()) ** 2)
    residual_sum_squares = np.sum(residuals**2)
    r_squared = 1 - residual_sum_squares / total_sum_squares

    coefficient_table = pd.DataFrame(
        {
            "Factor": ["Alpha"] + list(factor_returns.columns),
            "Exposure": coefficients,
        }
    ).set_index("Factor")

    coefficient_table.loc["Alpha", "Exposure"] *= TRADING_DAYS

    diagnostics = {
        "R-Squared": r_squared,
        "Annualized Alpha": coefficient_table.loc["Alpha", "Exposure"],
        "Residual Volatility": residuals.std() * np.sqrt(TRADING_DAYS),
    }

    return coefficient_table, diagnostics


def component_var_table(returns, portfolio_weights, confidence):
    covariance = returns.cov()
    daily_mean = returns.mean()
    portfolio_mean = float(portfolio_weights @ daily_mean.values)
    portfolio_variance_daily = float(
        portfolio_weights.T @ covariance.values @ portfolio_weights
    )

    if portfolio_variance_daily <= 0:
        return pd.DataFrame()

    portfolio_volatility_daily = np.sqrt(portfolio_variance_daily)
    z_score = NormalDist().inv_cdf(confidence)
    diversified_var = max(0, z_score * portfolio_volatility_daily - portfolio_mean)

    risk_contribution_pct = (
        portfolio_weights * (covariance.values @ portfolio_weights)
        / portfolio_variance_daily
    )
    component_var = risk_contribution_pct * diversified_var

    table = pd.DataFrame(
        {
            "Ticker": returns.columns,
            "Weight": portfolio_weights,
            "Component VaR": component_var,
            "VaR Contribution": risk_contribution_pct,
        }
    ).set_index("Ticker")

    return table


def drawdown_event_table(drawdown_series):
    in_drawdown = drawdown_series < 0
    groups = (in_drawdown != in_drawdown.shift()).cumsum()
    events = []

    for _, event_drawdown in drawdown_series[in_drawdown].groupby(groups):
        start_date = event_drawdown.index[0]
        trough_date = event_drawdown.idxmin()
        end_date = event_drawdown.index[-1]
        recovered = end_date != drawdown_series.index[-1]

        events.append(
            {
                "Start": start_date.date(),
                "Trough": trough_date.date(),
                "End": end_date.date(),
                "Recovered": recovered,
                "Days": len(event_drawdown),
                "Max Drawdown": event_drawdown.min(),
            }
        )

    if not events:
        return pd.DataFrame()

    return pd.DataFrame(events).sort_values("Max Drawdown").head(10)


def rolling_sharpe_ratio(returns, window, risk_free):
    rolling_excess = returns - risk_free / TRADING_DAYS
    rolling_return = rolling_excess.rolling(window).mean() * TRADING_DAYS
    rolling_risk = returns.rolling(window).std() * np.sqrt(TRADING_DAYS)
    return rolling_return / rolling_risk


def risk_limit_table(metric_values):
    checks = [
        {
            "Limit": "Annualized Volatility",
            "Current": metric_values["Annualized Volatility"],
            "Threshold": max_vol_limit / 100,
            "Pass": metric_values["Annualized Volatility"] <= max_vol_limit / 100,
            "Format": "percent",
        },
        {
            "Limit": "Max Drawdown Loss",
            "Current": abs(metric_values["Max Drawdown"]),
            "Threshold": max_drawdown_limit / 100,
            "Pass": abs(metric_values["Max Drawdown"]) <= max_drawdown_limit / 100,
            "Format": "percent",
        },
        {
            "Limit": f"Daily VaR {confidence_level:.0%}",
            "Current": metric_values["Daily VaR"],
            "Threshold": max_var_limit / 100,
            "Pass": metric_values["Daily VaR"] <= max_var_limit / 100,
            "Format": "percent",
        },
        {
            "Limit": "Sharpe Ratio",
            "Current": metric_values["Sharpe Ratio"],
            "Threshold": min_sharpe_limit,
            "Pass": metric_values["Sharpe Ratio"] >= min_sharpe_limit,
            "Format": "number",
        },
        {
            "Limit": "Largest Single-Name Weight",
            "Current": weights.max(),
            "Threshold": max_weight_limit / 100,
            "Pass": weights.max() <= max_weight_limit / 100,
            "Format": "percent",
        },
    ]

    table = pd.DataFrame(checks)
    table["Status"] = np.where(table["Pass"], "OK", "Breach")
    table["Current"] = table.apply(
        lambda row: format_percent(row["Current"])
        if row["Format"] == "percent"
        else format_number(row["Current"]),
        axis=1,
    )
    table["Threshold"] = table.apply(
        lambda row: format_percent(row["Threshold"])
        if row["Format"] == "percent"
        else format_number(row["Threshold"]),
        axis=1,
    )

    return table[["Limit", "Current", "Threshold", "Status"]].set_index("Limit")


def performance_attribution(asset_returns, benchmark_returns, portfolio_weights):
    asset_total_returns = (1 + asset_returns).prod() - 1
    contribution_to_return = portfolio_weights * asset_total_returns
    portfolio_total_return = contribution_to_return.sum()
    benchmark_total_return = (1 + benchmark_returns).prod() - 1

    table = pd.DataFrame(
        {
            "Weight": portfolio_weights,
            "Asset Total Return": asset_total_returns,
            "Contribution to Return": contribution_to_return,
        }
    )
    table["Contribution Share"] = np.where(
        portfolio_total_return == 0,
        np.nan,
        table["Contribution to Return"] / portfolio_total_return,
    )
    table = table.sort_values("Contribution to Return", ascending=False)

    summary = {
        "Portfolio Total Return": portfolio_total_return,
        "Benchmark Total Return": benchmark_total_return,
        "Active Return": portfolio_total_return - benchmark_total_return,
    }

    return table, summary


def brinson_attribution(asset_returns, all_returns, tickers, portfolio_weights):
    sector_rows = []

    for ticker, weight in zip(tickers, portfolio_weights):
        profile = fetch_company_profile(ticker)
        sector = profile.get("Sector", "Unclassified")
        sector_rows.append({"Ticker": ticker, "Sector": sector, "Weight": weight})

    holdings = pd.DataFrame(sector_rows)
    sector_weights = holdings.groupby("Sector")["Weight"].sum()
    available_sector_tickers = {
        sector: proxy
        for sector, proxy in SECTOR_PROXY_TICKERS.items()
        if proxy in all_returns.columns
    }

    rows = []
    sectors = sector_weights.index.tolist()
    benchmark_weight = 1 / len(sectors) if sectors else np.nan

    for sector in sectors:
        sector_holdings = holdings[holdings["Sector"] == sector]
        sector_tickers = sector_holdings["Ticker"].tolist()
        sector_holding_weights = sector_holdings.set_index("Ticker")["Weight"]
        normalized_weights = sector_holding_weights / sector_holding_weights.sum()

        portfolio_sector_return = (
            (1 + asset_returns[sector_tickers]).prod() - 1
        ).dot(normalized_weights)

        proxy_ticker = available_sector_tickers.get(sector)
        if proxy_ticker and proxy_ticker in all_returns.columns:
            benchmark_sector_return = (1 + all_returns[proxy_ticker].dropna()).prod() - 1
        else:
            benchmark_sector_return = portfolio_sector_return

        portfolio_weight = sector_weights.loc[sector]
        allocation = (portfolio_weight - benchmark_weight) * benchmark_sector_return
        selection = benchmark_weight * (portfolio_sector_return - benchmark_sector_return)
        interaction = (
            (portfolio_weight - benchmark_weight)
            * (portfolio_sector_return - benchmark_sector_return)
        )

        rows.append(
            {
                "Sector": sector,
                "Portfolio Weight": portfolio_weight,
                "Benchmark Weight": benchmark_weight,
                "Portfolio Sector Return": portfolio_sector_return,
                "Benchmark Sector Return": benchmark_sector_return,
                "Allocation Effect": allocation,
                "Selection Effect": selection,
                "Interaction Effect": interaction,
                "Total Effect": allocation + selection + interaction,
                "Benchmark Proxy": proxy_ticker or "Portfolio proxy",
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).set_index("Sector").sort_values("Total Effect", ascending=False)


def fixed_income_rate_risk(
    tickers,
    weights,
    rate_shock_bps,
    portfolio_value,
    rate_vol_bps,
    confidence,
):
    duration_proxy = {
        "SHY": 1.9,
        "IEF": 7.4,
        "TLT": 16.8,
        "BND": 6.1,
        "AGG": 6.2,
        "LQD": 8.4,
        "HYG": 3.6,
    }
    rate_shock = rate_shock_bps / 10000
    z_score = NormalDist().inv_cdf(confidence)
    rows = []

    for ticker, weight in zip(tickers, weights):
        duration = duration_proxy.get(ticker, 0)
        position_value = weight * portfolio_value
        dv01 = position_value * duration * 0.0001
        estimated_return = -duration * rate_shock
        delta_normal_rate_var = dv01 * rate_vol_bps * z_score
        rows.append(
            {
                "Ticker": ticker,
                "Weight": weight,
                "Position Value": position_value,
                "Duration Proxy": duration,
                "DV01": dv01,
                "Rate Shock Return": estimated_return,
                "Portfolio Contribution": weight * estimated_return,
                "Delta-Normal Rate VaR": delta_normal_rate_var,
            }
        )

    table = pd.DataFrame(rows).set_index("Ticker")
    return table, table["Portfolio Contribution"].sum()


def credit_risk_summary(all_returns, portfolio_returns):
    required = set(CREDIT_PROXY_TICKERS)
    if not required.issubset(all_returns.columns):
        return None, None

    credit_factors = pd.DataFrame(index=all_returns.index)
    credit_factors["High Yield Spread Proxy"] = all_returns["HYG"] - all_returns["SHY"]
    credit_factors["Investment Grade Spread Proxy"] = all_returns["LQD"] - all_returns["SHY"]
    credit_factors = credit_factors.dropna()

    aligned = pd.concat([portfolio_returns.rename("Portfolio"), credit_factors], axis=1).dropna()
    if aligned.shape[0] < 30:
        return None, None

    rows = []
    for factor in credit_factors.columns:
        factor_returns = aligned[factor]
        covariance = aligned["Portfolio"].cov(factor_returns)
        variance = factor_returns.var()
        beta = np.nan if variance == 0 else covariance / variance
        rows.append(
            {
                "Credit Factor": factor,
                "Credit Beta": beta,
                "Correlation": aligned["Portfolio"].corr(factor_returns),
                "Factor Volatility": factor_returns.std() * np.sqrt(TRADING_DAYS),
            }
        )

    stress_table = pd.DataFrame(
        {
            "Scenario": ["HY Spread Widening", "IG Spread Widening", "Broad Credit Stress"],
            "Portfolio Shock": [
                aligned["Portfolio"].corr(aligned["High Yield Spread Proxy"]) * -0.08,
                aligned["Portfolio"].corr(aligned["Investment Grade Spread Proxy"]) * -0.05,
                min(
                    aligned["Portfolio"].corr(aligned["High Yield Spread Proxy"]) * -0.08,
                    aligned["Portfolio"].corr(aligned["Investment Grade Spread Proxy"]) * -0.05,
                ),
            ],
        }
    ).set_index("Scenario")

    return pd.DataFrame(rows).set_index("Credit Factor"), stress_table


@st.cache_data(ttl=3600)
def fetch_credit_profile(ticker):
    try:
        info = yf.Ticker(ticker).get_info()
    except Exception:
        info = {}

    market_cap = info.get("marketCap", np.nan)
    total_debt = info.get("totalDebt", np.nan)
    ebitda = info.get("ebitda", np.nan)
    debt_to_equity = info.get("debtToEquity", np.nan)
    current_ratio = info.get("currentRatio", np.nan)
    quick_ratio = info.get("quickRatio", np.nan)
    beta = info.get("beta", np.nan)
    profit_margin = info.get("profitMargins", np.nan)
    operating_margin = info.get("operatingMargins", np.nan)
    recommendation = info.get("recommendationKey", "N/A")

    leverage_ratio = (
        np.nan
        if pd.isna(total_debt) or pd.isna(ebitda) or ebitda == 0
        else total_debt / ebitda
    )

    score = 0
    score += 2 if pd.notna(market_cap) and market_cap >= 200_000_000_000 else 1 if pd.notna(market_cap) and market_cap >= 20_000_000_000 else 0
    score += 2 if pd.notna(leverage_ratio) and leverage_ratio < 2 else 1 if pd.notna(leverage_ratio) and leverage_ratio < 4 else 0
    score += 2 if pd.notna(debt_to_equity) and debt_to_equity < 80 else 1 if pd.notna(debt_to_equity) and debt_to_equity < 180 else 0
    score += 2 if pd.notna(current_ratio) and current_ratio >= 1.5 else 1 if pd.notna(current_ratio) and current_ratio >= 1.0 else 0
    score += 2 if pd.notna(beta) and beta < 1.0 else 1 if pd.notna(beta) and beta < 1.5 else 0
    score += 2 if pd.notna(profit_margin) and profit_margin > 0.15 else 1 if pd.notna(profit_margin) and profit_margin > 0.05 else 0

    if score >= 10:
        rating_bucket = "AA/A"
        risk_level = "Low"
    elif score >= 8:
        rating_bucket = "A/BBB"
        risk_level = "Moderate"
    elif score >= 5:
        rating_bucket = "BBB/BB"
        risk_level = "Elevated"
    else:
        rating_bucket = "BB/B or Below"
        risk_level = "High"

    return {
        "Ticker": ticker,
        "Company": info.get("shortName") or info.get("longName") or ticker,
        "Sector": info.get("sector") or "Unclassified",
        "Official Rating": "N/A",
        "Proxy Rating Bucket": rating_bucket,
        "Credit Risk Level": risk_level,
        "Credit Score": score,
        "Market Cap": market_cap,
        "Total Debt": total_debt,
        "Debt / EBITDA": leverage_ratio,
        "Debt / Equity": debt_to_equity,
        "Current Ratio": current_ratio,
        "Quick Ratio": quick_ratio,
        "Beta": beta,
        "Profit Margin": profit_margin,
        "Operating Margin": operating_margin,
        "Analyst View": recommendation,
    }


def credit_rating_table(tickers):
    rows = [fetch_credit_profile(ticker) for ticker in tickers]
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).drop_duplicates(subset=["Ticker"]).set_index("Ticker")


def render_credit_ratings(tickers):
    ratings = credit_rating_table(tickers)
    if ratings.empty:
        st.warning("Credit rating data is unavailable.")
        return

    summary_cols = st.columns(4)
    summary_cols[0].metric("Companies", len(ratings))
    summary_cols[1].metric(
        "Low/Moderate Risk",
        int(ratings["Credit Risk Level"].isin(["Low", "Moderate"]).sum()),
    )
    summary_cols[2].metric(
        "High Risk",
        int((ratings["Credit Risk Level"] == "High").sum()),
    )
    summary_cols[3].metric(
        "Median Score",
        format_number(ratings["Credit Score"].median()),
    )

    display = ratings.copy()
    for column in ["Market Cap", "Total Debt"]:
        display[column] = display[column].map(
            lambda value: "N/A" if pd.isna(value) else f"${value / 1_000_000_000:,.1f}B"
        )
    for column in ["Profit Margin", "Operating Margin"]:
        display[column] = display[column].map(format_percent)
    for column in ["Debt / EBITDA", "Debt / Equity", "Current Ratio", "Quick Ratio", "Beta"]:
        display[column] = display[column].map(format_number)

    render_dark_table(display, height=320)
    st.caption(
        "Official agency ratings usually require licensed data. The proxy bucket is an internal model using leverage, liquidity, size, profitability and equity beta."
    )


def liquidity_risk_table(tickers, weights, prices, volumes, portfolio_value):
    if volumes.empty:
        return pd.DataFrame()

    rows = []
    latest_prices = prices[tickers].ffill().iloc[-1]
    average_volume = volumes.reindex(columns=tickers).tail(60).mean()
    average_dollar_volume = average_volume * latest_prices

    for ticker, weight in zip(tickers, weights):
        position_value = weight * portfolio_value
        dollar_volume = average_dollar_volume.get(ticker, np.nan)
        participation_10pct = dollar_volume * 0.10
        days_to_liquidate = (
            np.nan
            if pd.isna(participation_10pct) or participation_10pct <= 0
            else position_value / participation_10pct
        )
        liquidity_adjusted_var = metrics["Daily VaR"] * (1 + min(days_to_liquidate, 10) / 10)

        rows.append(
            {
                "Ticker": ticker,
                "Position Value": position_value,
                "Avg Dollar Volume": dollar_volume,
                "Days to Liquidate": days_to_liquidate,
                "Liquidity Adjusted VaR": liquidity_adjusted_var,
            }
        )

    return pd.DataFrame(rows).set_index("Ticker")


def rebalancing_table(tickers, current_weights, target_weights, portfolio_value, cost_bps):
    trade_weights = target_weights - current_weights
    trade_values = trade_weights * portfolio_value
    turnover = np.abs(trade_values).sum() / (2 * portfolio_value)
    transaction_cost = np.abs(trade_values).sum() * cost_bps / 10000

    table = pd.DataFrame(
        {
            "Ticker": tickers,
            "Current Weight": current_weights,
            "Target Weight": target_weights,
            "Trade Weight": trade_weights,
            "Trade Value": trade_values,
        }
    ).set_index("Ticker")

    summary = {
        "One-Way Turnover": turnover,
        "Estimated Transaction Cost": transaction_cost,
    }

    return table, summary


def estimate_garch_11(returns):
    clean_returns = returns.dropna() * 100
    if len(clean_returns) < 60:
        return None

    residuals = clean_returns - clean_returns.mean()
    variance_target = residuals.var()
    best_result = None
    best_likelihood = np.inf

    alpha_grid = np.arange(0.03, 0.21, 0.02)
    beta_grid = np.arange(0.70, 0.98, 0.02)

    for alpha in alpha_grid:
        for beta in beta_grid:
            if alpha + beta >= 0.995:
                continue

            omega = variance_target * (1 - alpha - beta)
            variances = np.empty(len(residuals))
            variances[0] = variance_target

            for index in range(1, len(residuals)):
                variances[index] = (
                    omega
                    + alpha * residuals.iloc[index - 1] ** 2
                    + beta * variances[index - 1]
                )

            if np.any(variances <= 0):
                continue

            likelihood = 0.5 * np.sum(np.log(variances) + residuals.values**2 / variances)
            if likelihood < best_likelihood:
                best_likelihood = likelihood
                best_result = {
                    "Omega": omega,
                    "Alpha": alpha,
                    "Beta": beta,
                    "Persistence": alpha + beta,
                    "Last Variance": variances[-1],
                    "Last Residual": residuals.iloc[-1],
                    "Mean Return": clean_returns.mean(),
                }

    if best_result is None:
        return None

    next_variance = (
        best_result["Omega"]
        + best_result["Alpha"] * best_result["Last Residual"] ** 2
        + best_result["Beta"] * best_result["Last Variance"]
    )
    daily_volatility = np.sqrt(next_variance) / 100
    annualized_volatility = daily_volatility * np.sqrt(TRADING_DAYS)

    best_result["Forecast Daily Volatility"] = daily_volatility
    best_result["Forecast Annualized Volatility"] = annualized_volatility
    return best_result


def ewma_volatility(returns, lambda_value=0.94):
    clean_returns = returns.dropna()
    if len(clean_returns) < 2:
        return np.nan

    variance = clean_returns.var()
    for value in clean_returns:
        variance = lambda_value * variance + (1 - lambda_value) * value**2
    return np.sqrt(variance)


def latest_rate_vol_bps(history_years=3):
    rates = download_interest_rates(FRED_RATE_SERIES, history_years)
    if rates.empty or "10Y Treasury" not in rates.columns:
        return 75

    rate_changes_bps = rates["10Y Treasury"].dropna().diff().dropna() * 100
    if rate_changes_bps.empty:
        return 75
    return float(rate_changes_bps.tail(252).std())


@st.cache_data(ttl=900)
def download_interest_rates(series_map, history_years):
    series_ids = ",".join(series_map.values())
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_ids}"

    try:
        request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=10) as response:
            rates = pd.read_csv(response)
    except Exception:
        return pd.DataFrame()

    rates = rates.rename(columns={"observation_date": "Date"})
    rates["Date"] = pd.to_datetime(rates["Date"])
    rates = rates.set_index("Date").replace(".", np.nan)

    for column in rates.columns:
        rates[column] = pd.to_numeric(rates[column], errors="coerce")

    rates = rates.rename(columns={value: key for key, value in series_map.items()})
    cutoff = rates.index.max() - pd.DateOffset(years=history_years)
    return rates.loc[rates.index >= cutoff].ffill().dropna(how="all")


@st.cache_data(ttl=300)
def download_live_rate_curve():
    try:
        raw = yf.download(
            list(LIVE_RATE_TICKERS.values()),
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=False,
        )
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

    if raw.empty:
        return pd.DataFrame(), pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]].rename(columns={"Close": list(LIVE_RATE_TICKERS.keys())[0]})

    close = close.rename(columns={value: key for key, value in LIVE_RATE_TICKERS.items()})
    close = close.dropna(how="all")

    latest = close.ffill().iloc[-1].dropna()
    maturity_order = ["13W T-Bill", "5Y Treasury", "10Y Treasury", "30Y Treasury"]
    latest_curve = pd.DataFrame(
        {
            "Maturity": [item for item in maturity_order if item in latest.index],
            "Yield": [latest[item] for item in maturity_order if item in latest.index],
        }
    )

    return close, latest_curve


@st.cache_data(ttl=900)
def fetch_yahoo_news(ticker, limit):
    encoded_ticker = quote_plus(ticker)
    url = (
        "https://feeds.finance.yahoo.com/rss/2.0/headline"
        f"?s={encoded_ticker}&region=US&lang=en-US"
    )
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urlopen(request, timeout=8) as response:
            xml_data = response.read()
    except Exception:
        return pd.DataFrame()

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return pd.DataFrame()

    rows = []
    for item in root.findall("./channel/item")[:limit]:
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        published = item.findtext("pubDate", default="").strip()
        source = item.findtext("source", default="Yahoo Finance").strip()

        if title:
            rows.append(
                {
                    "Ticker": ticker,
                    "Published": published,
                    "Source": source or "Yahoo Finance",
                    "Headline": title,
                    "Link": link,
                }
            )

    return pd.DataFrame(rows)


def fetch_news_for_tickers(tickers, limit):
    news_frames = []
    for ticker in tickers:
        ticker_news = fetch_yahoo_news(ticker, limit)
        if not ticker_news.empty:
            news_frames.append(ticker_news)

    if not news_frames:
        return pd.DataFrame()

    return pd.concat(news_frames, ignore_index=True)


@st.cache_data(ttl=300)
def download_named_close(ticker_map, period="3mo", interval="1d"):
    if not ticker_map:
        return pd.DataFrame()

    try:
        raw = yf.download(
            list(ticker_map.values()),
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False,
        )
    except Exception:
        return pd.DataFrame()

    if raw.empty:
        return pd.DataFrame()

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw.xs("Close", axis=1, level=1)
    else:
        close = raw[["Close"]].rename(columns={"Close": next(iter(ticker_map.values()))})

    close = close.rename(columns={value: key for key, value in ticker_map.items()})
    return close.dropna(how="all")


def summarize_price_moves(close_prices):
    rows = []
    if close_prices.empty:
        return pd.DataFrame()

    latest_row = close_prices.ffill().iloc[-1]
    for name in close_prices.columns:
        series = close_prices[name].dropna()
        if series.empty:
            continue
        latest = series.iloc[-1]
        prior_1d = series.iloc[-2] if len(series) >= 2 else np.nan
        prior_1w = series.iloc[-6] if len(series) >= 6 else np.nan
        prior_1m = series.iloc[-22] if len(series) >= 22 else np.nan
        rows.append(
            {
                "Name": name,
                "Latest": latest,
                "1D": np.nan if pd.isna(prior_1d) or prior_1d == 0 else latest / prior_1d - 1,
                "1W": np.nan if pd.isna(prior_1w) or prior_1w == 0 else latest / prior_1w - 1,
                "1M": np.nan if pd.isna(prior_1m) or prior_1m == 0 else latest / prior_1m - 1,
                "High": series.max(),
                "Low": series.min(),
            }
        )

    table = pd.DataFrame(rows).set_index("Name")
    return table.sort_values("1D", ascending=False)


@st.cache_data(ttl=300)
def download_custom_fx_cross(base_currency, quote_currency, period="3mo"):
    base_currency = base_currency.upper()
    quote_currency = quote_currency.upper()
    if base_currency == quote_currency:
        return pd.DataFrame({"Rate": [1.0]}, index=[pd.Timestamp.utcnow()])

    label = f"{base_currency}/{quote_currency}"
    direct_ticker = f"{base_currency}{quote_currency}=X"
    close = download_named_close({label: direct_ticker}, period=period)
    if not close.empty:
        return close.rename(columns={label: "Rate"})

    inverse_label = f"{quote_currency}/{base_currency}"
    inverse_ticker = f"{quote_currency}{base_currency}=X"
    inverse_close = download_named_close({inverse_label: inverse_ticker}, period=period)
    if inverse_close.empty:
        return pd.DataFrame()

    inverse_series = inverse_close[inverse_label].replace(0, np.nan)
    return (1 / inverse_series).to_frame("Rate").dropna()


@st.cache_data(ttl=600)
def fetch_google_news(query, limit):
    encoded_query = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urlopen(request, timeout=8) as response:
            xml_data = response.read()
    except Exception:
        return pd.DataFrame()

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return pd.DataFrame()

    rows = []
    for item in root.findall("./channel/item")[:limit]:
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        published = item.findtext("pubDate", default="").strip()
        source_node = item.find("source")
        source = source_node.text.strip() if source_node is not None and source_node.text else "Google News"
        if title:
            rows.append(
                {
                    "Published": published,
                    "Source": source,
                    "Headline": title,
                    "Link": link,
                }
            )

    return pd.DataFrame(rows)


def fetch_country_news(countries, limit):
    frames = []
    for country in countries:
        query = f"{country} stock market economy central bank"
        country_news = fetch_google_news(query, limit)
        if not country_news.empty:
            country_news.insert(0, "Country", country)
            frames.append(country_news)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data(ttl=86400)
def download_us_listed_equities():
    urls = {
        "NASDAQ": "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
        "OTHER": "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
    }
    frames = []

    for source, url in urls.items():
        try:
            raw = pd.read_csv(url, sep="|")
        except Exception:
            continue

        raw = raw[~raw.iloc[:, 0].astype(str).str.contains("File Creation Time", na=False)]

        if source == "NASDAQ":
            frame = pd.DataFrame(
                {
                    "Ticker": raw.get("Symbol"),
                    "Company": raw.get("Security Name"),
                    "Exchange": "NASDAQ",
                    "ETF": raw.get("ETF"),
                    "Test Issue": raw.get("Test Issue"),
                }
            )
        else:
            exchange_map = {
                "A": "NYSE American",
                "N": "NYSE",
                "P": "NYSE Arca",
                "Z": "Cboe BZX",
                "V": "IEXG",
            }
            frame = pd.DataFrame(
                {
                    "Ticker": raw.get("ACT Symbol"),
                    "Company": raw.get("Security Name"),
                    "Exchange": raw.get("Exchange").map(exchange_map).fillna(raw.get("Exchange")),
                    "ETF": raw.get("ETF"),
                    "Test Issue": raw.get("Test Issue"),
                }
            )

        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    universe = pd.concat(frames, ignore_index=True)
    universe = universe.dropna(subset=["Ticker"])
    universe["Ticker"] = universe["Ticker"].astype(str).str.strip()
    universe["Company"] = universe["Company"].astype(str).str.strip()
    universe = universe[
        (universe["ETF"].fillna("N") == "N")
        & (universe["Test Issue"].fillna("N") == "N")
        & (~universe["Ticker"].str.contains(r"[$\^/]", regex=True))
    ]
    universe["Asset Class"] = "Equity"
    universe["Region"] = "US"
    universe["Category"] = "Common Stock"
    universe["Duration Bucket"] = ""
    universe["Currency"] = "USD"
    return universe.drop_duplicates(subset=["Ticker"]).sort_values("Ticker")


def infer_fixed_income_category(company_name):
    name = str(company_name).upper()
    if any(keyword in name for keyword in ["TREASURY", "T-BILL", "T BILL", "GOVERNMENT"]):
        return "Government Bonds"
    if any(keyword in name for keyword in ["MUNICIPAL", "MUNI", "TAX-EXEMPT"]):
        return "Municipal Bonds"
    if any(keyword in name for keyword in ["HIGH YIELD", "JUNK"]):
        return "High Yield Credit"
    if any(keyword in name for keyword in ["INVESTMENT GRADE", "CORPORATE", "CREDIT"]):
        return "Investment Grade Credit"
    if any(keyword in name for keyword in ["MORTGAGE", "MBS", "CMBS", "ABS", "SECURITIZED"]):
        return "Securitized Credit"
    if any(keyword in name for keyword in ["INFLATION", "TIPS"]):
        return "Inflation Linked"
    if any(keyword in name for keyword in ["FLOATING", "FRN", "BANK LOAN", "SENIOR LOAN"]):
        return "Floating Rate / Loans"
    if any(keyword in name for keyword in ["CONVERTIBLE"]):
        return "Convertible Bonds"
    if any(keyword in name for keyword in ["PREFERRED"]):
        return "Preferred Securities"
    if any(keyword in name for keyword in ["EMERGING MARKET", "EMERGING MARKETS", "EM BOND"]):
        return "Emerging Market Debt"
    if any(keyword in name for keyword in ["SHORT DURATION", "ULTRA SHORT", "MONEY MARKET", "CASH"]):
        return "Ultra Short / Cash"
    if any(keyword in name for keyword in ["BOND", "FIXED INCOME", "INCOME", "DEBT"]):
        return "Aggregate / Multi-Sector Bonds"
    return "Fixed Income ETF"


def infer_duration_bucket(company_name):
    name = str(company_name).upper()
    if any(keyword in name for keyword in ["ULTRA SHORT", "SHORT TERM", "SHORT-TERM", "0-3", "1-3", "1-5", "CASH", "MONEY MARKET", "T-BILL"]):
        return "Short"
    if any(keyword in name for keyword in ["INTERMEDIATE", "3-7", "5-10", "7-10"]):
        return "Intermediate"
    if any(keyword in name for keyword in ["LONG", "10-20", "20+", "25+", "30 YEAR", "EXTENDED"]):
        return "Long"
    return "Mixed / Unspecified"


@st.cache_data(ttl=86400)
def download_us_fixed_income_etfs():
    urls = {
        "NASDAQ": "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
        "OTHER": "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
    }
    frames = []

    for source, url in urls.items():
        try:
            raw = pd.read_csv(url, sep="|")
        except Exception:
            continue

        if raw.empty:
            continue
        raw = raw[~raw.iloc[:, 0].astype(str).str.contains("File Creation Time", na=False)]

        if source == "NASDAQ":
            required = {"Symbol", "Security Name"}
            if not required.issubset(set(raw.columns)):
                continue
            frame = pd.DataFrame(
                {
                    "Ticker": raw.get("Symbol"),
                    "Company": raw.get("Security Name"),
                    "Exchange": "NASDAQ",
                    "ETF": raw.get("ETF"),
                    "Test Issue": raw.get("Test Issue"),
                }
            )
        else:
            required = {"ACT Symbol", "Security Name", "Exchange"}
            if not required.issubset(set(raw.columns)):
                continue
            exchange_map = {
                "A": "NYSE American",
                "N": "NYSE",
                "P": "NYSE Arca",
                "Z": "Cboe BZX",
                "V": "IEXG",
            }
            frame = pd.DataFrame(
                {
                    "Ticker": raw.get("ACT Symbol"),
                    "Company": raw.get("Security Name"),
                    "Exchange": raw.get("Exchange").map(exchange_map).fillna(raw.get("Exchange")),
                    "ETF": raw.get("ETF"),
                    "Test Issue": raw.get("Test Issue"),
                }
            )
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    universe = pd.concat(frames, ignore_index=True)
    if universe.empty or not {"Ticker", "Company"}.issubset(universe.columns):
        return pd.DataFrame()
    universe = universe.dropna(subset=["Ticker", "Company"])
    universe["Ticker"] = universe["Ticker"].astype(str).str.strip()
    universe["Company"] = universe["Company"].astype(str).str.strip()
    universe = universe[
        (universe["ETF"].fillna("N") == "Y")
        & (universe["Test Issue"].fillna("N") == "N")
        & (~universe["Ticker"].str.contains(r"[$\^/]", regex=True))
    ]

    fixed_income_keywords = (
        "BOND|TREASURY|T-BILL|T BILL|FIXED INCOME|INCOME|DEBT|CREDIT|"
        "MUNICIPAL|MUNI|MORTGAGE|MBS|CMBS|ABS|LOAN|FLOATING|FRN|"
        "PREFERRED|CONVERTIBLE|TIPS|INFLATION|HIGH YIELD|CASH|MONEY MARKET"
    )
    universe = universe[
        universe["Company"].str.upper().str.contains(fixed_income_keywords, regex=True, na=False)
    ]
    if universe.empty:
        return universe

    universe["Asset Class"] = "Fixed Income"
    universe["Region"] = "US"
    universe["Category"] = universe["Company"].map(infer_fixed_income_category)
    universe["Duration Bucket"] = universe["Company"].map(infer_duration_bucket)
    universe["Currency"] = "USD"
    return universe.drop_duplicates(subset=["Ticker"]).sort_values("Ticker")


@st.cache_data(ttl=86400)
def download_german_equities():
    try:
        tables = pd.read_html("https://en.wikipedia.org/wiki/DAX")
    except Exception:
        tables = []

    candidates = []
    for table in tables:
        columns = {str(column).lower(): column for column in table.columns}
        ticker_col = None
        company_col = None

        for lower_name, original_name in columns.items():
            if "ticker" in lower_name or "symbol" in lower_name:
                ticker_col = original_name
            if "company" in lower_name:
                company_col = original_name

        if ticker_col is not None and company_col is not None:
            candidate = pd.DataFrame(
                {
                    "Ticker": table[ticker_col].astype(str),
                    "Company": table[company_col].astype(str),
                }
            )
            candidates.append(candidate)
            break

    if candidates:
        universe = candidates[0]
        universe["Ticker"] = universe["Ticker"].str.replace(r"\s.*$", "", regex=True)
        universe["Ticker"] = universe["Ticker"].apply(
            lambda ticker: ticker if "." in ticker else f"{ticker}.DE"
        )
        universe["Exchange"] = "Xetra"
        universe["Region"] = "Germany"
    else:
        universe = pd.DataFrame(GERMAN_EQUITY_FALLBACK)

    universe["Asset Class"] = "Equity"
    universe["Category"] = "Common Stock"
    universe["Duration Bucket"] = ""
    universe["Currency"] = "EUR"
    universe["ETF"] = "N"
    universe["Test Issue"] = "N"
    return universe.drop_duplicates(subset=["Ticker"]).sort_values("Ticker")


def fixed_income_universe():
    frames = [pd.DataFrame(FIXED_INCOME_PRODUCTS)]
    try:
        us_fixed_income = download_us_fixed_income_etfs()
        if not us_fixed_income.empty:
            frames.append(us_fixed_income)
    except Exception:
        pass

    universe = pd.concat(frames, ignore_index=True)
    if universe.empty:
        return pd.DataFrame(FIXED_INCOME_PRODUCTS)
    universe["Asset Class"] = "Fixed Income"
    if "Exchange" not in universe.columns:
        universe["Exchange"] = ""
    universe["Exchange"] = universe["Exchange"].replace("", np.nan)
    fallback_exchange = pd.Series(
        np.where(universe["Ticker"].astype(str).str.endswith(".DE"), "Xetra", "US Listed"),
        index=universe.index,
    )
    universe["Exchange"] = universe["Exchange"].fillna(fallback_exchange)
    universe["ETF"] = "Y"
    universe["Test Issue"] = "N"
    return universe.drop_duplicates(subset=["Ticker"]).sort_values("Ticker")


def build_instrument_universe(region, asset_class):
    frames = []

    if asset_class in {"Equity", "All"}:
        if region in {"US", "Global"}:
            frames.append(download_us_listed_equities())
        if region in {"Germany", "Global"}:
            frames.append(download_german_equities())

    if asset_class in {"Fixed Income", "All"}:
        fixed_income = fixed_income_universe()
        if region != "Global":
            fixed_income = fixed_income[fixed_income["Region"] == region]
        frames.append(fixed_income)

    if not frames:
        return pd.DataFrame()

    columns = [
        "Ticker",
        "Company",
        "Asset Class",
        "Region",
        "Exchange",
        "Category",
        "Duration Bucket",
        "Currency",
    ]
    universe = pd.concat(frames, ignore_index=True)
    for column in columns:
        if column not in universe.columns:
            universe[column] = ""
    return universe[columns].drop_duplicates(subset=["Ticker"]).sort_values("Ticker")


def filter_instrument_universe(
    universe,
    search_text,
    exchange="All",
    category="All",
    currency="All",
):
    if universe.empty:
        return universe

    filtered = universe.copy()
    search_text = search_text.strip().upper()

    if search_text:
        search_terms = [term.strip() for term in search_text.split(",") if term.strip()]
        mask = pd.Series(False, index=filtered.index)
        for term in search_terms:
            for column in ["Ticker", "Company", "Asset Class", "Region", "Category", "Exchange"]:
                mask = mask | filtered[column].astype(str).str.upper().str.contains(
                    term,
                    regex=False,
                )
        filtered = filtered[mask]

    if exchange != "All" and "Exchange" in filtered.columns:
        filtered = filtered[filtered["Exchange"].astype(str) == exchange]
    if category != "All" and "Category" in filtered.columns:
        filtered = filtered[filtered["Category"].astype(str) == category]
    if currency != "All" and "Currency" in filtered.columns:
        filtered = filtered[filtered["Currency"].astype(str) == currency]

    return filtered


def filter_options(dataframe, column):
    if column not in dataframe.columns:
        return ["All"]
    values = (
        dataframe[column]
        .dropna()
        .astype(str)
        .replace("", np.nan)
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )
    return ["All"] + values


@st.cache_data(ttl=3600)
def fetch_company_profile(ticker):
    try:
        info = yf.Ticker(ticker).get_info()
    except Exception:
        info = {}

    return {
        "Ticker": ticker,
        "Company": info.get("shortName") or info.get("longName") or ticker,
        "Sector": info.get("sector") or "Unclassified",
        "Industry": info.get("industry") or "Unclassified",
        "Market Cap": info.get("marketCap", np.nan),
        "Exchange": info.get("exchange") or "N/A",
        "Country": info.get("country") or "N/A",
    }


def build_equity_universe(tickers):
    rows = [fetch_company_profile(ticker) for ticker in tickers]
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).drop_duplicates(subset=["Ticker"])


def render_equity_universe(
    seed_tickers,
    classification_view,
    search_text,
    max_rows,
    region,
    asset_class,
):
    listed_universe = build_instrument_universe(region, asset_class)

    if listed_universe.empty:
        st.warning("No instruments matched the selected region and asset class.")
        universe = build_equity_universe(seed_tickers)
    else:
        st.markdown("**Instrument Screener**")
        filter_cols = st.columns([0.34, 0.18, 0.22, 0.14, 0.12], gap="medium")
        with filter_cols[0]:
            page_search_text = st.text_input(
                "Keyword filter",
                value=search_text,
                placeholder="Ticker, company, category, region...",
                key="instrument_keyword_filter",
            )
        with filter_cols[1]:
            exchange_filter = st.selectbox(
                "Exchange",
                options=filter_options(listed_universe, "Exchange"),
                key="instrument_exchange_filter",
            )
        with filter_cols[2]:
            category_filter = st.selectbox(
                "Category",
                options=filter_options(listed_universe, "Category"),
                key="instrument_category_filter",
            )
        with filter_cols[3]:
            currency_filter = st.selectbox(
                "Currency",
                options=filter_options(listed_universe, "Currency"),
                key="instrument_currency_filter",
            )
        with filter_cols[4]:
            display_rows = st.number_input(
                "Rows",
                min_value=50,
                max_value=max(50, len(listed_universe)),
                value=min(max_rows, max(50, len(listed_universe))),
                step=50,
                key="instrument_display_rows",
            )

        filtered_universe = filter_instrument_universe(
            listed_universe,
            page_search_text,
            exchange_filter,
            category_filter,
            currency_filter,
        )
        displayed_universe = filtered_universe.head(int(display_rows))

        listed_cols = st.columns(4)
        listed_cols[0].metric("Instruments", f"{len(listed_universe):,}")
        listed_cols[1].metric("Matched Results", f"{len(filtered_universe):,}")
        listed_cols[2].metric("Displayed Results", f"{len(displayed_universe):,}")
        listed_cols[3].metric("Markets", listed_universe["Region"].nunique())

        render_dark_table(
            displayed_universe[
                [
                    "Ticker",
                    "Company",
                    "Asset Class",
                    "Region",
                    "Exchange",
                    "Category",
                    "Duration Bucket",
                    "Currency",
                ]
            ].set_index("Ticker"),
            height=280,
        )

        default_classification_tickers = seed_tickers[:]
        if page_search_text or exchange_filter != "All" or category_filter != "All" or currency_filter != "All":
            default_classification_tickers = displayed_universe["Ticker"].head(12).tolist()

        classify_input = st.text_input(
            "Tickers to classify",
            value=", ".join(default_classification_tickers),
            help="Enter tickers from the screener to enrich with sector, industry, market cap and instrument details.",
        )
        classify_tickers = parse_list(classify_input)
        universe = build_equity_universe(classify_tickers)
        instrument_details = listed_universe[
            listed_universe["Ticker"].isin(classify_tickers)
        ].set_index("Ticker")
        if not instrument_details.empty and not universe.empty:
            universe = universe.set_index("Ticker")
            for column in [
                "Company",
                "Asset Class",
                "Region",
                "Category",
                "Duration Bucket",
                "Currency",
                "Exchange",
            ]:
                universe[column] = instrument_details[column].combine_first(
                    universe.get(column, pd.Series(index=universe.index, dtype=object))
                )
            universe = universe.reset_index()

    if universe.empty:
        st.warning("No tickers selected for classification.")
        return

    st.markdown(
        '<div class="module-caption">Classification for selected candidate stocks and fixed income products.</div>',
        unsafe_allow_html=True,
    )

    summary_cols = st.columns(4)
    summary_cols[0].metric("Classified Instruments", len(universe))
    summary_cols[1].metric("Sectors", universe["Sector"].nunique())
    summary_cols[2].metric("Industries", universe["Industry"].nunique())
    summary_cols[3].metric(
        "Total Market Cap",
        "N/A"
        if universe["Market Cap"].isna().all()
        else f"${universe['Market Cap'].sum() / 1_000_000_000:,.0f}B",
    )

    if "Asset Class" not in universe.columns:
        universe["Asset Class"] = "Equity"
    if "Region" not in universe.columns:
        universe["Region"] = "N/A"
    if "Category" not in universe.columns:
        universe["Category"] = universe["Sector"]
    if "Duration Bucket" not in universe.columns:
        universe["Duration Bucket"] = ""
    if "Currency" not in universe.columns:
        universe["Currency"] = "N/A"

    if classification_view == "Sector":
        group_columns = ["Sector"]
    elif classification_view == "Industry":
        group_columns = ["Industry"]
    elif classification_view == "Asset Class + Region":
        group_columns = ["Asset Class", "Region", "Category", "Duration Bucket"]
    else:
        group_columns = ["Asset Class", "Region", "Sector", "Industry", "Category"]

    group_summary = (
        universe.groupby(group_columns, dropna=False)
        .agg(
            Tickers=("Ticker", lambda values: ", ".join(values)),
            Companies=("Company", lambda values: ", ".join(values)),
            Count=("Ticker", "count"),
            Market_Cap=("Market Cap", "sum"),
        )
        .sort_values(["Count", "Market_Cap"], ascending=False)
    )

    display_summary = group_summary.copy()
    display_summary["Market_Cap"] = display_summary["Market_Cap"].map(
        lambda value: "N/A" if pd.isna(value) or value == 0 else f"${value / 1_000_000_000:,.1f}B"
    )
    display_summary = display_summary.rename(columns={"Market_Cap": "Market Cap"})

    sector_counts = universe.groupby("Sector")["Ticker"].count().sort_values(ascending=False)

    left_col, right_col = st.columns([0.38, 0.62])
    with left_col:
        st.markdown("**Sector Distribution**")
        render_dark_bar_chart(sector_counts, height=245)
    with right_col:
        st.markdown("**Classification Summary**")
        render_dark_table(display_summary, height=245)

    st.markdown("**Company Universe**")
    company_table = universe.copy()
    company_table["Market Cap"] = company_table["Market Cap"].map(
        lambda value: "N/A" if pd.isna(value) else f"${value / 1_000_000_000:,.1f}B"
    )
    render_dark_table(
        company_table[
            [
                "Ticker",
                "Company",
                "Asset Class",
                "Region",
                "Sector",
                "Industry",
                "Category",
                "Duration Bucket",
                "Currency",
                "Market Cap",
                "Exchange",
                "Country",
            ]
        ].set_index("Ticker"),
        height=340,
    )


def render_live_kline(default_tickers):
    default_ticker = default_tickers[0] if default_tickers else "AAPL"

    interval_periods = {
        "1m": ["1d", "5d", "7d"],
        "5m": ["1d", "5d", "1mo", "60d"],
        "15m": ["5d", "1mo", "60d"],
        "30m": ["5d", "1mo", "60d"],
        "1h": ["5d", "1mo", "3mo", "6mo"],
        "1d": ["1mo", "3mo", "6mo", "1y", "2y"],
    }

    st.markdown("**Live Candlestick**")
    control_cols = st.columns([0.18, 0.14, 0.14, 0.54], gap="medium")
    with control_cols[0]:
        ticker = st.text_input(
            "Ticker",
            value=default_ticker,
            help="Yahoo Finance ticker, for example AAPL, MSFT, SAP.DE or ^GDAXI.",
            key="live_kline_ticker",
        ).strip().upper()
    with control_cols[1]:
        interval = st.selectbox(
            "Interval",
            options=list(interval_periods.keys()),
            index=1,
            key="live_kline_interval",
        )
    with control_cols[2]:
        period = st.selectbox(
            "Period",
            options=interval_periods[interval],
            index=1 if len(interval_periods[interval]) > 1 else 0,
            key=f"live_kline_period_{interval}",
        )
    with control_cols[3]:
        selected_indicators = st.multiselect(
            "Technical overlays",
            options=["SMA 20", "SMA 50", "EMA 12", "EMA 26", "BB Upper", "BB Lower", "VWAP"],
            default=["SMA 20", "SMA 50", "VWAP"],
            help="Overlay moving averages, Bollinger bands and VWAP on the K-line chart.",
            key="live_kline_indicators",
        )

    if not ticker:
        st.warning("Enter a ticker to load a live K-line chart.")
        return

    ohlc = download_ohlc(ticker, period, interval)
    if ohlc.empty:
        st.warning("OHLC data is temporarily unavailable for this ticker, interval or period.")
        return

    ohlc_with_indicators = add_technical_indicators(ohlc)
    latest = ohlc_with_indicators.iloc[-1]
    first_close = ohlc_with_indicators["Close"].iloc[0]
    period_return = np.nan if first_close == 0 else latest["Close"] / first_close - 1
    session_range = latest["High"] - latest["Low"]
    latest_volume = latest.get("Volume", np.nan)

    metric_cols = st.columns(5, gap="small")
    metric_cols[0].metric("Last", f"{latest['Close']:.2f}")
    metric_cols[1].metric("Period Return", format_percent(period_return))
    metric_cols[2].metric("Open", f"{latest['Open']:.2f}")
    metric_cols[3].metric("Range", f"{session_range:.2f}")
    metric_cols[4].metric(
        "Latest Volume",
        "N/A" if pd.isna(latest_volume) or latest_volume == 0 else f"{latest_volume:,.0f}",
    )

    last_bar_time = pd.to_datetime(ohlc_with_indicators.index[-1]).strftime("%Y-%m-%d %H:%M")
    st.markdown(f"**{ticker} K-Line ({interval}, {period})**")
    st.markdown(
        f'<div class="module-caption">Latest regular-session bar: {last_bar_time}. Source: Yahoo Finance, refreshed {data_timestamp()}.</div>',
        unsafe_allow_html=True,
    )
    render_dark_candlestick_chart(
        ohlc_with_indicators,
        selected_indicators=selected_indicators,
        height=500,
    )

    indicator_snapshot = [
        (indicator, latest.get(indicator, np.nan))
        for indicator in selected_indicators
        if indicator in ohlc_with_indicators.columns
    ]
    if indicator_snapshot:
        st.markdown("**Technical Snapshot**")
        indicator_cols = st.columns(min(6, len(indicator_snapshot)), gap="small")
        for column, (indicator, value) in zip(indicator_cols, indicator_snapshot):
            column.metric(indicator, "N/A" if pd.isna(value) else f"{value:.2f}")

    latest_rows = ohlc_with_indicators.tail(8).copy()
    latest_rows.insert(0, "Date", pd.to_datetime(latest_rows.index).strftime("%Y-%m-%d %H:%M"))
    latest_rows = latest_rows.reset_index(drop=True)
    for column in ["Open", "High", "Low", "Close"]:
        latest_rows[column] = latest_rows[column].map(lambda value: f"{value:.2f}")
    if "Volume" in latest_rows.columns:
        latest_rows["Volume"] = latest_rows["Volume"].map(
            lambda value: "N/A" if pd.isna(value) or value == 0 else f"{value:,.0f}"
        )
    for column in selected_indicators:
        if column in latest_rows.columns:
            latest_rows[column] = latest_rows[column].map(
                lambda value: "N/A" if pd.isna(value) else f"{value:.2f}"
            )
    st.markdown("**Recent OHLC Bars**")
    render_dark_table(latest_rows, height=260)


def render_move_table(summary, latest_decimals=2):
    display = summary.copy()
    if display.empty:
        st.warning("Market data is temporarily unavailable.")
        return

    for column in ["1D", "1W", "1M"]:
        if column in display.columns:
            display[column] = display[column].map(format_percent)
    for column in ["Latest", "High", "Low"]:
        if column in display.columns:
            display[column] = display[column].map(
                lambda value: "N/A" if pd.isna(value) else f"{value:,.{latest_decimals}f}"
            )
    render_dark_table(display, height=320)


def index_metadata_frame(countries):
    rows = []
    for country in countries:
        details = GLOBAL_MARKET_INDEX_DETAILS.get(country, {})
        rows.append(
            {
                "Country / Region": country,
                "Index Name": details.get("Index Name", country),
                "Ticker": details.get("Ticker", GLOBAL_MARKET_TICKERS.get(country, "")),
                "Provider": details.get("Provider", "N/A"),
                "Description": details.get("Description", ""),
            }
        )
    return pd.DataFrame(rows)


def render_index_move_table(summary, countries):
    if summary.empty:
        st.warning("Market data is temporarily unavailable.")
        return

    metadata = index_metadata_frame(countries).set_index("Country / Region")
    display = summary.copy()
    display.insert(0, "Ticker", metadata.reindex(display.index)["Ticker"])
    display.insert(0, "Index Name", metadata.reindex(display.index)["Index Name"])
    for column in ["1D", "1W", "1M"]:
        if column in display.columns:
            display[column] = display[column].map(format_percent)
    for column in ["Latest", "High", "Low"]:
        if column in display.columns:
            display[column] = display[column].map(
                lambda value: "N/A" if pd.isna(value) else f"{value:,.2f}"
            )
    render_dark_table(display, height=340)


def render_custom_fx_cross(market_period):
    st.markdown("**Custom FX Cross**")
    control_cols = st.columns([0.22, 0.22, 0.22, 0.34], gap="medium")
    with control_cols[0]:
        base_currency = st.selectbox(
            "Base currency",
            options=GLOBAL_CURRENCIES,
            index=GLOBAL_CURRENCIES.index("EUR"),
            key="custom_fx_base",
        )
    with control_cols[1]:
        quote_currency = st.selectbox(
            "Quote currency",
            options=GLOBAL_CURRENCIES,
            index=GLOBAL_CURRENCIES.index("USD"),
            key="custom_fx_quote",
        )
    with control_cols[2]:
        custom_period = st.selectbox(
            "History",
            options=["5d", "1mo", "3mo", "6mo", "1y"],
            index=["5d", "1mo", "3mo", "6mo", "1y"].index(market_period)
            if market_period in ["5d", "1mo", "3mo", "6mo", "1y"]
            else 2,
            key="custom_fx_period",
        )

    custom_fx = download_custom_fx_cross(base_currency, quote_currency, custom_period)
    pair_label = f"{base_currency}/{quote_currency}"

    if custom_fx.empty:
        st.warning(f"{pair_label} rate data is temporarily unavailable.")
        return

    latest_rate = custom_fx["Rate"].dropna().iloc[-1]
    first_rate = custom_fx["Rate"].dropna().iloc[0]
    custom_return = np.nan if first_rate == 0 else latest_rate / first_rate - 1

    with control_cols[3]:
        metric_cols = st.columns(2, gap="small")
        metric_cols[0].metric(pair_label, f"{latest_rate:,.4f}")
        metric_cols[1].metric("Period Move", format_percent(custom_return))

    render_dark_line_chart(custom_fx.rename(columns={"Rate": pair_label}), height=330)


def render_global_markets(
    countries,
    fx_pairs,
    market_period,
    news_limit,
    rate_history_years,
):
    countries = countries or ["United States", "Germany", "Japan", "China", "India"]
    fx_pairs = fx_pairs or ["DXY", "EUR/USD", "USD/JPY", "GBP/USD"]

    country_tickers = {
        country: GLOBAL_MARKET_TICKERS[country]
        for country in countries
        if country in GLOBAL_MARKET_TICKERS
    }
    fx_tickers = {
        pair: GLOBAL_FX_TICKERS[pair]
        for pair in fx_pairs
        if pair in GLOBAL_FX_TICKERS
    }

    st.markdown(
        f"""
        <div class="terminal-header">
            <div class="terminal-title">Global Markets</div>
            <div class="terminal-subtitle">
                Cross-country equity direction, FX moves, rate curves and live country-level news flow.
            </div>
            <div class="context-row">
                <span class="context-pill">Countries: {' / '.join(countries)}</span>
                <span class="context-pill">FX: {' / '.join(fx_pairs)}</span>
                <span class="context-pill">Sources: Yahoo Finance + FRED + Google News RSS</span>
                <span class="context-pill">Data pulled: {data_timestamp()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    index_close = download_named_close(country_tickers, period=market_period)
    fx_close = download_named_close(fx_tickers, period=market_period)
    index_summary = summarize_price_moves(index_close)
    fx_summary = summarize_price_moves(fx_close)

    top_cols = st.columns(4)
    if not index_summary.empty:
        best_country = index_summary["1D"].idxmax()
        worst_country = index_summary["1D"].idxmin()
        top_cols[0].metric("Best Equity Market 1D", best_country, format_percent(index_summary.loc[best_country, "1D"]))
        top_cols[1].metric("Weakest Equity Market 1D", worst_country, format_percent(index_summary.loc[worst_country, "1D"]))
    else:
        top_cols[0].metric("Best Equity Market 1D", "N/A")
        top_cols[1].metric("Weakest Equity Market 1D", "N/A")
    if not fx_summary.empty:
        top_fx = fx_summary["1D"].abs().idxmax()
        top_cols[2].metric("Largest FX Move 1D", top_fx, format_percent(fx_summary.loc[top_fx, "1D"]))
    else:
        top_cols[2].metric("Largest FX Move 1D", "N/A")
    top_cols[3].metric("News Countries", len(countries))

    equity_tab, fx_tab, rates_tab, news_tab = st.tabs(
        ["Equity Indices", "FX Monitor", "Rates", "Country News"]
    )

    with equity_tab:
        st.markdown("**Index Universe**")
        render_dark_table(
            index_metadata_frame([country for country in countries if country in GLOBAL_MARKET_TICKERS]).set_index("Country / Region"),
            height=220,
        )
        st.markdown("**Index Moves**")
        render_index_move_table(index_summary, countries)
        st.markdown("**Normalized Index Performance**")
        if index_close.empty:
            st.warning("Global equity index data is temporarily unavailable.")
        else:
            normalized = index_close.ffill().apply(lambda series: series / series.dropna().iloc[0] - 1 if not series.dropna().empty else series)
            render_dark_line_chart(normalized, height=380)

    with fx_tab:
        st.markdown("**FX Moves**")
        render_move_table(fx_summary, latest_decimals=4)
        st.markdown("**FX Performance**")
        if fx_close.empty:
            st.warning("FX data is temporarily unavailable.")
        else:
            normalized_fx = fx_close.ffill().apply(lambda series: series / series.dropna().iloc[0] - 1 if not series.dropna().empty else series)
            render_dark_line_chart(normalized_fx, height=380)
        render_custom_fx_cross(market_period)

    with rates_tab:
        official_rates = download_interest_rates(FRED_RATE_SERIES, rate_history_years)
        live_rates, live_curve = download_live_rate_curve()
        rate_left, rate_right = st.columns([0.42, 0.58], gap="medium")
        with rate_left:
            st.markdown("**Market-Implied Treasury Curve**")
            if live_curve.empty:
                st.warning("Live rate curve is temporarily unavailable.")
            else:
                rate_cols = st.columns(min(4, len(live_curve)), gap="small")
                for column, (_, row) in zip(rate_cols, live_curve.iterrows()):
                    column.metric(row["Maturity"], f"{row['Yield']:.2f}%")
                render_dark_line_chart(live_curve.set_index("Maturity"), height=285)
        with rate_right:
            st.markdown("**Official Rate History**")
            if official_rates.empty:
                st.warning("Official rate history is temporarily unavailable.")
                if not live_rates.empty:
                    render_dark_line_chart(live_rates, height=285)
            else:
                render_dark_line_chart(official_rates, height=285)

    with news_tab:
        news = fetch_country_news(countries, news_limit)
        if news.empty:
            st.warning("Country news is temporarily unavailable.")
        else:
            filter_country = st.multiselect(
                "Filter countries",
                options=countries,
                default=countries,
                key="global_news_country_filter",
            )
            filtered_news = news[news["Country"].isin(filter_country)] if filter_country else news
            st.metric("Headlines Loaded", len(filtered_news))
            news_cols = st.columns(2, gap="medium")
            for index, (_, article) in enumerate(filtered_news.iterrows()):
                with news_cols[index % 2]:
                    st.markdown(
                        f"**{article['Country']}** | [{article['Headline']}]({article['Link']})  \n"
                        f"<span style='color:#caa6ad;font-size:0.78rem'>{article['Source']} · {article['Published']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.divider()


def render_market_monitor(
    news_tickers,
    rate_history_years,
    news_items_per_ticker,
    classification_view,
    universe_search,
    max_universe_rows,
    region_filter,
    asset_class_filter,
):
    st.markdown(
        f"""
        <div class="terminal-header">
            <div class="terminal-title">Market Monitor</div>
            <div class="terminal-subtitle">
                Market Monitor: rates, curve dynamics, credit context and company-specific news for daily surveillance.
            </div>
            <div class="context-row">
                <span class="context-pill">Rate History: {rate_history_years}Y</span>
                <span class="context-pill">News Tickers: {' / '.join(news_tickers)}</span>
                <span class="context-pill">Source: FRED + Yahoo Finance RSS</span>
                <span class="context-pill">Data pulled: {data_timestamp()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rates_monitor_tab, live_kline_tab, universe_tab, ratings_tab, news_monitor_tab = st.tabs(
        ["Rates Dashboard", "Live K-Line", "Equity Universe", "Credit Ratings", "News Desk"]
    )

    with rates_monitor_tab:
        rates = download_interest_rates(FRED_RATE_SERIES, rate_history_years)
        live_rates, live_curve = download_live_rate_curve()

        if rates.empty and live_curve.empty:
            st.warning("Interest-rate data is temporarily unavailable.")
        else:
            if not live_curve.empty:
                st.markdown("**Market-Implied Treasury Curve**")
                live_cols = st.columns(min(4, len(live_curve)))
                for column, (_, row) in zip(live_cols, live_curve.iterrows()):
                    column.metric(row["Maturity"], f"{row['Yield']:.2f}%")
                if not (rates.empty and not live_rates.empty):
                    render_dark_line_chart(live_curve.set_index("Maturity"), height=260)

            if rates.empty:
                st.info("Official FRED history is temporarily unavailable; showing market-implied Treasury data where available.")
                if not live_rates.empty:
                    if live_curve.empty:
                        st.markdown("**Recent Market-Implied Yield Moves**")
                        render_dark_line_chart(live_rates, height=300)
                    else:
                        live_chart_left, live_chart_right = st.columns([0.42, 0.58], gap="medium")
                        with live_chart_left:
                            st.markdown("**Live Curve**")
                            render_dark_line_chart(live_curve.set_index("Maturity"), height=300)
                        with live_chart_right:
                            st.markdown("**Recent Market-Implied Yield Moves**")
                            render_dark_line_chart(live_rates, height=300)
            else:
                latest_rates = rates.ffill().iloc[-1]
                prior_rates = rates.ffill().shift(21).iloc[-1]
                rate_changes = latest_rates - prior_rates

                rate_cols = st.columns(4)
                for column, rate_name in zip(
                    rate_cols,
                    ["SOFR", "Fed Funds", "2Y Treasury", "10Y Treasury"],
                ):
                    latest_value = latest_rates.get(rate_name, np.nan)
                    change_value = rate_changes.get(rate_name, np.nan)
                    column.metric(
                        rate_name,
                        "N/A" if pd.isna(latest_value) else f"{latest_value:.2f}%",
                        None if pd.isna(change_value) else f"{change_value:+.2f} pp vs 1M",
                    )

                curve_cols = st.columns(3)
                two_ten_spread = latest_rates.get("10Y Treasury", np.nan) - latest_rates.get(
                    "2Y Treasury",
                    np.nan,
                )
                three_month_ten_spread = latest_rates.get(
                    "10Y Treasury",
                    np.nan,
                ) - latest_rates.get("3M Treasury", np.nan)
                mortgage_treasury_spread = latest_rates.get(
                    "30Y Mortgage",
                    np.nan,
                ) - latest_rates.get("10Y Treasury", np.nan)
                curve_cols[0].metric(
                    "10Y - 2Y Spread",
                    "N/A" if pd.isna(two_ten_spread) else f"{two_ten_spread:.2f} pp",
                )
                curve_cols[1].metric(
                    "10Y - 3M Spread",
                    "N/A"
                    if pd.isna(three_month_ten_spread)
                    else f"{three_month_ten_spread:.2f} pp",
                )
                curve_cols[2].metric(
                    "Mortgage - 10Y Spread",
                    "N/A"
                    if pd.isna(mortgage_treasury_spread)
                    else f"{mortgage_treasury_spread:.2f} pp",
                )

                latest_curve = latest_rates[
                    ["3M Treasury", "2Y Treasury", "10Y Treasury", "30Y Treasury"]
                ].dropna()
                curve_points = pd.DataFrame(
                    {
                        "Maturity": latest_curve.index,
                        "Yield": latest_curve.values,
                    }
                )

                rate_chart_tab, official_curve_tab, live_curve_tab, rate_table_tab = st.tabs(
                    [
                        "Official Rate History",
                        "Official Yield Curve",
                        "Market-Implied Live Curve",
                        "Latest Levels",
                    ]
                )
                with rate_chart_tab:
                    render_dark_line_chart(rates, height=300)
                with official_curve_tab:
                    render_dark_line_chart(curve_points.set_index("Maturity"), height=280)
                with live_curve_tab:
                    if live_curve.empty:
                        st.warning("Market-implied Treasury yield data is temporarily unavailable.")
                    else:
                        live_cols = st.columns(min(4, len(live_curve)))
                        for column, (_, row) in zip(live_cols, live_curve.iterrows()):
                            column.metric(row["Maturity"], f"{row['Yield']:.2f}%")
                        render_dark_line_chart(live_curve.set_index("Maturity"), height=260)
                        if not live_rates.empty:
                            st.markdown("**Recent Market-Implied Yield Moves**")
                            render_dark_line_chart(live_rates, height=280)
                with rate_table_tab:
                    latest_table = pd.DataFrame(
                        {
                            "Latest": latest_rates,
                            "1M Change": rate_changes,
                        }
                    )
                    render_dark_table(latest_table.map(lambda value: f"{value:.2f}%"), height=260)
                    if not live_curve.empty:
                        st.markdown("**Market-Implied Latest Levels**")
                        render_dark_table(live_curve.set_index("Maturity").map(lambda value: f"{value:.2f}%"), height=210)

    with live_kline_tab:
        render_tab_safely("Live K-Line", lambda: render_live_kline(news_tickers))

    with universe_tab:
        render_tab_safely(
            "Instrument universe",
            lambda: render_equity_universe(
                news_tickers,
                classification_view,
                universe_search,
                max_universe_rows,
                region_filter,
                asset_class_filter,
            ),
        )

    with ratings_tab:
        rating_input = st.text_input(
            "Company tickers for credit rating proxy",
            value=", ".join(news_tickers),
            help="Enter listed company tickers such as AAPL, MSFT, JPM, SAP.DE.",
        )
        rating_tickers = parse_list(rating_input)
        render_credit_ratings(rating_tickers)

    with news_monitor_tab:
        news = fetch_news_for_tickers(news_tickers, news_items_per_ticker)

        if news.empty:
            st.warning("News feed is temporarily unavailable.")
        else:
            ticker_filter = st.multiselect(
                "Filter tickers",
                options=news_tickers,
                default=news_tickers,
            )
            filtered_news = news[news["Ticker"].isin(ticker_filter)] if ticker_filter else news

            st.metric("Headlines Loaded", len(filtered_news))

            for _, article in filtered_news.iterrows():
                headline = article["Headline"]
                source = article["Source"]
                published = article["Published"]
                ticker = article["Ticker"]
                link = article["Link"]
                st.markdown(
                    f"**{ticker}** | [{headline}]({link})  \n"
                    f"<span style='color:#64748b;font-size:0.82rem'>{source} · {published}</span>",
                    unsafe_allow_html=True,
                )
                st.divider()


if page == "Market Monitor":
    news_tickers = parse_list(news_tickers_input)
    if not news_tickers:
        news_tickers = ["SPY"]
    render_market_monitor(
        news_tickers,
        rate_history_years,
        news_items_per_ticker,
        classification_view,
        universe_search,
        max_universe_rows,
        region_filter,
        asset_class_filter,
    )
    st.stop()


if page == "Global Markets":
    render_global_markets(
        selected_countries,
        selected_fx_pairs,
        global_period,
        global_news_items,
        global_rate_history_years,
    )
    st.stop()


tickers = parse_list(tickers_input)

if not tickers:
    st.warning("Enter at least one ticker.")
    st.stop()

selected_benchmark_labels = st.session_state.get(
    "selected_benchmark_labels",
    ["S&P 500 ETF"],
)
custom_benchmarks_input = st.session_state.get("custom_benchmarks_input", "")

benchmark_tickers = [
    BENCHMARK_OPTIONS[label]
    for label in selected_benchmark_labels
    if label in BENCHMARK_OPTIONS
]
benchmark_tickers.extend(parse_list(custom_benchmarks_input))
benchmark_tickers = list(dict.fromkeys(benchmark_tickers))

if not benchmark_tickers:
    benchmark_tickers = ["SPY"]

primary_benchmark = benchmark_tickers[0]

weights, weight_error = parse_weights(weights_input, len(tickers))
if weight_error:
    st.error(weight_error)
    st.stop()

portfolio_value = st.session_state.get("rebalancing_portfolio_value", 1000000)

extra_market_tickers = list(
    dict.fromkeys(
        FACTOR_PROXY_TICKERS
        + CREDIT_PROXY_TICKERS
        + list(SECTOR_PROXY_TICKERS.values())
    )
)
prices, volumes = download_prices(tickers, benchmark_tickers, period, extra_market_tickers)

missing_tickers = [
    ticker for ticker in tickers + benchmark_tickers if ticker not in prices.columns
]
if missing_tickers:
    st.error(f"Missing price data for: {', '.join(missing_tickers)}")
    st.stop()

required_columns = list(dict.fromkeys(tickers + benchmark_tickers))
required_prices = prices[required_columns].dropna()
if required_prices.shape[0] < 30:
    st.error("Not enough historical price data to calculate reliable risk metrics.")
    st.stop()

returns = required_prices.pct_change(fill_method=None).dropna()
asset_returns = returns[tickers]
benchmark_returns_df = returns[benchmark_tickers]
benchmark_returns = benchmark_returns_df[primary_benchmark]
portfolio_returns = asset_returns.dot(weights)

all_returns = prices.pct_change(fill_method=None).dropna(how="all")
factor_returns = build_factor_returns(all_returns)

portfolio_cumulative = (1 + portfolio_returns).cumprod()
benchmark_cumulative = (1 + benchmark_returns).cumprod()
benchmark_cumulative_df = (1 + benchmark_returns_df).cumprod()
asset_cumulative = (1 + asset_returns).cumprod()

metrics, portfolio_drawdown = portfolio_metrics(
    portfolio_returns,
    benchmark_returns,
    risk_free_rate,
)

rolling_vol = portfolio_returns.rolling(20).std() * np.sqrt(TRADING_DAYS)
correlation_matrix = asset_returns.corr()

covariance_matrix = asset_returns.cov() * TRADING_DAYS
portfolio_variance = float(weights.T @ covariance_matrix.values @ weights)
marginal_risk = covariance_matrix.values @ weights
risk_contribution = weights * marginal_risk / portfolio_variance

weights_df = pd.DataFrame(
    {
        "Ticker": tickers,
        "Weight": weights,
        "Annualized Return": asset_returns.apply(annualized_return),
        "Annualized Volatility": asset_returns.std() * np.sqrt(TRADING_DAYS),
        "Risk Contribution": risk_contribution,
    }
).set_index("Ticker")

summary_limits = risk_limit_table(metrics)
summary_breaches = int((summary_limits["Status"] == "Breach").sum())
summary_status = "PASS" if summary_breaches == 0 else "REVIEW"
status_class = "status-pass" if summary_status == "PASS" else "status-review"
date_start = required_prices.index.min().date()
date_end = required_prices.index.max().date()
portfolio_label = " / ".join(tickers)

st.markdown(
    f"""
    <div class="terminal-header">
        <div class="terminal-title">Portfolio Dashboard</div>
        <div class="terminal-subtitle">
            Portfolio Dashboard: multi-asset risk, attribution, liquidity, credit, rate sensitivity and governance monitoring.
        </div>
        <div class="context-row">
            <span class="context-pill">Portfolio: {portfolio_label}</span>
            <span class="context-pill">Primary Benchmark: {primary_benchmark}</span>
            <span class="context-pill">Window: {date_start} to {date_end}</span>
            <span class="context-pill">Confidence: {confidence_level:.0%}</span>
            <span class="context-pill {status_class}">Limit Status: {summary_status}</span>
            <span class="context-pill">Data pulled: {data_timestamp()}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

section_title("Executive Summary", tight=True)

metric_cols = st.columns(5)
metric_cols[0].metric("Annualized Return", format_percent(metrics["Annualized Return"]))
metric_cols[1].metric(
    "Annualized Volatility",
    format_percent(metrics["Annualized Volatility"]),
)
metric_cols[2].metric("Sharpe Ratio", format_number(metrics["Sharpe Ratio"]))
metric_cols[3].metric("Max Drawdown", format_percent(metrics["Max Drawdown"]))
metric_cols[4].metric(
    f"Daily VaR {confidence_level:.0%}",
    format_percent(metrics["Daily VaR"]),
)

st.markdown(
    '<div class="module-caption">Core portfolio health indicators and the main work surface are kept in a dense analyst layout.</div>',
    unsafe_allow_html=True,
)

comparison_df = pd.DataFrame(
    {
        "Portfolio": portfolio_cumulative,
    }
)
for benchmark_ticker in benchmark_tickers:
    comparison_df[benchmark_ticker] = benchmark_cumulative_df[benchmark_ticker]

risk_metric_rows = []
percent_metrics = {
    "Annualized Return",
    "Annualized Volatility",
    "Max Drawdown",
    "Tracking Error",
    "Daily VaR",
    "Daily CVaR",
    "Parametric VaR",
    "Cornish-Fisher VaR",
}

for metric_name, metric_value in metrics.items():
    if metric_name in percent_metrics:
        display_value = format_percent(metric_value)
    else:
        display_value = format_number(metric_value)

    risk_metric_rows.append({"Metric": metric_name, "Value": display_value})

risk_metrics_df = pd.DataFrame(risk_metric_rows).set_index("Metric")
risk_metrics_df["Value"] = risk_metrics_df["Value"].astype(str)

section_title("Performance Surface")
benchmark_control_cols = st.columns([0.54, 0.46], gap="medium")
with benchmark_control_cols[0]:
    st.multiselect(
        "Benchmarks",
        options=list(BENCHMARK_OPTIONS.keys()),
        default=selected_benchmark_labels,
        key="selected_benchmark_labels",
        help="The first selected benchmark is used as the primary benchmark for beta, tracking error and information ratio.",
    )
with benchmark_control_cols[1]:
    st.text_input(
        "Custom benchmark tickers",
        value=custom_benchmarks_input,
        key="custom_benchmarks_input",
        help="Optional Yahoo Finance tickers, for example ^GDAXI, QQQ, AGG.",
    )

snapshot_tab, drawdown_tab, rolling_tab = st.tabs(
    ["Cumulative Return", "Drawdown", "Rolling Volatility"]
)

with snapshot_tab:
    render_dark_line_chart(comparison_df, height=310)

with drawdown_tab:
    render_dark_line_chart(portfolio_drawdown.rename("Portfolio Drawdown"), height=310)

with rolling_tab:
    render_dark_line_chart(rolling_vol.rename("Portfolio Rolling Volatility"), height=310)

section_title("Portfolio Diagnostics")
risk_table_tab, allocation_tab, performance_tab, correlation_tab = st.tabs(
    ["Risk", "Allocation", "Assets", "Correlation"]
)

with risk_table_tab:
    render_dark_table(risk_metrics_df, height=260)

with allocation_tab:
    allocation_left, allocation_right = st.columns([0.44, 0.56], gap="medium")
    display_weights = weights_df.copy()
    for column in display_weights.columns:
        display_weights[column] = display_weights[column].map(format_percent)
    with allocation_left:
        render_dark_table(display_weights, height=230)
    with allocation_right:
        render_dark_bar_chart(weights_df["Risk Contribution"], height=230)

with performance_tab:
    render_dark_line_chart(asset_cumulative, height=300)

with correlation_tab:
    render_dark_table(correlation_matrix.map(lambda value: f"{value:.2f}"), height=260)

section_title("Stress Test")
shock_values = []
stress_cols = st.columns(min(8, len(tickers)), gap="small")
for index, ticker in enumerate(tickers):
    preset_shock = scenario_shock_for_ticker(
        ticker,
        scenario_preset,
        default_shock / 100,
    )

    with stress_cols[index % len(stress_cols)]:
        shock_pct = st.slider(
            ticker,
            min_value=-80,
            max_value=50,
            value=int(round(preset_shock * 100)),
            step=1,
            format="%d%%",
            key=f"stress_shock_{scenario_preset}_{ticker}",
            label_visibility="collapsed",
        )
        st.markdown(
            f"<div style='color:#caa6ad;font-size:0.72rem;font-weight:700;margin-top:0.12rem;margin-bottom:0.18rem'>{ticker} shock</div>",
            unsafe_allow_html=True,
        )
        shock_values.append(shock_pct / 100)

stress_return = float(np.dot(weights, np.array(shock_values)))
stress_loss = -stress_return if stress_return < 0 else 0

stress_metric_cols = st.columns(3, gap="small")
stress_metric_cols[0].metric(
    "Portfolio Stress Return",
    format_percent(stress_return),
)
stress_metric_cols[1].metric("Stress Loss", format_percent(stress_loss))
stress_metric_cols[2].metric("Scenario", scenario_preset)

stress_df = pd.DataFrame(
    {
        "Ticker": tickers,
        "Weight": weights,
        "Shock": shock_values,
        "Contribution": weights * np.array(shock_values),
    }
).set_index("Ticker")

for column in stress_df.columns:
    stress_df[column] = stress_df[column].map(format_percent)
render_dark_table(stress_df, height=210)

section_title("Analysis Workbench")
st.markdown(
    '<div class="module-caption">Modules are grouped by workflow: attribution and construction, market exposures, simulation models, and governance controls.</div>',
    unsafe_allow_html=True,
)

portfolio_group, market_group, simulation_group, governance_group = st.tabs(
    [
        "Portfolio Construction",
        "Market, Credit & Liquidity",
        "Simulation & Factors",
        "Governance & Tail Risk",
    ]
)

with portfolio_group:
    attribution_tab, rebalancing_tab, frontier_tab = st.tabs(
        ["Attribution", "Rebalancing", "Optimization"]
    )

with market_group:
    rates_tab, credit_tab, liquidity_tab = st.tabs(
        ["Rate Risk", "Credit Risk", "Liquidity Risk"]
    )

with simulation_group:
    mc_tab, factor_tab, volatility_tab = st.tabs(
        ["Monte Carlo", "Factor Exposure", "Volatility Forecast"]
    )

with governance_group:
    limits_tab, tail_tab, var_tab = st.tabs(
        ["Risk Limits", "Tail Risk Budget", "VaR Backtest"]
    )

with attribution_tab:
    attribution, attribution_summary = performance_attribution(
        asset_returns,
        benchmark_returns,
        weights,
    )

    attribution_cols = st.columns(3)
    attribution_cols[0].metric(
        "Portfolio Total Return",
        format_percent(attribution_summary["Portfolio Total Return"]),
    )
    attribution_cols[1].metric(
        "Benchmark Total Return",
        format_percent(attribution_summary["Benchmark Total Return"]),
    )
    attribution_cols[2].metric(
        "Active Return",
        format_percent(attribution_summary["Active Return"]),
    )

    display_attribution = attribution.copy()
    for column in display_attribution.columns:
        display_attribution[column] = display_attribution[column].map(format_percent)

    attribution_left, attribution_right = st.columns([0.68, 0.32], gap="medium")
    with attribution_left:
        render_dark_table(display_attribution, height=270)
    with attribution_right:
        render_dark_bar_chart(attribution["Contribution to Return"], height=170, compact=True)

    brinson = brinson_attribution(asset_returns, all_returns, tickers, weights)
    if not brinson.empty:
        st.markdown("**Brinson Attribution (Proxy-Based)**")
        brinson_display = brinson.copy()
        percent_columns = [
            "Portfolio Weight",
            "Benchmark Weight",
            "Portfolio Sector Return",
            "Benchmark Sector Return",
            "Allocation Effect",
            "Selection Effect",
            "Interaction Effect",
            "Total Effect",
        ]
        for column in percent_columns:
            brinson_display[column] = brinson_display[column].map(format_percent)
        brinson_left, brinson_right = st.columns([0.64, 0.36], gap="medium")
        with brinson_left:
            render_dark_table(brinson_display, height=285)
        with brinson_right:
            render_dark_grouped_bar_chart(
                brinson[["Allocation Effect", "Selection Effect", "Interaction Effect"]],
                height=220,
                compact=True,
            )

with rates_tab:
    rate_vol_bps = latest_rate_vol_bps()
    rate_risk, rate_risk_return = fixed_income_rate_risk(
        tickers,
        weights,
        rate_shock_bps,
        portfolio_value,
        rate_vol_bps,
        confidence_level,
    )

    rate_cols = st.columns(4)
    rate_cols[0].metric("Rate Shock", f"{rate_shock_bps} bps")
    rate_cols[1].metric(
        "Estimated Portfolio Impact",
        format_percent(rate_risk_return),
    )
    rate_cols[2].metric(
        "Duration-Weighted Exposure",
        format_number((rate_risk["Weight"] * rate_risk["Duration Proxy"]).sum()),
    )
    rate_cols[3].metric("10Y Rate Vol", f"{rate_vol_bps:.1f} bps/day")

    display_rate_risk = rate_risk.copy()
    for column in ["Weight", "Rate Shock Return", "Portfolio Contribution"]:
        display_rate_risk[column] = display_rate_risk[column].map(format_percent)
    for column in ["Position Value", "DV01", "Delta-Normal Rate VaR"]:
        display_rate_risk[column] = display_rate_risk[column].map(
            lambda value: f"${value:,.0f}"
        )
    display_rate_risk["Duration Proxy"] = display_rate_risk["Duration Proxy"].map(
        format_number
    )
    render_dark_table(display_rate_risk, height=280)

with credit_tab:
    credit_summary, credit_stress = credit_risk_summary(all_returns, portfolio_returns)

    st.markdown("**Issuer Credit Rating Proxy**")
    render_credit_ratings(tickers)

    if credit_summary is None:
        st.warning("Credit proxy data is unavailable for the selected period.")
    else:
        display_credit_summary = credit_summary.copy()
        display_credit_summary["Credit Beta"] = display_credit_summary[
            "Credit Beta"
        ].map(format_number)
        display_credit_summary["Correlation"] = display_credit_summary[
            "Correlation"
        ].map(format_number)
        display_credit_summary["Factor Volatility"] = display_credit_summary[
            "Factor Volatility"
        ].map(format_percent)

        render_dark_table(display_credit_summary, height=210)
        render_dark_table(credit_stress.map(format_percent), height=180)

with liquidity_tab:
    liquidity = liquidity_risk_table(
        tickers,
        weights,
        prices,
        volumes,
        portfolio_value,
    )

    if liquidity.empty:
        st.warning("Volume data is unavailable, so liquidity risk cannot be calculated.")
    else:
        liquidity_cols = st.columns(3)
        liquidity_cols[0].metric(
            "Max Days to Liquidate",
            format_number(liquidity["Days to Liquidate"].max()),
        )
        liquidity_cols[1].metric(
            "Median Days to Liquidate",
            format_number(liquidity["Days to Liquidate"].median()),
        )
        liquidity_cols[2].metric(
            "Worst Liquidity Adjusted VaR",
            format_percent(liquidity["Liquidity Adjusted VaR"].max()),
        )

        display_liquidity = liquidity.copy()
        display_liquidity["Position Value"] = display_liquidity["Position Value"].map(
            lambda value: f"${value:,.0f}"
        )
        display_liquidity["Avg Dollar Volume"] = display_liquidity[
            "Avg Dollar Volume"
        ].map(lambda value: "N/A" if pd.isna(value) else f"${value:,.0f}")
        display_liquidity["Days to Liquidate"] = display_liquidity[
            "Days to Liquidate"
        ].map(format_number)
        display_liquidity["Liquidity Adjusted VaR"] = display_liquidity[
            "Liquidity Adjusted VaR"
        ].map(format_percent)

        render_dark_table(display_liquidity, height=260)

with rebalancing_tab:
    rebalance_control_cols = st.columns([0.45, 0.32, 0.23], gap="medium")
    with rebalance_control_cols[0]:
        target_weights_input = st.text_input(
            "Target weights",
            value=weights_input,
            help="Optional target weights for rebalancing. Leave aligned with tickers.",
            key="rebalancing_target_weights",
        )
    with rebalance_control_cols[1]:
        portfolio_value = st.number_input(
            "Portfolio value",
            min_value=1000,
            max_value=100000000,
            value=int(st.session_state.get("rebalancing_portfolio_value", 1000000)),
            step=10000,
            key="rebalancing_portfolio_value",
        )
    with rebalance_control_cols[2]:
        transaction_cost_bps = st.slider(
            "Transaction cost",
            min_value=0,
            max_value=100,
            value=int(st.session_state.get("rebalancing_transaction_cost_bps", 10)),
            step=1,
            format="%d bps",
            key="rebalancing_transaction_cost_bps",
        )

    target_weights, target_weight_error = parse_weights(target_weights_input, len(tickers))
    if target_weight_error:
        st.error(f"Target weights error: {target_weight_error}")
    else:
        rebalancing, rebalancing_summary = rebalancing_table(
            tickers,
            weights,
            target_weights,
            portfolio_value,
            transaction_cost_bps,
        )

        rebalance_cols = st.columns(3)
        rebalance_cols[0].metric(
            "One-Way Turnover",
            format_percent(rebalancing_summary["One-Way Turnover"]),
        )
        rebalance_cols[1].metric(
            "Estimated Transaction Cost",
            f"${rebalancing_summary['Estimated Transaction Cost']:,.0f}",
        )
        rebalance_cols[2].metric("Portfolio Value", f"${portfolio_value:,.0f}")

        display_rebalancing = rebalancing.copy()
        for column in ["Current Weight", "Target Weight", "Trade Weight"]:
            display_rebalancing[column] = display_rebalancing[column].map(format_percent)
        display_rebalancing["Trade Value"] = display_rebalancing["Trade Value"].map(
            lambda value: f"${value:,.0f}"
        )
        render_dark_table(display_rebalancing, height=260)

with mc_tab:
    mc_percentiles, mc_terminal_returns = run_monte_carlo(
        portfolio_returns,
        forecast_horizon,
        monte_carlo_paths,
    )

    mc_cols = st.columns(4)
    mc_cols[0].metric(
        "Median Terminal Return",
        format_percent(mc_terminal_returns.quantile(0.50)),
    )
    mc_cols[1].metric(
        "5th Percentile Terminal Return",
        format_percent(mc_terminal_returns.quantile(0.05)),
    )
    mc_cols[2].metric(
        "Probability of Loss",
        format_percent((mc_terminal_returns < 0).mean()),
    )
    mc_cols[3].metric(
        "Expected Shortfall",
        format_percent(mc_terminal_returns[mc_terminal_returns <= mc_terminal_returns.quantile(0.05)].mean()),
    )

    render_dark_line_chart(mc_percentiles, height=280)

with frontier_tab:
    frontier, best_sharpe_weights, min_vol_weights = random_portfolio_frontier(
        asset_returns,
        risk_free_rate,
        frontier_portfolios,
    )

    current_point = pd.DataFrame(
        {
            "Portfolio": ["Current"],
            "Annualized Return": [metrics["Annualized Return"]],
            "Annualized Volatility": [metrics["Annualized Volatility"]],
            "Sharpe Ratio": [metrics["Sharpe Ratio"]],
        }
    )

    frontier_display = frontier.copy()
    frontier_display["Portfolio"] = "Random Portfolio"
    chart_data = pd.concat([frontier_display, current_point], ignore_index=True)

    render_dark_scatter_chart(
        chart_data,
        "Annualized Volatility",
        "Annualized Return",
        "Sharpe Ratio",
        height=300,
    )

    opt_cols = st.columns(2)
    with opt_cols[0]:
        st.markdown("**Max Sharpe Portfolio**")
        best_sharpe_df = best_sharpe_weights.to_frame("Weight")
        best_sharpe_df["Weight"] = best_sharpe_df["Weight"].map(format_percent)
        render_dark_table(best_sharpe_df, height=230)

    with opt_cols[1]:
        st.markdown("**Minimum Volatility Portfolio**")
        min_vol_df = min_vol_weights.to_frame("Weight")
        min_vol_df["Weight"] = min_vol_df["Weight"].map(format_percent)
        render_dark_table(min_vol_df, height=230)

with factor_tab:
    if factor_returns.empty:
        st.warning("Factor proxy data is unavailable for the selected period.")
    else:
        factor_loadings, factor_diagnostics = factor_regression(
            portfolio_returns,
            factor_returns,
        )

        if factor_loadings is None:
            st.warning("Not enough aligned observations to estimate factor exposure.")
        else:
            factor_cols = st.columns(3)
            factor_cols[0].metric(
                "Factor R-Squared",
                format_percent(factor_diagnostics["R-Squared"]),
            )
            factor_cols[1].metric(
                "Annualized Alpha",
                format_percent(factor_diagnostics["Annualized Alpha"]),
            )
            factor_cols[2].metric(
                "Residual Volatility",
                format_percent(factor_diagnostics["Residual Volatility"]),
            )

            display_factor_loadings = pd.DataFrame(
                {
                    "Factor": factor_loadings.index,
                    "Exposure": [
                        format_percent(value) if factor == "Alpha" else format_number(value)
                        for factor, value in factor_loadings["Exposure"].items()
                    ],
                }
            ).set_index("Factor")

            render_dark_table(display_factor_loadings, height=210)

            rolling_beta_window = min(63, max(21, len(portfolio_returns) // 4))
            rolling_market_beta = (
                portfolio_returns.rolling(rolling_beta_window).cov(factor_returns["Market"])
                / factor_returns["Market"].rolling(rolling_beta_window).var()
            )
            render_dark_line_chart(rolling_market_beta.rename("Rolling Market Beta"), height=260)

            factor_return_summary = pd.DataFrame(
                {
                    "Annualized Return": factor_returns.apply(annualized_return),
                    "Annualized Volatility": factor_returns.std() * np.sqrt(TRADING_DAYS),
                    "Correlation with Portfolio": factor_returns.corrwith(portfolio_returns),
                }
            )
            render_dark_table(factor_return_summary.map(format_percent), height=220)

with volatility_tab:
    garch_result = estimate_garch_11(portfolio_returns)
    ewma_daily_vol = ewma_volatility(portfolio_returns)
    historical_daily_vol = portfolio_returns.std()

    if garch_result is None:
        st.warning("Not enough observations to estimate GARCH(1,1).")
    else:
        vol_cols = st.columns(4)
        vol_cols[0].metric(
            "GARCH Daily Vol",
            format_percent(garch_result["Forecast Daily Volatility"]),
        )
        vol_cols[1].metric(
            "GARCH Annualized Vol",
            format_percent(garch_result["Forecast Annualized Volatility"]),
        )
        vol_cols[2].metric("Persistence", format_number(garch_result["Persistence"]))
        vol_cols[3].metric("EWMA Daily Vol", format_percent(ewma_daily_vol))

        forecast_table = pd.DataFrame(
            {
                "Model": ["Historical", "EWMA(0.94)", "GARCH(1,1)"],
                "Daily Volatility": [
                    historical_daily_vol,
                    ewma_daily_vol,
                    garch_result["Forecast Daily Volatility"],
                ],
                "Annualized Volatility": [
                    historical_daily_vol * np.sqrt(TRADING_DAYS),
                    ewma_daily_vol * np.sqrt(TRADING_DAYS),
                    garch_result["Forecast Annualized Volatility"],
                ],
            }
        ).set_index("Model")
        render_dark_table(forecast_table.map(format_percent), height=170)

        parameter_table = pd.DataFrame(
            {
                "Parameter": ["Omega", "Alpha", "Beta", "Alpha + Beta"],
                "Estimate": [
                    garch_result["Omega"],
                    garch_result["Alpha"],
                    garch_result["Beta"],
                    garch_result["Persistence"],
                ],
            }
        ).set_index("Parameter")
        render_dark_table(parameter_table.map(lambda value: f"{value:.4f}"), height=170)

with tail_tab:
    component_var = component_var_table(
        asset_returns,
        weights,
        confidence_level,
    )
    worst_days = portfolio_returns.nsmallest(10).to_frame("Portfolio Return")
    worst_days["Benchmark Return"] = benchmark_returns.loc[worst_days.index]

    tail_cols = st.columns(4)
    tail_cols[0].metric("Worst Daily Return", format_percent(portfolio_returns.min()))
    tail_cols[1].metric("Daily Skewness", format_number(portfolio_returns.skew()))
    tail_cols[2].metric(
        "Excess Kurtosis",
        format_number(portfolio_returns.kurtosis()),
    )
    tail_cols[3].metric(
        "Positive Return Hit Rate",
        format_percent((portfolio_returns > 0).mean()),
    )

    var_comparison = pd.DataFrame(
        {
            "Model": ["Historical", "Parametric Normal", "Cornish-Fisher", "Expected Shortfall"],
            "Daily Risk Estimate": [
                metrics["Daily VaR"],
                metrics["Parametric VaR"],
                metrics["Cornish-Fisher VaR"],
                metrics["Daily CVaR"],
            ],
        }
    ).set_index("Model")
    st.markdown("**VaR Model Comparison**")
    render_dark_table(var_comparison.map(format_percent), height=170)

    if component_var.empty:
        st.warning("Component VaR cannot be calculated because portfolio variance is zero.")
    else:
        display_component_var = component_var.copy()
        for column in display_component_var.columns:
            display_component_var[column] = display_component_var[column].map(format_percent)

        st.markdown("**Parametric Component VaR**")
        render_dark_table(display_component_var, height=210)
        render_dark_bar_chart(component_var["VaR Contribution"], height=210)

    st.markdown("**Worst Portfolio Return Days**")
    render_dark_table(worst_days.map(format_percent), height=210)

    drawdown_events = drawdown_event_table(portfolio_drawdown)
    st.markdown("**Largest Drawdown Events**")
    if drawdown_events.empty:
        st.info("No drawdown events detected for the selected period.")
    else:
        drawdown_events_display = drawdown_events.copy()
        drawdown_events_display["Max Drawdown"] = drawdown_events_display[
            "Max Drawdown"
        ].map(format_percent)
        render_dark_table(drawdown_events_display, height=210)

with limits_tab:
    limits = risk_limit_table(metrics)
    breach_count = int((limits["Status"] == "Breach").sum())
    status_text = "PASS" if breach_count == 0 else "REVIEW"

    rolling_window = min(63, max(21, len(portfolio_returns) // 4))
    rolling_risk_df = pd.DataFrame(
        {
            "Rolling Volatility": portfolio_returns.rolling(rolling_window).std()
            * np.sqrt(TRADING_DAYS),
            "Rolling Sharpe": rolling_sharpe_ratio(
                portfolio_returns,
                rolling_window,
                risk_free_rate,
            ),
            "Rolling VaR": portfolio_returns.rolling(rolling_window).apply(
                lambda values: value_at_risk(pd.Series(values), confidence_level),
                raw=False,
            ),
        }
    )

    limits_left, limits_right = st.columns([0.44, 0.56], gap="medium")
    with limits_left:
        limits_cols = st.columns(2, gap="small")
        limits_cols[0].metric("Limit Status", status_text)
        limits_cols[1].metric("Breaches", breach_count)
        limits_cols[0].metric("Rolling Window", "63D")
        limits_cols[1].metric("Largest Weight", format_percent(weights.max()))
        render_dark_table(limits, height=252)

    with limits_right:
        st.markdown("**Rolling Risk Monitor**")
        render_dark_line_chart(rolling_risk_df, height=310)

with var_tab:
    var_level = value_at_risk(portfolio_returns, confidence_level)
    var_breaches = portfolio_returns < -var_level
    expected_breaches = len(portfolio_returns) * (1 - confidence_level)
    realized_breaches = int(var_breaches.sum())
    breach_ratio = np.nan if expected_breaches == 0 else realized_breaches / expected_breaches
    kupiec = kupiec_test(portfolio_returns, var_level, confidence_level)
    basel_zone = basel_traffic_light(len(portfolio_returns), realized_breaches, confidence_level)

    var_cols = st.columns(6)
    var_cols[0].metric(f"Historical VaR {confidence_level:.0%}", format_percent(var_level))
    var_cols[1].metric("Realized Breaches", realized_breaches)
    var_cols[2].metric("Expected Breaches", format_number(expected_breaches))
    var_cols[3].metric("Breach Ratio", format_number(breach_ratio))
    var_cols[4].metric("Kupiec p-value", format_number(kupiec["P-Value"]))
    with var_cols[5]:
        render_status_metric("Basel Zone", basel_zone)

    var_backtest_df = pd.DataFrame(
        {
            "Portfolio Return": portfolio_returns,
            "VaR Threshold": -var_level,
            "Breach": var_breaches.astype(int),
        }
    )
    render_dark_line_chart(var_backtest_df[["Portfolio Return", "VaR Threshold"]], height=280)

    kupiec_table = pd.DataFrame(
        {
            "Metric": [
                "Observations",
                "Breaches",
                "Expected Breaches",
                "Observed Breach Rate",
                "LR Statistic",
                "P-Value",
                "Basel Traffic Light",
            ],
            "Value": [
                len(portfolio_returns),
                kupiec["Breaches"],
                format_number(kupiec["Expected Breaches"]),
                format_percent(kupiec["Observed Breach Rate"]),
                format_number(kupiec["LR"]),
                format_number(kupiec["P-Value"]),
                basel_zone,
            ],
        }
    ).set_index("Metric")
    kupiec_table["Value"] = kupiec_table["Value"].astype(str)
    kupiec_table.loc["Basel Traffic Light", "Value"] = status_badge(basel_zone)
    st.markdown("**Kupiec POF Test / Basel Backtesting**")
    backtest_left, backtest_right = st.columns([0.38, 0.62], gap="medium")
    with backtest_left:
        render_dark_table(kupiec_table, height=250, escape=False)
    with backtest_right:
        backtest_tail = var_backtest_df.tail(20).copy()
        backtest_tail["Portfolio Return"] = backtest_tail["Portfolio Return"].map(format_percent)
        backtest_tail["VaR Threshold"] = backtest_tail["VaR Threshold"].map(format_percent)
        render_dark_table(backtest_tail, height=250)
