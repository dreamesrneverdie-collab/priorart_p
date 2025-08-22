"""
Patent Search Assistant Web Interface
"""

import streamlit as st
import json
from src.core.extractor import CoreConceptExtractor
from typing import Dict, List

def display_concept_matrix(concept_matrix: Dict):
    """Display concept matrix in a nice format"""
    st.subheader("📊 Concept Matrix", divider="rainbow")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("Problem/Purpose", icon="🎯")
        st.write(concept_matrix["problem_purpose"])
        
    with col2:
        st.info("Object/System", icon="⚙️")
        st.write(concept_matrix["object_system"])
        
    with col3:
        st.info("Environment/Field", icon="🌍")
        st.write(concept_matrix["environment_field"])

def display_seed_keywords(seed_keywords: Dict[str, List[str]]):
    """Display seed keywords in a nice format"""
    st.subheader("🔑 Generated Keywords", divider="rainbow")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("Problem/Purpose Keywords", icon="🎯")
        for kw in seed_keywords["problem_purpose"]:
            st.write(f"• {kw}")
            
    with col2:
        st.info("Object/System Keywords", icon="⚙️")
        for kw in seed_keywords["object_system"]:
            st.write(f"• {kw}")
            
    with col3:
        st.info("Environment/Field Keywords", icon="🌍")
        for kw in seed_keywords["environment_field"]:
            st.write(f"• {kw}")

def init_session_state():
    """Initialize session state variables"""
    if "extractor" not in st.session_state:
        st.session_state.extractor = CoreConceptExtractor()
    if "current_state" not in st.session_state:
        st.session_state.current_state = None
    if "concept_matrix" not in st.session_state:
        st.session_state.concept_matrix = None
    if "seed_keywords" not in st.session_state:
        st.session_state.seed_keywords = None
    if "keywords_approved" not in st.session_state:
        st.session_state.keywords_approved = False
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "edited_keywords" not in st.session_state:
        st.session_state.edited_keywords = None

def main():
    st.set_page_config(
        page_title="Patent Search Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("🔍 Patent Search Assistant")
    st.markdown("---")

    # Input section
    with st.expander("📝 Enter Patent Idea", expanded=True):
        input_text = st.text_area(
            "Describe your patent idea",
            placeholder="Enter your patent idea description here...",
            height=200
        )
        
        start_button = st.button("🚀 Start Analysis", use_container_width=True)

    # Process input and display initial results
    if start_button and input_text:
        with st.spinner("🔄 Analyzing your patent idea..."):
            results = st.session_state.extractor.extract_keywords(input_text)
            st.session_state.current_state = results
            st.session_state.concept_matrix = results.get("concept_matrix")
            st.session_state.seed_keywords = results.get("seed_keywords")
            
        st.success("✅ Initial analysis complete!")

    # Display results and get user feedback
    if st.session_state.concept_matrix and st.session_state.seed_keywords:
        display_concept_matrix(st.session_state.concept_matrix.dict())
        display_seed_keywords(st.session_state.seed_keywords.dict())
        
        st.markdown("---")
        st.subheader("🔄 Feedback & Actions", divider="rainbow")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve Keywords", use_container_width=True):
                st.session_state.keywords_approved = True
                st.session_state.feedback = {"action": "approve"}
                st.success("Keywords approved! Processing will continue...")
                
        with col2:
            if st.button("❌ Reject & Regenerate", use_container_width=True):
                st.text_area("Feedback for regeneration", key="reject_feedback")
                if st.button("Submit Feedback"):
                    st.session_state.feedback = {
                        "action": "reject",
                        "feedback": st.session_state.reject_feedback
                    }
                    st.info("Feedback submitted, regenerating keywords...")
                
        with col3:
            if st.button("✏️ Edit Keywords", use_container_width=True):
                st.session_state.editing = True
                
                # Create input fields for each keyword category
                edited_keywords = {}
                
                st.info("Edit Keywords - Enter new keywords separated by commas")
                
                for field, keywords in st.session_state.seed_keywords.dict().items():
                    current_str = ", ".join(keywords)
                    new_input = st.text_area(
                        f"Edit {field.replace('_', ' ').title()}",
                        value=current_str,
                        key=f"edit_{field}"
                    )
                    edited_keywords[field] = [k.strip() for k in new_input.split(",") if k.strip()]
                
                if st.button("Save Edited Keywords"):
                    st.session_state.feedback = {
                        "action": "edit",
                        "edited_keywords": edited_keywords
                    }
                    st.success("Keywords updated!")

    # Display final results if processing is complete
    if st.session_state.keywords_approved and st.session_state.current_state.get("final_url"):
        st.markdown("---")
        st.subheader("🎯 Search Results", divider="rainbow")
        
        for result in st.session_state.current_state["final_url"]:
            with st.expander(f"Patent: {result['url']}", expanded=False):
                st.write(f"User Scenario Score: {result['user_scenario']:.2f}")
                st.write(f"User Problem Score: {result['user_problem']:.2f}")
                st.markdown(f"[View Patent]({result['url']})")

if __name__ == "__main__":
    main()
