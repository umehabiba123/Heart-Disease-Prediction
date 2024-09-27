import streamlit as st
import pandas as pd
import requests
import joblib
# Load the saved model
model = joblib.load('heartDisease-umehabiba_Fakhira-batch1.pkl')
preprocessor = joblib.load('scalar.pkl')
BASE_URL = "http://127.0.0.1:8000"


# API connectivity
def register_patient(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/user", json=data)
    return response

def authentication(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/token", data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

def prediction(token, predicted_outcome):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = { 
        "predicted_outcome" : predicted_outcome
    }
    response = requests.post(f"{BASE_URL}/prediction/", json = data, headers=headers)
    return response

#                             ---------------------------------------------


# Function to make predictions using the loaded model
def predict_heart_disease(input_data):
    input_data_preprocessed = preprocessor.transform(input_data)
    prediction = model.predict(input_data_preprocessed)
    return prediction



# Custom styles for headers and buttons
st.markdown("""
    <style>

        .main-header {
            font-size: 32px;
            text-align: center;
            color: #ff6347;
            font-weight: bold;
        }
        .sub-header {
            font-size: 24px;
            color: #4CAF50;
        }
        .save-btn {
            background-color: #ff6347;
            color: white;
            font-size: 18px;
            padding: 10px;
            border-radius: 8px;
        }
        .save-btn:hover {
            background-color: #e55347;
        }
    </style>
""", unsafe_allow_html=True)



#                                    App title with custom styling
st.markdown("<h1 class='main-header'>Heart Disease Prediction</h1>", unsafe_allow_html=True)

#                                             Sidebar menu
menu = ["Prediction Insights", "User Registration", "User Authentication"]
choice = st.sidebar.selectbox("Menu", menu)


#  User Registration 
if choice == "User Registration":
    st.markdown("<h2 class='sub-header'>Register a New User</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Register"):
        # Check if both username and password are provided
        if not username or not password:
            st.error("Username and password cannot be empty.")
        else:
            response = register_patient(username, password)
            if response.status_code == 200:
                st.success("User registered successfully!")
            else:
                st.error("Error occurred during registration")

#   User Authentication


elif choice == "User Authentication":
    
    st.markdown("<h2 class='sub-header'>Authorize Your Account</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Authorize"):
        token = authentication(username, password)
        if token:
            st.session_state["token"] = token
            st.success("Authorization successful!")
        else:
            st.error("Authorization failed! Please check your credentials.")


#   Prediction Insights

elif choice == "Prediction Insights":
    st.image('https://res.cloudinary.com/dhditogyd/image/upload/v1723716507/Data%20Science%20Media/Heart%20Disease%20prediction/red_heart.webp')

    st.header('User Information Submission')

    # Input form
    age = st.slider('Age', min_value=0, max_value=120, value=40)
    sex = st.selectbox('Gender', options=["Male", "Female"])
    cp = st.selectbox('Chest Pain Type', options=["Typical Angina", "Atypical Angina", "Non-Anginal Pain", "Asymptomatic"])
    trestbps = st.slider('Resting Blood Pressure', min_value=50, max_value=250, value=120)
    chol = st.slider('Cholesterol Level', min_value=100, max_value=400, value=200)
    fbs = st.selectbox('Fasting Blood Sugar > 120 mg/dl', options=["No", "Yes"])
    restecg = st.selectbox('Resting ECG Results', options=["lv hypertrophy", "normal", "st-t abnormality"])
    thalch = st.slider('Maximum Heart Rate Achieved', min_value=0, max_value=250, step=1)
    exang = st.selectbox('Exercise Induced Angina', options=["False", "True"])
    oldpeak = st.number_input('ST Depression Induced by Exercise', min_value=0.0, max_value=10.0, step=0.1)
    slope = st.selectbox('Slope of Peak Exercise ST Segment', options=["downsloping", "flat", "upsloping"])
    ca = st.selectbox('Number of Major Vessels Colored by Fluoroscopy', options=[0, 1, 2, 3])
    thal = st.selectbox('Thalassemia', options=["fixed defect", "normal", "reversible defect"])

    input_data = pd.DataFrame([[age, sex, cp, trestbps, chol, fbs, restecg, thalch, exang, oldpeak, slope, ca, thal]],
                                      columns=['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalch', 'exang', 'oldpeak', 'slope', 'ca', 'thal'])




    col1, col2 = st.columns([1, 6])
    
    with col1:
        if st.button('Predict', key="predict_btn"):
            

            result = predict_heart_disease(input_data)
            if result is not None:
                if result[0] == 0:
                    st.session_state['result'] = "No heart disease"
                elif result[0] == 1:
                    st.session_state['result'] = "Mild heart disease"
                elif result[0] == 2:
                    st.session_state['result'] = "Moderate heart disease"
                elif result[0] == 3:
                    st.session_state['result'] = "Severe heart disease"
                elif result[0] == 4:
                    st.session_state['result'] = "Critical heart disease"
            else:
                st.error("Please make a prediction first!")
            st.write("### Your Result:")
            st.markdown(f"<span style='display: inline-block;'>{st.session_state['result']}</span>", unsafe_allow_html=True)
    
        
    with col2:
        if st.button('Save Prediction', key="save_btn"):
            if st.session_state.get("token"):
                if st.session_state.get('result'):
                    response = prediction(st.session_state["token"], st.session_state['result'])
                    if response.status_code == 200:
                        st.success("Prediction saved successfully!")
                    else:
                        st.error("Error occurred during saving!")
                else:
                    st.error("No prediction to save. Please make a prediction first.")
            else: 
                st.error("Unauthorized Access: Please Verify Credentials")
st.sidebar.markdown(
    """
    <style>
    /* Styling the container */
    .sidebar-container {
        background-color: ##C0C0C0; /* Dark background */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Main Header Styling */
    .sub-header {
        font-size: 26px;
        color: #f39c12; /* Bright yellow-orange */
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
    }

    /* Content Styling */
    .content {
        font-size: 18px;
        color: ##C0C0C0; /* Light grayish white */
        text-align: center;
        line-height: 1.5;
        padding: 10px;
    }

    /* Note Styling */
    .note {
        font-size: 16px;
        color: #e74c3c; /* Red note */
        font-weight: bold;
        margin-top: 10px;
    }

    /* New Section Below */
    .section-container {
        background-color: ##C0C0C0; /* Slightly lighter than container */
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }

    .section-header {
        font-size: 24px;
        color: #1abc9c; /* Bright teal */
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }

    .section-content {
        font-size: 16px;
        color: #ecf0f1; /* Light grayish white */
        text-align: left;
        line-height: 1.6;
        padding: 10px;
    }

    .tip {
        font-size: 14px;
        color: #f39c12; /* Bright yellow-orange for tips */
        font-weight: bold;
        margin-top: 10px;
        text-align: center;
    }
    </style>

    <div class='sidebar-container'>
        <h2 class='sub-header'>Stay Healthy</h2>
        <div class='content'>
            Regular check-ups and a healthy lifestyle can help prevent heart disease.
        </div>
        <div class='note'>Your health is your wealth!</div>
    </div>

    <!-- New Section Below -->
    <div class='section-container'>
        <h2 class='section-header'>Daily Wellness Tips</h2>
        <div class='section-content'>
            1. Stay hydrated by drinking at least 8 glasses of water every day.<br>
            2. Incorporate at least 30 minutes of physical activity into your routine.<br>
            3. Maintain a balanced diet rich in fruits, vegetables, and whole grains.
        </div>
        <div class='tip'>Remember: Small changes lead to big results!</div>
    </div>
    """,
    unsafe_allow_html=True
)
