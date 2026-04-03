import streamlit as st
from stocknotebridge import Snapi

# Set up the sandbox page
st.set_page_config(page_title="Samco API Sandbox", layout="wide")
st.title("🧪 Samco API v3.1 - Isolation Test")
st.markdown("---")

# -------------------------------------------------------------------------
# STATE MANAGEMENT
# Prevent re-authentication on every Streamlit rerun
# -------------------------------------------------------------------------
if 'samco_token' not in st.session_state:
    st.session_state.samco_token = None
if 'samco_snapi' not in st.session_state:
    st.session_state.samco_snapi = None


# -------------------------------------------------------------------------
# AUTHENTICATION LOGIC (Step 2)
# -------------------------------------------------------------------------
def authenticate_samco():
    st.info("Attempting to authenticate with Samco servers...")
    try:
        # 1. Retrieve secrets securely
        user_id = st.secrets["samco"]["userId"]
        password = st.secrets["samco"]["password"]
        yob = str(st.secrets["samco"]["yob"]) # Ensure YOB is passed as a string

        # 2. Initialize the bridge
        snapi = Snapi()

        # 3. Attempt Headless Login
        login_response = snapi.login(userid=user_id, password=password, yob=yob)

        # 4. Process the Response
        if login_response and login_response.get('sessionToken'):
            # Store the token
            st.session_state.samco_token = login_response['sessionToken']
            
            # Re-initialize Snapi with the active token for future calls
            # Note: Checking documentation to ensure this is how Snapi handles existing sessions
            st.session_state.samco_snapi = Snapi()
            st.session_state.samco_snapi.set_session_token(st.session_state.samco_token) 

            st.success("✅ Authentication Successful! Token acquired.")
            with st.expander("View Raw Login Response (Safe to share, masks password)"):
                st.json(login_response)
        else:
            st.error("Authentication failed. No token found in the response.")
            st.json(login_response) # Output the raw response to see what Samco returned

    except Exception as e:
        st.error(f"🚨 Authentication Exception Caught: {e}")
        st.warning("If you see a connection reset or timeout error here, it is highly likely related to Streamlit Cloud's dynamic IPs and Samco's v3.1 whitelist policy.")


# -------------------------------------------------------------------------
# UI CONTROLS & REST VERIFICATION (Step 3)
# -------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Get Token")
    if st.button("Run Authentication Test", type="primary"):
        authenticate_samco()

with col2:
    st.subheader("Step 2: Test Connection")
    # Only allow the REST test if we have successfully created the Snapi object
    if st.button("Fetch Limits (REST Test)"):
        if st.session_state.samco_snapi and st.session_state.samco_token:
            try:
                # Using get_limits() as a safe, non-execution REST call to verify the token works
                limits = st.session_state.samco_snapi.get_limits()
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
