"""
Estilos CSS personalizados para PT_CALIDAD
"""
import streamlit as st

def load_css():
    """Cargar estilos CSS personalizados"""
    
    st.markdown("""
    <style>
         /* Estilos generales */
     .main-header {
         font-size: 2.5rem;
         font-weight: bold;
         color: #1f2937;
         text-align: center;
         margin-bottom: 0.5rem;
     }
     
     .sub-header {
         font-size: 1.5rem;
         font-weight: 600;
         color: #1f2937;
         margin-bottom: 1rem;
     }
    
    .card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
         .metric-card {
         background: linear-gradient(135deg, #1f2937 0%, #1f2937 100%);
         color: white;
         border-radius: 10px;
         padding: 1.5rem;
         text-align: center;
         margin: 0.5rem;
     }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Estilos para tablas */
    .dataframe {
        font-size: 0.9rem;
    }
    
         .dataframe th {
         background-color: #dbeafe;
         font-weight: 600;
         color: #1f2937;
     }
    
         /* Estilos para botones */
     .stButton > button {
         background-color: #1f2937;
         color: white;
         border: none;
         border-radius: 5px;
         padding: 0.5rem 1rem;
         font-weight: 500;
     }
     
     .stButton > button:hover {
         background-color: #1f2937;
     }
    
         /* Estilos para sidebar */
     .css-1d391kg {
         background-color: #f0f4ff;
     }
    
    /* Estilos para gráficos */
    .plotly-graph-div {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Estilos para alertas */
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    /* Estilos para formularios */
    .stTextInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 1px solid #ced4da;
    }
    
    /* Estilos para archivos */
    .stFileUploader > div > div > div {
        border-radius: 5px;
        border: 2px dashed #ced4da;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .sub-header {
            font-size: 1.2rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
    
    /* Estilos para tarjetas de evaluación */
    .evaluation-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .evaluation-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        border-color: #1f2937;
    }
    
         .evaluation-card::before {
         content: '';
         position: absolute;
         top: 0;
         left: 0;
         right: 0;
         height: 4px;
         background: linear-gradient(90deg, #1f2937, #1f2937);
     }
    
    .card-header {
        margin-bottom: 20px;
    }
    
    .card-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .card-subtitle {
        color: #666;
        font-size: 12px;
    }
    
    .card-content {
        margin-bottom: 20px;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 20px;
    }
    
         .info-section, .metrics-section {
         background: #f8f9fa;
         padding: 16px;
         border-radius: 12px;
         border-left: 4px solid #1f2937;
     }
    
    .info-grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        font-size: 13px;
        line-height: 1.4;
    }
    
    .metrics-grid {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    
    .metric-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .metric-label {
        font-weight: 600;
        color: #333;
        font-size: 12px;
    }
    
         .metric-value {
         font-weight: bold;
         color: #1f2937;
         font-size: 14px;
     }

    .card-actions {
        display: flex;
        justify-content: flex-end;
    }
    
         .detail-btn {
         background: linear-gradient(135deg, #1f2937, #1f2937);
         color: white;
         border: none;
         padding: 10px 20px;
         border-radius: 8px;
         font-size: 14px;
         font-weight: 600;
         cursor: pointer;
         transition: all 0.3s ease;
         box-shadow: 0 2px 8px rgba(30, 58, 138, 0.3);
     }
     
     .detail-btn:hover {
         transform: translateY(-2px);
         box-shadow: 0 4px 16px rgba(30, 58, 138, 0.4);
         background: linear-gradient(135deg, #1f2937, #1f2937);
     }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-excellent {
        background-color: #28a745;
        color: white;
    }
    
    .status-good {
        background-color: #17a2b8;
        color: white;
    }
    
    .status-regular {
        background-color: #ffc107;
        color: #212529;
    }
    
    .status-bad {
        background-color: #dc3545;
        color: white;
    }
    
    .status-success {
        background-color: #28a745;
        color: white;
    }
    
    .status-info {
        background-color: #17a2b8;
        color: white;
    }
    
    .status-warning {
        background-color: #ffc107;
        color: #212529;
    }
    
    .status-error {
        background-color: #dc3545;
        color: white;
    }
    
         .quality-metrics {
         background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
         border-radius: 8px;
         padding: 15px;
         border-left: 4px solid #1f2937;
     }
    
    .product-info {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #6c757d;
    }
    
    .container-header {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        border-left: 4px solid #007bff;
    }
    /* Estilos para tarjeta única */
    .single-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .single-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        border-color: #1f2937;
        transform: translateY(-2px);
    }
    
    .card-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
    }
    
    .card-left {
        flex: 1;
        min-width: 200px;
    }
    
    .card-id {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    
    .box-icon {
        font-size: 18px;
        color: #8B4513;
    }
    
    .fcl-number {
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }
    
    .card-dates {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .date-item {
        font-size: 12px;
        color: #666;
    }
    
    .card-middle {
        flex: 2;
        min-width: 300px;
    }
    
    .product-info {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    
    .info-item {
        font-size: 13px;
        color: #333;
        line-height: 1.4;
    }
    
    .card-right {
        flex: 1;
        min-width: 150px;
        text-align: right;
    }
    
    .quality-metrics {
        margin-bottom: 12px;
    }
    
    .metric-item {
        font-size: 13px;
        color: #333;
        margin-bottom: 4px;
    }
    
         .detail-button {
         background: linear-gradient(135deg, #1f2937, #1f2937);
         color: white;
         border: none;
         padding: 8px 16px;
         border-radius: 6px;
         font-size: 12px;
         font-weight: 600;
         cursor: pointer;
         transition: all 0.3s ease;
     }
     
     .detail-button:hover {
         transform: translateY(-1px);
         box-shadow: 0 2px 8px rgba(30, 58, 138, 0.3);
         background: linear-gradient(135deg, #1f2937, #1f2937);
     }
    
        
     .clickable-card {
         background: var(--background-color, white);
         border: 1px solid var(--border-color, #e0e0e0);
         border-radius: 8px;
         padding: 12px;
         margin-bottom: 8px;
         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
         transition: all 0.3s ease;
         height: 100%;
         display: flex;
         flex-direction: column;
         justify-content: center;
         cursor: pointer;
         color: var(--text-color, #333);
     }
     
     .clickable-card:hover {
         box-shadow: 0 6px 16px rgba(0,0,0,0.15);
         border-color: #1f2937;
         transform: translateY(-2px);
         background: var(--hover-background, linear-gradient(135deg, #f8fff8 0%, #ffffff 100%));
     }
     
    
     :root {
         --background-color: white;
         --border-color: #e0e0e0;
         --text-color: #333;
         --hover-background: linear-gradient(135deg, #f8fff8 0%, #ffffff 100%);
     }
     
     
     [data-testid="stAppViewContainer"] [data-testid="stDecoration"] {
         --background-color: #262730;
         --border-color: #464646;
         --text-color: #fafafa;
         --hover-background: linear-gradient(135deg, #2a2a2a 0%, #262730 100%);
     }
     
     
     .stApp[data-testid="stAppViewContainer"] {
         --background-color: #262730;
         --border-color: #464646;
         --text-color: #fafafa;
         --hover-background: linear-gradient(135deg, #2a2a2a 0%, #262730 100%);
     }
     
    
     @media (prefers-color-scheme: dark) {
         .clickable-card {
             background: #262730;
             border: 1px solid #464646;
             color: #fafafa;
         }
         
         .clickable-card:hover {
             background: linear-gradient(135deg, #2a2a2a 0%, #262730 100%);
             border-color: #1f2937;
         }
         
         .clickable-card h3 {
             color: #fafafa !important;
         }
         
         .clickable-card p {
             color: #cccccc !important;
         }
     }
     
     
     [data-testid="stAppViewContainer"] {
         --background-color: #262730;
         --border-color: #464646;
         --text-color: #fafafa;
         --hover-background: linear-gradient(135deg, #2a2a2a 0%, #262730 100%);
     }
     
     
     .stApp[data-testid="stAppViewContainer"] .clickable-card {
         background: #262730 !important;
         border: 1px solid #464646 !important;
         color: #fafafa !important;
     }
     
     .stApp[data-testid="stAppViewContainer"] .clickable-card:hover {
         background: linear-gradient(135deg, #2a2a2a 0%, #262730 100%) !important;
         border-color: #1f2937 !important;
     }
     
     .stApp[data-testid="stAppViewContainer"] .clickable-card h3 {
         color: #fafafa !important;
     }
     
     .stApp[data-testid="stAppViewContainer"] .clickable-card p {
         color: #cccccc !important;
     }
     
     
     .stApp[data-testid="stAppViewContainer"]:not([data-testid="stDecoration"]) .clickable-card {
         background: white !important;
         border: 1px solid #e0e0e0 !important;
         color: #333 !important;
     }
     
     .stApp[data-testid="stAppViewContainer"]:not([data-testid="stDecoration"]) .clickable-card:hover {
         background: linear-gradient(135deg, #f8fff8 0%, #ffffff 100%) !important;
         border-color: #1f2937 !important;
     }
     
     .stApp[data-testid="stAppViewContainer"]:not([data-testid="stDecoration"]) .clickable-card h3 {
         color: #333 !important;
     }
     
     .stApp[data-testid="stAppViewContainer"]:not([data-testid="stDecoration"]) .clickable-card p {
         color: #666 !important;
     }
    
    .clickable-card:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    
    .simple-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
         .simple-card:hover {
         box-shadow: 0 4px 8px rgba(0,0,0,0.1);
         border-color: #1f2937;
     }
    
    .card-left-section {
        text-align: center;
    }
    
    .card-left-section h3 {
        color: #333;
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: bold;
    }
    
    .card-middle-section {
        padding: 4px 0;
    }
    
    .card-middle-section p {
        margin: 3px 0;
        font-size: 12px;
        line-height: 1.3;
        color: #333;
    }
    
    .card-main-info h4 {
        color: #333;
        margin: 0 0 5px 0;
        font-size: 16px;
    }
    
    .card-product-info p, .card-metrics p {
        margin: 3px 0;
        font-size: 12px;
        line-height: 1.3;
    }
    
    .card-status {
        text-align: center;
    }
    
         .modal-btn {
         background: linear-gradient(135deg, #1f2937, #1f2937);
         color: white;
         border: none;
         padding: 6px 12px;
         border-radius: 6px;
         font-size: 12px;
         font-weight: 600;
         cursor: pointer;
         transition: all 0.3s ease;
         margin-top: 8px;
     }
     
     .modal-btn:hover {
         transform: translateY(-1px);
         box-shadow: 0 2px 8px rgba(30, 58, 138, 0.3);
     }
    
    /* Estilos para modal */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .modal-content {
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 800px;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
         .modal-header {
         background: linear-gradient(135deg, #1f2937, #1f2937);
         color: white;
         padding: 20px;
         border-radius: 12px 12px 0 0;
         display: flex;
         justify-content: space-between;
         align-items: center;
     }
    
    .modal-header h2 {
        margin: 0;
        font-size: 20px;
    }
    
    .modal-close {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.3s ease;
    }
    
    .modal-close:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .modal-body {
        padding: 20px;
    }
    
    .modal-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
    }
    
         .modal-section {
         background: #f8f9fa;
         padding: 15px;
         border-radius: 8px;
         border-left: 4px solid #1f2937;
     }
    
    .modal-section h4 {
        margin: 0 0 10px 0;
        color: #333;
        font-size: 16px;
    }
    
    .info-list div {
        margin: 5px 0;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .modal-actions {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .action-btn {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .export-btn {
        background: #007bff;
        color: white;
    }
    
    .email-btn {
        background: #28a745;
        color: white;
    }
    
    .reevaluate-btn {
        background: #ffc107;
        color: #212529;
    }
    
    .close-btn {
        background: #dc3545;
        color: white;
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"]{
        padding: 1px;
    }
    
    [data-testid="stHeader"]{
        height: 2.5rem;
    }
    
         div[data-baseweb="select"] span {
         font-size: 11px !important;
     }
     
     
     
     
     
     .streamlit-dark .clickable-card {
         background: #262730 !important;
         border: 1px solid #464646 !important;
         color: #fafafa !important;
     }
     
     .streamlit-dark .clickable-card:hover {
         background: linear-gradient(135deg, #2a2a2a 0%, #262730 100%) !important;
         border-color: #1f2937 !important;
     }
     
     .streamlit-dark .clickable-card h3 {
         color: #fafafa !important;
     }
     
     .streamlit-dark .clickable-card p {
         color: #cccccc !important;
     }
     
     .streamlit-light .clickable-card {
         background: white !important;
         border: 1px solid #e0e0e0 !important;
         color: #333 !important;
     }
     
     .streamlit-light .clickable-card:hover {
         background: linear-gradient(135deg, #f8fff8 0%, #ffffff 100%) !important;
         border-color: #1f2937 !important;
     }
     
     .streamlit-light .clickable-card h3 {
         color: #333 !important;
     }
     
     .streamlit-light .clickable-card p {
         color: #666 !important;
     }
    </style>
    """, unsafe_allow_html=True)
