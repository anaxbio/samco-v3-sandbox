import streamlit as st
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge

st.set_page_config(page_title="Samco API Sandbox", layout="wide")
st.title("🧪 Samco API v3.1 - Isolation Test")
st.markdown("---")

# -------------------------------------------------------------------------
# STATE MANAGEMENT
# -------------------------------------------------------------------------
if 'samco_token' not in st.session_state:
    st.session_state.samco_token = None
if 'samco_bridge' not in st.session_state:
    st.session_state.samco_bridge = None

# -------------------------------------------------------------------------
# AUTHENTICATION LOGIC
# -------------------------------------------------------------------------
def authenticate_samco(totp_code):
    if not totp_code:
        st.warning("⚠️ Please enter the 8-digit TOTP code first.")
        return

    st.info("Attempting to authenticate with Samco servers...")
    try:
        user_id = st.secrets["samco"]["userId"]
        password = st.secrets["samco"]["password"]
        yob = str(st.secrets["samco"]["yob"]) 

        samco = StocknoteAPIPythonBridge()

        # THE FIX: Injecting the dynamic TOTP code as the accessToken
        login_response = samco.login(body={
            "userId": user_id, 
            "password": password, 
            "yob": yob,
            "accessToken": totp_code 
        })

        # Process Response
        if type(login_response) is dict and login_response.get('sessionToken'):
            st.session_state.samco_token = login_response['sessionToken']
            samco.set_session_token(sessionToken=st.session_state.samco_token)
            st.session_state.samco_bridge = samco

            st.success("✅ Authentication Successful! Token acquired.")
            with st.expander("View Raw Login Response"):
                st.json(login_response)
        else:
            st.error("Authentication failed. Check the raw response below.")
            st.write(login_response) 

    except Exception as e:
        st.error(f"🚨 Exception Caught: {e}")

# -------------------------------------------------------------------------
# UI CONTROLS
# -------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Get Token")
    # NEW: Text input for the TOTP
    user_totp = st.text_input("Enter 8-digit App Code:", max_chars=8)
    
    if st.button("Run Authentication Test", type="primary"):
        authenticate_samco(user_totp)

with col2:
    st.subheader("Step 2: Test Connection")
    if st.button("Fetch Limits (REST Test)"):
        if st.session_state.samco_bridge and st.session_state.samco_token:
            try:
                limits = st.session_state.samco_bridge.get_limits()
                st.success("✅ REST Call Successful!")
                st.json(limits)
            except Exception as e:
                st.error(f"REST Call Failed: {e}")
        else:
            st.warning("⚠️ Please authenticate first using the button on the left.")

# -------------------------------------------------------------------------
# STATUS FOOTER
# -------------------------------------------------------------------------
st.markdown("---")
st.write("**Current Token Status:**", "🟢 Active" if st.session_state.samco_token else "🔴 None")
