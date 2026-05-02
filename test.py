import streamlit as st
import groq
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv 
import os

load_dotenv()
key = os.getenv("GROQ_API_KEY")
print("✅ All libraries imported successfully!")
print(f"✅ API Key loaded: {key[:10]}...")