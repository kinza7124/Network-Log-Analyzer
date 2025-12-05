



import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
import pickle
import numpy as np
import os
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from dotenv import load_dotenv
import threading
import random
import re
import html



# Load environment variables - try .env first, then env_template.txt as fallback
if not load_dotenv():
    # If .env doesn't exist, try loading from env_template.txt
    if Path('env_template.txt').exists():
        load_dotenv('env_template.txt')



# Import model classes
from train_model import GHF_ART_Optimized
from claude_chatbot import ClaudeSecurityChatbot



# Page config
st.set_page_config(
    page_title="Network Security SOC Dashboard",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="expanded"
)
# ==========================================
# ENHANCED THEME SYSTEM WITH TOGGLE
# ==========================================

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark mode

# Theme toggle in sidebar
st.sidebar.title("🔧 Control Panel")
st.sidebar.markdown("---")

# Theme selector at the top of sidebar
theme_options = {
    "🌙 Dark Mode": "dark",
    "☀️ Light Mode": "light",
    "🌓 Auto": "auto"
}

current_theme_label = [k for k, v in theme_options.items() if v == st.session_state.theme][0]
new_theme_label = st.sidebar.radio("Theme", list(theme_options.keys()), 
                                   index=list(theme_options.keys()).index(current_theme_label),
                                   key="theme_selector",
                                   help="Switch between dark and light themes")

if theme_options[new_theme_label] != st.session_state.theme:
    st.session_state.theme = theme_options[new_theme_label]
    st.rerun()

st.sidebar.markdown("---")
# ==========================================
# DYNAMIC CSS BASED ON SELECTED THEME
# ==========================================

def get_theme_css(theme):
    """Return CSS based on selected theme"""
    
    if theme == 'light':
        return """
        <style>
            /* GLOBAL LIGHT THEME VARIABLES - HIGH CONTRAST */
            :root {
                --primary-color: #0066cc;        /* Professional Blue */
                --primary-hover: #0052a3;
                --background-color: #ffffff;     /* White */
                --secondary-bg: #f8f9fa;         /* Light Gray Cards */
                --card-border: #d1d5db;          /* Medium Gray Border */
                --text-primary: #111827;         /* Near Black - HIGH CONTRAST */
                --text-secondary: #374151;       /* Dark Gray */
                --text-muted: #6b7280;           /* Medium Gray */
                --accent-glow: rgba(0, 102, 204, 0.15);
                --sidebar-bg: #f3f4f6;           /* Light Gray */
                --sidebar-text: #111827;         /* Near Black */
                
                /* Severity Colors (Professional for Light Mode) */
                --sev-critical: #dc2626;         /* Darker Red */
                --sev-high: #ea580c;             /* Darker Orange */
                --sev-medium: #ca8a04;           /* Darker Yellow */
                --sev-low: #0284c7;              /* Darker Blue */
                --sev-normal: #059669;           /* Darker Green */
                
                /* Chart Colors */
                --chart-grid: #e5e7eb;
                --chart-text: #374151;
            }

            /* Main App Background */
            .stApp {
                background-color: var(--background-color);
                color: var(--text-primary);
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
            }

            /* Main Header Styling */
            .main-header-container {
                background: linear-gradient(135deg, rgba(0, 102, 204, 0.15) 0%, rgba(0, 102, 204, 0.05) 100%);
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                border-left: 6px solid var(--primary-color);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            
            .main-header {
                font-family: 'Segoe UI', sans-serif;
                font-size: 3.2rem;
                font-weight: 800;
                background: linear-gradient(90deg, #0066cc 0%, #0099ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
                letter-spacing: 0.5px;
                line-height: 1.2;
            }
            
            .header-subtitle {
                font-size: 1.2rem;
                color: var(--text-secondary);
                margin-top: 0.5rem;
                font-weight: 500;
            }

            /* Subheaders - HIGH CONTRAST */
            .stSubheader, .st-emotion-cache-16txtl3 {
                color: var(--text-primary) !important;
                font-weight: 700 !important;
                border-left: 4px solid var(--primary-color);
                padding-left: 12px;
                margin-top: 1.5rem !important;
                background: rgba(0, 102, 204, 0.05);
                padding: 12px 15px;
                border-radius: 0 8px 8px 0;
            }

            /* Metric Cards */
            div[data-testid="stMetric"] {
                background-color: var(--secondary-bg);
                border: 1px solid var(--card-border);
                border-radius: 10px;
                padding: 20px 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            div[data-testid="stMetric"]:hover {
                border-color: var(--primary-color);
                box-shadow: 0 8px 24px rgba(0, 102, 204, 0.15);
                transform: translateY(-2px);
            }
            
            [data-testid="stMetricValue"] {
                font-size: 2.5rem !important;
                font-weight: 800 !important;
                color: var(--primary-color) !important;
                line-height: 1.2;
            }
            
            [data-testid="stMetricLabel"] {
                color: var(--text-secondary) !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                margin-top: 5px !important;
            }

            /* Sidebar Styling */
            section[data-testid="stSidebar"] {
                background-color: var(--sidebar-bg) !important;
                border-right: 1px solid var(--card-border);
            }
            
            section[data-testid="stSidebar"] *,
            section[data-testid="stSidebar"] .st-emotion-cache-16txtl3,
            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3,
            section[data-testid="stSidebar"] h4,
            section[data-testid="stSidebar"] h5,
            section[data-testid="stSidebar"] h6,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] div,
            section[data-testid="stSidebar"] label {
                color: var(--sidebar-text) !important;
                font-weight: 500;
            }

            /* MAIN CONTENT RADIO BUTTONS - LIGHT MODE */
            .stRadio > div > label,
            .stCheckbox > label {
                color: var(--text-primary) !important;
                font-weight: 500;
            }
            
            .stRadio [role="radiogroup"] label {
                color: var(--text-primary) !important;
                font-weight: 500 !important;
            }
            
            /* Selected radio button */
            .stRadio [role="radiogroup"] [data-testid="stRadio"] > div:has(input:checked) label {
                color: var(--primary-color) !important;
                font-weight: 600 !important;
            }

            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 10px 24px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0, 102, 204, 0.3);
            }

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                background-color: var(--secondary-bg);
                border-radius: 8px;
                padding: 4px;
                border: 1px solid var(--card-border);
                gap: 4px;
            }
            
            .stTabs [data-baseweb="tab"] {
                color: var(--text-secondary);
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
                transition: all 0.2s ease;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: var(--primary-color) !important;
                color: white !important;
                font-weight: 600;
            }

            /* Plotly Charts */
            [data-testid="stPlotlyChart"] {
                background-color: var(--secondary-bg);
                border-radius: 10px;
                border: 1px solid var(--card-border);
                padding: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }

            /* Alert Boxes */
            .alert-box {
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
                background-color: var(--secondary-bg);
                border-left: 5px solid;
                border: 1px solid var(--card-border);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            
            .critical { 
                border-left-color: var(--sev-critical); 
                background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
            }
            
            .high { 
                border-left-color: var(--sev-high); 
                background: linear-gradient(135deg, rgba(234, 88, 12, 0.1) 0%, rgba(234, 88, 12, 0.05) 100%);
            }

            /* Input Fields - Light Mode */
            .stTextInput > div > div > input, 
            .stNumberInput > div > div > input,
            .stTextArea > div > div > textarea {
                background-color: var(--secondary-bg);
                color: var(--text-primary);
                border: 2px solid var(--card-border);
                border-radius: 8px;
                padding: 10px;
                font-weight: 500;
            }
            
            .stTextInput > div > div > input:focus,
            .stNumberInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.2);
                outline: none;
            }

            /* Expander */
            .streamlit-expanderHeader {
                background-color: var(--secondary-bg);
                color: var(--text-primary);
                border-radius: 8px;
                border: 1px solid var(--card-border);
                font-weight: 600;
                padding: 12px;
            }

            /* Dataframes */
            .dataframe {
                background-color: var(--secondary-bg) !important;
                color: var(--text-primary) !important;
                border: 1px solid var(--card-border) !important;
            }
            
            .dataframe th {
                background-color: rgba(0, 102, 204, 0.1) !important;
                color: var(--text-primary) !important;
                font-weight: 700 !important;
            }

            /* Success/Error Messages */
            .stAlert {
                border-radius: 8px !important;
                border-left: 5px solid !important;
            }
            
            .stAlert p {
                color: var(--text-primary) !important;
                font-weight: 500;
            }

            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--secondary-bg);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--text-muted);
                border-radius: 4px;
            }

            /* Ensure all text is visible */
            .stApp *:not([data-testid="stMetricValue"]):not(.stTabs [aria-selected="true"]):not(.stButton > button) {
                color: var(--text-primary) !important;
            }
        </style>
        """
    else:  # DARK THEME - AGGRESSIVE FIX FOR INPUT FIELDS
        return """
        <style>
            /* GLOBAL DARK THEME VARIABLES */
            :root {
                --primary-color: #00ff9d;
                --primary-hover: #00cc7a;
                --background-color: #0a0e17;
                --card-bg: #1a1f2e;
                --card-border: rgba(255, 255, 255, 0.1);
                --text-primary: #ffffff;
                --text-secondary: #e0e0e0;
                --text-muted: #8a95a6;
                --input-bg: #1a1f2e;
                --input-border: rgba(255, 255, 255, 0.2);
                --input-text: #ffffff;
                --sidebar-bg: rgba(17, 24, 39, 0.98);
                --sidebar-text: #ffffff;
                --sev-critical: #ff4757;
                --sev-high: #ffa502;
                --sev-medium: #ffd32a;
                --sev-low: #0fbcf9;
                --sev-normal: #00ff9d;
                --transparent-blue: rgba(0, 100, 255, 0.1);
            }

            /* ========================================== */
            /* AGGRESSIVE INPUT FIELD FIXES - DARK MODE */
            /* ========================================== */
            
            /* FORCE ALL INPUT FIELDS TO DARK BACKGROUND AND WHITE TEXT */
            input[type="text"],
            input[type="number"],
            input[type="password"],
            input[type="email"],
            input[type="tel"],
            input[type="url"],
            input[type="search"],
            input[type="date"],
            input[type="time"],
            input[type="datetime-local"],
            textarea,
            select {
                background-color: var(--input-bg) !important;
                color: var(--input-text) !important;
                border: 2px solid var(--input-border) !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
                font-size: 1rem !important;
                font-weight: 500 !important;
                caret-color: var(--primary-color) !important;
            }
            
            /* Specific Streamlit input selectors */
            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input,
            [data-testid="stTextArea"] textarea {
                background-color: var(--input-bg) !important;
                color: var(--input-text) !important;
                border: 2px solid var(--input-border) !important;
                border-radius: 8px !important;
                padding: 12px 16px !important;
                font-size: 1rem !important;
                font-weight: 500 !important;
                caret-color: var(--primary-color) !important;
            }
            
            /* Focus states */
            input:focus,
            textarea:focus,
            select:focus,
            .stTextInput input:focus,
            .stNumberInput input:focus,
            .stTextArea textarea:focus {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(0, 255, 157, 0.2) !important;
                outline: none !important;
                background-color: #222836 !important;
            }
            
            /* Placeholder text */
            input::placeholder,
            textarea::placeholder {
                color: var(--text-muted) !important;
                opacity: 0.8 !important;
            }
            
            /* Input labels */
            .stTextInput label,
            .stNumberInput label,
            .stTextArea label,
            .stSelectbox label,
            [data-testid="stTextInput"] label,
            [data-testid="stNumberInput"] label,
            [data-testid="stTextArea"] label {
                color: var(--text-primary) !important;
                font-weight: 600 !important;
                margin-bottom: 8px !important;
                display: block !important;
                font-size: 1rem !important;
            }
            
            /* ========================================== */
            /* MAIN APP BACKGROUND */
            /* ========================================== */
            .stApp {
                background-color: var(--background-color) !important;
                color: var(--text-primary) !important;
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
                line-height: 1.6;
            }
            
            /* Force all text in app to be white */
            .stApp,
            .stApp *,
            .stApp p,
            .stApp div,
            .stApp span,
            .stApp h1,
            .stApp h2,
            .stApp h3,
            .stApp h4,
            .stApp h5,
            .stApp h6 {
                color: var(--text-primary) !important;
            }

            .stApp p,
            .stApp div,
            .stApp span ,
            .stApp *{
            color: var(#black) !important;
            }
            /* Exceptions for colored elements */
            [data-testid="stMetricValue"] {
                color: var(--primary-color) !important;
            }
  
        /* ========================================== */
        /* HEADER STYLING - WHITE TEXT */
        /* ========================================== */
        .main-header-container {
            background: linear-gradient(135deg, 
                rgba(0, 255, 157, 0.15) 0%, 
                rgba(0, 204, 255, 0.1) 50%,
                rgba(0, 255, 157, 0.05) 100%);
            padding: 2.5rem;
            border-radius: 15px;
            margin-bottom: 2.5rem;
            border-left: 8px solid var(--primary-color);
            box-shadow: 0 8px 32px rgba(0, 255, 157, 0.15);
            text-align: center;
        }
        
        .main-header {
            font-family: 'Segoe UI', 'Courier New', monospace;
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(90deg, #00ff9d 0%, #00ccff 50%, #00ff9d 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            text-shadow: 0 0 40px rgba(0, 255, 157, 0.5);
            letter-spacing: 1.5px;
            line-height: 1.2;
            background-size: 200% auto;
            animation: shimmer 3s infinite linear;
        }
        
        @keyframes shimmer {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }
        
            
            .header-subtitle {
                font-size: 1.3rem;
                color: var(--text-secondary) !important;
                margin-top: 0.8rem;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            
            /* ========================================== */
            /* SUBHEADERS */
            /* ========================================== */
            .stSubheader, .st-emotion-cache-16txtl3 {
                color: var(--text-primary) !important;
                font-weight: 700 !important;
                border-left: 4px solid var(--primary-color);
                padding-left: 15px;
                margin-top: 2rem !important;
                background: rgba(26, 31, 46, 0.5);
                padding: 12px 15px;
                border-radius: 0 8px 8px 0;
            }
            
            /* ========================================== */
            /* METRIC CARDS */
            /* ========================================== */
            div[data-testid="stMetric"] {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
                transition: all 0.4s ease;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            [data-testid="stMetricValue"] {
                font-size: 2.8rem !important;
                font-weight: 800 !important;
                color: var(--primary-color) !important;
                text-shadow: 0 0 25px rgba(0, 255, 157, 0.7);
                line-height: 1.2;
            }
            
            [data-testid="stMetricLabel"] {
                color: var(--text-secondary) !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                margin-top: 8px !important;
            }
            
            /* ========================================== */
            /* SIDEBAR */
            /* ========================================== */
            section[data-testid="stSidebar"] {
                background-color: var(--sidebar-bg) !important;
                border-right: 1px solid var(--card-border);
            }
            
            section[data-testid="stSidebar"] *,
            section[data-testid="stSidebar"] .st-emotion-cache-16txtl3,
            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3,
            section[data-testid="stSidebar"] h4,
            section[data-testid="stSidebar"] h5,
            section[data-testid="stSidebar"] h6,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] div,
            section[data-testid="stSidebar"] label {
                color: var(--sidebar-text) !important;
                font-weight: 500;
            }
            
            /* ========================================== */
            /* BUTTONS */
            /* ========================================== */
            .stButton > button {
                background: linear-gradient(135deg, 
                    rgba(0, 184, 148, 0.9) 0%, 
                    rgba(0, 160, 133, 0.9) 100%);
                color: #00ff9d !important;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                padding: 12px 28px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                transition: all 0.3s ease;
                box-shadow: 0 8px 24px rgba(0, 184, 148, 0.4);
            }
            
            .stButton > button:hover {
                transform: translateY(-4px);
                box-shadow: 0 0 35px rgba(0, 255, 157, 0.6);
            }
            
            /* ========================================== */
            /* TABS */
            /* ========================================== */
            .stTabs [data-baseweb="tab-list"] {
                background: rgba(26, 31, 46, 0.8);
                border-radius: 10px;
                padding: 6px;
                border: 1px solid var(--card-border);
                gap: 4px;
            }
            
            .stTabs [data-baseweb="tab"] {
                color: var(--text-secondary);
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            
            .stTabs [aria-selected="true"] {
                color: var(--primary-color) !important;
                border: 1px solid var(--primary-color);
                font-weight: 700;
                text-shadow: 0 0 10px rgba(0, 255, 157, 0.5);
                background: rgba(0, 255, 157, 0.15) !important;
            }
            
            /* ========================================== */
            /* DROPDOWNS */
            /* ========================================== */
            .stSelectbox > div > div {
                background: var(--input-bg) !important;
                border: 2px solid var(--input-border) !important;
                border-radius: 8px !important;
                color: var(--text-primary) !important;
            }
            
            .stSelectbox [data-baseweb="popover"] {
                background: var(--card-bg) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 8px !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            }
            
            .stSelectbox [data-baseweb="popover"] li {
                color: var(--text-primary) !important;
                background: transparent !important;
                padding: 12px 16px !important;
                border-bottom: 1px solid var(--card-border) !important;
            }
/* ========================================== */
/* FILE UPLOADER - BLACK TEXT */
/* ========================================== */
.stFileUploader {
    border: 2px dashed #666666 !important;
    border-radius: 10px !important;
    background: #f8f9fa !important;
}

.stFileUploader label,
.stFileUploader p,
.stFileUploader div,
.stFileUploader span,
.stFileUploader * {
    color: #000000 !important;
}

/* Hover state for drag and drop */
.stFileUploader:hover {
    border-color: var(--primary-color) !important;
    background: #e9ecef !important;
}

/* File names and status text */
.stFileUploader .file-info,
.stFileUploader .file-name,
.stFileUploader .file-status {
    color: #000000 !important;
    font-weight: 500;
}

/* "Browse files" button text */
.stFileUploader button,
.stFileUploader button span {
    color: #000000 !important;
    font-weight: 600;
}

            /* ========================================== */
            /* RADIO BUTTONS */
            /* ========================================== */
            .stRadio label,
            .stCheckbox label,
            .stRadio [role="radiogroup"] label {
                color: var(--text-primary) !important;
                font-weight: 500 !important;
            }
            
            .stRadio [role="radiogroup"] {
                background: rgba(26, 31, 46, 0.7);
                padding: 16px;
                border-radius: 10px;
                border: 1px solid var(--card-border);
            }
            
            /* ========================================== */
            /* ALERT BOXES */
            /* ========================================== */
            .alert-box {
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                background: var(--card-bg);
                border-left: 8px solid;
                border: 1px solid var(--card-border);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            }
            
            .critical { 
                border-left-color: var(--sev-critical);
                background: linear-gradient(135deg, 
                    rgba(255, 71, 87, 0.25) 0%, 
                    rgba(255, 71, 87, 0.1) 100%);
            }
            
            /* ========================================== */
            /* EXPANDER - BASE STYLING */
            /* ========================================== */
            .streamlit-expanderHeader {
                background: var(--card-bg);
                color: var(--text-primary) !important;
                border-radius: 8px;
                border: 1px solid var(--card-border);
                font-weight: 700;
                padding: 14px;
            }
            
            /* ========================================== */
            /* DATAFRAMES */
            /* ========================================== */
            .dataframe {
                background: var(--card-bg) !important;
                color: var(--text-primary) !important;
                border: 1px solid var(--card-border) !important;
            }
            
            .dataframe th {
                background: rgba(0, 255, 157, 0.2) !important;
                font-weight: 700 !important;
            }
            
            /* ========================================== */
            /* SCROLLBAR */
            /* ========================================== */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(26, 31, 46, 0.5);
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--text-muted);
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--text-secondary);
            }
            
            /* ========================================== */
            /* ADDITIONAL GLOBAL OVERRIDES */
            /* ========================================== */
            
            /* Ensure all text in forms is visible */
            form * {
                color: var(--text-primary) !important;
            }
            
            /* Override any inline styles Streamlit might add */
            input[style*="background-color"],
            textarea[style*="background-color"] {
                background-color: var(--input-bg) !important;
                color: var(--input-text) !important;
            }
            
            /* Force dark mode on all form elements */
            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea {
                -webkit-appearance: none !important;
                -moz-appearance: none !important;
                appearance: none !important;
                background-color: var(--input-bg) !important;
                color: var(--input-text) !important;
            }
            
            /* Target even more specific selectors */
            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea {
                background-color: var(--input-bg) !important;
                color: var(--input-text) !important;
                border: 2px solid var(--input-border) !important;
            }
            
            /* Chrome autofill fix */
            input:-webkit-autofill,
            input:-webkit-autofill:hover, 
            input:-webkit-autofill:focus, 
            input:-webkit-autofill:active {
                -webkit-box-shadow: 0 0 0 30px var(--input-bg) inset !important;
                -webkit-text-fill-color: var(--input-text) !important;
                caret-color: var(--primary-color) !important;
            }
            
            /* ========================================== */
            /* CRITICAL FIX FOR ALL ALERT CONTENT IN TAB 2 */
            /* ========================================== */
            
            /* Target ALL content in Live Alerts tab (Tab 2) */
            section[data-testid="stTabPanel"]:nth-child(2) .stJson,
            section[data-testid="stTabPanel"]:nth-child(2) .stJson *,
            section[data-testid="stTabPanel"]:nth-child(2) pre,
            section[data-testid="stTabPanel"]:nth-child(2) code,
            section[data-testid="stTabPanel"]:nth-child(2) .stMarkdown,
            section[data-testid="stTabPanel"]:nth-child(2) .stMarkdown * {
                background-color: rgba(0, 0, 0, 0.8) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 8px;
                padding: 15px !important;
                margin: 10px 0 !important;
            }
            
            /* Specifically target JSON data */
            .stJson,
            .stJson *,
            .stJson pre,
            .stJson code {
                background-color: rgba(0, 0, 0, 0.8) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                border-radius: 8px;
                padding: 15px !important;
                margin: 10px 0 !important;
            }
            
            /* ========================================== */
            /* ATTACK DETECTED SECTION AND FOLLOWING CONTENT */
            /* ========================================== */
            
            /* Attack detected messages - transparent blue */
            .stError,
            .stAlert,
            .stSuccess,
            .stInfo,
            .stWarning {
                background-color: rgba(0, 100, 255, 0.2) !important;
                border: 1px solid rgba(0, 100, 255, 0.5) !important;
                border-radius: 8px;
                padding: 20px !important;
                margin: 15px 0 !important;
                color: #ffffff !important;
            }
            
            /* Text that comes immediately after attack detected */
            .stError + div,
            .stError ~ div:not(.streamlit-expanderHeader):not(.stButton):not(.stCheckbox):not(.stRadio):not(.stSelectbox) {
                background-color: rgba(0, 100, 255, 0.15) !important;
                border: 1px solid rgba(0, 100, 255, 0.3) !important;
                border-radius: 8px;
                padding: 20px !important;
                margin: 15px 0 !important;
            }
            
            /* Make sure text is white in these sections */
            .stError + div *,
            .stError ~ div:not(.streamlit-expanderHeader):not(.stButton):not(.stCheckbox):not(.stRadio):not(.stSelectbox) * {
                color: #ffffff !important;
            }
            
            /* ========================================== */
            /* CRITICAL ALERT HEADER - WHITE BACKGROUND, BLACK TEXT */
            /* ========================================== */
            
            /* Critical alert headers */
            .streamlit-expanderHeader:has(+ .streamlit-expanderContent .critical),
            .streamlit-expanderHeader[aria-expanded="true"]:has(+ .streamlit-expanderContent .critical),
            .streamlit-expanderHeader[aria-expanded="false"]:has(+ .streamlit-expanderContent .critical) {
                background-color: #ffffff !important;
                color: #000000 !important;
                border: 2px solid var(--sev-critical) !important;
                font-weight: 800 !important;
            }
            
            /* ========================================== */
            /* ALERT EXPANDER CONTENT - TRANSPARENT BLUE */
            /* ========================================== */
            
            /* Alert expander content */
            .streamlit-expanderContent {
                background-color: rgba(0, 100, 255, 0.1) !important;
                border: 1px solid rgba(0, 100, 255, 0.3) !important;
                border-radius: 8px;
                margin-top: 10px !important;
            }
            
            /* Text inside alert expanders */
            .streamlit-expanderContent * {
                color: #ffffff !important;
                background-color: transparent !important;
            }
            
            /* Alert boxes inside expanders */
            .streamlit-expanderContent .alert-box {
                background-color: rgba(0, 100, 255, 0.2) !important;
                border: 1px solid rgba(0, 100, 255, 0.5) !important;
                color: #ffffff !important;
            }
            
            /* Columns inside expanders */
            .streamlit-expanderContent .stColumn,
            .streamlit-expanderContent .stColumn * {
                color: #ffffff !important;
                background-color: transparent !important;
            }
            
            /* ========================================== */
            /* SPECIFIC FOR TAB 2 - LIVE ALERTS */
            /* ========================================== */
            
            /* Ensure everything in Tab 2 has proper contrast */
            section[data-testid="stTabPanel"]:nth-child(2) * {
                color: #ffffff !important;
            }
            
            /* Force dark backgrounds for all containers in Tab 2 */
            section[data-testid="stTabPanel"]:nth-child(2) div:not(.streamlit-expanderHeader):not(.stButton) {
                background-color: transparent !important;
            }
            
            /* Make sure all text is visible */
            section[data-testid="stTabPanel"]:nth-child(2) p,
            section[data-testid="stTabPanel"]:nth-child(2) div,
            section[data-testid="stTabPanel"]:nth-child(2) span,
            section[data-testid="stTabPanel"]:nth-child(2) strong {
                color: #ffffff !important;
            }
            
            /* ========================================== */
            /* FIX FOR JSON SPECIFICALLY */
            /* ========================================== */
            
            /* Override any Streamlit JSON styling */
            .stJson {
                background-color: rgba(0, 0, 0, 0.8) !important;
            }
            
            .stJson pre {
                background-color: rgba(0, 0, 0, 0.8) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                padding: 20px !important;
                border-radius: 8px;
                overflow: auto;
            }
            
            /* Make JSON syntax highlighting visible */
            .stJson span {
                color: #ffffff !important;
                background-color: transparent !important;
            }
            
            /* ========================================== */
            /* ADD EXTRA SAFETY FOR ALL DARK BACKGROUNDS */
            /* ========================================== */
            
            /* Force dark backgrounds for critical elements */
            div[style*="background-color: white"],
            div[style*="background-color: #fff"],
            div[style*="background-color: #ffffff"],
            pre[style*="background-color: white"],
            pre[style*="background-color: #fff"],
            pre[style*="background-color: #ffffff"] {
                background-color: rgba(0, 0, 0, 0.8) !important;
                color: #ffffff !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
            }
        </style>
        """

# Apply the selected theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)# Initialize session state
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'alert_count' not in st.session_state:
    st.session_state.alert_count = 0
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'detector' not in st.session_state:
    st.session_state.detector = None
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None




# Email configuration from .env (strip quotes if present)
def get_env_var(key, default):
    """Get environment variable and strip quotes"""
    value = os.getenv(key, default)
    if value and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return value



EMAIL_CONFIG = {
    'smtp_server': get_env_var('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(get_env_var('SMTP_PORT', '587')),
    'sender_email': get_env_var('SENDER_EMAIL', 'your_email@gmail.com'),
    'sender_password': get_env_var('SENDER_PASSWORD', 'your_app_password'),
    'admin_email': get_env_var('ADMIN_EMAIL', 'admin@example.com'),
    'enabled': get_env_var('EMAIL_ENABLED', 'false').lower() == 'true'
}



# Load model and chatbot
@st.cache_resource
def load_detector():
    """Load the trained GHF-ART model"""
    try:
        with open('ghf_art_model.pkl', 'rb') as f:
            saved_data = pickle.load(f)
        return saved_data
    except FileNotFoundError:
        st.error("Model not found! Please run train_model.py first.")
        return None



@st.cache_resource
def load_chatbot():
    """Load the chatbot"""
    try:
        return ClaudeSecurityChatbot()
    except Exception as e:
        st.warning(f"Chatbot initialization warning: {e}")
        return None



@st.cache_data
def load_processed_logs():
    """Load processed network logs from trained model"""
    try:
        if Path('network_logs_processed.csv').exists():
            df = pd.read_csv('network_logs_processed.csv')
            # Convert timestamp if it exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            return df
        return None
    except Exception as e:
        st.error(f"Error loading processed logs: {e}")
        return None



# Initialize components
model_data = load_detector()
if model_data and st.session_state.detector is None:
    st.session_state.detector = model_data



if st.session_state.chatbot is None:
    st.session_state.chatbot = load_chatbot()



# Email sending function
def send_alert_email(alert_data, force_send=False):
    """
    Send email alert to network administrator
    
    Args:
        alert_data: Dictionary containing attack detection results
        force_send: If True, send email regardless of severity (default: False)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not EMAIL_CONFIG['enabled']:
        return False
    
    # Only send email for actual attacks
    is_attack = alert_data.get('is_attack', False)
    if not is_attack and not force_send:
        return False
    
    # Determine if we should send email based on severity
    severity = alert_data.get('severity', 'LOW')
    should_send = force_send or (is_attack and severity in ['CRITICAL', 'HIGH', 'MEDIUM'])
    
    if not should_send:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['admin_email']
        
        # Subject based on severity
        if severity == 'CRITICAL':
            subject = f"CRITICAL: Network Attack Detected - Immediate Action Required"
        elif severity == 'HIGH':
            subject = f"HIGH: Network Attack Detected - Urgent Review"
        else:
            subject = f"Network Security Alert - {severity} Severity"
        
        msg['Subject'] = subject
        
        # Get data for HTML email
        data = alert_data.get('data', {})
        timestamp = datetime.fromisoformat(alert_data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        
        # Collect threat indicators
        indicators = []
        if data.get('src_bytes', 0) > 10000:
            indicators.append("Unusually high data transfer (potential data exfiltration)")
        if data.get('count', 0) > 50:
            indicators.append("High connection count (potential DoS/DDoS attack)")
        if data.get('num_failed_logins', 0) > 0:
            indicators.append("Failed login attempts detected (brute force attack)")
        if data.get('root_shell', 0) > 0:
            indicators.append("Root shell access attempt (privilege escalation)")
        if data.get('logged_in', 0) == 0 and data.get('service') in ['http', 'ssh', 'ftp']:
            indicators.append("Unauthorized access attempt to critical service")
        
        # Create HTML email with green theme styling (HTML only, no plain text)
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #1e8449;
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 25px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
        }}
        .alert-box {{
            background-color: white;
            border-left: 5px solid #27ae60;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .severity-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            margin: 10px 0;
        }}
        .severity-critical {{
            background-color: #e74c3c;
            color: white;
        }}
        .severity-high {{
            background-color: #f39c12;
            color: white;
        }}
        .severity-medium {{
            background-color: #3498db;
            color: white;
        }}
        .severity-low {{
            background-color: #95a5a6;
            color: white;
        }}
        .info-section {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .info-section h3 {{
            color: #27ae60;
            margin-top: 0;
            border-bottom: 2px solid #27ae60;
            padding-bottom: 10px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #ddd;
        }}
        .info-label {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .info-value {{
            color: #34495e;
        }}
        .threat-indicators {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .threat-indicators ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .threat-indicators li {{
            margin: 8px 0;
            color: #856404;
        }}
        .actions {{
            background-color: #d4edda;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .actions h3 {{
            color: #155724;
            margin-top: 0;
        }}
        .actions ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .actions li {{
            margin: 8px 0;
            color: #155724;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid rgba(255, 255, 255, 0.3);
            color: #ffffff;
            font-size: 12px;
        }}
        .footer a {{
            color: #ffffff;
            text-decoration: underline;
        }}
        .footer a:hover {{
            color: #d5f4e6;
        }}
        .score-display {{
            font-size: 32px;
            font-weight: bold;
            color: #27ae60;
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            margin: 15px 0;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin: 2px;
        }}
        .badge-success {{
            background-color: #27ae60;
            color: white;
        }}
        .badge-danger {{
            background-color: #e74c3c;
            color: white;
        }}
        .badge-warning {{
            background-color: #f39c12;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Network Security Alert</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px;">Automated Notification System</p>
        </div>
        
        <div class="alert-box">
            <div style="text-align: center;">
                <span class="severity-badge severity-{severity.lower()}">{severity}</span>
            </div>
            <div class="score-display">
                Attack Score: {alert_data['attack_score']:.4f}
            </div>
            <div style="text-align: center; margin: 15px 0;">
                <span class="badge badge-{'danger' if alert_data.get('is_attack') else 'success'}">
                    {'ANOMALY DETECTED' if alert_data.get('is_attack') else 'NORMAL'}
                </span>
            </div>
        </div>
        
        <div class="info-section">
            <h3>Alert Details</h3>
            <div class="info-row">
                <span class="info-label">Timestamp:</span>
                <span class="info-value">{timestamp}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Severity Level:</span>
                <span class="info-value">{severity}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Attack Score:</span>
                <span class="info-value">{alert_data['attack_score']:.4f} / 1.0</span>
            </div>
            <div class="info-row">
                <span class="info-label">Prediction:</span>
                <span class="info-value">{'ANOMALY DETECTED' if alert_data.get('is_attack') else 'NORMAL TRAFFIC'}</span>
            </div>
        </div>
        
        <div class="info-section">
            <h3>🌐 Network Traffic Information</h3>
            <div class="info-row">
                <span class="info-label">Protocol Type:</span>
                <span class="info-value">{data.get('protocol_type', 'N/A').upper()}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Service:</span>
                <span class="info-value">{data.get('service', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Connection Flag:</span>
                <span class="info-value">{data.get('flag', 'N/A')}</span>
            </div>
        </div>
        
        <div class="info-section">
            <h3>📤 Source Information</h3>
            <div class="info-row">
                <span class="info-label">Source IP:</span>
                <span class="info-value">{data.get('src_ip', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Source Bytes:</span>
                <span class="info-value">{data.get('src_bytes', 'N/A'):,} bytes</span>
            </div>
            <div class="info-row">
                <span class="info-label">Connection Duration:</span>
                <span class="info-value">{data.get('duration', 'N/A')} seconds</span>
            </div>
        </div>
        
        <div class="info-section">
            <h3>📥 Destination Information</h3>
            <div class="info-row">
                <span class="info-label">Destination IP:</span>
                <span class="info-value">{data.get('dst_ip', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Destination Bytes:</span>
                <span class="info-value">{data.get('dst_bytes', 'N/A'):,} bytes</span>
            </div>
        </div>
        
        <div class="info-section">
            <h3>📊 Connection Statistics</h3>
            <div class="info-row">
                <span class="info-label">Total Connections:</span>
                <span class="info-value">{data.get('count', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Service Connections:</span>
                <span class="info-value">{data.get('srv_count', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Failed Login Attempts:</span>
                <span class="info-value">{data.get('num_failed_logins', 0)}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Root Shell Access:</span>
                <span class="info-value">{'Yes' if data.get('root_shell', 0) > 0 else 'No'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Logged In:</span>
                <span class="info-value">{'Yes' if data.get('logged_in', 0) > 0 else 'No'}</span>
            </div>
        </div>
"""
        
        # Add threat indicators
        if indicators:
            html_body += """
        <div class="threat-indicators">
                            <h3>Threat Indicators Detected</h3>
            <ul>
"""
            for indicator in indicators:
                html_body += f"                <li>{indicator}</li>\n"
            html_body += """
            </ul>
        </div>
"""
        else:
            html_body += """
        <div class="threat-indicators">
                            <h3>Threat Indicators</h3>
            <p>• Anomalous pattern detected by GHF-ART model</p>
        </div>
"""
        
        # Add recommended actions
        html_body += """
        <div class="actions">
                            <h3>Recommended Actions</h3>
            <ol>
"""
        if severity == 'CRITICAL':
            html_body += """
                <li><strong>IMMEDIATE:</strong> Block source IP address</li>
                <li><strong>IMMEDIATE:</strong> Isolate affected systems</li>
                <li>Review firewall logs for related activity</li>
                <li>Check for data exfiltration</li>
                <li>Notify security team immediately</li>
"""
        elif severity == 'HIGH':
            html_body += """
                <li>Block source IP address</li>
                <li>Review connection logs</li>
                <li>Check for related suspicious activity</li>
                <li>Monitor affected services closely</li>
"""
        else:
            html_body += """
                <li>Review connection details</li>
                <li>Monitor for similar patterns</li>
                <li>Add to watchlist if pattern repeats</li>
"""
        
        html_body += f"""
            </ol>
        </div>
        
        <div class="footer">
            <p><strong>Network Security SOC Dashboard</strong></p>
            <p>Generated by GHF-ART (Generalized Hierarchical Fuzzy Adaptive Resonance Theory) Anomaly Detection System</p>
            <p>For more details, access the dashboard at: <a href="http://localhost:8501">http://localhost:8501</a></p>
            <p style="margin-top: 15px; font-size: 11px; color: #ffffff;">This is an automated alert. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach only HTML version (styled email)
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"Email authentication failed. Check your email credentials in .env file. Error: {e}")
        return False
    except smtplib.SMTPException as e:
        st.error(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        st.error(f"Email sending failed: {str(e)}")
        return False



# Real-time monitoring function
def detect_attack(network_data, model_data):
    """Detect if network data is an attack"""
    if model_data is None:
        return None
    
    model = model_data['model']
    scaler = model_data['scaler']
    encoder = model_data['encoder']
    
    # Define all expected numerical columns in the exact order used during training
    expected_num_cols = [
        'duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment',
        'urgent', 'hot', 'num_failed_logins', 'logged_in', 'num_compromised',
        'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
        'num_shells', 'num_access_files', 'num_outbound_cmds',
        'is_host_login', 'is_guest_login', 'count', 'srv_count',
        'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
        'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
        'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
        'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
        'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
        'dst_host_srv_rerror_rate'
    ]
    
    # Preprocess data
    if isinstance(network_data, dict):
        df = pd.DataFrame([network_data])
    else:
        df = network_data.copy()
    
    # Handle categorical columns
    cat_cols = ['protocol_type', 'service', 'flag']
    for col in cat_cols:
        if col not in df.columns:
            df[col] = 'unknown'
    
    try:
        # Encode categorical features
        X_cat = encoder.transform(df[cat_cols])
        
        # Prepare numerical features in the exact order expected by the scaler
        X_num_list = []
        for col in expected_num_cols:
            if col in df.columns:
                X_num_list.append(df[col].values)
            else:
                # Fill missing columns with 0 (default value)
                X_num_list.append(np.zeros(len(df)))
        
        # Stack numerical features into array
        X_num = np.column_stack(X_num_list)
        
        # Scale numerical features
        X_num_scaled = scaler.transform(X_num)
        
        # Combine numerical and categorical features
        X_processed = np.hstack([X_num_scaled, X_cat])
        
        X_processed_df = pd.DataFrame(X_processed)
        predictions, scores = model.predict(X_processed_df)
        
        is_attack = bool(predictions[0] == -1)
        attack_score = float(scores[0])
        
        # Only assign severity if it's actually an attack
        if is_attack:
            if attack_score > 0.9:
                severity = "CRITICAL"
            elif attack_score > 0.7:
                severity = "HIGH"
            elif attack_score > 0.5:
                severity = "MEDIUM"
            else:
                severity = "LOW"
        else:
            # Normal traffic - no severity needed
            severity = "NORMAL"
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'is_attack': is_attack,
            'attack_score': attack_score,
            'severity': severity,
            'prediction': int(predictions[0]),
            'data': network_data if isinstance(network_data, dict) else network_data.to_dict('records')[0]
        }
        
        return result
    except Exception as e:
        st.error(f"Detection error: {e}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None



# Load alerts
def load_alerts():
    """Load alerts from JSON file"""
    try:
        with open('attack_alerts.json', 'r') as f:
            alerts = json.load(f)
        return alerts
    except FileNotFoundError:
        return []



# Save alerts
def save_alert(alert):
    """Save alert to JSON file - only saves actual attacks"""
    # Only save if it's actually an attack
    if not alert.get('is_attack', False):
        return  # Don't save normal traffic as alerts
    
    alerts = load_alerts()
    alerts.append(alert)
    with open('attack_alerts.json', 'w') as f:
        json.dump(alerts, f, indent=2, default=str)



# Simulate real-time traffic
def simulate_normal_traffic():
    """Generate simulated normal network traffic patterns that match training data"""
    # Try to load actual normal samples from processed data for better accuracy
    try:
        if Path('network_logs_processed.csv').exists():
            df_logs = pd.read_csv('network_logs_processed.csv')
            # Get normal traffic samples (anomaly_prediction != -1)
            normal_samples = df_logs[df_logs.get('anomaly_prediction', -1) != -1]
            if len(normal_samples) > 0:
                # Sample a random normal traffic pattern
                sample = normal_samples.sample(n=1).iloc[0]
                packet = sample.to_dict()
                # Ensure IPs are present
                if 'src_ip' not in packet or pd.isna(packet.get('src_ip')):
                    packet['src_ip'] = f"192.168.1.{random.randint(2, 254)}"
                if 'dst_ip' not in packet or pd.isna(packet.get('dst_ip')):
                    packet['dst_ip'] = f"10.0.0.{random.randint(2, 100)}"
                return packet
    except:
        pass
    
    # Fallback: Generate simulated normal traffic with very conservative values
    normal_services = ['http', 'ftp', 'smtp', 'domain', 'ssh', 'pop_3', 'eco_i', 'ecr_i']
    normal_protocols = ['tcp', 'udp']
    normal_flags = ['SF']  # Only SF for truly normal (S0 can be suspicious)
    
    # Use very conservative values that match typical normal traffic
    packet = {
        'duration': random.randint(0, 50),  # Very short durations
        'protocol_type': random.choice(normal_protocols),
        'service': random.choice(normal_services),
        'flag': 'SF',  # Always SF for normal
        'src_bytes': random.randint(0, 2000),  # Very low byte counts
        'dst_bytes': random.randint(0, 1000),
        'land': 0,
        'wrong_fragment': 0,
        'urgent': 0,
        'hot': 0,  # Zero hot indicators
        'num_failed_logins': 0,
        'logged_in': 1,  # Always logged in
        'num_compromised': 0,
        'root_shell': 0,
        'su_attempted': 0,
        'num_root': 0,
        'num_file_creations': 0,  # Zero file creations
        'num_shells': 0,
        'num_access_files': 0,  # Zero file access
        'num_outbound_cmds': 0,
        'is_host_login': 0,
        'is_guest_login': 0,
        'count': random.randint(1, 5),  # Very low connection count
        'srv_count': random.randint(1, 5),
        'serror_rate': 0.0,  # Zero error rates
        'srv_serror_rate': 0.0,
        'rerror_rate': 0.0,
        'srv_rerror_rate': 0.0,
        'same_srv_rate': 1.0,  # Perfect same service rate
        'diff_srv_rate': 0.0,
        'srv_diff_host_rate': 0.0,
        'dst_host_count': random.randint(1, 5),
        'dst_host_srv_count': random.randint(1, 5),
        'dst_host_same_srv_rate': 1.0,
        'dst_host_diff_srv_rate': 0.0,
        'dst_host_same_src_port_rate': 1.0,
        'dst_host_srv_diff_host_rate': 0.0,
        'dst_host_serror_rate': 0.0,
        'dst_host_srv_serror_rate': 0.0,
        'dst_host_rerror_rate': 0.0,
        'dst_host_srv_rerror_rate': 0.0,
        'src_ip': f"192.168.1.{random.randint(2, 254)}",
        'dst_ip': f"10.0.0.{random.randint(2, 100)}"
    }
    return packet



def simulate_attack_traffic():
    """Generate simulated attack network traffic patterns"""
    attack_services = ['private', 'telnet', 'ftp', 'http', 'smtp']
    attack_protocols = ['tcp', 'udp', 'icmp']
    attack_flags = ['S0', 'REJ', 'RSTO', 'RSTR', 'SH']  # Suspicious flags
    
    packet = {
        'duration': random.randint(100, 1000),  # Longer durations
        'protocol_type': random.choice(attack_protocols),
        'service': random.choice(attack_services),
        'flag': random.choice(attack_flags),
        'src_bytes': random.randint(5000, 50000),  # Higher byte counts
        'dst_bytes': random.randint(1000, 10000),
        'land': random.randint(0, 1),
        'wrong_fragment': random.randint(0, 3),
        'urgent': random.randint(0, 1),
        'hot': random.randint(5, 30),  # High hot indicators
        'num_failed_logins': random.randint(0, 5),  # Failed logins
        'logged_in': random.randint(0, 1),  # Often not logged in
        'num_compromised': random.randint(0, 10),
        'root_shell': random.randint(0, 1),  # Root shell attempts
        'su_attempted': random.randint(0, 2),
        'num_root': random.randint(0, 10),
        'num_file_creations': random.randint(0, 20),
        'num_shells': random.randint(0, 2),
        'num_access_files': random.randint(0, 10),
        'num_outbound_cmds': random.randint(0, 2),
        'is_host_login': random.randint(0, 1),
        'is_guest_login': random.randint(0, 1),
        'count': random.randint(50, 500),  # High connection count (DoS indicator)
        'srv_count': random.randint(50, 500),
        'serror_rate': random.uniform(0.3, 1.0),  # High error rates
        'srv_serror_rate': random.uniform(0.3, 1.0),
        'rerror_rate': random.uniform(0.3, 1.0),
        'srv_rerror_rate': random.uniform(0.3, 1.0),
        'same_srv_rate': random.uniform(0, 0.5),  # Low same service rate
        'diff_srv_rate': random.uniform(0.5, 1.0),  # High different service rate
        'srv_diff_host_rate': random.uniform(0.5, 1.0),
        'dst_host_count': random.randint(50, 100),  # High host count
        'dst_host_srv_count': random.randint(50, 100),
        'dst_host_same_srv_rate': random.uniform(0, 0.5),
        'dst_host_diff_srv_rate': random.uniform(0.5, 1.0),
        'dst_host_same_src_port_rate': random.uniform(0, 0.5),
        'dst_host_srv_diff_host_rate': random.uniform(0.5, 1.0),
        'dst_host_serror_rate': random.uniform(0.3, 1.0),
        'dst_host_srv_serror_rate': random.uniform(0.3, 1.0),
        'dst_host_rerror_rate': random.uniform(0.3, 1.0),
        'dst_host_srv_rerror_rate': random.uniform(0.3, 1.0),
        'src_ip': f"192.168.1.{random.randint(2, 254)}",
        'dst_ip': f"10.0.0.{random.randint(2, 100)}"
    }
    return packet



def simulate_traffic(traffic_type='random'):
    """
    Generate simulated network traffic with all required features
    
    Args:
        traffic_type: 'normal', 'attack', or 'random' (default: random)
    """
    if traffic_type == 'normal':
        return simulate_normal_traffic()
    elif traffic_type == 'attack':
        return simulate_attack_traffic()
    else:
        # Random: 50% normal, 50% attack
        return random.choice([simulate_normal_traffic(), simulate_attack_traffic()])



# Main Dashboard
# Main Dashboard
st.markdown("""
<div class="main-header-container">
    <h1 class="main-header">Network Security SOC Dashboard</h1>
    <div class="header-subtitle">Unified Network Security Dashboard • Real-time Monitoring • AI-Powered Threat Detection</div>
</div>
""", unsafe_allow_html=True)

# Real-time monitoring toggle
monitoring_status = st.sidebar.checkbox("Enable Real-time Monitoring", value=st.session_state.monitoring_active)



if monitoring_status != st.session_state.monitoring_active:
    st.session_state.monitoring_active = monitoring_status
    if monitoring_status:
        st.sidebar.success("Monitoring started")
    else:
        st.sidebar.info("⏸️ Monitoring paused")



# Load alerts
alerts = load_alerts()



# Main metrics
col1, col2, col3, col4 = st.columns(4)



with col1:
    st.metric("Total Alerts", len(alerts))



with col2:
    critical = len([a for a in alerts if a.get('severity') == 'CRITICAL'])
    st.metric("Critical Alerts", critical, delta=f"+{critical}")



with col3:
    recent = len([a for a in alerts if (datetime.now() - datetime.fromisoformat(a['timestamp'])).seconds < 300])
    st.metric("Last 5 Minutes", recent)



with col4:
    if alerts:
        last_alert = datetime.fromisoformat(alerts[-1]['timestamp'])
        seconds_ago = (datetime.now() - last_alert).seconds
        st.metric("Last Alert", f"{seconds_ago}s ago")
    else:
        st.metric("Last Alert", "No alerts")



st.markdown("---")



# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Live Alerts", "Test Data", "ChatOps", "Settings"])



# TAB 1: Dashboard with Visualizations
with tab1:
    st.subheader("Network Security Analytics")
    
    # Load processed logs from trained model
    processed_logs = load_processed_logs()
    
    # Option to switch between Dataset EDA and Live Alerts
    view_mode = st.radio(
        "Select View:",
        ["Dataset EDA (Full Dataset Analysis)", "Live Alerts (Real-time Attack Visualizations)"],
        horizontal=True,
        key="dashboard_view_mode"
    )
    
    st.markdown("---")
    
    # Determine which data to use for visualizations
    use_alerts = len(alerts) > 0
    use_processed_logs = processed_logs is not None and len(processed_logs) > 0
    
    # Show Dataset EDA visualizations
    if view_mode == "Dataset EDA (Full Dataset Analysis)":
        if use_processed_logs:
            df_logs = processed_logs.copy()
            
            # Calculate severity based on anomaly_score
            def get_severity(score):
                """Convert anomaly score to severity level"""
                if pd.isna(score) or score is None:
                    return 'LOW'
                score = float(score)
                if score > 0.9:
                    return 'CRITICAL'
                elif score > 0.7:
                    return 'HIGH'
                elif score > 0.5:
                    return 'MEDIUM'
                else:
                    return 'LOW'
            
            # Get all data (both normal and anomalies) for EDA
            df_all = df_logs.copy()
            
            # Ensure anomaly_score column exists
            if 'anomaly_score' not in df_all.columns:
                df_all['anomaly_score'] = 0.0
            
            # Convert to numeric
            df_all['anomaly_score'] = pd.to_numeric(df_all['anomaly_score'], errors='coerce').fillna(0.0)
            
            # Filter anomalies
            df_anomalies = df_all[df_all.get('anomaly_prediction', -1) == -1].copy()
            df_normal = df_all[df_all.get('anomaly_prediction', -1) != -1].copy()
            
            # Overall statistics
            st.markdown("### Dataset Overview")
            overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
            
            with overview_col1:
                st.metric("Total Records", f"{len(df_all):,}")
            with overview_col2:
                st.metric("Normal Traffic", f"{len(df_normal):,}", delta=f"{(len(df_normal)/len(df_all)*100):.1f}%")
            with overview_col3:
                st.metric("Anomalies Detected", f"{len(df_anomalies):,}", delta=f"{(len(df_anomalies)/len(df_all)*100):.1f}%")
            with overview_col4:
                if len(df_anomalies) > 0:
                    avg_score = df_anomalies['anomaly_score'].mean()
                    st.metric("Avg Anomaly Score", f"{avg_score:.3f}")
                else:
                    st.metric("Avg Anomaly Score", "N/A")
            
            if len(df_anomalies) > 0:
                df_anomalies['severity'] = df_anomalies['anomaly_score'].apply(get_severity)
                
                # Visualizations
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    # Severity distribution
                    severity_counts = df_anomalies['severity'].value_counts()
                    
                    # Ensure all severity levels are represented
                    all_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                    for sev in all_severities:
                        if sev not in severity_counts.index:
                            severity_counts[sev] = 0
                    
                    # Sort by severity order
                    severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                    severity_counts = severity_counts.reindex([s for s in severity_order if s in severity_counts.index])
                    
                    # Remove zero counts for cleaner display
                    severity_counts = severity_counts[severity_counts > 0]
                    
                    if len(severity_counts) > 0:
                        # Set Plotly template based on theme
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        
                        # Create color list based on theme
                        if st.session_state.theme == 'dark':
                            color_map = {
                                'CRITICAL': '#ff4757',
                                'HIGH': '#ffa502',
                                'MEDIUM': '#ffd32a',
                                'LOW': '#0fbcf9'
                            }
                        else:
                            color_map = {
                                'CRITICAL': '#dc3545',
                                'HIGH': '#fd7e14',
                                'MEDIUM': '#ffc107',
                                'LOW': '#0dcaf0'
                            }
                        
                        colors = [color_map.get(sev, '#95a5a6') for sev in severity_counts.index]
                        
                        fig_pie = px.pie(
                            values=severity_counts.values,
                            names=severity_counts.index,
                            title="Severity Distribution (Dataset EDA)",
                            color_discrete_sequence=colors,
                            template=plotly_template
                        )
                        fig_pie.update_traces(
                            textposition='inside', 
                            textinfo='percent+label',
                            marker=dict(colors=colors, line=dict(color='#0e1117' if st.session_state.theme == 'dark' else '#ffffff', width=2))
                        )
                        fig_pie.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        st.caption(f"Breakdown: {', '.join([f'{k}: {v:,}' for k, v in severity_counts.items()])}")
                        with st.expander("Interpretation: Severity Distribution"):
                            st.markdown("""
                            **What this chart shows:**
                            - **CRITICAL (Red)**: Immediate action required - attacks with score > 0.9
                            - **HIGH (Orange)**: Urgent attention needed - attacks with score 0.7-0.9
                            - **MEDIUM (Yellow)**: Monitor closely - attacks with score 0.5-0.7
                            - **LOW (Blue)**: Minor anomalies - attacks with score < 0.5
                            
                            **Insight**: A larger proportion of CRITICAL alerts indicates a serious security threat requiring immediate response.
                            """)
                
                with viz_col2:
                    # Normal vs Anomaly distribution
                    normal_anomaly_counts = pd.Series({
                        'Normal': len(df_normal),
                        'Anomaly': len(df_anomalies)
                    })
                    
                    plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                    colors = ['#00ff9d', '#ff4757'] if st.session_state.theme == 'dark' else ['#198754', '#dc3545']
                    
                    fig_normal = px.pie(
                        values=normal_anomaly_counts.values,
                        names=normal_anomaly_counts.index,
                        title="Normal vs Anomaly Distribution",
                        color_discrete_sequence=colors,
                        template=plotly_template
                    )
                    fig_normal.update_traces(
                        textposition='inside',
                        textinfo='percent+label+value'
                    )
                    fig_normal.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                    )
                    st.plotly_chart(fig_normal, use_container_width=True)
                    with st.expander("Interpretation: Normal vs Anomaly"):
                        st.markdown("""
                        **What this chart shows:**
                        - **Green (Normal)**: Traffic patterns matching known normal behavior
                        - **Red (Anomaly)**: Traffic patterns deviating from normal (potential attacks)
                        
                        **Insight**: 
                        - High anomaly percentage indicates significant security concerns
                        - Low anomaly percentage suggests mostly normal network operations
                        """)
                
                # Timeline if timestamp exists
                if 'timestamp' in df_anomalies.columns and df_anomalies['timestamp'].notna().any():
                    st.subheader("Temporal Analysis")
                    time_col1, time_col2 = st.columns(2)
                    
                    with time_col1:
                        df_anomalies['hour'] = df_anomalies['timestamp'].dt.floor('1H')
                        timeline = df_anomalies.groupby('hour').size().reset_index(name='count')
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        line_color = '#ff4757' if st.session_state.theme == 'dark' else '#dc3545'
                        
                        fig_timeline = px.line(
                            timeline,
                            x='hour',
                            y='count',
                            title="Anomalies per Hour (Dataset EDA)",
                            labels={'hour': 'Time', 'count': 'Anomaly Count'},
                            markers=True,
                            template=plotly_template
                        )
                        fig_timeline.update_traces(line_color=line_color, line_width=2)
                        fig_timeline.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_timeline, use_container_width=True)
                    
                    with time_col2:
                        # Anomaly score distribution
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        bar_color = '#00ff9d' if st.session_state.theme == 'dark' else '#198754'
                        
                        fig_hist = px.histogram(
                            df_anomalies,
                            x='anomaly_score',
                            nbins=30,
                            title="Anomaly Score Distribution (Dataset EDA)",
                            labels={'anomaly_score': 'Anomaly Score', 'count': 'Frequency'},
                            color_discrete_sequence=[bar_color],
                            template=plotly_template
                        )
                        fig_hist.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                
                # Protocol and Service analysis
                st.subheader("Protocol & Service Analysis")
                proto_col1, proto_col2 = st.columns(2)
                
                with proto_col1:
                    if 'protocol_type' in df_anomalies.columns:
                        protocol_counts = df_anomalies['protocol_type'].value_counts()
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        bar_color = '#0fbcf9' if st.session_state.theme == 'dark' else '#0dcaf0'
                        
                        fig_protocol = px.bar(
                            x=protocol_counts.index,
                            y=protocol_counts.values,
                            title="Anomalies by Protocol (Dataset EDA)",
                            labels={'x': 'Protocol', 'y': 'Count'},
                            color_discrete_sequence=[bar_color],
                            template=plotly_template
                        )
                        fig_protocol.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_protocol, use_container_width=True)
                
                with proto_col2:
                    if 'service' in df_anomalies.columns:
                        service_counts = df_anomalies['service'].value_counts().head(10)
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        bar_color = '#ff4757' if st.session_state.theme == 'dark' else '#fd7e14'
                        
                        fig_service = px.bar(
                            x=service_counts.index,
                            y=service_counts.values,
                            title="Top 10 Attacked Services (Dataset EDA)",
                            labels={'x': 'Service', 'y': 'Count'},
                            color_discrete_sequence=[bar_color],
                            template=plotly_template
                        )
                        fig_service.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_service, use_container_width=True)
                
                # Advanced EDA Visualizations
                st.subheader("Advanced Dataset Analytics")
                adv_col1, adv_col2 = st.columns(2)
                
                with adv_col1:
                    # Data Transfer Analysis
                    if 'src_bytes' in df_anomalies.columns and 'dst_bytes' in df_anomalies.columns:
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        
                        if st.session_state.theme == 'dark':
                            color_map = {
                                'CRITICAL': '#ff4757',
                                'HIGH': '#ffa502',
                                'MEDIUM': '#ffd32a',
                                'LOW': '#0fbcf9'
                            }
                        else:
                            color_map = {
                                'CRITICAL': '#dc3545',
                                'HIGH': '#fd7e14',
                                'MEDIUM': '#ffc107',
                                'LOW': '#0dcaf0'
                            }
                        
                        fig_scatter = px.scatter(
                            df_anomalies.head(1000),
                            x='src_bytes',
                            y='dst_bytes',
                            color='severity',
                            size='anomaly_score',
                            hover_data=['protocol_type', 'service', 'count'],
                            title="Data Transfer Pattern Analysis (Dataset EDA)",
                            labels={'src_bytes': 'Source Bytes', 'dst_bytes': 'Destination Bytes'},
                            color_discrete_map=color_map,
                            template=plotly_template
                        )
                        fig_scatter.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
                
                with adv_col2:
                    # Connection Pattern Analysis
                    if 'count' in df_anomalies.columns and 'srv_count' in df_anomalies.columns:
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        
                        if st.session_state.theme == 'dark':
                            color_map = {
                                'CRITICAL': '#ff4757',
                                'HIGH': '#ffa502',
                                'MEDIUM': '#ffd32a',
                                'LOW': '#0fbcf9'
                            }
                        else:
                            color_map = {
                                'CRITICAL': '#dc3545',
                                'HIGH': '#fd7e14',
                                'MEDIUM': '#ffc107',
                                'LOW': '#0dcaf0'
                            }
                        
                        fig_conn = px.scatter(
                            df_anomalies.head(1000),
                            x='count',
                            y='srv_count',
                            color='severity',
                            size='anomaly_score',
                            hover_data=['service', 'protocol_type'],
                            title="Connection Pattern Analysis (Dataset EDA)",
                            labels={'count': 'Total Connections', 'srv_count': 'Service Connections'},
                            color_discrete_map=color_map,
                            template=plotly_template
                        )
                        fig_conn.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_conn, use_container_width=True)
                
                # Error Rate and Flag Analysis
                adv_col3, adv_col4 = st.columns(2)
                
                with adv_col3:
                    # Error Rate Analysis
                    if 'serror_rate' in df_anomalies.columns and 'rerror_rate' in df_anomalies.columns:
                        error_df = df_anomalies[['serror_rate', 'rerror_rate', 'severity']].head(1000)
                        fig_error = go.Figure()
                        
                        if st.session_state.theme == 'dark':
                            severity_colors = {
                                'CRITICAL': '#ff4757',
                                'HIGH': '#ffa502',
                                'MEDIUM': '#ffd32a',
                                'LOW': '#0fbcf9'
                            }
                        else:
                            severity_colors = {
                                'CRITICAL': '#dc3545',
                                'HIGH': '#fd7e14',
                                'MEDIUM': '#ffc107',
                                'LOW': '#0dcaf0'
                            }

                        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                            severity_data = error_df[error_df['severity'] == severity]
                            if len(severity_data) > 0:
                                fig_error.add_trace(go.Scatter(
                                    x=severity_data['serror_rate'],
                                    y=severity_data['rerror_rate'],
                                    mode='markers',
                                    name=severity,
                                    marker=dict(
                                        size=8, 
                                        opacity=0.6, 
                                        color=severity_colors.get(severity, '#aaa')
                                    )
                                ))
                        
                        fig_error.update_layout(
                            title="Error Rate Analysis (Dataset EDA)",
                            xaxis_title="SYN Error Rate",
                            yaxis_title="REJ Error Rate",
                            hovermode='closest',
                            template="plotly_dark" if st.session_state.theme == 'dark' else "plotly_white",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_error, use_container_width=True)
                
                with adv_col4:
                    # Flag Distribution
                    if 'flag' in df_anomalies.columns:
                        flag_counts = df_anomalies['flag'].value_counts()
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        
                        fig_flag = px.bar(
                            x=flag_counts.index,
                            y=flag_counts.values,
                            title="Attack Distribution by Flag (Dataset EDA)",
                            labels={'x': 'Flag Type', 'y': 'Count'},
                            color=flag_counts.values,
                            color_continuous_scale='Reds',
                            template=plotly_template
                        )
                        fig_flag.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_flag, use_container_width=True)
                
                # Heatmap
                if 'service' in df_anomalies.columns and 'protocol_type' in df_anomalies.columns:
                    st.subheader("Service-Protocol Correlation")
                    heatmap_data = pd.crosstab(df_anomalies['service'], df_anomalies['protocol_type'])
                    
                    plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                    
                    fig_heatmap = px.imshow(
                        heatmap_data,
                        labels=dict(x="Protocol", y="Service", color="Attack Count"),
                        title="Attack Heatmap: Service vs Protocol (Dataset EDA)",
                        color_continuous_scale='Viridis',
                        aspect="auto",
                        template=plotly_template
                    )
                    fig_heatmap.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.info("No anomalies detected in the dataset. All traffic was classified as normal.")
        else:
            st.warning("Dataset not available. Please ensure 'network_logs_processed.csv' exists from the trained model.")
    
    # Show Live Alerts visualizations
    elif view_mode == "Live Alerts (Real-time Attack Visualizations)":
        st.markdown("### Real-time Attack Analytics")
        st.info("This view shows visualizations based on live alerts detected in real-time. Use the 'Live Alerts' tab to generate new alerts.")
        
        if use_alerts:
            # Filter to only show actual attacks
            attack_alerts = [a for a in alerts if a.get('is_attack', False) and a.get('severity', '') != 'NORMAL']
            
            if len(attack_alerts) > 0:
                df_alerts = pd.DataFrame(attack_alerts)
                df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'])
                
                # Overview metrics
                st.markdown("#### Live Alert Overview")
                alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
                
                with alert_col1:
                    st.metric("Total Live Alerts", f"{len(attack_alerts):,}")
                
                with alert_col2:
                    critical_live = len([a for a in attack_alerts if a.get('severity') == 'CRITICAL'])
                    st.metric("Critical Alerts", f"{critical_live:,}")
                
                with alert_col3:
                    if 'attack_score' in df_alerts.columns:
                        avg_score = df_alerts['attack_score'].mean()
                        st.metric("Avg Attack Score", f"{avg_score:.3f}")
                    else:
                        st.metric("Avg Attack Score", "N/A")
                
                with alert_col4:
                    if 'timestamp' in df_alerts.columns:
                        recent_count = len(df_alerts[df_alerts['timestamp'] > (datetime.now() - pd.Timedelta(hours=1))])
                        st.metric("Last Hour", f"{recent_count:,}")
                    else:
                        st.metric("Last Hour", "N/A")
                
                st.markdown("---")
                
                # Visualizations
                viz_col1, viz_col2 = st.columns(2)
        
                with viz_col1:
                    # Severity distribution
                    severity_counts = df_alerts['severity'].value_counts()
                    
                    # Ensure all severity levels are represented
                    all_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                    for sev in all_severities:
                        if sev not in severity_counts.index:
                            severity_counts[sev] = 0
                    
                    # Sort by severity order
                    severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                    severity_counts = severity_counts.reindex([s for s in severity_order if s in severity_counts.index])
                    
                    # Remove zero counts for cleaner display
                    severity_counts = severity_counts[severity_counts > 0]
                    
                    if len(severity_counts) > 0:
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        
                        if st.session_state.theme == 'dark':
                            color_map = {
                                'CRITICAL': '#ff4757',
                                'HIGH': '#ffa502',
                                'MEDIUM': '#ffd32a',
                                'LOW': '#0fbcf9'
                            }
                        else:
                            color_map = {
                                'CRITICAL': '#dc3545',
                                'HIGH': '#fd7e14',
                                'MEDIUM': '#ffc107',
                                'LOW': '#0dcaf0'
                            }
                        
                        colors = [color_map.get(sev, '#95a5a6') for sev in severity_counts.index]
                        
                        fig_pie = px.pie(
                            values=severity_counts.values,
                            names=severity_counts.index,
                            title="Severity Distribution",
                            color_discrete_sequence=colors,
                            template=plotly_template
                        )
                        fig_pie.update_traces(
                            textposition='inside', 
                            textinfo='percent+label',
                            marker=dict(colors=colors, line=dict(color='#0e1117' if st.session_state.theme == 'dark' else '#ffffff', width=2))
                        )
                        fig_pie.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Display breakdown
                        st.caption(f"Breakdown: {', '.join([f'{k}: {v:,}' for k, v in severity_counts.items()])}")
                    else:
                        st.info("No severity data available")
                    with st.expander("Interpretation: Severity Distribution"):
                        st.markdown("""
                        **What this chart shows:**
                        - **CRITICAL (Red)**: Immediate action required - attacks with score > 0.9
                        - **HIGH (Orange)**: Urgent attention needed - attacks with score 0.7-0.9
                        - **MEDIUM (Yellow)**: Monitor closely - attacks with score 0.5-0.7
                        - **LOW (Blue)**: Minor anomalies - attacks with score < 0.5
                        
                        **Insight**: A larger proportion of CRITICAL alerts indicates a serious security threat requiring immediate response.
                        """)
                
                with viz_col2:
                    # Timeline
                    df_alerts['minute'] = df_alerts['timestamp'].dt.floor('1min')
                    timeline = df_alerts.groupby('minute').size().reset_index(name='count')
                    
                    plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                    line_color = '#00ff9d' if st.session_state.theme == 'dark' else '#0066cc'
                    
                    fig_timeline = px.line(
                        timeline,
                        x='minute',
                        y='count',
                        title="Attacks per Minute",
                        labels={'minute': 'Time', 'count': 'Attack Count'},
                        template=plotly_template
                    )
                    fig_timeline.update_traces(line_color=line_color, line_width=2)
                    fig_timeline.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
                    with st.expander("Interpretation: Attack Timeline"):
                        st.markdown("""
                        **What this chart shows:**
                        - **X-axis**: Time (grouped by minute)
                        - **Y-axis**: Number of attacks detected per minute
                        
                        **Insight**: 
                        - **Spikes**: Indicate coordinated attacks or DoS attempts
                        - **Steady increase**: Suggests ongoing infiltration
                        - **Sudden drops**: May indicate successful mitigation or attacker pause
                        - **Patterns**: Help identify attack windows and plan defenses
                        """)
                
                # Attack score distribution
                st.subheader("Attack Score Distribution")
                
                plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                bar_color = '#ff4757' if st.session_state.theme == 'dark' else '#dc3545'
                
                fig_hist = px.histogram(
                    df_alerts,
                    x='attack_score',
                    nbins=20,
                    title="Distribution of Attack Scores",
                    labels={'attack_score': 'Attack Score', 'count': 'Frequency'},
                    color_discrete_sequence=[bar_color],
                    template=plotly_template
                )
                fig_hist.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                with st.expander("Interpretation: Attack Score Distribution"):
                    st.markdown("""
                    **What this chart shows:**
                    - **X-axis**: Attack score (0.0 to 1.0) - higher = more anomalous
                    - **Y-axis**: Frequency (how many attacks have each score)
                    
                    **Insight**:
                    - **Right-skewed (high scores)**: Many severe attacks detected
                    - **Left-skewed (low scores)**: Mostly minor anomalies
                    - **Normal distribution**: Mixed threat levels
                    - **Bimodal**: Two distinct attack types (e.g., DoS vs. intrusion)
                    
                    **Action**: Focus resources on high-score attacks (right side of chart).
                    """)
                
                # Protocol and Service analysis
                viz_col3, viz_col4 = st.columns(2)
                
                with viz_col3:
                    if 'data' in df_alerts.columns:
                        protocols = df_alerts['data'].apply(lambda x: x.get('protocol_type', 'N/A') if isinstance(x, dict) else 'N/A')
                        protocol_counts = protocols.value_counts()
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        bar_color = '#0fbcf9' if st.session_state.theme == 'dark' else '#0dcaf0'
                        
                        fig_protocol = px.bar(
                            x=protocol_counts.index,
                            y=protocol_counts.values,
                            title="Attacks by Protocol",
                            labels={'x': 'Protocol', 'y': 'Count'},
                            color_discrete_sequence=[bar_color],
                            template=plotly_template
                        )
                        fig_protocol.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_protocol, use_container_width=True)
                        with st.expander("Interpretation: Attacks by Protocol"):
                            st.markdown("""
                            **What this chart shows:**
                            - **X-axis**: Network protocols (TCP, UDP, ICMP, etc.)
                            - **Y-axis**: Number of attacks using each protocol
                            
                            **Insight**:
                            - **TCP dominance**: Common for most attacks (web, SSH, etc.)
                            - **UDP spikes**: Often indicates DoS/DDoS attacks
                            - **ICMP**: May indicate reconnaissance or ping floods
                            
                            **Action**: Implement protocol-specific filtering for high-risk protocols.
                            """)
                
                with viz_col4:
                    if 'data' in df_alerts.columns:
                        services = df_alerts['data'].apply(lambda x: x.get('service', 'N/A') if isinstance(x, dict) else 'N/A')
                        service_counts = services.value_counts().head(10)
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        bar_color = '#ffa502' if st.session_state.theme == 'dark' else '#fd7e14'
                        
                        fig_service = px.bar(
                            x=service_counts.index,
                            y=service_counts.values,
                            title="Top 10 Attacked Services",
                            labels={'x': 'Service', 'y': 'Count'},
                            color_discrete_sequence=[bar_color],
                            template=plotly_template
                        )
                        fig_service.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_service, use_container_width=True)
                        with st.expander("Interpretation: Top Attacked Services"):
                            st.markdown("""
                            **What this chart shows:**
                            - **X-axis**: Network services (HTTP, FTP, SSH, etc.)
                            - **Y-axis**: Number of attacks targeting each service
                            
                            **Insight**:
                            - **High-value targets**: Services with most attacks need extra protection
                            - **Common targets**: HTTP/HTTPS often targeted (web attacks)
                            - **Critical services**: SSH, FTP indicate credential attacks
                            - **Unusual services**: Rare service attacks may indicate zero-day exploits
                            
                            **Action**: Prioritize security patches and monitoring for top-targeted services.
                            """)
                
                # Additional Advanced Visualizations for Alerts
                st.subheader("Advanced Analytics")
                
                # Row 1: Data Transfer and Connection Analysis
                adv_col1, adv_col2 = st.columns(2)
                
                with adv_col1:
                    # Data Transfer Analysis
                    if 'data' in df_alerts.columns:
                        data_list = []
                        for idx, row in df_alerts.iterrows():
                            data = row.get('data', {})
                            if isinstance(data, dict):
                                data_list.append({
                                    'src_bytes': data.get('src_bytes', 0),
                                    'dst_bytes': data.get('dst_bytes', 0),
                                    'severity': row.get('severity', 'UNKNOWN'),
                                    'attack_score': row.get('attack_score', 0),
                                    'protocol': data.get('protocol_type', 'N/A'),
                                    'service': data.get('service', 'N/A'),
                                    'count': data.get('count', 0)
                                })
                        
                        if data_list:
                            transfer_df = pd.DataFrame(data_list)
                            
                            plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                            
                            if st.session_state.theme == 'dark':
                                color_map = {
                                    'CRITICAL': '#ff4757',
                                    'HIGH': '#ffa502',
                                    'MEDIUM': '#ffd32a',
                                    'LOW': '#0fbcf9'
                                }
                            else:
                                color_map = {
                                    'CRITICAL': '#dc3545',
                                    'HIGH': '#fd7e14',
                                    'MEDIUM': '#ffc107',
                                    'LOW': '#0dcaf0'
                                }
                            
                            fig_scatter = px.scatter(
                                transfer_df,
                                x='src_bytes',
                                y='dst_bytes',
                                color='severity',
                                size='attack_score',
                                hover_data=['protocol', 'service', 'count'],
                                title="Data Transfer Pattern Analysis",
                                labels={'src_bytes': 'Source Bytes', 'dst_bytes': 'Destination Bytes'},
                                color_discrete_map=color_map,
                                template=plotly_template
                            )
                            fig_scatter.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)',
                                font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                            )
                            st.plotly_chart(fig_scatter, use_container_width=True)
                            with st.expander("Interpretation: Data Transfer Patterns"):
                                st.markdown("""
                                **What this chart shows:**
                                - **X-axis**: Source bytes (data sent)
                                - **Y-axis**: Destination bytes (data received)
                                - **Color**: Severity level
                                - **Size**: Attack score
                                
                                **Insight**:
                                - **Top-right clusters**: High data transfer (potential exfiltration)
                                - **Bottom-right**: High upload, low download (data exfiltration)
                                - **Top-left**: Low upload, high download (normal browsing)
                                - **Large bubbles**: High severity threats
                                
                                **Action**: Investigate high source byte transfers as potential data exfiltration.
                                """)
                
                with adv_col2:
                    # Connection Pattern Analysis
                    if 'data' in df_alerts.columns:
                        conn_list = []
                        for idx, row in df_alerts.iterrows():
                            data = row.get('data', {})
                            if isinstance(data, dict):
                                conn_list.append({
                                    'count': data.get('count', 0),
                                    'srv_count': data.get('srv_count', data.get('count', 0)),
                                    'severity': row.get('severity', 'UNKNOWN'),
                                    'attack_score': row.get('attack_score', 0),
                                    'service': data.get('service', 'N/A'),
                                    'protocol': data.get('protocol_type', 'N/A')
                                })
                        
                        if conn_list:
                            conn_df = pd.DataFrame(conn_list)
                            
                            plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                            
                            if st.session_state.theme == 'dark':
                                color_map = {
                                    'CRITICAL': '#ff4757',
                                    'HIGH': '#ffa502',
                                    'MEDIUM': '#ffd32a',
                                    'LOW': '#0fbcf9'
                                }
                            else:
                                color_map = {
                                    'CRITICAL': '#dc3545',
                                    'HIGH': '#fd7e14',
                                    'MEDIUM': '#ffc107',
                                    'LOW': '#0dcaf0'
                                }
                            
                            fig_conn = px.scatter(
                                conn_df,
                                x='count',
                                y='srv_count',
                                color='severity',
                                size='attack_score',
                                hover_data=['service', 'protocol'],
                                title="Connection Pattern Analysis",
                                labels={'count': 'Total Connections', 'srv_count': 'Service Connections'},
                                color_discrete_map=color_map,
                                template=plotly_template
                            )
                            fig_conn.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)', 
                                plot_bgcolor='rgba(0,0,0,0)',
                                font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                            )
                            st.plotly_chart(fig_conn, use_container_width=True)
                            with st.expander("Interpretation: Connection Patterns"):
                                st.markdown("""
                                **What this chart shows:**
                                - **X-axis**: Total connection count
                                - **Y-axis**: Service connection count
                                - **Color**: Severity level
                                
                                **Insight**:
                                - **High count, high srv_count**: DoS/DDoS attack pattern
                                - **Diagonal line**: Normal correlation between connections
                                - **Outliers**: Unusual connection patterns requiring investigation
                                
                                **Action**: Monitor connections with count > 50 as potential DoS attacks.
                                """)
                
                # Row 2: Flag Distribution
                if 'data' in df_alerts.columns:
                    flag_list = []
                    for idx, row in df_alerts.iterrows():
                        data = row.get('data', {})
                        if isinstance(data, dict) and 'flag' in data:
                            flag_list.append(data['flag'])
                    
                    if flag_list:
                        flag_counts = pd.Series(flag_list).value_counts()
                        
                        plotly_template = "plotly_dark" if st.session_state.theme == 'dark' else "plotly_white"
                        
                        fig_flag = px.bar(
                            x=flag_counts.index,
                            y=flag_counts.values,
                            title="Attack Distribution by Connection Flag",
                            labels={'x': 'Flag Type', 'y': 'Count'},
                            color=flag_counts.values,
                            color_continuous_scale='Reds',
                            template=plotly_template
                        )
                        fig_flag.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color='#f0f4f8' if st.session_state.theme == 'dark' else '#212529'
                        )
                        st.plotly_chart(fig_flag, use_container_width=True)
                        with st.expander("Interpretation: Flag Distribution"):
                            st.markdown("""
                            **What this chart shows:**
                            - **X-axis**: Connection flags (SF, S0, REJ, etc.)
                            - **Y-axis**: Number of attacks with each flag
                            
                            **Flag Meanings**:
                            - **SF**: SYN-FIN flag (normal established connection) - **If highest, indicates sophisticated attacks using normal-looking connections to evade detection**
                            - **S0**: Connection attempt without established connection (suspicious if high)
                            - **REJ**: Rejected connection (clear attack indicator)
                            - **RSTO**: Reset from origin (suspicious - connection reset by source)
                            - **RSTR**: Reset to origin (suspicious - connection reset to source)
                            - **SH**: SYN-ACK-Half open (suspicious)
                            
                            **Key Insight**:
                            - **High SF count**: Advanced persistent threats (APTs) or data exfiltration using normal connections
                            - **High S0/REJ**: Port scanning or connection probing attacks
                            - **High RSTO/RSTR**: Network reconnaissance or connection hijacking attempts
                            
                            **Action**: 
                            - If SF is highest: Investigate data transfer patterns and connection duration (sophisticated attacks)
                            - Monitor REJ, RSTO, RSTR flags as clear attack indicators
                            - High SF with high data transfer = potential data exfiltration
                            """)
            else:
                st.info("No live alerts available. Start monitoring to see real-time attack visualizations.")
        else:
            st.info("No live alerts available. Start monitoring to see real-time attack visualizations.")



# TAB 2: Live Alerts
with tab2:
    st.subheader("Live Alert Feed")
    
    # Real-time monitoring simulation
    if model_data:
        traffic_type = st.selectbox("Traffic Type", ["Random (50% Normal, 50% Attack)", "Normal Traffic", "Attack Traffic"], key="live_traffic_type")
        traffic_type_map = {
            "Random (50% Normal, 50% Attack)": "random",
            "Normal Traffic": "normal",
            "Attack Traffic": "attack"
        }
        
        if st.button("Analyze New Traffic Sample", key="btn_live_analyze_2"):
            with st.spinner("Analyzing network traffic..."):
                sample_traffic = simulate_traffic(traffic_type_map[traffic_type])
                
                # Show what type of traffic is being analyzed
                if traffic_type_map[traffic_type] == 'normal':
                    st.info(f"Analyzing **Normal Traffic** sample (should be classified as normal)...")
                elif traffic_type_map[traffic_type] == 'attack':
                    st.info(f"Analyzing **Attack Traffic** sample (should be classified as attack)...")
                else:
                    st.info(f"Analyzing **Random Traffic** sample (50% normal, 50% attack)...")
                
                result = detect_attack(sample_traffic, model_data)
                
                if result:
                    # Debug info
                    expected_type = traffic_type_map[traffic_type]
                    actual_type = "ATTACK" if result['is_attack'] else "NORMAL"
                    
                    if result['is_attack']:
                        # It's an attack - save alert and notify
                        save_alert(result)
                        st.session_state.alert_count += 1
                        
                        # Show warning if normal traffic was expected but attack detected
                        if expected_type == 'normal':
                            st.warning("⚠️ **Note:** Normal traffic was expected, but model detected an anomaly. This may indicate the simulated pattern doesn't match training data patterns.")
                        
                        # Send email for all attacks (CRITICAL, HIGH, MEDIUM)
                        email_sent = send_alert_email(result)
                        if email_sent:
                            st.success(f"Email alert sent to {EMAIL_CONFIG['admin_email']}")
                        elif EMAIL_CONFIG['enabled']:
                            st.warning("Email configured but sending failed. Check email settings.")
                        
                        st.error(f"**ATTACK DETECTED**")
                        st.markdown(f"**Severity:** {result['severity']}")
                        st.markdown(f"**Attack Score:** {result['attack_score']:.4f}")
                        st.markdown(f"**Prediction:** Anomaly (Cluster: {result['prediction']})")
                        st.json(result)
                    else:
                        # Normal traffic - show success message
                        st.success("**NORMAL TRAFFIC DETECTED**")
                        st.markdown(f"**Status:** Safe - No threats found")
                        st.markdown(f"**Anomaly Score:** {result['attack_score']:.4f}")
                        st.info("This traffic pattern matches known normal behavior. No action required.")
                        
                        # Show warning if attack traffic was expected but normal detected
                        if expected_type == 'attack':
                            st.warning("⚠️ **Note:** Attack traffic was expected, but model classified it as normal. The simulated attack pattern may not be strong enough.")
                        
                        # Show traffic details
                        data = result.get('data', {})
                        if isinstance(data, dict):
                            st.markdown("**Traffic Details:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"Protocol: {data.get('protocol_type', 'N/A')}")
                                st.write(f"Service: {data.get('service', 'N/A')}")
                                st.write(f"Flag: {data.get('flag', 'N/A')}")
                            with col2:
                                st.write(f"Source Bytes: {data.get('src_bytes', 0):,}")
                                st.write(f"Connections: {data.get('count', 0)}")
                                st.write(f"Logged In: {'Yes' if data.get('logged_in', 0) else 'No'}")
                else:
                    st.error("Failed to analyze traffic. Please try again.")
        
        # Display alerts (only show actual attacks, not normal traffic)
        alerts = load_alerts()
        # Filter to only show actual attacks
        attack_alerts = [a for a in alerts if a.get('is_attack', False) and a.get('severity', '') != 'NORMAL']
        
        if attack_alerts:
            st.markdown(f"### Recent Attack Alerts ({len(attack_alerts)} total)")
            for alert in reversed(attack_alerts[-20:]):  # Show last 20
                severity = alert.get('severity', 'UNKNOWN')
                timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%H:%M:%S")
                score = alert.get('attack_score', 0)
                
                # Skip if severity is NORMAL (shouldn't happen, but safety check)
                if severity == "NORMAL":
                    continue
                
                if severity == "CRITICAL":
                    color_class = "critical"
                    severity_label = "CRITICAL"
                elif severity == "HIGH":
                    color_class = "high"
                    severity_label = "HIGH"
                elif severity == "MEDIUM":
                    color_class = "medium"
                    severity_label = "MEDIUM"
                else:
                    color_class = "low"
                    severity_label = "LOW"
                
                with st.expander(f"{severity_label} - {timestamp} (Score: {score:.4f})", expanded=(severity=="CRITICAL")):
                    st.markdown(f'<div class="alert-box {color_class}">', unsafe_allow_html=True)
                    data = alert.get('data', {})
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.write(f"**Protocol:** {data.get('protocol_type', 'N/A')}")
                        st.write(f"**Service:** {data.get('service', 'N/A')}")
                    with col_b:
                        st.write(f"**Src Bytes:** {data.get('src_bytes', 'N/A')}")
                        st.write(f"**Dst Bytes:** {data.get('dst_bytes', 'N/A')}")
                    with col_c:
                        st.write(f"**Connections:** {data.get('count', 'N/A')}")
                        st.write(f"**Flag:** {data.get('flag', 'N/A')}")
                    
                    if data.get('src_ip'):
                        st.write(f"**Source IP:** {data.get('src_ip')} → **Dest IP:** {data.get('dst_ip')}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No alerts to display")



# TAB 3: Test Data Input
with tab3:
    st.subheader("Test Network Data - Normal or Attack?")
    st.markdown("Upload CSV file or manually enter network traffic data to test if it's normal or an attack.")
    
    if not model_data:
        st.error("Model not loaded! Please ensure 'ghf_art_model.pkl' exists. Run train_model.py first.")
    else:
        # Test Data Input Section
        st.markdown("### Test Your Network Data")
        test_mode = st.radio("Choose input method:", ["Upload CSV File", "Manual Entry", "Simulate Random Traffic"], horizontal=True)
        
        if test_mode == "Upload CSV File":
            uploaded_file = st.file_uploader("Upload network traffic CSV file", type=['csv'])
            if uploaded_file:
                try:
                    test_df = pd.read_csv(uploaded_file)
                    st.success(f"Loaded {len(test_df)} records")
                    
                    if st.button("Analyze Uploaded Data", key="btn_upload_analyze"):
                        with st.spinner("Analyzing network traffic..."):
                            results = []
                            for idx, row in test_df.iterrows():
                                result = detect_attack(row.to_dict(), model_data)
                                if result:
                                    results.append(result)
                                    if result['is_attack']:
                                        save_alert(result)
                            
                            if results:
                                st.success(f"Analysis complete: {len(results)} records processed")
                                attack_count = sum(1 for r in results if r['is_attack'])
                                st.metric("Attacks Detected", attack_count, delta=f"{attack_count}/{len(results)}")
                                
                                # Show results table
                                results_df = pd.DataFrame(results)
                                st.dataframe(results_df[['timestamp', 'is_attack', 'severity', 'attack_score']], use_container_width=True)
                                
                                # Download results
                                csv_results = results_df.to_csv(index=False)
                                st.download_button("Download Results", csv_results, "test_results.csv", "text/csv", key="btn_download_results")
                except Exception as e:
                    st.error(f"Error processing file: {e}")
        
        elif test_mode == "Manual Entry":
            st.markdown("**Enter Network Traffic Parameters:**")
            st.info("💡 **Tip:** Use default values for normal traffic patterns, or adjust values to test attack scenarios.")
        
            col1, col2 = st.columns(2)
            
            with col1:
                duration = st.number_input("Duration (seconds)", value=10, step=1, min_value=0, help="Normal: 0-200, Attack: 100-1000")
                protocol_type = st.selectbox("Protocol Type", ['tcp', 'udp', 'icmp'], help="Normal: tcp/udp, Attack: any")
                service = st.selectbox("Service", ['http', 'ftp', 'smtp', 'telnet', 'private', 'domain', 'ssh', 'other'], help="Normal: http/ftp/smtp/domain/ssh, Attack: private/telnet")
                flag = st.selectbox("Flag", ['SF', 'S0', 'REJ', 'RSTO', 'SH', 'RSTR', 'S1'], help="Normal: SF/S0, Attack: REJ/RSTO/RSTR")
                src_bytes = st.number_input("Source Bytes", value=1000, step=100, min_value=0, help="Normal: 0-5000, Attack: 5000-50000")
                dst_bytes = st.number_input("Destination Bytes", value=500, step=100, min_value=0, help="Normal: 0-2000, Attack: 1000-10000")
        
            with col2:
                count = st.number_input("Connection Count", value=5, step=1, min_value=1, help="Normal: 1-10, Attack: 50-500")
                logged_in = st.selectbox("Logged In", [0, 1], index=1, help="Normal: 1, Attack: 0 or 1")
                num_failed_logins = st.number_input("Failed Logins", value=0, step=1, min_value=0, help="Normal: 0, Attack: 1-5")
                root_shell = st.selectbox("Root Shell", [0, 1], index=0, help="Normal: 0, Attack: 0 or 1")
                hot = st.number_input("Hot Indicators", value=0, step=1, min_value=0, help="Normal: 0-2, Attack: 5-30")
                num_file_creations = st.number_input("File Creations", value=0, step=1, min_value=0, help="Normal: 0-2, Attack: 0-20")
        
            if st.button("Analyze Manual Entry", key="btn_manual_analyze") and model_data:
                with st.spinner("Analyzing network traffic..."):
                    # Calculate rates based on count for more realistic patterns
                    same_srv_rate = 0.9 if count > 0 else 0.0  # Normal traffic has high same service rate
                    diff_srv_rate = 1.0 - same_srv_rate
                    
                    manual_data = {
                        'duration': duration,
                        'protocol_type': protocol_type,
                        'service': service,
                        'flag': flag,
                        'src_bytes': src_bytes,
                        'dst_bytes': dst_bytes,
                        'land': 0,  # Normal traffic rarely has land=1
                        'wrong_fragment': 0,  # Normal traffic has no wrong fragments
                        'urgent': 0,  # Normal traffic rarely urgent
                        'hot': hot,
                        'num_failed_logins': num_failed_logins,
                        'logged_in': logged_in,
                        'num_compromised': 0,  # Normal traffic has no compromised indicators
                        'root_shell': root_shell,
                        'su_attempted': 0,  # Normal traffic has no su attempts
                        'num_root': 0,  # Normal traffic has no root access
                        'num_file_creations': num_file_creations,
                        'num_shells': 0,  # Normal traffic has no shells
                        'num_access_files': min(num_file_creations, 2),  # Low file access for normal
                        'num_outbound_cmds': 0,  # Normal traffic has no outbound commands
                        'is_host_login': 0,  # Usually not host login
                        'is_guest_login': 0,  # Usually not guest login
                        'count': count,
                        'srv_count': count,  # Same as count for normal traffic
                        'serror_rate': 0.05 if count > 0 else 0.0,  # Low error rates for normal
                        'srv_serror_rate': 0.05 if count > 0 else 0.0,
                        'rerror_rate': 0.05 if count > 0 else 0.0,
                        'srv_rerror_rate': 0.05 if count > 0 else 0.0,
                        'same_srv_rate': same_srv_rate,  # High same service rate for normal
                        'diff_srv_rate': diff_srv_rate,
                        'srv_diff_host_rate': 0.1,  # Low different host rate
                        'dst_host_count': max(1, count // 2),  # Proportional to count
                        'dst_host_srv_count': max(1, count // 2),
                        'dst_host_same_srv_rate': 0.9,  # High same service rate
                        'dst_host_diff_srv_rate': 0.1,
                        'dst_host_same_src_port_rate': 0.9,  # High same port rate
                        'dst_host_srv_diff_host_rate': 0.1,
                        'dst_host_serror_rate': 0.05,  # Low error rates
                        'dst_host_srv_serror_rate': 0.05,
                        'dst_host_rerror_rate': 0.05,
                        'dst_host_srv_rerror_rate': 0.05
                    }
                    
                    result = detect_attack(manual_data, model_data)
                    
                    if result:
                        if result['is_attack']:
                            save_alert(result)
                            st.session_state.alert_count += 1
                            
                            # Send email for all attacks
                            email_sent = send_alert_email(result)
                            if email_sent:
                                st.success(f"Email alert sent to {EMAIL_CONFIG['admin_email']}")
                            elif EMAIL_CONFIG['enabled']:
                                st.warning("Email configured but sending failed. Check email settings.")
                            
                            st.error(f"**ATTACK DETECTED**")
                            st.markdown(f"**Severity:** {result['severity']}")
                            st.markdown(f"**Attack Score:** {result['attack_score']:.4f}")
                            st.markdown(f"**Prediction:** Anomaly (Cluster: {result['prediction']})")
                            
                            # Show interpretation
                            if result['attack_score'] > 0.9:
                                st.warning("**CRITICAL**: This traffic pattern strongly indicates a malicious attack. Immediate investigation required.")
                            elif result['attack_score'] > 0.7:
                                st.warning("**HIGH**: Suspicious activity detected. Review connection patterns and source IP.")
                            else:
                                st.info("**MODERATE**: Unusual traffic pattern detected. Monitor for further anomalies.")
                        else:
                            # Normal traffic
                            st.success("**NORMAL TRAFFIC**")
                            st.markdown(f"**Status:** Safe - No threats found")
                            st.markdown(f"**Anomaly Score:** {result['attack_score']:.4f}")
                            st.info("This traffic pattern matches known normal behavior. No action required.")
                        
                        st.json(result)
                    else:
                        st.error("Failed to analyze traffic. Please try again.")
        
        elif test_mode == "Simulate Random Traffic":
            # Real-time monitoring simulation
            traffic_type = st.selectbox("Traffic Type", ["Random (50% Normal, 50% Attack)", "Normal Traffic", "Attack Traffic"], key="simulate_traffic_type")
            traffic_type_map = {
                "Random (50% Normal, 50% Attack)": "random",
                "Normal Traffic": "normal",
                "Attack Traffic": "attack"
            }
            
            if st.button("Analyze New Traffic Sample", key="btn_simulate_analyze"):
                with st.spinner("Analyzing network traffic..."):
                    sample_traffic = simulate_traffic(traffic_type_map[traffic_type])
                    result = detect_attack(sample_traffic, model_data)
                    
                    if result:
                        if result['is_attack']:
                            # It's an attack
                            save_alert(result)
                            st.session_state.alert_count += 1
                            
                            # Send email for all attacks
                            email_sent = send_alert_email(result)
                            if email_sent:
                                st.success(f"Email alert sent to {EMAIL_CONFIG['admin_email']}")
                            elif EMAIL_CONFIG['enabled']:
                                st.warning("Email configured but sending failed. Check email settings.")
                            
                            st.error(f"**ATTACK DETECTED**")
                            st.markdown(f"**Severity:** {result['severity']}")
                            st.markdown(f"**Attack Score:** {result['attack_score']:.4f}")
                            st.markdown(f"**Prediction:** Anomaly (Cluster: {result['prediction']})")
                            st.json(result)
                        else:
                            # Normal traffic
                            st.success("**NORMAL TRAFFIC**")
                            st.markdown(f"**Status:** Safe - No threats found")
                            st.markdown(f"**Anomaly Score:** {result['attack_score']:.4f}")
                            st.info("This traffic pattern matches known normal behavior. No action required.")
                            st.json(result)
                    else:
                        st.error("Failed to analyze traffic. Please try again.")
            
            # Show recent alerts in test mode too
            attack_alerts = [a for a in load_alerts() if a.get('is_attack', False) and a.get('severity', '') != 'NORMAL']
            if attack_alerts:
                st.markdown("---")
                st.markdown(f"### Recent Detected Attacks")
                for alert in reversed(attack_alerts[-5:]):  # Show last 5
                    severity = alert.get('severity', 'UNKNOWN')
                    timestamp = datetime.fromisoformat(alert['timestamp']).strftime("%H:%M:%S")
                    score = alert.get('attack_score', 0)
                    
                    if severity == "NORMAL": continue
                    
                    with st.expander(f"{severity} - {timestamp} (Score: {score:.4f})"):
                        st.json(alert)



# TAB 4: ChatOps
with tab4:
    st.subheader("ChatOps Assistant")
    
    if st.session_state.chatbot and st.session_state.chatbot.df is not None:
        # Helper function to clean HTML from text
        def clean_html(text):
            """Remove HTML tags from text"""
            if not isinstance(text, str):
                text = str(text)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            # Decode HTML entities
            text = html.unescape(text)
            return text.strip()
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg['role'] == 'user':
                    # User messages - clean and display
                    user_content = clean_html(msg['content'])
                    st.markdown(f"""
                    <div class="user-msg">
                        <strong>You:</strong><br>{html.escape(user_content)}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Assistant messages - clean HTML and display as markdown
                    assistant_content = clean_html(msg['content'])
                    st.markdown(f"""
                    <div class="bot-msg">
                        <strong>Assistant:</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    # Display content as markdown (supports **bold**, lists, etc.)
                    st.markdown(assistant_content)
        
        # Chat input
        user_input = st.text_input("Ask about network security:", placeholder="e.g., Show me critical alerts from the last 2 hours", key="chat_input")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            send_btn = st.button("Send", key="btn_chat_send")
        
        if send_btn and user_input:
            st.session_state.chat_messages.append({'role': 'user', 'content': user_input})
            with st.spinner("Analyzing..."):
                response = st.session_state.chatbot.chat(user_input)
            st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        # Quick actions
        st.markdown("---")
        st.markdown("**Quick Actions:**")
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            if st.button("Security Summary", key="btn_quick_summary"):
                st.session_state.chat_messages.append({'role': 'user', 'content': "Give me a security status summary"})
                response = st.session_state.chatbot.chat("Give me a security status summary")
                st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
                st.rerun()
            
            if st.button("Critical Alerts", key="btn_quick_critical"):
                st.session_state.chat_messages.append({'role': 'user', 'content': "Show me critical alerts"})
                response = st.session_state.chatbot.chat("Show me critical alerts")
                st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
                st.rerun()
        
        with quick_col2:
            if st.button("Attack Patterns", key="btn_quick_patterns"):
                st.session_state.chat_messages.append({'role': 'user', 'content': "What attack patterns were detected?"})
                response = st.session_state.chatbot.chat("What attack patterns were detected?")
                st.session_state.chat_messages.append({'role': 'assistant', 'content': response})
                st.rerun()
            
            if st.button("Clear Chat", key="btn_clear_chat"):
                st.session_state.chat_messages = []
                st.rerun()
    else:
        st.warning("Chatbot not available. Ensure network_logs_processed.csv exists.")



# TAB 5: Settings
with tab5:
    st.subheader("System Settings")
    
    st.markdown("### Email Configuration")
    email_status = "Enabled" if EMAIL_CONFIG['enabled'] else "Disabled"
    status_color = "#00ff9d" if EMAIL_CONFIG['enabled'] else "#ff2b2b" if st.session_state.theme == 'dark' else "#dc3545"
    st.markdown(f"""
    <div style="background-color: #1A1C24; padding: 15px; border-radius: 8px; border-left: 4px solid {status_color}; margin: 10px 0; color: #e6e6e6;">
        <strong>Email Alerts:</strong> <span style="color: {status_color}; font-weight: 600;">{email_status}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if EMAIL_CONFIG['enabled']:
        st.write(f"**SMTP Server:** {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
        st.write(f"**Sender Email:** {EMAIL_CONFIG['sender_email']}")
        st.write(f"**Admin Email:** {EMAIL_CONFIG['admin_email']}")
        
        # Test email button
        if st.button("Test Email Configuration", key="btn_test_email"):
            test_alert = {
                'timestamp': datetime.now().isoformat(),
                'severity': 'MEDIUM',
                'attack_score': 0.6,
                'is_attack': True,
                'data': {
                    'protocol_type': 'tcp',
                    'service': 'http',
                    'src_ip': '192.168.1.100',
                    'dst_ip': '10.0.0.1',
                    'src_bytes': 5000,
                    'count': 10
                }
            }
            if send_alert_email(test_alert, force_send=True):
                st.success("Test email sent successfully! Check your inbox.")
            else:
                st.error("Test email failed. Check your email credentials.")
    else:
        st.warning("Email alerts are disabled. Set EMAIL_ENABLED=true in .env file")
        st.write("Configure email settings in `.env` file or `env_template.txt`")
    
    st.markdown("### Model Status")
    if model_data:
        st.success("GHF-ART Model loaded successfully")
    else:
        st.error("Model not found. Run train_model.py first.")
    
    st.markdown("### Data Status")
    if Path('network_logs_processed.csv').exists():
        df_check = pd.read_csv('network_logs_processed.csv')
        st.success(f"Network logs loaded: {len(df_check)} records")
    else:
        st.warning("network_logs_processed.csv not found")
    
    st.markdown("### Maintenance")
    if st.button("Clear Alert History", key="btn_clear_alerts"):
        with open('attack_alerts.json', 'w') as f:
            json.dump([], f)
        st.success("Alert history cleared")
        st.rerun()



# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)



with footer_col1:
    if st.session_state.theme == 'dark':
        status_color = "#00ff9d" if st.session_state.monitoring_active else "#ff2b2b"
    else:
        status_color = "#0066cc" if st.session_state.monitoring_active else "#dc3545"
    status_text = "Monitoring Active" if st.session_state.monitoring_active else "Monitoring Paused"
    st.markdown(f'<span style="color: {status_color}; font-weight: 600;">Status:</span> {status_text}', unsafe_allow_html=True)



with footer_col2:
    st.write(f"**Auto-refresh:** Manual")



with footer_col3:
    st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")