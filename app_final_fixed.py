import streamlit as st
import os
import base64
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet
import io

# 🔐 BACKBLAZE B2 CONFIGURATION
B2_CONFIG = {
    'KEY_ID': '85cf99ffd52a',
    'APPLICATION_KEY': '005397d0277899393475ff8a8108c70aa69967815c', 
    'BUCKET_NAME': 'securebanking'
}

st.set_page_config(
    page_title="Secure Banking Transfer",
    page_icon="🏦",
    layout="wide"
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; text-align: center; margin-bottom: 2rem; }
    .big-button { font-size: 1.2rem !important; padding: 20px !important; }
    .login-container { max-width: 400px; margin: 0 auto; padding: 2rem; }
    .success-box { background: #D1FAE5; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .file-id-box { background: #F3F4F6; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

class WorkingCloudStorage:
    def __init__(self):
        self.connected = False
        self.bucket = None
        self.connect()
    
    def connect(self):
        """Connect to Backblaze B2"""
        try:
            from b2sdk.v2 import B2Api
            self.api = B2Api()
            self.api.authorize_account("production", B2_CONFIG['KEY_ID'], B2_CONFIG['APPLICATION_KEY'])
            self.bucket = self.api.get_bucket_by_name(B2_CONFIG['BUCKET_NAME'])
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            return False
    
    def download_file_working(self, cloud_path):
        """WORKING DOWNLOAD METHOD - Uses correct B2 SDK approach"""
        try:
            # Remove leading slash if present
            cloud_path = cloud_path.lstrip('/')
            
            st.info(f"🔍 Downloading: {cloud_path}")
            
            # METHOD 1: Use get_download_url_for_filename (recommended approach)
            try:
                download_url = self.bucket.get_download_url(file_name=cloud_path)
                
                # Download via requests
                import requests
                response = requests.get(download_url)
                if response.status_code == 200:
                    return response.content, "✅ File downloaded via URL!"
                else:
                    st.warning(f"URL download failed: {response.status_code}")
            except Exception as url_error:
                st.warning(f"URL method failed: {str(url_error)}")
            
            # METHOD 2: Direct file download (alternative approach)
            try:
                # Get file info first
                file_info = self.bucket.get_file_info_by_name(cloud_path)
                if file_info:
                    # Download the file content
                    file_response = self.bucket.download_file_by_name(cloud_path)
                    
                    # Use BytesIO to capture content
                    file_buffer = io.BytesIO()
                    file_response.save(file_buffer)
                    file_content = file_buffer.getvalue()
                    file_buffer.close()
                    
                    return file_content, "✅ File downloaded directly!"
                else:
                    return None, "❌ File not found in bucket"
                    
            except Exception as direct_error:
                return None, f"❌ Direct download failed: {str(direct_error)}"
                
        except Exception as e:
            return None, f"❌ Download error: {str(e)}"

class WorkingBankingApp:
    def __init__(self):
        self.cloud = WorkingCloudStorage()
        
        # Initialize encryption
        if 'fernet_key' not in st.session_state:
            st.session_state.fernet_key = Fernet.generate_key()
            st.session_state.fernet = Fernet(st.session_state.fernet_key)
        
        # User management
        if 'users' not in st.session_state:
            st.session_state.users = {
                "demo@bank.com": {
                    "password_hash": hashlib.sha256("Demo@123".encode()).hexdigest(),
                    "name": "Demo User"
                }
            }
        
        # File storage
        if 'file_metadata' not in st.session_state:
            st.session_state.file_metadata = {}
        
        # Authentication
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.current_user = ""

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, email, password):
        if email in st.session_state.users:
            user_data = st.session_state.users[email]
            if user_data["password_hash"] == self.hash_password(password):
                st.session_state.logged_in = True
                st.session_state.current_user = email
                return True
        return False

    def register(self, email, password, name):
        if email in st.session_state.users:
            return False, "User already exists"
        
        st.session_state.users[email] = {
            "password_hash": self.hash_password(password),
            "name": name
        }
        
        if email not in st.session_state.file_metadata:
            st.session_state.file_metadata[email] = {}
            
        return True, "Registration successful!"

    def encrypt_data(self, data):
        return st.session_state.fernet.encrypt(data)

    def decrypt_data(self, encrypted_data):
        return st.session_state.fernet.decrypt(encrypted_data)

    def upload_file(self, uploaded_file):
        """Upload file to cloud"""
        try:
            # Read file data
            file_data = uploaded_file.getvalue()
            
            # Encrypt the data
            encrypted_data = self.encrypt_data(file_data)
            
            # Generate file ID
            file_id = base64.urlsafe_b64encode(os.urandom(8)).decode()[:8]
            cloud_filename = f"users/{st.session_state.current_user}/{file_id}_{uploaded_file.name}"
            
            # Upload to B2
            try:
                self.cloud.bucket.upload_bytes(encrypted_data, cloud_filename)
                
                # Store metadata
                if st.session_state.current_user not in st.session_state.file_metadata:
                    st.session_state.file_metadata[st.session_state.current_user] = {}
                
                st.session_state.file_metadata[st.session_state.current_user][file_id] = {
                    'name': uploaded_file.name,
                    'cloud_path': cloud_filename,
                    'size': len(file_data),
                    'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                return True, file_id, "✅ File uploaded successfully!"
                
            except Exception as upload_error:
                return False, None, f"❌ Upload failed: {str(upload_error)}"
                
        except Exception as e:
            return False, None, f"❌ Error: {str(e)}"

    def download_file(self, file_id):
        """Download file from cloud"""
        try:
            # Check if we have metadata for this file
            user_files = st.session_state.file_metadata.get(st.session_state.current_user, {})
            
            if file_id in user_files:
                file_info = user_files[file_id]
                cloud_path = file_info['cloud_path']
            else:
                # Try to guess the path
                cloud_path = f"users/{st.session_state.current_user}/{file_id}"
                file_info = {'name': f'file_{file_id}', 'cloud_path': cloud_path}
            
            # Download from cloud
            file_content, message = self.cloud.download_file_working(cloud_path)
            
            if file_content:
                try:
                    # Try to decrypt
                    decrypted_data = self.decrypt_data(file_content)
                    return True, decrypted_data, file_info
                except:
                    # Return encrypted data if decryption fails
                    return True, file_content, {**file_info, 'encrypted': True}
            else:
                return False, None, message
                
        except Exception as e:
            return False, None, f"❌ Download error: {str(e)}"

    def run(self):
        st.markdown('<h1 class="main-header">🏦 Secure Banking Transfer</h1>', unsafe_allow_html=True)
        
        # Show cloud status
        if self.cloud.connected:
            st.success("✅ Connected to Backblaze B2 Cloud")
        else:
            st.error("❌ Cloud Disconnected")
        
        if not st.session_state.logged_in:
            self.show_login()
        else:
            self.show_main_app()

    def show_login(self):
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 🔐 Login to Secure Banking")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", value="demo@bank.com")
                password = st.text_input("Password", type="password", value="Demo@123")
                login_btn = st.form_submit_button("Login")
                
                if login_btn:
                    if self.login(email, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                register_btn = st.form_submit_button("Register")
                
                if register_btn:
                    if password == confirm:
                        success, message = self.register(email, password, name)
                        if success:
                            st.success(f"✅ {message}")
                            if self.login(email, password):
                                st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ Passwords don't match")
        
        st.markdown("---")
        st.info("**Demo Credentials:** demo@bank.com / Demo@123")
        st.markdown('</div>', unsafe_allow_html=True)

    def show_main_app(self):
        st.sidebar.success(f"👋 Welcome, {st.session_state.users[st.session_state.current_user]['name']}")
        
        if self.cloud.connected:
            st.sidebar.success("☁️ Cloud: CONNECTED")
        else:
            st.sidebar.error("☁️ Cloud: DISCONNECTED")
        
        # File count
        user_files = st.session_state.file_metadata.get(st.session_state.current_user, {})
        st.sidebar.metric("📁 Files", len(user_files))
        
        if st.sidebar.button("🔄 Reconnect to Cloud"):
            success = self.cloud.connect()
            if success:
                st.sidebar.success("✅ Reconnected!")
            else:
                st.sidebar.error("❌ Reconnection failed")
            st.rerun()
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()
        
        menu = st.sidebar.radio("Navigation", ["Dashboard", "Upload", "Download", "My Files"])
        
        if menu == "Dashboard":
            self.show_dashboard()
        elif menu == "Upload":
            self.show_upload()
        elif menu == "Download":
            self.show_download()
        elif menu == "My Files":
            self.show_my_files()

    def show_dashboard(self):
        st.markdown("## 📊 Dashboard")
        
        user_files = st.session_state.file_metadata.get(st.session_state.current_user, {})
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if self.cloud.connected:
                st.success("✅ Connected to Backblaze B2 Cloud")
                st.info("Your files are securely stored in the cloud with encryption.")
            else:
                st.error("❌ Cloud disconnected - please reconnect")
        with col2:
            st.metric("📁 Files", len(user_files))

    def show_upload(self):
        st.markdown("## 📤 Upload to Cloud")
        
        if not self.cloud.connected:
            st.error("❌ Cloud disconnected - cannot upload")
            return
        
        uploaded_file = st.file_uploader("Choose file to upload", type=['pdf', 'txt', 'jpg', 'png', 'docx'])
        
        if uploaded_file:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size} bytes")
            
            if st.button("🔒 Encrypt & Upload", type="primary"):
                with st.spinner("Uploading to cloud..."):
                    success, file_id, message = self.upload_file(uploaded_file)
                    
                    if success:
                        st.success(message)
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Upload Successful!</h4>
                            <p><strong>File ID:</strong></p>
                            <div class="file-id-box">{file_id}</div>
                            <p><em>Save this File ID to download your file later!</em></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(message)

    def show_download(self):
        st.markdown("## 📥 Download from Cloud")
        
        if not self.cloud.connected:
            st.error("❌ Cloud disconnected - cannot download")
            return
        
        # Show user's files for easy access
        user_files = st.session_state.file_metadata.get(st.session_state.current_user, {})
        
        if user_files:
            st.write("**Your uploaded files:**")
            for fid, info in user_files.items():
                st.write(f"- `{fid}` : {info['name']} ({info['size']} bytes)")
        
        file_id = st.text_input("Enter File ID to download", placeholder="Enter your File ID here...")
        
        if st.button("🚀 DOWNLOAD NOW", type="primary", use_container_width=True):
            if not file_id.strip():
                st.error("❌ Please enter a File ID")
                return
                
            with st.spinner("Downloading from cloud..."):
                success, file_data, message = self.download_file(file_id)
                
                if success:
                    if isinstance(message, dict):  # file_info
                        file_info = message
                        st.success("✅ File downloaded successfully!")
                        
                        # Determine file type for download
                        if file_info.get('encrypted'):
                            file_name = f"encrypted_{file_id}.bin"
                            mime_type = "application/octet-stream"
                        else:
                            file_name = f"downloaded_{file_info.get('name', file_id)}"
                            mime_type = "application/octet-stream"
                        
                        # Create download button
                        st.download_button(
                            label="📥 CLICK TO DOWNLOAD FILE",
                            data=file_data,
                            file_name=file_name,
                            mime=mime_type,
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.error(f"Unexpected response: {message}")
                else:
                    st.error(f"❌ {message}")

    def show_my_files(self):
        st.markdown("## 📁 My Files")
        
        user_files = st.session_state.file_metadata.get(st.session_state.current_user, {})
        
        if not user_files:
            st.info("No files uploaded yet. Go to the Upload section to add files.")
            return
        
        st.write(f"**Total files:** {len(user_files)}")
        
        for file_id, file_info in user_files.items():
            with st.expander(f"📄 {file_info['name']} - {file_info['upload_time']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**File ID:** `{file_id}`")
                    st.write(f"**Cloud Path:** `{file_info['cloud_path']}`")
                    st.write(f"**Size:** {file_info['size']} bytes")
                    st.write(f"**Type:** {file_info.get('type', 'Unknown')}")
                with col2:
                    if st.button(f"Download", key=f"dl_{file_id}", type="primary"):
                        # Trigger download
                        success, file_data, message = self.download_file(file_id)
                        if success:
                            st.download_button(
                                label="📥 Download Now",
                                data=file_data,
                                file_name=f"decrypted_{file_info['name']}",
                                mime="application/octet-stream",
                                key=f"btn_{file_id}"
                            )
                        else:
                            st.error(message)

if __name__ == "__main__":
    app = WorkingBankingApp()
    app.run()