import streamlit as st
import hashlib
from config import AUTH_CONFIG
import time

class Authenticator:
    """Gère l'authentification des utilisateurs."""
    
    def __init__(self):
        """Initialise l'authentificateur avec la configuration depuis config.py"""
        self.credentials = AUTH_CONFIG
        if 'last_attempt_time' not in st.session_state:
            st.session_state.last_attempt_time = 0
    
    def _hash_password(self, password: str) -> str:
        """Hash le mot de passe avec SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self) -> bool:
        """Gère le processus de login."""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if st.session_state.authenticated:
            return True
        
        # Cache le header Streamlit
        st.markdown("""
            <style>
                [data-testid="stHeader"] {visibility: hidden;}
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                .block-container {padding-top: 1rem;}
                
                /* Style pour l'animation de succès */
                @keyframes slideIn {
                    from {
                        transform: translateY(-10px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                .success-message {
                    animation: slideIn 0.5s ease-out;
                    padding: 1rem;
                    background-color: rgba(36, 161, 88, 0.1);
                    border-left: 4px solid #24A158;
                    margin: 1rem 0;
                }
                .error-message {
                    animation: slideIn 0.5s ease-out;
                    padding: 1rem;
                    background-color: rgba(176, 52, 40, 0.1);
                    border-left: 4px solid #B03428;
                    margin: 1rem 0;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Centrer le formulaire de login
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### Connexion au Dashboard NPS")
            
            # Vérifier le délai entre les tentatives
            current_time = time.time()
            time_since_last_attempt = current_time - st.session_state.last_attempt_time
            
            # Si moins de 3 secondes depuis la dernière tentative
            if time_since_last_attempt < 3:
                st.warning(f"Veuillez patienter {3 - int(time_since_last_attempt)} secondes avant de réessayer...")
                time.sleep(min(3 - time_since_last_attempt, 3))
            
            username = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            
            login_placeholder = st.empty()
            
            if st.button("Se connecter"):
                st.session_state.last_attempt_time = current_time
                
                with st.spinner("Vérification des identifiants..."):
                    time.sleep(1)  # Délai artificiel pour l'UX
                    
                    if username in self.credentials["users"]:
                        stored_password = self.credentials["users"][username]["password"]
                        if self._hash_password(password) == stored_password:
                            # Animation de succès
                            success_placeholder = st.empty()
                            for i in range(3):
                                success_placeholder.markdown(f"""
                                    <div class="success-message">
                                        <h3>Connexion réussie! {'.' * (i + 1)}</h3>
                                    </div>
                                """, unsafe_allow_html=True)
                                time.sleep(0.5)
                            
                            st.session_state.authenticated = True
                            st.session_state.user = username
                            st.session_state.user_role = self.credentials["users"][username]["role"]
                            time.sleep(0.5)  # Petit délai avant le rechargement
                            st.rerun()
                        else:
                            time.sleep(1)  # Délai avant l'affichage de l'erreur
                            st.markdown("""
                                <div class="error-message">
                                    <h3>❌ Mot de passe incorrect</h3>
                                    <p>Veuillez vérifier vos identifiants et réessayer.</p>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        time.sleep(1)  # Délai avant l'affichage de l'erreur
                        st.markdown("""
                            <div class="error-message">
                                <h3>❌ Utilisateur inconnu</h3>
                                <p>Cet email n'est pas enregistré dans notre système.</p>
                            </div>
                        """, unsafe_allow_html=True)
        
        return st.session_state.authenticated

    def check_admin(self) -> bool:
        """Vérifie si l'utilisateur courant est un administrateur."""
        return (st.session_state.get('authenticated', False) and 
                st.session_state.get('user_role') == "admin")
    
    def logout(self):
        """Déconnecte l'utilisateur."""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_role = None