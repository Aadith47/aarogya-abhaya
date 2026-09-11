import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf

st.title("Child Malnutrition Detection")
st.write("Upload a child image to detect visible signs of malnutrition.")

# Load trained model
model = tf.keras.models.load_model("malnutrition_model.h5")

uploaded_file = st.file_uploader("Upload Child Image", type=["jpg","jpeg","png"])

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    img = image.resize((224,224))
    img_array = np.array(img)/255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]

    if prediction > 0.5:
        st.error(f"Prediction: Malnourished ({prediction*100:.2f}%)")
    else:
        st.success(f"Prediction: Healthy ({(1-prediction)*100:.2f}%)")

    st.warning("⚠ This is a demo system and not a medical diagnostic tool.")