st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');

body {
    background: radial-gradient(circle at 50% 10%, #1a0033 0%, #05050f 70%);
    font-family: 'Roboto Mono', monospace;
    overflow-x: hidden;
}

.big-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 5.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00ff9f, #00b8ff, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 40px #00ff9f, 0 0 80px #00b8ff, 0 0 120px #ff00ff;
    animation: neonpulse 2s ease-in-out infinite alternate;
    text-align: center;
    margin-bottom: 20px;
}

@keyframes neonpulse {
    from { text-shadow: 0 0 20px #00ff9f, 0 0 40px #00b8ff; }
    to { text-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff, 0 0 140px #ff00ff; }
}

.glass-box, .stMetric, .stDataFrame, .plotly-chart-container {
    background: rgba(15,15,45,0.85);
    backdrop-filter: blur(30px);
    border: 2px solid #00ff9f;
    border-radius: 16px;
    box-shadow: 0 0 60px rgba(0,255,159,0.5);
    transition: all 0.4s ease;
    text-align: center !important;
    overflow: hidden;
}

.glass-box:hover, .stMetric:hover, .stDataFrame:hover, .plotly-chart-container:hover {
    transform: perspective(1000px) rotateX(8deg) rotateY(8deg) scale(1.02);
    box-shadow: 0 0 100px rgba(0,255,159,0.9);
}

.stMetric label {
    color: #00ff9f !important;
    font-weight: bold;
    text-shadow: 0 0 10px #00ff9f;
    text-align: center !important;
}

.stMetric div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 2rem !important;
    text-align: center !important;
}

.stDataFrame {
    text-align: center !important;
}

.stDataFrame th, .stDataFrame td {
    text-align: center !important;
    color: #e0e0e0 !important;
}

.stButton button {
    background: transparent;
    border: 2px solid #00ff9f;
    color: #fff;
    box-shadow: 0 0 25px #00ff9f;
    transition: all 0.4s ease;
    font-weight: 700;
    text-align: center;
}

.stButton button:hover {
    background: rgba(0,255,159,0.15);
    box-shadow: 0 0 60px #00ff9f, 0 0 100px #00b8ff;
    transform: scale(1.05);
}

/* Kill username suggestions completely */
input[type="text"][autocomplete="off"],
input[type="text"][name="username"],
input[type="text"][id="username"] {
    -webkit-text-fill-color: #fff !important;
    background: rgba(0,0,0,0.7) !important;
    border: 1px solid #00ff9f !important;
    color: #fff !important;
    appearance: none !important;
    -moz-appearance: none !important;
    -webkit-appearance: none !important;
}

input:-internal-autofill-selected,
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 30px rgba(0,0,0,0.7) inset !important;
    background: rgba(0,0,0,0.7) !important;
    color: #fff !important;
}

/* Prevent text overflow in boxes */
.stMetric, .glass-box, .stDataFrame {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: normal;
    word-wrap: break-word;
}
</style>
""", unsafe_allow_html=True)
