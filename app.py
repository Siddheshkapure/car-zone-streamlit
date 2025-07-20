import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pickle
import math

# ----------------- Load model and data -----------------
model = pickle.load(open('model.pkl', 'rb'))
cars_data = pd.read_csv('Cardetails.csv')

# ----------------- Helper Functions -----------------
def get_brand_name(car_name):
    return car_name.split(' ')[0].strip()

def encode_input(df):
    df = df.copy()
    df['owner'].replace(['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner', 'Test Drive Car'],
                        [1, 2, 3, 4, 5], inplace=True)
    df['fuel'].replace(['Diesel', 'Petrol', 'LPG', 'CNG'], [1, 2, 3, 4], inplace=True)
    df['seller_type'].replace(['Individual', 'Dealer', 'Trustmark Dealer'], [1, 2, 3], inplace=True)
    df['transmission'].replace(['Manual', 'Automatic'], [1, 2], inplace=True)
    df['name'].replace([
        'Maruti', 'Skoda', 'Honda', 'Hyundai', 'Toyota', 'Ford', 'Renault',
        'Mahindra', 'Tata', 'Chevrolet', 'Datsun', 'Jeep', 'Mercedes-Benz',
        'Mitsubishi', 'Audi', 'Volkswagen', 'BMW', 'Nissan', 'Lexus',
        'Jaguar', 'Land', 'MG', 'Volvo', 'Daewoo', 'Kia', 'Fiat', 'Force',
        'Ambassador', 'Ashok', 'Isuzu', 'Opel'], list(range(1, 32)), inplace=True)
    return df

cars_data['name'] = cars_data['name'].apply(get_brand_name)

# ----------------- Streamlit App -----------------
st.set_page_config(page_title="Car Zone", page_icon="🚗", layout="wide")

# Side logo and project name
st.sidebar.image('logo.png', width=150)  # Logo
st.sidebar.title("Car Price Prediction")  # Project name

# Tabs
tabs = st.tabs([
    "🏠 Home", "🚗 Car Price Prediction", "🚙 Top 5 Cars Under Budget",
    "⛽ Filter Cars by Fuel", "📈 Mileage vs Price", "🔍 Compare Two Cars",
    "❤️ Saved Cars", "💸 Loan EMI Calculator"
])

# ----------------- 1. Home -----------------
with tabs[0]:
    st.title("Welcome to Car Zone 🚗")
    st.markdown("<h3 style='text-align: center;'>Your one-stop solution for buying, comparing, and predicting car prices!</h3>", unsafe_allow_html=True)
    st.video('animation.mp4')

    # Footer with project info
    st.markdown("---")
    st.markdown("""
    **Name:** Siddhesh Sachin Kapure  
    **Roll No:** 20  
    **Class:** TEAIDS  
    """)

# ----------------- 2. Car Price Prediction -----------------
with tabs[1]:
    st.header("🚗 Predict Car Selling Price")
    with st.form("prediction_form"):
        name = st.selectbox('Car Brand', sorted(cars_data['name'].unique()))
        year = st.slider('Year of Manufacture', 1994, 2024, 2020)
        km_driven = st.slider('Kilometers Driven', 11, 200000, 30000)
        fuel = st.selectbox('Fuel Type', cars_data['fuel'].unique())
        seller_type = st.selectbox('Seller Type', cars_data['seller_type'].unique())
        transmission = st.selectbox('Transmission Type', cars_data['transmission'].unique())
        owner = st.selectbox('Owner Type', cars_data['owner'].unique())
        mileage = st.slider('Mileage (km/l)', 10, 40, 18)
        engine = st.slider('Engine Capacity (CC)', 700, 5000, 1200)
        max_power = st.slider('Max Power (BHP)', 0, 200, 75)
        seats = st.slider('Number of Seats', 2, 10, 5)
        submit = st.form_submit_button("Predict Price 🚗💰")

    if submit:
        input_data = pd.DataFrame([[name, year, km_driven, fuel, seller_type, transmission, owner, mileage, engine, max_power, seats]],
                                  columns=['name', 'year', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner', 'mileage', 'engine', 'max_power', 'seats'])
        input_encoded = encode_input(input_data)
        prediction = model.predict(input_encoded)[0]
        st.success(f"🎉 Estimated Car Price: ₹ {round(prediction/100000, 2)} Lakh")

# ----------------- 3. Top 5 Cars Under Budget -----------------
with tabs[2]:
    st.header("🚙 Top 5 Best Cars Under Your Budget")
    budget = st.number_input('Enter your Budget (in ₹)', min_value=50000, max_value=10000000, value=500000, step=50000)
    if st.button("Find Top 5 Cars 💡"):
        top_cars = cars_data[cars_data['selling_price'] <= budget].sort_values(by='selling_price', ascending=False).head(5)
        if not top_cars.empty:
            st.success(f"Found {len(top_cars)} cars under your budget!")
            st.dataframe(top_cars[['name', 'year', 'km_driven', 'fuel', 'transmission', 'selling_price']])
        else:
            st.warning("No cars found under this budget.")

# ----------------- 4. Filter Cars by Fuel -----------------
with tabs[3]:
    st.header("⛽ Filter Cars by Fuel Type and More")
    fuel_choice = st.selectbox('Fuel Type', ['All'] + list(cars_data['fuel'].unique()))
    transmission_choice = st.selectbox('Transmission', ['All'] + list(cars_data['transmission'].unique()))
    owner_choice = st.selectbox('Owner', ['All'] + list(cars_data['owner'].unique()))
    brand_choice = st.selectbox('Brand', ['All'] + list(cars_data['name'].unique()))
    price_range = st.slider('Price Range', 0, int(cars_data['selling_price'].max()), (0, 1000000), step=50000)

    filtered_data = cars_data.copy()
    if fuel_choice != 'All':
        filtered_data = filtered_data[filtered_data['fuel'] == fuel_choice]
    if transmission_choice != 'All':
        filtered_data = filtered_data[filtered_data['transmission'] == transmission_choice]
    if owner_choice != 'All':
        filtered_data = filtered_data[filtered_data['owner'] == owner_choice]
    if brand_choice != 'All':
        filtered_data = filtered_data[filtered_data['name'] == brand_choice]
    filtered_data = filtered_data[(filtered_data['selling_price'] >= price_range[0]) & 
                                  (filtered_data['selling_price'] <= price_range[1])]
    st.dataframe(filtered_data[['name', 'year', 'km_driven', 'fuel', 'transmission', 'selling_price']])

# ----------------- 5. Mileage vs Price (Best Value Cars) -----------------
with tabs[4]:
    st.header("📈 Mileage vs Price - Best Value Cars")
    cars_data['value_for_money'] = cars_data['selling_price'] / pd.to_numeric(cars_data['mileage'], errors='coerce')
    best_value_cars = cars_data.sort_values(by='value_for_money').head(5)
    if not best_value_cars.empty:
        st.success("Top 5 Best Value for Money Cars:")
        st.dataframe(best_value_cars[['name', 'year', 'km_driven', 'fuel', 'mileage', 'selling_price', 'value_for_money']])
    else:
        st.warning("No cars available for value for money analysis.")

# ----------------- 6. Compare Two Cars -----------------
with tabs[5]:
    st.header("🔍 Compare Two Cars")
    col1, col2 = st.columns(2)
    with col1:
        car1 = st.selectbox('First Car', sorted(cars_data['name'].unique()))
    with col2:
        car2 = st.selectbox('Second Car', sorted(cars_data['name'].unique()))
    
    if st.button("Compare Cars 🆚"):
        car1_data = cars_data[cars_data['name'] == car1].sort_values(by='selling_price').head(1)
        car2_data = cars_data[cars_data['name'] == car2].sort_values(by='selling_price').head(1)

        if not car1_data.empty and not car2_data.empty:
            compare_df = pd.DataFrame({
                'Car': [car1, car2],
                'Price (₹)': [car1_data['selling_price'].values[0], car2_data['selling_price'].values[0]],
                'Fuel': [car1_data['fuel'].values[0], car2_data['fuel'].values[0]],
                'Transmission': [car1_data['transmission'].values[0], car2_data['transmission'].values[0]],
                'Year': [car1_data['year'].values[0], car2_data['year'].values[0]]
            })
            st.table(compare_df)
            better_car = car1 if car1_data['selling_price'].values[0] <= car2_data['selling_price'].values[0] else car2
            st.success(f"✅ Suggestion: **{better_car}** offers better value!")

# ----------------- 7. Save Favorite Cars -----------------
with tabs[6]:
    st.header("❤️ Save Favorite Cars")
    if "saved_cars" not in st.session_state:
        st.session_state.saved_cars = []

    saved_car = st.selectbox('Select Car to Save', sorted(cars_data['name'].unique()))
    if st.button("Save Car ❤️"):
        st.session_state.saved_cars.append(saved_car)
        st.success(f"🚗 **{saved_car}** has been saved to your favorites!")
    
    if st.session_state.saved_cars:
        st.subheader("Your Saved Cars")
        st.write(st.session_state.saved_cars)

# ----------------- 8. EMI Calculator -----------------
with tabs[7]:
    st.header("💸 Loan EMI Calculator")
    car_price = st.number_input("Car Price (₹)", min_value=50000, max_value=10000000, value=500000, step=50000)
    loan_term = st.slider("Loan Term (in months)", 12, 60, 36)
    interest_rate = st.slider("Annual Interest Rate (%)", 5.0, 20.0, 10.0, 0.5)
    
    emi = (car_price * (interest_rate / 100) * (1 + interest_rate / 100) ** loan_term) / ((1 + interest_rate / 100) ** loan_term - 1)
    st.write(f"EMI for ₹{car_price} loan at {interest_rate}% interest for {loan_term} months is ₹{round(emi, 2)}")
