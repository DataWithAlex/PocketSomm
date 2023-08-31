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

    # Print the response data for debugging purposes
    st.write(response_data)  # Using Streamlit's st.write to display the response data


    # If signup was successful, store the personal information in Firestore
    if "localId" in response_data:
        users_ref = db.collection('users')
        users_ref.document(response_data["localId"]).set(personal_data)

def get_user_data(uid):
    users_ref = db.collection('users')
    doc = users_ref.document(uid).get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None

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
    st.title("My Preferences")
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
                    st.write(f"Welcome, {user_data['first_name']}!")
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



def main():
    

    # Create columns for image and text. Adjust the width ratio to bring image closer to text.
    #col1, col2 = st.columns([1, 4])

    # Load the image
    image = Image.open('Pocket.png')
    # image = Image.open(IMAGE_PATH)

    # Display the text in the second column
    #col1.write("**PocketSomm**")

     # Display the image in the first column with a specific width
     # Create three columns
    col1, col2, col3, col4, col5 = st.columns(5)

    # Display image in the center column
    #col1.image(image, width=500)
    st.image(image)  # Adjust width as per your need.

    # Display the text in the second column
    st.write("PocketSomm gathers your wine preferences and helps recommend wines based on your preferences and other wines you like.")

    user = None  # Initialize user to None
    if 'user' not in st.session_state or not st.session_state.user:
        user = login()
        if user:
            st.session_state.user = user
    else:
        user = st.session_state.user

    # Add this check to ensure user is not None
    if user:
        user_data = get_user_data(user["localId"])
        
        # Check if wine preferences are already saved
        if user_data and 'red_wine' in user_data:
            display_preferences(user_data)
        else:
            # If not, display the survey and save the preferences
            wine_preference_survey(user["localId"])

    if 'start_tasting' not in st.session_state:
        st.session_state.start_tasting = False

    if st.button("Start Tasting"):
        start_tasting()





    

def start_tasting():

        if st.session_state.start_tasting:
            wine_options = ["Red", "White", "Rosé", "Sparkling"]
            selected_wine = st.selectbox("Choose a type of wine:", wine_options, key="wine_options_key")

        # Visual Examination
        st.subheader("Look")
        appearance = st.text_input("Describe the wine's appearance:")
        clarity = st.radio("Select the clarity:", ["Clear", "Cloudy", "Opaque"])
        intensity_options = ["Pale", "Medium", "Deep"]
        intensity = st.selectbox("Intensity:", intensity_options, key="intensity_options_key") 
        hue_options = ["Purple", "Ruby", "Garnet", "Tawny", "Brown", "Straw", "Yellow", "Gold", "Amber", "Brown", "Pink", "Salmon", "Copper"]
        hue = st.selectbox("Choose the Hue of the Wine:", hue_options, key="hue_options_key")

        # Olfactory Examination
        st.subheader("Olfactory Profile")
        aroma_options = ["Fruity", "Floral", "Spicy", "Woody", "Earthy", "Citrus"]
        selected_aromas = st.multiselect("Select the wine's aromas:", aroma_options)

        # Gustatory Examination
        st.subheader("Taste Profile")
        tastes = ["Sweet", "Sour", "Salty", "Bitter"]
        taste_intensity = {taste: st.slider(taste, 0, 10) for taste in tastes}

        # Final Impressions
        st.subheader("Final Impressions")
        overall_impressions = st.text_area("Share your overall impressions of the wine:")
        rating = st.slider("Rate the wine (out of 5):", 0, 5)

        if st.button("Submit Tasting"):
            st.write("Thank you for your tasting notes!")
    
        buf = create_infographic(selected_wine, appearance, clarity, intensity, selected_aromas, taste_intensity, overall_impressions, rating)
    
        # Convert buffer to PIL Image for display
        image = Image.open(buf)
        st.image(image, caption="Your Wine Tasting Infographic", use_column_width=True)
    
        buf.seek(0)
        st.download_button(label="Download Infographic", data=buf, file_name="wine_tasting_infographic.jpeg", mime="image/jpeg")


if __name__ == "__main__":
    main()

    
