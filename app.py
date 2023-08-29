import streamlit as st
import matplotlib.pyplot as plt
import io
from PIL import Image

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
    if 'start_tasting' not in st.session_state:
        st.session_state.start_tasting = False
    
    st.title("Wine Tasting App")
    st.write("Welcome to our wine tasting experience. Let's explore the world of wines!")
    
    # Start tasting button
    if st.button("Start Tasting"):
        st.session_state.start_tasting = True

    if st.session_state.start_tasting:
        wine_options = ["Red", "White", "Rosé", "Sparkling"]
        selected_wine = st.selectbox("Choose a type of wine:", wine_options)

        # Visual Examination
        st.subheader("Visual Examination")
        appearance = st.text_input("Describe the wine's appearance:")
        clarity = st.radio("Select the clarity:", ["Clear", "Cloudy", "Opaque"])
        intensity = st.slider("Intensity:", 0, 10)

        # Olfactory Examination
        st.subheader("Olfactory Examination")
        aroma_options = ["Fruity", "Floral", "Spicy", "Woody", "Earthy", "Citrus"]
        selected_aromas = st.multiselect("Select the wine's aromas:", aroma_options)

        # Gustatory Examination
        st.subheader("Gustatory Examination")
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

