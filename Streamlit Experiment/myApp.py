import streamlit as st
import pandas as pd
import numpy as np

st.title('My First Streamlit App')

# Create some sample data
data = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100)
})

# Display a chart
st.line_chart(data)

# Add interactive widgets
name = st.text_input('Enter your name:')
if name:
    st.write(f'Hello, {name}!')