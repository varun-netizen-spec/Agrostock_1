import streamlit as st
import requests
import base64
import json
from PIL import Image
import io
import time

st.set_page_config(
    page_title="AgrStock Cattle Health AI",
    page_icon="🐄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 1rem;
    }
    .healthy-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    .sick-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🐄 AgrStock Cattle Health Scanner</h1>', unsafe_allow_html=True)
st.markdown("### AI-Powered Cattle Disease Detection")

# Your EXACT API details from Roboflow
API_KEY = "t6Q3duhVtran9JV68OBa"  # This is visible in your screenshot
MODEL_ID = "cattle-smwai-1vl7w/2"
API_URL = "https://detect.roboflow.com"

# Main app layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Cattle Image")
    
    uploaded_file = st.file_uploader(
        "Choose an image of cattle", 
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear photo of cattle for health analysis"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Confidence settings
        confidence = st.slider("Detection Confidence", 0.1, 1.0, 0.5, 0.1)

with col2:
    st.subheader("🔍 Analysis Results")
    
    if uploaded_file and st.button("🚀 Analyze Cattle Health", type="primary", use_container_width=True):
        with st.spinner("AI is analyzing the cattle image..."):
            try:
                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # API request - USING THE EXACT ENDPOINT FROM YOUR ROBoFLOW
                response = requests.post(
                    f"{API_URL}/{MODEL_ID}",
                    params={
                        "api_key": API_KEY,
                        "confidence": confidence,
                        "overlap": 30,
                        "format": "json"
                    },
                    data=img_str,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30
                )
                
                st.write(f"🔧 API Status: {response.status_code}")
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Display results
                    if 'predictions' in results and len(results['predictions']) > 0:
                        st.success(f"✅ Found {len(results['predictions'])} cattle detection(s)")
                        
                        healthy_count = 0
                        issues_found = []
                        
                        for i, prediction in enumerate(results['predictions']):
                            condition = prediction['class']
                            confidence_score = prediction['confidence']
                            
                            if condition == "Healthy":
                                healthy_count += 1
                                st.markdown(f"""
                                <div class="healthy-box">
                                    <h4>🐄 Healthy Cattle #{i+1}</h4>
                                    <p>Confidence: {confidence_score:.1%}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                issues_found.append(condition)
                                st.markdown(f"""
                                <div class="sick-box">
                                    <h4>🚨 {condition}</h4>
                                    <p>Confidence: {confidence_score:.1%}</p>
                                    <p>Location: X={prediction['x']:.0f}, Y={prediction['y']:.0f}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Summary
                        st.markdown("---")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Total Detected", len(results['predictions']))
                        with col_b:
                            st.metric("Healthy", healthy_count)
                        with col_c:
                            st.metric("Issues Found", len(issues_found))
                        
                        if issues_found:
                            st.warning(f"**Alert:** Detected {len(set(issues_found))} different health conditions")
                            for issue in set(issues_found):
                                st.error(f"• {issue}")
                    
                    else:
                        st.info("🤔 No cattle detected in the image. Try a clearer photo.")
                        
                    # Raw results expander
                    with st.expander("📊 View Raw API Response"):
                        st.json(results)
                        
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    st.write("Response:", response.text)
                    st.info("💡 Try: 1) Check API key 2) Wait a minute 3) Try different image")
                    
            except Exception as e:
                st.error(f"💥 Error: {str(e)}")
                st.info("Please try again with a different image")

# Instructions
st.markdown("---")
st.subheader("📖 How It Works")
st.markdown("""
1. **Upload** a clear photo of cattle
2. **Click** "Analyze Cattle Health" 
3. **Get instant** AI analysis of health conditions
4. **Identify** issues like Ringworm, Lumky Skin, etc.

**Supported Conditions:** Healthy, Dermatophilosis, Lumky Skin, Pediculosis, Ringworm
""")

# Footer
st.markdown("---")
st.caption("AgrStock MVP | Powered by Roboflow Computer Vision")