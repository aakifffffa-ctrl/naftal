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
    border-bottom: 3px solid #ffcc00;
    font-size: 28px;
    font-weight: bold;
    padding-bottom: 10px;
    margin-bottom: 25px;
}

div[data-testid="stMetricValue"] {
    font-size: 24px;
    color: #003366;
}
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown('<div class="main-header">منصة نفطال الذكية لتطوير بيانات الزبائن ⛽</div>', unsafe_allow_html=True)

# القائمة الجانبية
st.sidebar.title("خيارات التحكم ⚙️")
selected_option = st.sidebar.radio(
    "انتقل إلى:",
    ["لوحة القيادة (Dashboard)", "تحليل بيانات الزبائن", "إضافة زبون جديد"]
)

# بيانات تجريبية (Dummy Data)
@st.cache_data
def load_data():
    np.random.seed(42)
    data = pd.DataFrame({
        'رقم الزبون': [f'CUST-{i:03d}' for i in range(1, 51)],
        'اسم الزبون': [f'زبون {i}' for i in range(1, 51)],
        'المنطقة': np.random.choice(['الجزائر العاصمة', 'وهران', 'قسنطينة', 'ورقلة'], 50),
        'نوع الوقود المفصل': np.random.choice(['سيرغاز (GPL)', 'بنزين بدون رصاص', 'مازوت'], 50),
        'حجم الاستهلاك الشهري (لتر)': np.random.randint(100, 2000, 50),
        'تقييم الخدمة': np.random.choice(['ممتاز', 'جيد', 'متوسط'], 50)
    })
    return data

df = load_data()

# الصفحة الأولى: لوحة القيادة
if selected_option == "لوحة القيادة (Dashboard)":
    st.subheader("📊 إحصائيات عامة")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الزبائن", len(df))
    col2.metric("معدل الاستهلاك الشهري", f"{int(df['حجم الاستهلاك الشهري (لتر)'].mean())} لتر")
    col3.metric("المنطقة الأكثر نشاطاً", df['المنطقة'].mode()[0])
    col4.metric("الوقود الأكثر طلباً", df['نوع الوقود المفصل'].mode()[0])
    
    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("### توزيع الزبائن حسب المنطقة")
        fig_region = px.pie(df, names='المنطقة', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_region, use_container_width=True)
        
    with col_right:
        st.write("### استهلاك الوقود حسب النوع")
        fig_fuel = px.bar(df, x='نوع الوقود المفصل', y='حجم الاستهلاك الشهري (لتر)', color='نوع الوقود المفصل', barmode='group')
        st.plotly_chart(fig_fuel, use_container_width=True)

# الصفحة الثانية: تحليل بيانات الزبائن
elif selected_option == "تحليل بيانات الزبائن":
    st.subheader("🔍 جدول البيانات التفاعلي")
    
    region_filter = st.multiselect("تصفية حسب المنطقة:", options=df['المنطقة'].unique(), default=df['المنطقة'].unique())
    filtered_df = df[df['المنطقة'].isin(region_filter)]
    
    st.dataframe(filtered_df, use_container_width=True)

# الصفحة الثالثة: إضافة زبون
elif selected_option == "إضافة زبون جديد":
    st.subheader("📝 تسجيل بيانات زبون جديد")
    
    with st.form("add_customer_form"):
        name = st.text_input("اسم الزبون / الشركة")
        region = st.selectbox("المنطقة", ['الجزائر العاصمة', 'وهران', 'قسنطينة', 'ورقلة'])
        fuel_type = st.selectbox("نوع الوقود", ['سيرغاز (GPL)', 'بنزين بدون رصاص', 'مازوت'])
        consumption = st.number_input("حجم الاستهلاك المتوقع (لتر)", min_value=100, step=50)
        
        submit = st.form_submit_button("حفظ البيانات")
        if submit:
            st.success(f"تم تسجيل الزبون ({name}) بنجاح في قاعدة البيانات!")
