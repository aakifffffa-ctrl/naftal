# -*- coding: utf-8 -*-
"""
منصة نفطال الذكية لتحليل بيانات الزبائن ودعم اتخاذ القرار التسويقي
دراسة حالة: مؤسسة نفطال - خنشلة
مشروع مذكرة تخرج تقني سامي (BTS) - تخصص تسويق
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==========================================
# 1. تهيئة الصفحة والتصميم (Page Config & CSS)
# ==========================================
st.set_page_config(
    page_title="منصة نفطال الذكية لتحليل بيانات الزبائن",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom RTL CSS and Visual Identity for Naftal Theme
st.markdown("""
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
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-right: 8px solid #ffcc00;
    }
    
    .metric-card {
        background-color: white;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-top: 4px solid #1e3c72;
        text-align: center;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1e3c72;
    }
    
    .metric-label {
        font-size: 14px;
        color: #6c757d;
    }
    
    .decision-card {
        background-color: #ffffff;
        border-right: 5px solid #28a745;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .decision-card.high { border-right-color: #dc3545; }
    .decision-card.medium { border-right-color: #ffc107; }
    .decision-card.low { border-right-color: #17a2b8; }
    
    .stAlert {
        direction: rtl;
        text-align: right;
    }
    
    div[data-testid="stSidebar"] {
        background-color: #111827;
        color: white;
    }
    div[data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
""", unsafe_content_style=True)

# ==========================================
# 2. توليد البيانات التجريبية (Synthetic Data)
# ==========================================
@st.cache_data
def generate_synthetic_data():
    """توليد بيانات تجريبية واقعية لمؤسسة توزيع المحروقات بنفطال خنشلة"""
    np.random.seed(42)
    n_records = 1200
    n_customers = 180
    
    customer_ids = [f"CUST-{1000 + i}" for i in range(n_customers)]
    customer_types = ['B2C - أفراد', 'B2B - خواص', 'مؤسسات عمومية']
    type_weights = [0.55, 0.30, 0.15]
    
    municipalities = ['خنشلة (المركز)', 'قايس', 'ششار', 'محمل', 'عين الطويلة', 'بوحمامة', 'طامزة', 'أولاد رشاش']
    muni_weights = [0.35, 0.18, 0.12, 0.10, 0.09, 0.07, 0.05, 0.04]
    
    products = {
        'سيرغاز (GPL/C)': {'price': 9.0, 'unit': 'لتر'},
        'بنزين بدون رصاص': {'price': 45.6, 'unit': 'لتر'},
        'مازوت (المازوت)': {'price': 29.0, 'unit': 'لتر'},
        'زيوت المحركات (Naftalia)': {'price': 2800.0, 'unit': 'قارورة'},
        'قارورات غاز البوتان': {'price': 200.0, 'unit': 'قارورة'},
        'عجلات ومشتقاتها': {'price': 8500.0, 'unit': 'وحدة'}
    }
    
    cust_mapping = {}
    for cid in customer_ids:
        cust_mapping[cid] = {
            'name': f"زبون {cid}",
            'type': np.random.choice(customer_types, p=type_weights),
            'muni': np.random.choice(municipalities, p=muni_weights),
            'phone': f"032-{np.random.randint(100000, 999999)}"
        }
        
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 8, 30)
    days_range = (end_date - start_date).days
    
    data = []
    prod_names = list(products.keys())
    
    for i in range(1, n_records + 1):
        cid = np.random.choice(customer_ids)
        c_info = cust_mapping[cid]
        prod = np.random.choice(prod_names, p=[0.25, 0.30, 0.25, 0.10, 0.07, 0.03])
        
        # الكميات حسب المنتج
        if 'زيوت' in prod or 'عجلات' in prod:
            qty = np.random.randint(1, 5)
        elif 'قارورات' in prod:
            qty = np.random.randint(1, 20)
        else:
            qty = np.random.randint(15, 500) if c_info['type'] != 'B2C - أفراد' else np.random.randint(10, 60)
            
        unit_price = products[prod]['price']
        total_price = qty * unit_price
        
        tx_date = start_date + timedelta(days=np.random.randint(0, days_range))
        
        data.append({
            'معرف_العملية': f"TXN-{10000 + i}",
            'معرف_الزبون': cid,
            'اسم_الزبون': c_info['name'],
            'نوع_الزبون': c_info['type'],
            'البلدية': c_info['muni'],
            'رقم_الهاتف': c_info['phone'],
            'تاريخ_العملية': tx_date,
            'المنتج': prod,
            'الكمية': qty,
            'سعر_الوحدة': unit_price,
            'المبلغ_الإجمالي': total_price
        })
        
    df = pd.DataFrame(data)
    df['تاريخ_العملية'] = pd.to_datetime(df['تاريخ_العملية'])
    return df

# ==========================================
# 3. محرك معالجة البيانات وتنظيفها
# ==========================================
def clean_and_preprocess_data(df):
    """تنظيف البيانات واكتشاف الأخطاء وتوحيد الأنساق"""
    report = {}
    report['original_rows'] = len(df)
    
    # حذف التكرارات
    df = df.drop_duplicates()
    report['duplicates_removed'] = report['original_rows'] - len(df)
    
    # التعامل مع التواريخ
    date_col = [col for col in df.columns if 'تاريخ' in col or 'date' in col.lower()]
    if date_col:
        df[date_col[0]] = pd.to_datetime(df[date_col[0]], errors='coerce')
        df = df.dropna(subset=[date_col[0]])
        report['date_column'] = date_col[0]
    
    # التعامل مع المبالغ
    amount_col = [col for col in df.columns if 'مبلغ' in col or 'إجمالي' in col or 'amount' in col.lower() or 'total' in col.lower()]
    if amount_col:
        df[amount_col[0]] = pd.to_numeric(df[amount_col[0]], errors='coerce').fillna(0)
        report['amount_column'] = amount_col[0]
        
    report['clean_rows'] = len(df)
    report['unique_customers'] = df['معرف_الزبون'].nunique() if 'معرف_الزبون' in df.columns else 0
    report['missing_values'] = df.isnull().sum().sum()
    
    return df, report

# ==========================================
# 4. محرك تحليل RFM و Segmentation
# ==========================================
def calculate_rfm(df, ref_date=None):
    """حساب مؤشرات RFM وتقسيم الزبائن"""
    if ref_date is None:
        ref_date = df['تاريخ_العملية'].max() + timedelta(days=1)
        
    rfm = df.groupby('معرف_الزبون').agg({
        'تاريخ_العملية': lambda x: (ref_date - x.max()).days,
        'معرف_العملية': 'count',
        'المبلغ_الإجمالي': 'sum',
        'اسم_الزبون': 'first',
        'نوع_الزبون': 'first',
        'البلدية': 'first',
        'رقم_الهاتف': 'first'
    }).reset_index()
    
    rfm.columns = ['معرف_الزبون', 'Recency', 'Frequency', 'Monetary', 'اسم_الزبون', 'نوع_الزبون', 'البلدية', 'رقم_الهاتف']
    
    # حساب الأوساط للدرجات
    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), q=4, labels=[4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
    except Exception:
        # Fallback if qcut fails
        rfm['R_Score'] = pd.cut(rfm['Recency'], bins=4, labels=[4, 3, 2, 1])
        rfm['F_Score'] = pd.cut(rfm['Frequency'], bins=4, labels=[1, 2, 3, 4])
        rfm['M_Score'] = pd.cut(rfm['Monetary'], bins=4, labels=[1, 2, 3, 4])

    rfm['R_Score'] = rfm['R_Score'].astype(int)
    rfm['F_Score'] = rfm['F_Score'].astype(int)
    rfm['M_Score'] = rfm['M_Score'].astype(int)
    
    # دمج الدرجات
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    # تصنيف الشريحة
    def assign_segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 3 and f >= 3 and m >= 3:
            return 'Champions (الأبطال)'
        elif r >= 3 and f >= 2:
            return 'Loyal Customers (الزبائن الأوفياء)'
        elif r >= 3 and f == 1:
            return 'New Customers (زبائن جدد)'
        elif r == 2 and f >= 2:
            return 'Need Attention (يحتاجون اهتمام)'
        elif r == 2 and f == 1:
            return 'Promising (واعددون)'
        elif r == 1 and f >= 3:
            return 'Can\'t Lose Them (لا يمكن خسارتهم)'
        elif r == 1 and f == 2:
            return 'At Risk (معرضون للفقدان)'
        else:
            return 'Hibernating / Lost (غائبون / مفقودون)'
            
    rfm['Segment'] = rfm.apply(assign_segment, axis=1)
    
    # درجة المخاطرة
    def assign_risk(r):
        if r <= 1:
            return 'مرتفع جداً'
        elif r == 2:
            return 'متوسط'
        else:
            return 'منخفض'
            
    rfm['Risk_Level'] = rfm['R_Score'].apply(assign_risk)
    
    return rfm

# ==========================================
# 5. تحليلات ABC و Pareto و CLV
# ==========================================
def calculate_abc_pareto(rfm):
    """تحليل ABC و Pareto للزبائن"""
    rfm_sorted = rfm.sort_values(by='Monetary', ascending=False).reset_index(drop=True)
    rfm_sorted['Cum_Monetary'] = rfm_sorted['Monetary'].cumsum()
    total_monetary = rfm_sorted['Monetary'].sum()
    rfm_sorted['Cum_Percentage'] = (rfm_sorted['Cum_Monetary'] / total_monetary) * 100
    
    def abc_classify(perc):
        if perc <= 70:
            return 'A (عالية القيمة جداً)'
        elif perc <= 90:
            return 'B (متوسطة القيمة)'
        else:
            return 'C (منخفضة القيمة)'
            
    rfm_sorted['ABC_Class'] = rfm_sorted['Cum_Percentage'].apply(abc_classify)
    return rfm_sorted

def calculate_clv(rfm):
    """حساب القيمة التراكمية للزبون CLV بطريقة مبسطة ومفسرة"""
    # CLV = Average Value * Purchase Frequency * Estimated Lifespan (Months)
    avg_order = rfm['Monetary'] / rfm['Frequency']
    purchase_freq = rfm['Frequency'] / 18 # فرضية: فترة البيانات 18 شهر
    estimated_lifespan_months = 24
    
    rfm['Estimated_CLV'] = avg_order * purchase_freq * estimated_lifespan_months
    return rfm

# ==========================================
# 6. المساعد الذكي ووظائف اتخاذ القرار
# ==========================================
def generate_decision_center(rfm, df):
    """مولد قرارات مركز دعم القرار التسويقي"""
    decisions = []
    
    # 1. تحليل الزبائن المفقودين
    at_risk_count = len(rfm[rfm['Segment'].str.contains('At Risk|Hibernating')])
    at_risk_pct = (at_risk_count / len(rfm)) * 100
    
    if at_risk_pct > 20:
        decisions.append({
            'title': 'ارتفاع نسبة الزبائن المعرضين للفقدان والغائبين',
            'evidence': f"تبين أن {at_risk_pct:.1f}% من إجمالي الزبائن ({at_risk_count} زبون) لم يقوموا بشراء منذ فترة طويلة.",
            'decision': 'إطلاق حملة تسويقية لإعادة التنشيط (Re-activation Campaign).',
            'action': 'إرسال عروض خاصة وتخفيضات على زيوت المحركات Naftalia للخواص والمؤسسات عبر الاتصال المباشر.',
            'priority': 'عالية',
            'class': 'high'
        })
        
    # 2. تركيز المبيعات (Pareto)
    top_20_count = int(len(rfm) * 0.2)
    top_20_rev = rfm.sort_values(by='Monetary', ascending=False).head(top_20_count)['Monetary'].sum()
    total_rev = rfm['Monetary'].sum()
    top_20_pct = (top_20_rev / total_rev) * 100
    
    decisions.append({
        'title': 'تركيز الإيرادات وفق قاعدة باريتو (20/80)',
        'evidence': f"تحقق أفضل 20% من الشريحة ({top_20_count} زبون) نسبة {top_20_pct:.1f}% من إجمالي المبيعات.",
        'decision': 'تأسيس برنامج رعاية للزبائن الأبطال (VIP Loyalty Program).',
        'action': 'تخصيص مدير حساب خاص للزبائن المؤسساتيين وتسهيلات في سداد شحنات سيرغاز والمازوت.',
        'priority': 'عالية',
        'class': 'high'
    })
    
    # 3. الأداء الجغرافي
    muni_perf = df.groupby('البلدية')['المبلغ_الإجمالي'].sum().sort_values(ascending=False)
    top_muni = muni_perf.index[0]
    lowest_muni = muni_perf.index[-1]
    
    decisions.append({
        'title': f"التفاوت في التغطية الجغرافية بين البلديات ({top_muni} مقابل {lowest_muni})",
        'evidence': f"تتصدر بلدية {top_muni} المبيعات بـ {muni_perf.max():,.0f} د.ج، بينما تسجل {lowest_muni} أدنى حصة بـ {muni_perf.min():,.0f} د.ج.",
        'decision': 'إعادة توزيع الحملات الترويجية الميدانية للبلديات الضعيفة وتوفير مخزون إضافي للمحطات الأكثر طلباً.',
        'action': 'دراسة إمكانية توسيع نقاط توزيع قارورات الغاز والخدمات الملحقة في بلديات الشريط الحدودي والنائي.',
        'priority': 'متوسطة',
        'class': 'medium'
    })
    
    return decisions

# ==========================================
# 7. تحميل البيانات الأساسي والجلسة
# ==========================================
if 'df' not in st.session_state:
    st.session_state.df = generate_synthetic_data()

# Sidebar Setup
st.sidebar.image("https://img.icons8.com/color/96/000000/gas-station.png", width=80)
st.sidebar.title("منصة نفطال الذكية")
st.sidebar.caption("فرع التوزيع - ولاية خنشلة")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "القائمة الرئيسية:",
    [
        "📊 لوحة القيادة (Dashboard)",
        "🧹 إدارة وتنظيف البيانات",
        "🎯 تحليل RFM وتجزئة الزبائن",
        "📈 تحليلات Pareto & ABC",
        "💎 القيمة التراكمية (CLV)",
        "📦 تحليل المنتجات والخدمات",
        "🗺️ التحليل الجغرافي (البلديات)",
        "⚠️ الزبائن المعرضون للفقدان",
        "🗂️ إدارة علاقات الزبائن (CRM)",
        "🎯 مركز دعم القرار التسويقي",
        "🤖 المحلل الذكي (AI Analyst)",
        "📋 التقرير الشامل والتصدير"
    ]
)

# Filtering Mechanism in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 فلاتر عامة للتحليل")
filtered_df = st.session_state.df.copy()

muni_filter = st.sidebar.multiselect("اختر البلدية:", options=filtered_df['البلدية'].unique())
if muni_filter:
    filtered_df = filtered_df[filtered_df['البلدية'].isin(muni_filter)]
    
type_filter = st.sidebar.multiselect("نوع الزبون:", options=filtered_df['نوع_الزبون'].unique())
if type_filter:
    filtered_df = filtered_df[filtered_df['نوع_الزبون'].isin(type_filter)]

# Pre-calculate RFM on filtered data
rfm_df = calculate_rfm(filtered_df)
rfm_df = calculate_clv(rfm_df)

st.sidebar.info("💡 البيانات المعروضة تجريبية لأغراض العرض واختبار نموذج مذكرة التخرج.")

# ==========================================
# 8. عرض الصفحات والمحتوى
# ==========================================

# ------------------------------------------
# PAGE 1: Dashboard
# ------------------------------------------
if menu == "📊 لوحة القيادة (Dashboard)":
    st.markdown("""
        <div class="main-header">
            <h2>منصة نفطال الذكية لتحليل بيانات الزبائن ودعم اتخاذ القرار التسويقي</h2>
            <p>دراسة حالة: مؤسسة نفطال - وحدة التوزيع خنشلة | مذكرة تخرج تقني سامي تسويق</p>
        </div>
    """, unsafe_content_style=True)
    
    # Top Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{rfm_df['معرف_الزبون'].nunique()}</div>
            <div class="metric-label">إجمالي الزبائن</div>
        </div>""", unsafe_content_style=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{len(filtered_df):,}</div>
            <div class="metric-label">إجمالي العمليات</div>
        </div>""", unsafe_content_style=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{filtered_df['المبلغ_الإجمالي'].sum():,.0f} د.ج</div>
            <div class="metric-label">إجمالي المبيعات</div>
        </div>""", unsafe_content_style=True)
    with col4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{filtered_df['المبلغ_الإجمالي'].mean():,.0f} د.ج</div>
            <div class="metric-label">متوسط قيمة العملية</div>
        </div>""", unsafe_content_style=True)

    st.markdown("<br>", unsafe_content_style=True)
    
    col5, col6, col7, col8 = st.columns(4)
    active_pct = (len(rfm_df[rfm_df['R_Score'] >= 3]) / len(rfm_df)) * 100
    risk_pct = (len(rfm_df[rfm_df['Risk_Level'] == 'مرتفع جداً']) / len(rfm_df)) * 100
    top_prod = filtered_df.groupby('المنتج')['المبلغ_الإجمالي'].sum().idxmax()
    top_muni = filtered_df.groupby('البلدية')['المبلغ_الإجمالي'].sum().idxmax()
    
    with col5:
        st.metric("نسبة الزبائن النشطين", f"{active_pct:.1f}%")
    with col6:
        st.metric("نسبة الخطر العالي", f"{risk_pct:.1f}%")
    with col7:
        st.metric("أفضل منتج إيراداً", top_prod)
    with col8:
        st.metric("أفضل بلدية نشاطاً", top_muni)
        
    st.markdown("---")
    
    # Charts Row
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 تطور المبيعات عبر الزمن")
        df_time = filtered_df.set_index('تاريخ_العملية').resample('M')['المبلغ_الإجمالي'].sum().reset_index()
        fig_time = px.line(df_time, x='تاريخ_العملية', y='المبلغ_الإجمالي', markers=True, color_discrete_sequence=['#1e3c72'])
        fig_time.update_layout(xaxis_title="التاريخ", yaxis_title="الإيرادات (د.ج)")
        st.plotly_chart(fig_time, use_container_width=True)
        
    with c2:
        st.subheader("📊 توزيع المبيعات حسب المنتجات")
        df_prod = filtered_df.groupby('المنتج')['المبلغ_الإجمالي'].sum().reset_index()
        fig_prod = px.pie(df_prod, values='المبلغ_الإجمالي', names='المنتج', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_prod, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("🗺️ المبيعات حسب البلديات")
        df_muni = filtered_df.groupby('البلدية')['المبلغ_الإجمالي'].sum().reset_index().sort_values('المبلغ_الإجمالي', ascending=True)
        fig_muni = px.bar(df_muni, x='المبلغ_الإجمالي', y='البلدية', orientation='h', color='المبلغ_الإجمالي', color_continuous_scale='Blues')
        st.plotly_chart(fig_muni, use_container_width=True)
        
    with c4:
        st.subheader("🧩 توزيع الشرائح (RFM Segments)")
        df_seg = rfm_df['Segment'].value_counts().reset_index()
        df_seg.columns = ['Segment', 'Count']
        fig_seg = px.bar(df_seg, x='Segment', y='Count', color='Segment', color_discrete_sequence=px.colors.qualitative.Dark2)
        st.plotly_chart(fig_seg, use_container_width=True)

# ------------------------------------------
# PAGE 2: Data Cleaning
# ------------------------------------------
elif menu == "🧹 إدارة وتنظيف البيانات":
    st.title("🧹 جودة البيانات ومعالجتها")
    st.write("تتيح هذه الصفحة استيراد بيانات جديدة للزبائن والعمليات، وفحص جودتها قبل إجراء التحليلات التسويقية.")
    
    uploaded_file = st.file_uploader("قم برفع ملف CSV أو Excel لحركات البيع:", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            st.session_state.df = df_upload
            st.success("تم رفع البيانات بنجاح وتحديث النظام!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
            
    df_clean, report = clean_and_preprocess_data(st.session_state.df)
    
    st.subheader("📋 تقرير جودة البيانات الحالي (Data Quality Audit)")
    
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.metric("إجمالي السجلات", report['original_rows'])
    q2.metric("السجلات المكررة المحذوفة", report['duplicates_removed'])
    q3.metric("عدد الزبائن الفريدين", report['unique_customers'])
    q4.metric("القيم الناقصة المعالجة", report['missing_values'])
    q5.metric("السجلات الصالحة للتحليل", report['clean_rows'])
    
    st.markdown("---")
    st.subheader("👀 معاينة السجلات الأولى من البيانات")
    st.dataframe(df_clean.head(10), use_container_width=True)

# ------------------------------------------
# PAGE 3: RFM & Segmentation
# ------------------------------------------
elif menu == "🎯 تحليل RFM وتجزئة الزبائن":
    st.title("🎯 تحليل RFM وتجزئة الزبائن (Customer Segmentation)")
    st.markdown("""
    يعتمد نموذج **RFM** على قياس ثلاثة أبعاد جوهرية لسلوك الزبون:
    * **Recency (حداثة الشراء):** كم يوماً مضى منذ آخر عملية شراء؟
    * **Frequency (تكرار الشراء):** كم عدد العمليات المنجزة؟
    * **Monetary (القيمة النقدية):** ما إجمالي ما أنفقه الزبون؟
    """)
    
    st.subheader("📊 ملخص الشرائح التسويقية")
    seg_summary = rfm_df.groupby('Segment').agg(
        عدد_الزبائن=('معرف_الزبون', 'count'),
        إجمالي_الإيرادات=('Monetary', 'sum'),
        متوسط_الانفاق=('Monetary', 'mean'),
        متوسط_تكرار_الشراء=('Frequency', 'mean'),
        متوسط_أيام_الغئاب=('Recency', 'mean')
    ).reset_index()
    
    seg_summary['نسبة_الزبائن'] = (seg_summary['عدد_الزبائن'] / len(rfm_df)) * 100
    st.dataframe(seg_summary.style.format({
        'إجمالي_الإيرادات': '{:,.0f} د.ج',
        'متوسط_الانفاق': '{:,.0f} د.ج',
        'نسبة_الزبائن': '{:.1f}%',
        'متوسط_تكرار_الشراء': '{:.1f}',
        'متوسط_أيام_الغئاب': '{:.0f} يوم'
    }), use_container_width=True)
    
    st.markdown("---")
    st.subheader("💡 التوصيات والإجراءات التسويقية لكل شريحة")
    
    seg_dict = {
        'Champions (الأبطال)': 'الحفاظ عليهم عبر خدمات VIP تخصيص مدراء حسابات وتقديم أولوية التوزيع.',
        'Loyal Customers (الزبائن الأوفياء)': 'بناء برنامج مكافآت وتوفير تسهيلات دفع لتشجيع زيادة أحجام الطلبيات.',
        'New Customers (زبائن جدد)': 'تقديم دليل ترحيبي وتواصل مباشر للتعريف بكامل منتجات نفطال (زيوت، سيرغاز).',
        'At Risk (معرضون للفقدان)': 'إرسال تنبيهات وتخفيضات تشجيعية فورية قبل انتقالهم لفئة المفقودين.',
        'Hibernating / Lost (غائبون / مفقودون)': 'إجراء استقصاء لمعرفة أسباب التحول إلى المنافسين وإطلاق استراتيجية إعادة التنشيط.'
    }
    
    for seg, rec in seg_dict.items():
        st.info(f"**شريحة {seg}:** {rec}")

# ------------------------------------------
# PAGE 4: Pareto & ABC Analysis
# ------------------------------------------
elif menu == "📈 تحليلات Pareto & ABC":
    st.title("📈 تحليل باريتو (Pareto 80/20) وتصنيف ABC")
    st.markdown("يساعد هذا التحليل في التعرف على الفئة القليلة من الزبائن التي تولد الغالبية العظمى من إيرادات المؤسسة.")
    
    abc_df = calculate_abc_pareto(rfm_df)
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=abc_df.index,
        y=abc_df['Monetary'],
        name='إيراد الزبون (د.ج)',
        marker_color='#1e3c72'
    ))
    fig_pareto.add_trace(go.Scatter(
        x=abc_df.index,
        y=abc_df['Cum_Percentage'],
        name='النسبة التراكمية (%)',
        yaxis='y2',
        line=dict(color='#ffcc00', width=3)
    ))
    
    fig_pareto.update_layout(
        title='مخطط باريتو التراكمي لإيرادات الزبائن',
        yaxis=dict(title='الإيرادات (د.ج)'),
        yaxis2=dict(title='النسبة التراكمية (%)', overlaying='y', side='left', maxrange=[0, 110]),
        xaxis=dict(title='الزبائن مرتبين حسب المساهمة')
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    st.subheader("📊 توزيع تصنيف ABC")
    abc_summary = abc_df.groupby('ABC_Class').agg(
        عدد_الزبائن=('معرف_الزبون', 'count'),
        إجمالي_الإيرادات=('Monetary', 'sum')
    ).reset_index()
    abc_summary['نسبة الإيراد'] = (abc_summary['إجمالي_الإيرادات'] / abc_summary['إجمالي_الإيرادات'].sum()) * 100
    
    st.dataframe(abc_summary.style.format({
        'إجمالي_الإيرادات': '{:,.0f} د.ج',
        'نسبة الإيراد': '{:.1f}%'
    }), use_container_width=True)

# ------------------------------------------
# PAGE 5: Customer Lifetime Value (CLV)
# ------------------------------------------
elif menu == "💎 القيمة التراكمية (CLV)":
    st.title("💎 تحليل القيمة التراكمية مدى الحياة (CLV)")
    st.markdown("""
    تُمثل **القيمة التراكمية للزبون (Customer Lifetime Value)** إجمالي الأرباح أو الإيرادات التقديرية التي يحققها الزبون للمؤسسة طوال فترة العلاقة التجارية.
    """)
    
    top_clv = rfm_df.sort_values(by='Estimated_CLV', ascending=False).head(15)
    
    fig_clv = px.bar(top_clv, x='Estimated_CLV', y='اسم_الزبون', orientation='h',
                     title='أعلى 15 زبون من حيث القيمة التراكمية المتوقعة (CLV)',
                     color='Estimated_CLV', color_continuous_scale='Viridis')
    st.plotly_chart(fig_clv, use_container_width=True)
    
    st.subheader("📑 جدول قيم CLV التفصيلي للزبائن")
    st.dataframe(rfm_df[['معرف_الزبون', 'اسم_الزبون', 'نوع_الزبون', 'Frequency', 'Monetary', 'Estimated_CLV']].sort_values(by='Estimated_CLV', ascending=False).style.format({
        'Monetary': '{:,.0f} د.ج',
        'Estimated_CLV': '{:,.0f} د.ج'
    }), use_container_width=True)

# ------------------------------------------
# PAGE 6: Product Analytics
# ------------------------------------------
elif menu == "📦 تحليل المنتجات والخدمات":
    st.title("📦 تحليل أداء المنتجات والخدمات التسويقية")
    
    prod_summary = filtered_df.groupby('المنتج').agg(
        عدد_العمليات=('معرف_العملية', 'count'),
        إجمالي_الكمية=('الكمية', 'sum'),
        إجمالي_المبيعات=('المبلغ_الإجمالي', 'sum'),
        متوسط_سعر_العملية=('المبلغ_الإجمالي', 'mean')
    ).reset_index().sort_values(by='إجمالي_المبيعات', ascending=False)
    
    st.dataframe(prod_summary.style.format({
        'إجمالي_الكمية': '{:,.0f}',
        'إجمالي_المبيعات': '{:,.0f} د.ج',
        'متوسط_سعر_العملية': '{:,.0f} د.ج'
    }), use_container_width=True)
    
    st.markdown("---")
    st.subheader("💡 توصيات المنتجات بناءً على التحليل")
    
    top_p = prod_summary.iloc[0]['المنتج']
    st.success(f"📌 **المنتج الأعلى مساهمة في الإيرادات ({top_p}):** يوصى بضمان استمرارية الإمدادات ومراقبة المخزون لتجنب أي انقطاع في المحطات.")

# ------------------------------------------
# PAGE 7: Geographical Analytics
# ------------------------------------------
elif menu == "🗺️ التحليل الجغرافي (البلديات)":
    st.title("🗺️ التحليل الجغرافي وحصة بلديات خنشلة")
    
    muni_summary = filtered_df.groupby('البلدية').agg(
        عدد_الزبائن=('معرف_الزبون', 'nunique'),
        عدد_العمليات=('معرف_العملية', 'count'),
        إجمالي_المبيعات=('المبلغ_الإجمالي', 'sum')
    ).reset_index().sort_values(by='إجمالي_المبيعات', ascending=False)
    
    col_g1, col_g2 = st.columns([3, 2])
    with col_g1:
        fig_muni_pie = px.pie(muni_summary, values='إجمالي_المبيعات', names='البلدية', title='توزيع المبيعات حسب البلدية')
        st.plotly_chart(fig_muni_pie, use_container_width=True)
    with col_g2:
        st.dataframe(muni_summary.style.format({'إجمالي_المبيعات': '{:,.0f} د.ج'}), use_container_width=True)

# ------------------------------------------
# PAGE 8: Churn & At-Risk Customers
# ------------------------------------------
elif menu == "⚠️ الزبائن المعرضون للفقدان":
    st.title("⚠️ نظام اكتشاف الزبائن المعرضين للفقدان (At-Risk Detection)")
    st.write("يعتمد هذا النظام على تتبع انخفاض التكرار وزيادة مدة الغياب للتنبؤ بخطر انسحاب الزبون.")
    
    at_risk_df = rfm_df[rfm_df['Risk_Level'].isin(['مرتفع جداً', 'متوسط'])].sort_values(by='Recency', ascending=False)
    
    st.warning(f"⚠️ تم كشف {len(at_risk_df)} زبون في مستويات خطر متوسطة إلى مرتفعة جداً.")
    
    st.dataframe(at_risk_df[['معرف_الزبون', 'اسم_الزبون', 'البلدية', 'رقم_الهاتف', 'Recency', 'Frequency', 'Monetary', 'Risk_Level', 'Segment']].style.format({
        'Monetary': '{:,.0f} د.ج',
        'Recency': '{:.0f} يوم غياب'
    }), use_container_width=True)

# ------------------------------------------
# PAGE 9: CRM
# ------------------------------------------
elif menu == "🗂️ إدارة علاقات الزبائن (CRM)":
    st.title("🗂️ بطاقة الزبون الموحدة (CRM Detailed Profile)")
    
    selected_cust_id = st.selectbox("اختر الزبون لعرض الملف التفصيلي:", options=rfm_df['معرف_الزبون'].unique())
    
    cust_data = rfm_df[rfm_df['معرف_الزبون'] == selected_cust_id].iloc[0]
    cust_txs = filtered_df[filtered_df['معرف_الزبون'] == selected_cust_id]
    
    c_c1, c_c2 = st.columns(2)
    with c_c1:
        st.markdown(f"""
        * **معرف الزبون:** {cust_data['معرف_الزبون']}
        * **الاسم:** {cust_data['اسم_الزبون']}
        * **نوع الزبون:** {cust_data['نوع_الزبون']}
        * **البلدية:** {cust_data['البلدية']}
        * **رقم الهاتف:** {cust_data['رقم_الهاتف']}
        """)
    with c_c2:
        st.markdown(f"""
        * **الشريحة (RFM Segment):** {cust_data['Segment']}
        * **مستوى الخطر:** {cust_data['Risk_Level']}
        * **إجمالي المبيعات:** {cust_data['Monetary']:,.0f} د.ج
        * **عدد العمليات:** {cust_data['Frequency']}
        * **آخر عملية شراء:** منذ {cust_data['Recency']} يوم
        """)
        
    st.markdown("---")
    st.subheader("📜 سجل عمليات الزبون")
    st.dataframe(cust_txs[['معرف_العملية', 'تاريخ_العملية', 'المنتج', 'الكمية', 'المبلغ_الإجمالي']], use_container_width=True)

# ------------------------------------------
# PAGE 10: Marketing Decision Center
# ------------------------------------------
elif menu == "🎯 مركز دعم القرار التسويقي":
    st.title("🎯 مركز دعم القرار التسويقي (Marketing Decision Center)")
    st.markdown("ربط نتائج تحليل البيانات بقرارات تسويقية إجرائية قابلة للتطبيق بمؤسسة نفطال.")
    
    decisions = generate_decision_center(rfm_df, filtered_df)
    
    for d in decisions:
        st.markdown(f"""
        <div class="decision-card {d['class']}">
            <h4>🎯 {d['title']} (الأولوية: {d['priority']})</h4>
            <p><strong>الدليل من البيانات:</strong> {d['evidence']}</p>
            <p><strong>القرار المقترح:</strong> {d['decision']}</p>
            <p><strong>الإجراء التنفيذي:</strong> {d['action']}</p>
        </div>
        """, unsafe_content_style=True)

# ------------------------------------------
# PAGE 11: AI Marketing Analyst
# ------------------------------------------
elif menu == "🤖 المحلل الذكي (AI Analyst)":
    st.title("🤖 المساعد الذكي للتحليل التسويقي (AI Marketing Analyst)")
    st.write("أسأل النظام الذكي لاستخراج التبصرات التسويقية المباشرة من قاعدة البيانات.")
    
    query = st.selectbox("اختر سؤالاً تحليلياً أو اكتب استفسارك:", [
        "من هم أفضل الزبائن المساهمين في الإيرادات؟",
        "ما هو المنتج الأكثر مبيعاً في ولاية خنشلة؟",
        "ما هي البلديات التي تحتاج إلى تعزيز النشاط التسويقي؟",
        "ما هي التوصية العاجلة لمعالجة الزبائن المعرضين للفقدان؟"
    ])
    
    if st.button("تحليل الإجابة 🚀"):
        if "أفضل الزبائن" in query:
            top_c = rfm_df.sort_values(by='Monetary', ascending=False).iloc[0]
            st.success(f"🤖 **التحليل:** أفضل زبون حالياً هو **{top_c['اسم_الزبون']}** بإجمالي إيرادات قدره **{top_c['Monetary']:,.0f} د.ج** وتنتمي لشريحة **{top_c['Segment']}**.")
        elif "المنتج الأكثر" in query:
            top_p = filtered_df.groupby('المنتج')['المبلغ_الإجمالي'].sum().idxmax()
            st.success(f"🤖 **التحليل:** المنتج الأكثر تحقيقاً للإيرادات هو **{top_p}**.")
        elif "البلديات" in query:
            low_m = filtered_df.groupby('البلدية')['المبلغ_الإجمالي'].sum().idxmin()
            st.warning(f"🤖 **التحليل:** بلدية **{low_m}** تسجل أدنى معدل نشاط، يوصى بزيادة الحملات الترويجية فيها.")
        else:
            st.info("🤖 **التحليل:** يوصى بتطبيق حملة re-engagement فورية وإرسال رسائل تذكيرية للزبائن الذين تجاوزت مدة غيابهم 90 يوماً.")

# ------------------------------------------
# PAGE 12: Reports & Export
# ------------------------------------------
elif menu == "📋 التقرير الشامل والتصدير":
    st.title("📋 التقرير التنفيذي الشامل والتصدير")
    
    st.write("يمكنك تصدير مخرجات التحليل التسويقي بصيغة CSV لتضمينها في ملحقات مذكرة التخرج.")
    
    csv_buffer = io.StringIO()
    rfm_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 تحميل تقرير تجزئة الزبائن (RFM Report CSV)",
        data=csv_buffer.getvalue(),
        file_name="naftal_customer_segmentation_report.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    st.subheader("📄 ملخص نتائج المذكرة للعرض أمام اللجنة")
    st.markdown("""
    1. **أهمية البيانات:** تم الانتقال من القرارات العشوائية إلى القرارات المبنية على الأدلة الرقمية (Data-Driven Decisions).
    2. **التجزئة السلوكية:** كشف النموذج أن الشريحة الأكثر قيمة تتطلب استراتيجيات الاحتفاظ، بينما تحتاج الشريحة الغائبة إلى إعادة تنشيط.
    3. **الكفاءة التسويقية:** ترشيد الميزانيات التسويقية لمؤسسة نفطال من خلال توجيه الحملات نحو الشرائح والبلديات الأكثر استجابة.
    """)
