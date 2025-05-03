import streamlit as st
from streamlit_option_menu import option_menu
import pickle
import json
import numpy as np
import hashlib

# ----------------- Load Model and Symptoms -----------------
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

with open("symptoms.json", "r") as f:
    all_symptoms = json.load(f)

# ----------------- User Database (Simple) -----------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "history" not in st.session_state:
    st.session_state.history = {}

# ----------------- Helper Functions -----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    hashed = hash_password(password)
    return st.session_state.users.get(username) == hashed

def register_user(username, password):
    if username in st.session_state.users:
        return False
    st.session_state.users[username] = hash_password(password)
    return True

def add_history(username, symptoms, prediction, confidence):
    if username not in st.session_state.history:
        st.session_state.history[username] = []
    st.session_state.history[username].append({
        "symptoms": symptoms,
        "prediction": prediction,
        "confidence": confidence
    })

# ----------------- Navigation -----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ----------------- Centered Layout Helper -----------------
def centered_container():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2

# ----------------- Pages -----------------

def login_page():
    with centered_container():
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.success("Login successful!")
                st.session_state.user = username
            else:
                st.error("Invalid username or password.")

        st.info("Don't have an account?")
        if st.button("Go to Register"):
            st.session_state.page = "register"

def register_page():
    with centered_container():
        st.title("📝 Register")
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")

        if st.button("Register"):
            if register_user(username, password):
                st.success("Registration successful! Please login.")
                st.session_state.page = "login"
            else:
                st.error("Username already exists. Please choose another.")

        if st.button("Back to Login"):
            st.session_state.page = "login"

def home_page():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://img.freepik.com/free-photo/medicine-blue-background-flat-lay_23-2149341573.jpg?semt=ais_hybrid&w=740');
            background-size: cover;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🏠 Welcome, " + st.session_state.user)
    st.write("Explore disease predictions based on your symptoms.")
    
    st.subheader("🔍 Features of Our Website")
    
    # Displaying Features in a List
    st.markdown(
        """
        - **Disease Prediction**: Input your symptoms and receive a predicted disease along with confidence level.
        - **Personalized History**: View a history of your past predictions and symptoms.
        - **User-Friendly Interface**: A simple, intuitive design to make it easy for everyone to use.
        - **Professional Healthcare Links**: Direct access to professional medical advice through links to websites like [WebMD](https://www.webmd.com/).
        - **Secure Login and Registration**: Only authorized users can access prediction history and personal data.
        """
    )

    # Optionally, you can also display the features in a card layout for a more visual appeal
    st.markdown(
        """
        <style>
        .card {
            display: inline-block;
            width: 250px;
            padding: 20px;
            margin: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        </style>
        <div class="card">
            <h4>🔍 Disease Prediction</h4>
            <p>Input your symptoms and receive a predicted disease with confidence level.</p>
        </div>
        <div class="card">
            <h4>📜 History</h4>
            <p>Check your past predictions and symptoms easily.</p>
        </div>
        <div class="card">
            <h4>🌐 Professional Advice</h4>
            <p>Access trusted healthcare information through external links like WebMD.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def predict_page():

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #fff0f5;  /* Lavender Blush */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        
    st.title("🩺 Disease Prediction")
    selected_symptoms = st.multiselect("Select your Symptoms:", all_symptoms)

    if st.button("Predict Disease"):
        if not selected_symptoms:
            st.warning("Please select at least one symptom.")
        else:
            input_vector = np.zeros(len(all_symptoms))
            for symptom in selected_symptoms:
                index = all_symptoms.index(symptom)
                input_vector[index] = 1

            prediction = model.predict([input_vector])[0]
            prediction_proba = model.predict_proba([input_vector])
            confidence = np.max(prediction_proba) * 100

            st.success(f"🧬 Predicted Disease: **{prediction}**")
            st.info(f"Prediction Confidence: **{confidence:.2f}%**")

            add_history(st.session_state.user, selected_symptoms, prediction, confidence)

            # ---- Add advice box based on prediction
            with st.expander("📝 Advice on Your Prediction"):
                if prediction == "Disease A":
                    st.write("It looks like you might be suffering from **Disease A**. Please ensure to get sufficient rest, stay hydrated, and consult a specialist as soon as possible.")
                elif prediction == "Disease B":
                    st.write("It seems like **Disease B** is likely. We recommend visiting a healthcare provider to confirm the diagnosis and get proper treatment.")
                else:
                    st.write(f"Based on your symptoms, the model predicts **{prediction}**. It would be best to follow up with a healthcare professional for proper guidance.")

            # ---- Add Practo Link after the prediction results
            st.markdown(
                """
                ---
                Need more healthcare advice? Check out [Practo](https://www.practo.com/) for doctor consultations and health services.
                """, 
                unsafe_allow_html=True
            )


def history_page():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f5f5dc;  /* Beige */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📜 Prediction History")
    history = st.session_state.history.get(st.session_state.user, [])
    if not history:
        st.info("No history found.")
    else:
        for entry in reversed(history):
            st.markdown(f"**Symptoms**: {', '.join(entry['symptoms'])}")
            st.markdown(f"**Prediction**: {entry['prediction']}")
            st.markdown(f"**Confidence**: {entry['confidence']:.2f}%")
            st.markdown("---")



def main_app():
    with st.sidebar:
        choice = option_menu(
            menu_title=f"Welcome, {st.session_state.user}",
            options=["Home", "Predict", "History",  "Logout"],
            icons=["house", "activity", "clock-history", "briefcase", "box-arrow-right"],
            menu_icon="cast",
            default_index=0
        )

    if choice == "Home":
        home_page()
    elif choice == "Predict":
        predict_page()
    elif choice == "History":
        history_page()
    
    elif choice == "Logout":
        st.session_state.user = None
        st.session_state.page = "login"

# ----------------- Main Router -----------------
if st.session_state.user:
    main_app()
else:
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
