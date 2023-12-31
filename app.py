import os
import streamlit as st
import matplotlib.pyplot as plt
import io
import requests
from PIL import Image
import json
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

# Hide the made from Streamlit:
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
st.markdown('<style>body { margin-top: 20px; }</style>', unsafe_allow_html=True)

#### SECTION 1: FIREBASE SET-UP ####

# Firebase Constants
FIREBASE_WEB_API_KEY = 'AIzaSyDUW2pzxpjNKe7mrda8zm3wj_hZMxoDdzI'

# Load Firebase credentials from TOML file for signup
firebase_credentials_string = st.secrets["textkey"]
firebase_credentials_dict = json.loads(firebase_credentials_string)

cred = credentials.Certificate(firebase_credentials_dict)

# Check if the app is already initialized
try:
    firebase_admin.get_app()
except ValueError as e:
    initialize_app(cred)

db = firestore.client()

def login_with_firebase(email, password):
    SIGNIN_ENDPOINT = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(SIGNIN_ENDPOINT, data=data)
    return response.json()

def signup_with_firebase(email, password, personal_data):
    SIGNUP_ENDPOINT = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(SIGNUP_ENDPOINT, data=data)
    response_data = response.json()

    # DEBUGGING LINE: Print the response data for debugging purposes
    # st.write(response_data)  # Using Streamlit's st.write to display the response data

    # If signup was successful, store the personal information in Firestore
    if "localId" in response_data:
        users_ref = db.collection('users')
        users_ref.document(response_data["localId"]).set(personal_data)

def get_user_data(uid):
    user_ref = db.collection('users').document(uid)
    doc = user_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {}  # Return an empty dictionary if no data is found

def update_user_profile(uid, user_data):
    users_ref = db.collection('users')
    users_ref.document(uid).update(user_data)

def add_wine_tasting_record(uid, wine_data):
    users_ref = db.collection('users')
    user_document = users_ref.document(uid)
    wine_records = user_document.collection('wine_records')
    wine_records.add(wine_data)

def get_wine_tasting_records(uid):
    users_ref = db.collection('users')
    user_document = users_ref.document(uid)
    wine_records = user_document.collection('wine_records').stream()
    return [record.to_dict() for record in wine_records]


def wine_preference_survey(uid=None):
    st.subheader("Wine Preference Survey")
    red_wine_preference = st.slider("Rate your preference for Red Wine (0=Dislike, 10=Love)", 0, 10)
    white_wine_preference = st.slider("Rate your preference for White Wine", 0, 10)
    rose_wine_preference = st.slider("Rate your preference for Rosé", 0, 10)
    sparkling_wine_preference = st.slider("Rate your preference for Sparkling Wine", 0, 10)
    # Add more questions as needed...
    return {
        "red_wine": red_wine_preference,
        "white_wine": white_wine_preference,
        "rose_wine": rose_wine_preference,
        "sparkling_wine": sparkling_wine_preference
    }


def display_preferences(user_data):
    st.subheader(":wine_glass: Your Preferences :grapes:")
    st.write("Here are your wine preferences:")
    st.write(f"Red Wine: {user_data['red_wine']}/10")
    st.write(f"White Wine: {user_data['white_wine']}/10")
    st.write(f"Rosé: {user_data['rose_wine']}/10")
    st.write(f"Sparkling Wine: {user_data['sparkling_wine']}/10")

def login():

    st.subheader("Welcome Sommeliers!")
    menu = ["Login", "Signup"]
    choice = st.selectbox("Login/Signup", menu, key="menu_key")

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            firebase_response = login_with_firebase(email, password) or {}
            
            if "idToken" in firebase_response:
                user_data = get_user_data(firebase_response["localId"])
                if user_data:
                    st.title(f"Welcome, {user_data['first_name']}!")
                    return firebase_response
                else:
                    st.error("Error retrieving user data")
            else:
                st.error("Invalid email/password")
        return None

    elif choice == "Signup":
        st.subheader("Create a new account")
        new_user_email = st.text_input("Email")
        new_user_password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm password", type='password')

        # Collect additional personal information
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        phone_number = st.text_input("Phone Number")

        if st.button("Signup"):
            if new_user_password == confirm_password:
                personal_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_number": phone_number,
                    "email": new_user_email
                }
                firebase_response = signup_with_firebase(new_user_email, new_user_password, personal_data) or {}
                if "idToken" in firebase_response:
                    st.success("Account created successfully!")
                    st.write(f"Welcome, {first_name}!")
                    return firebase_response
                else:
                    st.error("Error creating account")
            else:
                st.error("Passwords do not match")



def create_infographic(selected_wine, appearance, clarity, intensity, selected_aromas, taste_intensity, overall_impressions, rating):
    fig, ax = plt.subplots(figsize=(6, 6))

    # Wine Type
    ax.text(0.5, 1, f"Wine Type: {selected_wine}", ha='center', fontsize=14)

    # Appearance
    ax.text(0.5, 0.9, f"Appearance: {appearance}", ha='center')
    ax.text(0.5, 0.85, f"Clarity: {clarity}", ha='center')
    ax.text(0.5, 0.8, f"Intensity: {intensity}", ha='center')

    # Olfactory Examination
    aromas_str = ", ".join(selected_aromas)
    ax.text(0.5, 0.75, f"Aromas: {aromas_str}", ha='center', wrap=True)

    # Gustatory Examination
    taste_strs = [f"{taste}: {intensity}" for taste, intensity in taste_intensity.items()]
    taste_str = ", ".join(taste_strs)
    ax.text(0.5, 0.7, "Tastes - " + taste_str, ha='center', wrap=True)

    # Overall Impressions & Rating
    ax.text(0.5, 0.6, f"Overall Impressions: {overall_impressions}", ha='center', wrap=True)
    ax.text(0.5, 0.5, f"Rating: {rating} out of 5", ha='center')

    ax.axis("off")  # hide axes

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='jpeg')
    buf.seek(0)
    return buf


#### TO FIX BUG WHERE SELECTING SIGN IN HIDES EVERYTHING:
def save_wine_preferences(uid, preferences):
    """Save wine preferences to Firestore."""
    users_ref = db.collection('users')
    users_ref.document(uid).update(preferences)

def wine_preference_survey(uid):
    st.subheader("Wine Preference Survey")
    red_wine_preference = st.slider("Rate your preference for Red Wine (0=Dislike, 10=Love)", 0, 10)
    white_wine_preference = st.slider("Rate your preference for White Wine", 0, 10)
    rose_wine_preference = st.slider("Rate your preference for Rosé", 0, 10)
    sparkling_wine_preference = st.slider("Rate your preference for Sparkling Wine", 0, 10)
    
    preferences = {
        "red_wine": red_wine_preference,
        "white_wine": white_wine_preference,
        "rose_wine": rose_wine_preference,
        "sparkling_wine": sparkling_wine_preference
    }
    
    if st.button("Submit Preferences"):
        save_wine_preferences(uid, preferences)
        st.success("Preferences saved successfully!")
        return True  # Preferences were successfully saved

    return False  # Preferences were not saved yet

def profile_page(uid):
    st.subheader("Profile Page")

    user_data = get_user_data(uid)

    st.markdown("## Personal Information")
    first_name = st.text_input("First Name", value=user_data.get('first_name', ''))
    last_name = st.text_input("Last Name", value=user_data.get('last_name', ''))
    phone_number = st.text_input("Phone Number", value=user_data.get('phone_number', ''))

    if st.button("Update Profile"):
        updated_data = {
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number
        }
        update_user_profile(uid, updated_data)
        st.success("Profile updated successfully!")

    st.markdown("## Wine Tasting Records")
    records = get_wine_tasting_records(uid)
    for record in records:
        st.write(f"Wine Type: {record['wine_type']}, Rating: {record['rating']}/5")

def main():
    # Load the image
    image = Image.open('Pocket.png')
    st.image(image)

    # Display the text
    st.write("Do you like drinking wine but have a hard time figuring out your preferences? Pocket Somm is an app that identifies your preferences and recommends which Wines are best for your taste.")

    user = None
    if 'user' not in st.session_state or not st.session_state.user:
        user = login()
        if user:
            st.session_state.user = user
    else:
        user = st.session_state.user

    # Check if the user is logged in
    if user:
        # User navigation options
        page_choices = ["Home", "Profile"]
        if "page" not in st.session_state:
            st.session_state.page = st.sidebar.selectbox("Navigation", page_choices, index=0)
        else:
            st.session_state.page = st.sidebar.selectbox("Navigation", page_choices, index=page_choices.index(st.session_state.page))
        
        user_data = get_user_data(user["localId"])

        if st.session_state.page == "Home":
            # Check if wine preferences are already saved
            if user_data and 'red_wine' in user_data:
                display_preferences(user_data)
            else:
                # If not, display the survey and save the preferences
                if wine_preference_survey(user["localId"]):  # Checking the return value to refresh the page
                    st.session_state.page = "Profile"  # If preferences were saved, navigate to profile

            if st.button("Start Tasting"):
                start_tasting()

        elif st.session_state.page == "Profile":
            profile_page(user["localId"])

            # Check if wine preferences are already saved
            if user_data and 'red_wine' in user_data:
                display_preferences(user_data)
            else:
                # If not, display the survey and save the preferences
                wine_preference_survey(user["localId"])

            if st.button("Start Tasting"):
                start_tasting()


def start_tasting():
    
    # Initialize session_state variables if not present
    if 'selected_wine' not in st.session_state:
        st.session_state.selected_wine = "Red"
        st.session_state.appearance = ""
        st.session_state.clarity = "Clear"
        st.session_state.intensity = "Pale"  # Changed to default to "Pale"
        st.session_state.hue = "Ruby"
        st.session_state.selected_aromas = []
        st.session_state.taste_intensity = {taste: 5 for taste in ["Sweet", "Sour", "Salty", "Bitter"]}  # Default to medium intensity (5)
        st.session_state.overall_impressions = ""
        st.session_state.rating = 3  # Remains as an integer value

    wine_options = ["Red", "White", "Rosé", "Sparkling"]
    st.session_state.selected_wine = st.selectbox("Choose a type of wine:", wine_options, index=wine_options.index(st.session_state.selected_wine))

    # Visual Examination
    st.subheader("Look")
    st.session_state.appearance = st.text_input("Describe the wine's appearance:", value=st.session_state.appearance)
    st.session_state.clarity = st.radio("Select the clarity:", ["Clear", "Cloudy", "Opaque"], index=["Clear", "Cloudy", "Opaque"].index(st.session_state.clarity))
    
    intensity_options = ["Pale", "Medium", "Deep"]
    # If st.session_state.intensity is a string, get its index; else, use the integer value directly
    intensity_index = intensity_options.index(st.session_state.intensity) if isinstance(st.session_state.intensity, str) else st.session_state.intensity - 1
    st.session_state.intensity = st.selectbox("Intensity:", intensity_options, index=intensity_index)

    hue_options = ["Purple", "Ruby", "Garnet", "Tawny", "Brown", "Straw", "Yellow", "Gold", "Amber", "Green"]
    st.session_state.hue = st.selectbox("Hue:", hue_options, index=hue_options.index(st.session_state.hue))
    
    # Aroma Assessment
    st.subheader("Sniff")
    st.session_state.selected_aromas = st.multiselect("Select the aromas you identify:", ["Fruity", "Floral", "Spicy", "Nutty", "Chemical", "Pungent", "Waxed", "Woody", "Earth", "Herbal"], default=st.session_state.selected_aromas)
    
    # Taste Assessment
    st.subheader("Sip")
    for taste in ["Sweet", "Sour", "Salty", "Bitter"]:
        st.session_state.taste_intensity[taste] = st.slider(f"How {taste.lower()} is the wine?", 0, 10, st.session_state.taste_intensity[taste])
    
    # Overall Impressions and Rating
    st.session_state.overall_impressions = st.text_area("Describe your overall impressions:", value=st.session_state.overall_impressions)
    st.session_state.rating = st.slider("Overall Rating (0-5):", 0, 5, st.session_state.rating)

    
    if st.button("Submit"):
        # Process the tasting data (e.g., save to a database, display a summary, etc.)
        st.success("Thank you for submitting your tasting notes!")

if __name__ == "__main__":
    main()

    
