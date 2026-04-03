import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.title("💎 تجربة تشغيل النظام")
st.write("إذا ظهرت هذه الرسالة، فالسيرفر يعمل والمشكلة كانت في الكود السابق.")

uploaded = st.sidebar.file_uploader("ارفع ملف")
if uploaded:
    st.write("تم رفع الملف بنجاح!")
