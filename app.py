import streamlit as st
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge

st.set_page_config(page_title="Samco API Sandbox", layout="wide")
st.title("🧪 Samco API v3.1 - Isolation Test")
st.markdown("---")

# -------------------------------------------------------------------------
# STATE MANAGEMENT
# Prevent re-authentication on every Streamlit rerun
# -------------------------------------------------------------------------
if 'samco_token' not in st.session_state:
    st.session_state.samco_token = None
if 'samco_bridge' not in st.session_state:
    st.session_state.samco_bridge = None

# -------------------------------------------------------------------------
# AUTHENTICATION LOGIC (Step 2)
# -------------------------------------------------------------------------
def authenticate_samco():
    st.info("Attempting to authenticate with Samco servers...")
    try:
        # Securely pull from Streamlit Secrets (DO NOT HARDCODE)
        user_id = st.secrets["samco"]["userId"]
        password = st.secrets["samco"]["password"]
        yob = str(st.secrets["samco"]["yob"]) 

        # Initialize the official SDK bridge
        samco = StocknoteAPIPythonBridge()

        # Attempt Headless Login (Requires the 'body' dictionary)
        login_response = samco.login(body={
            "userId": user_id, 
            "password": password, 
            "yob": yob
        })

        # Process Response
        if type(login_response) is dict and login_response.get('sessionToken'):
            st.session_state.samco_token = login_response['sessionToken']
            
            # Lock the session token into the bridge object
            samco.set_session_token(sessionToken=st.session_state.samco_token)
            st.session_state.samco_bridge = samco

            st.success("✅ Authentication Successful! Token acquired.")
            with st.expander("View Raw Login Response (Safe to share, masks password)"):
                st.json(login_response)
        else:
            st.error("Authentication failed. Check the raw response below.")
            st.write(login_response) 

    except Exception as e:
        st.error(f"🚨 Exception Caught: {e}")
        st.warning("If this is a connection timeout, we've hit the dynamic IP whitelist block.")

# -------------------------------------------------------------------------
# UI CONTROLS & REST VERIFICATION (Step 3 - Restored!)
# -------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Get Token")
    if st.button("Run Authentication Test", type="primary"):
        authenticate_samco()

with col2:
    st.subheader("Step 2: Test Connection")
    # Only allow the REST test if we have successfully created the bridge object
    if st.button("Fetch Limits (REST Test)"):
        if st.session_state.samco_bridge and st.session_state.samco_token:
            try:
                # Using get_limits() to verify the token works on subsequent calls
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
st.write(
    "**Current Token Status:**", 
    "🟢 Active" if st.session_state.samco_token else "🔴 None"
)
