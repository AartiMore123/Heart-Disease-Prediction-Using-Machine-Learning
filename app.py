import streamlit as st
import numpy as np
import pickle
import pandas as pd
import re



# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Heart Disease App", layout="wide")

# ======================
# LOAD MODEL
# ======================
with open("heart_model.pkl", "rb") as f:
    model, scaler = pickle.load(f)

# ======================
# SESSION STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "history" not in st.session_state:
    st.session_state.history = []

def go(page):
    st.session_state.page = page

# ======================
# SIDEBAR (LOGO)
# ======================
st.sidebar.markdown("""
<div style="text-align:center;">
    <img src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" width="80">
    <h3 style="color:#0d47a1;">HeartCare App</h3>
</div>
<hr>
""", unsafe_allow_html=True)

if st.sidebar.button("🏠 Home"): go("Home")
if st.sidebar.button("🔐 Login"): go("Login")
if st.sidebar.button("🩺 Health"): go("Health")
if st.sidebar.button("📊 Prediction"): go("Prediction")
if st.sidebar.button("🙏 Thank You"): go("ThankYou")
if st.sidebar.button("🔒 Admin"): go("Admin")

# ======================
# GLOBAL STYLE
# ======================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #e3f2fd, #ffffff);
}
h1, h2 {
    color: #0d47a1;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HOME PAGE
# ======================
if st.session_state.page == "Home":
    st.title("❤️ Heart Disease Prediction System")

    st.markdown("### 📊 Mini Dashboard")

    df1 = pd.DataFrame({"Risk":[70,30]}, index=["H","R"])
    df2 = pd.DataFrame({"BP":[120,140,160]})
    df3 = pd.DataFrame({"C":[180,220,260]})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**❤️ Risk**")
        st.bar_chart(df1, height=100)

    with col2:
        st.markdown("**🩸 BP**")
        st.line_chart(df2, height=100)

    with col3:
        st.markdown("**🧪 Chol**")
        st.area_chart(df3, height=100)

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk", "27%")
    c2.metric("Healthy", "73%")
    c3.metric("Patients", "45K+")

    st.button("➡️ Go to Login", on_click=go, args=("Login",))

# ======================
# LOGIN PAGE
# ======================
elif st.session_state.page == "Login":
    st.title("🔐 Patient Login")

    name = st.text_input("Full Name")
    mobile = st.text_input("Mobile Number")
    location = st.text_input("Location")

    # LOGIN BUTTON
    if st.button("Next ➡️ Health Page"):
        if len(name.split()) < 2:
            st.error("Enter full name")
        elif not re.fullmatch(r"\d{10}", mobile):
            st.error("Enter valid 10-digit mobile number")
        else:
            # SAVE DATA
            st.session_state.user = name
            st.session_state.contact = mobile
            st.session_state.location = location

            go("Health")
 
# ======================
# HEALTH PAGE
# ======================
elif st.session_state.page == "Health":
    st.title("🩺 Health Information")

    col1, col2 = st.columns(2)

    with col1:
        age = st.slider("Age", 20, 80)
        sex = st.selectbox("Sex", ["Female", "Male"])
        cp = st.selectbox("Chest Pain", [0,1,2,3])
        trestbps = st.slider("BP", 80, 200)

    with col2:
        chol = st.slider("Cholesterol", 100, 400)
        thalach = st.slider("Heart Rate", 60, 220)
        oldpeak = st.slider("Oldpeak", 0.0, 6.0)

    if st.button("Next ➡️ Prediction"):
        st.session_state.input = [age, 1 if sex=="Male" else 0, cp, trestbps, chol, 0, 1, thalach, 0, oldpeak, 1, 0, 2]
        go("Prediction")

# ======================
# PREDICTION PAGE
# ======================
elif st.session_state.page == "Prediction":
    st.title("📊 Prediction Result")

    if "input" in st.session_state:
        data = np.array([st.session_state.input])
        data = scaler.transform(data)

        pred = model.predict(data)

        if pred[0] == 1:
            result = "High Risk"
            st.error("⚠️ High Risk")
        else:
            result = "Low Risk"
            st.success("✅ Low Risk")

        # SAVE FULL HISTORY
        st.session_state.history.append({
            "Name": st.session_state.get("user", "Unknown"),
            "Contact": st.session_state.get("contact", "NA"),
            "Location": st.session_state.get("location", "NA"),
            "Result": result
        })

        chart = pd.DataFrame({
            "Status": ["Healthy", "Risk"],
            "Value": [70, 30]
        })
        st.bar_chart(chart.set_index("Status"))

        st.button("Next ➡️ Thank You", on_click=go, args=("ThankYou",))

# ======================
# THANK YOU PAGE
# ======================
elif st.session_state.page == "ThankYou":
    st.title("🙏 Thank You")
    st.success("Visit Again!")
    st.button("🏠 Go to Home", on_click=go, args=("Home",))


# ======================
# ADMIN PAGE (WHITE UI)
# ======================
elif st.session_state.page == "Admin":

    st.markdown("""
    <style>
    .stApp {
        background: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🔒 Admin Dashboard")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "tanu" and pwd == "Tanu 123":
            st.success("Welcome Admin 👑")

            st.markdown("### 📊 Dashboard")
            c1, c2 = st.columns(2)
            c1.metric("Total Users", len(st.session_state.history))
            c2.metric("High Risk Cases", sum(1 for x in st.session_state.history if x["Result"]=="High Risk"))

            st.markdown("### 📜 User History")

            if st.session_state.history:
                df = pd.DataFrame(st.session_state.history)
                df = df[["Name", "Contact", "Location", "Result"]]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No data yet")

        else:
            st.error("Invalid Credentials")
            
            # CLEAR HISTORY BUTTON
        if st.button("🗑 Clear History"):
           st.session_state.history = []
           st.success("History Cleared Successfully")
           