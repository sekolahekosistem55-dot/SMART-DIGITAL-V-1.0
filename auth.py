import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
from config import Config
from security import SecurityManager

class AuthManager:
    def __init__(self):
        self.security = SecurityManager()
    
    def verify_google_token(self, token: str) -> dict:
        """Verify Google OAuth token"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                Config.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
        except ValueError as e:
            raise e
    
    def login_user(self, user_info: dict):
        """Login user and set session state"""
        st.session_state['authenticated'] = True
        st.session_state['user_id'] = user_info['id']
        st.session_state['user_email'] = user_info['email']
        st.session_state['user_name'] = user_info['name']
        st.session_state['session_token'] = self.security.create_session_token(
            user_info['id'], user_info['email']
        )
    
    def logout_user(self):
        """Logout user and clear session"""
        for key in ['authenticated', 'user_id', 'user_email', 'user_name', 'session_token', 'grade_level']:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if 'authenticated' not in st.session_state:
            return False
        
        if not st.session_state['authenticated']:
            return False
        
        # Verify session token
        if 'session_token' in st.session_state:
            try:
                self.security.verify_session_token(st.session_state['session_token'])
                return True
            except:
                self.logout_user()
                return False
        
        return False
