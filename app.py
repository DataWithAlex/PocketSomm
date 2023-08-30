import streamlit as st
import matplotlib.pyplot as plt
import io
from PIL import Image
import pyrebase


### Firebase Authentication: 



firebase_config = {
    "apiKey": "AIzaSyDUW2pzxpjNKe7mrda8zm3wj_hZMxoDdzI",
    "authDomain": "pocketsomm-15bd1.firebaseapp.com",
    "databaseURL": "https://pocketsomm-15bd1.firebaseio.com",
    "projectId": "pocketsomm-15bd1",
    "storageBucket": "pocketsomm-15bd1.appspot.com",
    "messagingSenderId": "67664070012",
    "appId": "1:67664070012:web:59593f2b095773d58910f9",
    "measurementId": "G-XNJHXDNLK9"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def login():
    st.sidebar.title("User Authentication")
    
    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu, key="selected_login")
    
    if choice == "Login":
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.sidebar.success("Logged in as: {}".format(email))
                return user
            except:
                st.sidebar.error("Invalid email/password")
        return None

    elif choice == "Signup":
        st.subheader("Create a new account")
        new_user_email = st.text_input("Email")
        new_user_password = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm password", type='password')
        
        if st.button("Signup"):
            if new_user_password == confirm_password:
                try:
                    auth.create_user_with_email_and_password(new_user_email, new_user_password)
                    st.success("Account created successfully!")
                    user = auth.sign_in_with_email_and_password(new_user_email, new_user_password)
                    st.sidebar.success("Logged in as: {}".format(new_user_email))
                    return user
                except:
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


######


def main():
    # Initialize the state
    user = login()
    if user:
        st.title(f"Welcome!")

    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()

    if 'start_tasting' not in st.session_state:
        st.session_state.start_tasting = False
    
    st.title("PocketSomm")
    # st.image('images/logo.jpg', use_column_width=True, width=10)
    st.write("Welcome to our wine tasting experience. Let's explore the world of wines!")
    
    # Start tasting button
    if st.button("Start Tasting"):
        st.session_state.start_tasting = True

    if st.session_state.start_tasting:
        wine_options = ["Red", "White", "Rosé", "Sparkling"]
        selected_wine = st.selectbox("Choose a type of wine:", wine_options, key = "wine_options_key")

        # Visual Examination
        st.subheader("Look")
        appearance = st.text_input("Describe the wine's appearance:")
        #clarity = st.radio("Select the clarity:", ["Clear", "Cloudy", "Opaque"])
        intensity_options = ["Pale", "Medium", "Deep"]
        intensity = st.selectbox("Intensity:", intensity_options, key = "intensity_options_key") # Wine Folly

        hue_options = ["Purple", "Ruby", "Garnet", "Tawny", "Brown", "Straw", "Yellow", "Gold", "Amber", "Brown", "Pink", "Salmon", "Copper"]
        hue = st.selectbox("Choose the Hue of the Wine:", hue_options, key = "hue_options_key")

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

        # Once all inputs are given, provide an option to submit or save the tasting session
            # In the section after the user submits their tasting:
        # ... [Rest of your code]

# In the section after the user submits their tasting:
        if st.button("Submit Tasting"):
            st.write("Thank you for your tasting notes!")
    
        buf = create_infographic(selected_wine, appearance, clarity, intensity, selected_aromas, taste_intensity, overall_impressions, rating)
    
    # Convert buffer to PIL Image for display
        image = Image.open(buf)
        st.image(image, caption="Your Wine Tasting Infographic", use_column_width=True)
    
        buf.seek(0)
        st.download_button(label="Download Infographic", data=buf, file_name="wine_tasting_infographic.jpeg", mime="image/jpeg")


###########



if __name__ == "__main__":
    main()

