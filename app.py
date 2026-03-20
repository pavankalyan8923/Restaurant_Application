import streamlit as st
import sqlite3
import random
import time
import base64
import qrcode
from io import BytesIO

st.set_page_config(page_title="Restaurant App", layout="wide")

# ---------------- LOAD LOCAL IMAGE ---------------- #
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

bg_image = get_base64_image("images/backgroung.jpg")

# ---------------- GLOBAL STYLE ---------------- #
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

# ---------------- LOGOUT ---------------- #
def logout_button():
    col1, col2 = st.columns([9,1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.session_state.cart = {}
            st.session_state.page = "login"
            st.rerun()

# ---------------- TOP BACK BUTTON ---------------- #
def top_back_button(target_page="category"):
    col1, col2 = st.columns([1,9])
    with col1:
        if st.button("⬅ Back", key=f"top_back_{target_page}"):
            st.session_state.page = target_page
            st.rerun()

# ---------------- MENU ---------------- #
menu = {
    "Veg Dum Biryani": {"price": 200, "category": "Veg", "img": "images/Veg Dum Biryani.jpg"},
    "Paneer Dum Biryani": {"price": 230, "category": "Veg", "img": "images/Paneer Dum Biryani.jpg"},
    "Egg Dum Biryani": {"price": 220, "category": "Egg", "img": "images/Egg Dum Biryani.jpg"},
    "Chicken Dum Biryani": {"price": 250, "category": "Non-Veg", "img": "images/Chicken Dum Biryani.jpg"},
    "Mutton Dum Biryani": {"price": 320, "category": "Non-Veg", "img": "images/Mutton Dum Biryani.jpg"},
    "Prawns Dum Biryani": {"price": 300, "category": "Non-Veg", "img": "images/Prawns Dum Biryani.jpg"},
    "Chicken Tikka Biryani": {"price": 280, "category": "Non-Veg", "img": "images/Chicken Tikka Biryani.jpg"},
    "Tandoor Dum Biryani": {"price": 290, "category": "Non-Veg", "img": "images/Tandoor Dum Biryani.jpg"},
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
    top_back_button("login")

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

# ---------------- CATEGORY ---------------- #
def category_page():
    logout_button()
    st.title("🍽 Select Category")

    col1, col2, col3, col4 = st.columns(4)

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
        if st.button("🥚 Egg"):
            st.session_state.category = "Egg"
            st.session_state.page = "menu"
            st.rerun()

    with col4:
        if st.button("🫓 Breads"):
            st.session_state.category = "Breads"
            st.session_state.page = "menu"
            st.rerun()

# ---------------- MENU ---------------- #
def menu_page():
    logout_button()
    top_back_button("category")

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
    top_back_button("menu")

    st.title("🛒 Cart")

    if not st.session_state.cart:
        st.warning("🛒 Your cart is empty!")
        if st.button("🍽 Go to Menu"):
            st.session_state.page = "category"
            st.rerun()
        return

    total = 0

    for item, (qty, price) in list(st.session_state.cart.items()):
        col1, col2, col3, col4 = st.columns([3,1,1,1])

        with col1:
            st.write(item)

        with col2:
            new_qty = st.number_input("Qty", min_value=0, value=qty, key=f"cart{item}")

        st.session_state.cart[item] = (new_qty, price)

        with col3:
            total_item = new_qty * price
            st.write(f"₹{total_item}")

        with col4:
            if st.button("❌", key=f"remove{item}"):
                del st.session_state.cart[item]
                st.rerun()

        total += total_item

    gst = total * 0.05
    grand_total = total + gst

    st.write("---")
    st.write(f"Total (incl. GST): ₹{grand_total:.2f}")

    if st.button("Proceed to Payment"):
        st.session_state.page = "payment"
        st.rerun()

# ---------------- PAYMENT ---------------- #
def payment_page():
    logout_button()
    top_back_button("cart")

    st.title("💳 UPI Payment")

    total = 0
    for item, (qty, price) in st.session_state.cart.items():
        total += qty * price

    gst = total * 0.05
    grand_total = round(total + gst, 2)

    st.subheader(f"Total Amount: ₹{grand_total}")

    upi_id = "9160358923-3@ybl"
    name = "Wonder Kitchen"

    upi_link = f"upi://pay?pa={upi_id}&pn={name}&am={grand_total}&cu=INR"

    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer)

    st.image(buffer, caption="📱 Scan & Pay using GPay / PhonePe / Paytm")
    st.info("After completing payment, click confirm below")

    if st.button("✅ I Have Paid"):
        st.session_state.last_order = st.session_state.cart.copy()
        st.session_state.cart = {}
        st.session_state.page = "success"
        st.rerun()

# ---------------- SUCCESS PAGE ---------------- #
def success_page():
    logout_button()

    st.markdown("<h1 style='text-align:center; color:lightgreen;'>✅ Order Placed Successfully!</h1>", unsafe_allow_html=True)
    st.balloons()

    st.write("### 🎉 Thank you for your order!")
    st.write("Your food is being prepared 🍽️")

    st.write("---")
    st.write("### 🧾 Order Summary")

    total = 0

    for item, (qty, price) in st.session_state.get("last_order", {}).items():
        st.write(f"{item} x {qty} = ₹{qty * price}")
        total += qty * price

    gst = total * 0.05
    grand_total = total + gst

    st.write("---")
    st.write(f"**Total Paid: ₹{grand_total:.2f}**")

    st.success("🚚 Estimated Delivery: 30-40 mins")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "category"
        st.rerun()

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
elif st.session_state.page == "success":
    success_page()