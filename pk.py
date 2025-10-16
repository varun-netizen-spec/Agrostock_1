# app.py - AgroStock: Complete Cattle Management System
import streamlit as st
import pandas as pd
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="AgroStock - Cattle Analytics",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for colorful UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        display: inline-block;
        margin-left: 10px;
    }
    .farmer-badge { background-color: #96CEB4; color: white; }
    .vet-badge { background-color: #4ECDC4; color: white; }
    .admin-badge { background-color: #FF6B6B; color: white; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #96CEB4 0%, #4ECDC4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .login-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem auto;
        max-width: 500px;
    }
</style>
""", unsafe_allow_html=True)

class AgroStockAuth:
    def __init__(self):
        # Pre-defined users (no database)
        self.users = {
            'admin': {
                'password_hash': self.hash_password('admin123'),
                'role': 'admin',
                'email': 'admin@agrostock.com',
                'farm_name': 'AgroStock HQ'
            },
            'farmer': {
                'password_hash': self.hash_password('farmer123'),
                'role': 'farmer', 
                'email': 'farmer@greenfarm.com',
                'farm_name': 'Green Valley Farm'
            },
            'vet': {
                'password_hash': self.hash_password('vet123'),
                'role': 'veterinarian',
                'email': 'vet@animalcare.com',
                'farm_name': 'Animal Care Clinic'
            }
        }
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login_user(self, username, password):
        if username in self.users and self.users[username]['password_hash'] == self.hash_password(password):
            user_data = self.users[username]
            return True, username, user_data['role'], user_data['farm_name']
        return False, None, None, None

def load_data():
    """Load all CSV datasets"""
    try:
        milk_yield = pd.read_csv('milk_yield.csv')
        cattle_health = pd.read_csv('cattle_health.csv')
        vaccination = pd.read_csv('vaccination_breeding.csv')
        feed_optimization = pd.read_csv('feed_optimization.csv')
        financial = pd.read_csv('financial_marketplace.csv')
        return milk_yield, cattle_health, vaccination, feed_optimization, financial
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None

def show_dashboard(milk_yield, cattle_health, vaccination, feed_optimization, financial, user_role, farm_name):
    """Main dashboard after login"""
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown('<h1 class="main-header">🐄 AgroStock Analytics</h1>', unsafe_allow_html=True)
    with col2:
        role_badge = f'<span class="role-badge {user_role}-badge">{user_role.upper()}</span>'
        st.markdown(f"**Welcome!** {role_badge}", unsafe_allow_html=True)
    with col3:
        st.write(f"**Farm:** {farm_name}")
    
    # Role-based tabs
    if user_role == 'admin':
        tabs = st.tabs(["📊 Overview", "🐄 Cattle Health", "💉 Vaccination", "🍽️ Feed", "💰 Financial", "⚙️ Admin"])
    elif user_role == 'veterinarian':
        tabs = st.tabs(["📊 Overview", "🐄 Cattle Health", "💉 Vaccination", "🍽️ Feed"])
    else:  # farmer
        tabs = st.tabs(["📊 Overview", "🐄 Cattle Health", "💉 Vaccination", "🍽️ Feed", "💰 Financial"])
    
    with tabs[0]:  # Overview
        st.subheader("🏠 Farm Overview Dashboard")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_cattle = len(cattle_health['Cattle_ID'].unique())
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Cattle</h3>
                <h2>{total_cattle}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            sick_cattle = len(cattle_health[cattle_health['Health_Status'] == 'Sick'])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Sick Cattle</h3>
                <h2>{sick_cattle}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_milk_yield = milk_yield['Milk_Yield (L)'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3>Avg Milk Yield</h3>
                <h2>{avg_milk_yield:.1f} L</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_revenue = financial['Total_Revenue (₹)'].sum() if financial is not None else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Revenue</h3>
                <h2>₹{total_revenue:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Health Status Distribution
            health_counts = cattle_health['Health_Status'].value_counts()
            fig1 = px.pie(values=health_counts.values, names=health_counts.index, 
                         title="Health Status Distribution", color=health_counts.index,
                         color_discrete_map={'Normal': '#96CEB4', 'Sick': '#FF6B6B'})
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Milk Yield Trends
            milk_yield['Date'] = pd.to_datetime(milk_yield['Date'])
            daily_yield = milk_yield.groupby('Date')['Milk_Yield (L)'].mean().reset_index()
            fig2 = px.line(daily_yield, x='Date', y='Milk_Yield (L)', title='Daily Milk Yield Trends')
            st.plotly_chart(fig2, use_container_width=True)
    
    with tabs[1]:  # Cattle Health
        st.subheader("🐄 Cattle Health Monitoring")
        
        # Health Alerts
        sick_cattle = cattle_health[cattle_health['Health_Status'] == 'Sick']
        if not sick_cattle.empty:
            st.markdown("""
            <div class="alert-card">
                <h4>🚨 Health Alerts - Sick Cattle Need Attention</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for _, cattle in sick_cattle.head(5).iterrows():
                st.write(f"**{cattle['Cattle_ID']}** - {cattle['Disease_Type']} - Temp: {cattle['Body_Temperature (°C)']}°C")
        
        # Health Data Table
        st.dataframe(cattle_health, use_container_width=True)
        
        # Health Analytics
        col1, col2 = st.columns(2)
        with col1:
            disease_counts = cattle_health['Disease_Type'].value_counts()
            fig = px.bar(disease_counts, x=disease_counts.index, y=disease_counts.values,
                        title="Disease Distribution", color=disease_counts.values)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            breed_health = cattle_health.groupby('Breed')['Health_Status'].value_counts().unstack().fillna(0)
            fig = px.bar(breed_health, title="Health Status by Breed", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:  # Vaccination
        st.subheader("💉 Vaccination & Breeding Management")
        
        if vaccination is not None:
            # Vaccination Alerts
            vaccination['Next_Vaccination_Due'] = pd.to_datetime(vaccination['Next_Vaccination_Due'])
            due_soon = vaccination[vaccination['Next_Vaccination_Due'] <= pd.to_datetime('2025-04-30')]
            
            if not due_soon.empty:
                st.markdown("""
                <div class="alert-card">
                    <h4>💉 Vaccination Due Soon</h4>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(due_soon[['Cattle_ID', 'Breed', 'Next_Vaccination_Due', 'Veterinarian']])
            
            # Breeding Status
            preg_count = len(vaccination[vaccination['Breeding_Status'] == 'Pregnant'])
            st.markdown(f"""
            <div class="success-card">
                <h4>🤰 Breeding: {preg_count} Pregnant Cattle</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(vaccination, use_container_width=True)
    
    with tabs[3]:  # Feed Optimization
        st.subheader("🍽️ Feed Optimization")
        
        if feed_optimization is not None:
            # Feed Recommendations
            st.markdown("### 📋 Feed Recommendations")
            
            col1, col2 = st.columns(2)
            with col1:
                high_energy_feeds = feed_optimization[feed_optimization['Energy (kcal/kg)'] > 2500]
                st.write("**High Energy Feeds (>2500 kcal/kg):**")
                st.dataframe(high_energy_feeds[['Feed_Name', 'Energy (kcal/kg)', 'Cost_per_kg (₹)']])
            
            with col2:
                cost_effective = feed_optimization[feed_optimization['Cost_per_kg (₹)'] < 25]
                st.write("**Cost Effective Feeds (<₹25/kg):**")
                st.dataframe(cost_effective[['Feed_Name', 'Cost_per_kg (₹)', 'Milk_Yield_Impact']])
            
            # Feed Analytics
            fig = px.scatter(feed_optimization, x='Cost_per_kg (₹)', y='Energy (kcal/kg)', 
                           color='Feed_Name', size='Protein (%)', hover_data=['Feed_Name'],
                           title="Feed Cost vs Energy Content")
            st.plotly_chart(fig, use_container_width=True)
    
    if user_role in ['farmer', 'admin'] and len(tabs) > 4:
        with tabs[4]:  # Financial
            st.subheader("💰 Financial Analytics")
            
            if financial is not None:
                # Financial Summary
                total_revenue = financial['Total_Revenue (₹)'].sum()
                total_profit = financial['Profit_or_Loss'].sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
                with col2:
                    st.metric("Total Profit", f"₹{total_profit:,.0f}")
                with col3:
                    st.metric("Transactions", len(financial))
                
                # Product Performance
                product_revenue = financial.groupby('Product_Name')['Total_Revenue (₹)'].sum()
                fig = px.pie(values=product_revenue.values, names=product_revenue.index,
                           title="Revenue by Product")
                st.plotly_chart(fig, use_container_width=True)
                
                # Transaction History
                st.dataframe(financial, use_container_width=True)
    
    if user_role == 'admin' and len(tabs) > 5:
        with tabs[5]:  # Admin Panel
            st.subheader("⚙️ Admin Panel")
            st.write("**System Administration**")
            
            # User Management
            st.write("### 👥 User Management")
            user_data = {
                'Username': ['admin', 'farmer', 'vet'],
                'Role': ['Admin', 'Farmer', 'Veterinarian'],
                'Email': ['admin@agrostock.com', 'farmer@greenfarm.com', 'vet@animalcare.com'],
                'Status': ['Active', 'Active', 'Active']
            }
            st.dataframe(pd.DataFrame(user_data))
            
            # System Stats
            st.write("### 📈 System Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Cattle Records", len(cattle_health))
                st.metric("Milk Yield Records", len(milk_yield))
            with col2:
                st.metric("Financial Transactions", len(financial) if financial is not None else 0)
                st.metric("Feed Options", len(feed_optimization) if feed_optimization is not None else 0)

def login_page(auth):
    """Login/Register page"""
    st.markdown('<h1 class="main-header">🐄 AgroStock</h1>', unsafe_allow_html=True)
    st.markdown("### Smart Cattle Analytics Platform")
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("🔐 Login to AgroStock")
        
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Login", use_container_width=True):
                if username and password:
                    success, username, role, farm_name = auth.login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.session_state.farm_name = farm_name
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with col2:
            if st.button("🆕 Demo Accounts", use_container_width=True):
                st.info("""
                **Demo Accounts:**
                - 👨‍💼 Admin: admin / admin123
                - 👨‍🌾 Farmer: farmer / farmer123  
                - 🩺 Veterinarian: vet / vet123
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick stats preview
        st.markdown("---")
        st.subheader("📊 Platform Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**250+** Cattle")
        with col2:
            st.write("**1,000+** Records")
        with col3:
            st.write("**₹500K+** Revenue")

def main():
    """Main application"""
    
    # Initialize authentication
    if 'auth' not in st.session_state:
        st.session_state.auth = AgroStockAuth()
    
    # Check login status
    if not st.session_state.get('logged_in', False):
        login_page(st.session_state.auth)
        return
    
    # Load data and show dashboard
    with st.spinner("🔄 Loading cattle data..."):
        milk_yield, cattle_health, vaccination, feed_optimization, financial = load_data()
    
    if cattle_health is not None:
        show_dashboard(milk_yield, cattle_health, vaccination, feed_optimization, financial,
                     st.session_state.role, st.session_state.farm_name)
    else:
        st.error("❌ Could not load data files. Please ensure all CSV files are in the same directory.")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        for key in ['logged_in', 'username', 'role', 'farm_name']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
