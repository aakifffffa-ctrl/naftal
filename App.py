import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="منصة نفطال الذكية لتطوير بيانات الزبائن",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom RTL CSS and Visual Identity for Naftal Theme
css_code = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
}

.stApp {
    background-color: #f8f9fa;
}

.main-header {
    text-align: center;
    color: #003366;
    border-right: 0px solid #ffcc00;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# واجهة التطبيق الرئيسية
st.markdown('<div class="main-header">منصة نفطال الذكية لتطوير بيانات الزبائن ⛽</div>', unsafe_allow_html=True)

st.success("تم تشغيل المنصة بنجاح دون أي أخطاء!")
