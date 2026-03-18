import streamlit as st
import sqlite3
import random
import time
import base64

st.set_page_config(page_title="Restaurant App", layout="wide")

# ---------------- LOAD LOCAL IMAGE ---------------- #
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

bg_image = get_base64_image("Food image.jpg")

# ---------------- GLOBAL STYLE (APPLY TO ALL PAGES) ---------------- #
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
}}

h1, h2, h3, h4, h5, h6, p, label {{
    color: white !important;
}}

input {{
    background-color: rgba(255,255,255,0.9) !important;
    color: black !important;
}}

div.stButton > button {{
    width: 100%;
    background: linear-gradient(to right, #7b2ff7, #f107a3);
    color: white !important;
    border-radius: 8px;
    height: 45px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ---------------- #
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT, password TEXT)''')

# ---------------- SESSION ---------------- #
if "page" not in st.session_state:
    st.session_state.page = "login"

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "user" not in st.session_state:
    st.session_state.user = None

if "category" not in st.session_state:
    st.session_state.category = None

# ---------------- LOGOUT FUNCTION ---------------- #
def logout_button():
    col1, col2 = st.columns([9,1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.cart = {}
            st.session_state.page = "login"
            st.rerun()

# ---------------- MENU WITH CATEGORY ---------------- #
menu = {
    "Chicken Pahadi Kabab": {
        "price": 400,
        "category": "Non-Veg",
        "img": "images/Beetroot.jpg"
    },
    "Chicken Lollypop": {
        "price": 380,
        "category": "Non-Veg",
        "img": "images/Beetroot.jpg"
    },
    "Chicken Manchurian": {
        "price": 395,
        "category": "Non-Veg",
        "img": "images/Beetroot.jpg"
    },
    "Prawns Fried Rice": {
        "price": 400,
        "category": "Non-Veg",
        "img": "images/Beetroot.jpg"
    },

    "Fried Rice": {
        "price": 200,
        "category": "Veg",
        "img": "images/Capsicum.jpg"
    },

    "Lassi": {
        "price": 20,
        "category": "Cool Drinks",
        "img": "images/Maaza.jpg"
    }
}

# ---------------- LOGIN ---------------- #
def login():
    st.markdown("<h1 style='text-align:center;'>Log In 🔐</h1>", unsafe_allow_html=True)

    user = st.text_input("Email / Mobile")
    password = st.text_input("Password", type="password")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Log In"):
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, password))
            if c.fetchone():
                st.session_state.user = user
                st.session_state.page = "category"
                st.rerun()
            else:
                st.error("Invalid credentials")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Forgot Password"):
            st.session_state.page = "forgot"
            st.rerun()

    with col2:
        if st.button("Sign Up"):
            st.session_state.page = "signup"
            st.rerun()

# ---------------- FORGOT PASSWORD ---------------- #
def forgot_password():
    logout_button()
    st.title("🔑 Reset Password")

    user = st.text_input("Enter Email / Mobile")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Reset Password"):
        c.execute("SELECT * FROM users WHERE username=?", (user,))
        if c.fetchone():
            c.execute("UPDATE users SET password=? WHERE username=?", (new_pass, user))
            conn.commit()
            st.success("Password updated!")
            time.sleep(1)
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("User not found")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- CATEGORY PAGE ---------------- #
def category_page():
    logout_button()
    st.title("🍽 Select Category")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🍗 Non-Veg"):
            st.session_state.category = "Non-Veg"
            st.session_state.page = "menu"
            st.rerun()

    with col2:
        if st.button("🥦 Veg"):
            st.session_state.category = "Veg"
            st.session_state.page = "menu"
            st.rerun()

    with col3:
        if st.button("🥤 Cool Drinks"):
            st.session_state.category = "Cool Drinks"
            st.session_state.page = "menu"
            st.rerun()

# ---------------- MENU PAGE ---------------- #
def menu_page():
    logout_button()
    st.title(f"📋 {st.session_state.category} Menu")

    cols = st.columns(3)

    filtered_items = {k: v for k, v in menu.items() if v["category"] == st.session_state.category}

    for i, (item, details) in enumerate(filtered_items.items()):
        with cols[i % 3]:
            st.image(details["img"], use_container_width=True)
            st.write(f"**{item}**")
            st.write(f"₹{details['price']}")

            qty = st.number_input(f"Qty {item}", min_value=0, key=item)

            if st.button(f"Add {item}", key=f"add{item}"):
                if qty > 0:
                    st.session_state.cart[item] = (qty, details["price"])
                    st.success("Added to cart")
                    st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Back"):
            st.session_state.page = "category"
            st.rerun()

    with col2:
        if st.button("Go to Cart 🛒"):
            st.session_state.page = "cart"
            st.rerun()

# ---------------- CART ---------------- #
def cart_page():
    logout_button()
    st.title("🛒 Cart")

    total = 0

    for item, (qty, price) in list(st.session_state.cart.items()):
        col1, col2, col3, col4 = st.columns([3,1,1,1])

        with col1:
            st.write(item)
        with col2:
            new_qty = st.number_input("Qty", value=qty, key=f"cart{item}")
        with col3:
            total_item = new_qty * price
            st.write(f"₹{total_item}")
        with col4:
            if st.button("❌", key=f"remove{item}"):
                del st.session_state.cart[item]
                st.rerun()

        st.session_state.cart[item] = (new_qty, price)
        total += total_item

    gst = total * 0.05
    grand_total = total + gst

    st.write("---")
    st.write(f"Total: ₹{grand_total:.2f}")

    if st.button("Proceed to Payment"):
        st.session_state.page = "payment"
        st.rerun()

# ---------------- PAYMENT ---------------- #
def payment_page():
    logout_button()
    st.title("💳 Payment")

    if st.button("Pay Now"):
        if random.choice([True, False]):
            st.success("✅ Payment Successful")
            st.session_state.cart = {}
            time.sleep(1)
            st.session_state.page = "category"
            st.rerun()
        else:
            st.error("❌ Payment Failed")

# ---------------- SIGNUP ---------------- #
def signup():
    st.title("📝 Create Account")

    user = st.text_input("Email / Mobile")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        c.execute("INSERT INTO users VALUES (?, ?)", (user, password))
        conn.commit()
        st.success("Account created!")
        st.session_state.page = "login"
        st.rerun()

# ---------------- NAVIGATION ---------------- #
if st.session_state.page == "login":
    login()
elif st.session_state.page == "signup":
    signup()
elif st.session_state.page == "forgot":
    forgot_password()
elif st.session_state.page == "category":
    category_page()
elif st.session_state.page == "menu":
    menu_page()
elif st.session_state.page == "cart":
    cart_page()
elif st.session_state.page == "payment":
    payment_page()