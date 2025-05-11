import streamlit as st
import requests
import wikipedia
from datetime import datetime, timedelta
import json

# Configure Wikipedia
wikipedia.set_lang("en")

# ======================
# API INTEGRATION FUNCTIONS
# ======================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_rxnav_info(drug_name):
    """RxNav API - Drug names and RxCUI identifiers"""
    try:
        url = f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={drug_name}"
        response = requests.get(url, timeout=10)
        data = response.json()
        concepts = data.get("drugGroup", {}).get("conceptGroup", [])
        return [f"{c['name']} (RxCUI: {c['rxcui']})" 
                for group in concepts if group.get("conceptProperties") 
                for c in group["conceptProperties"]]
    except Exception as e:
        return [f"RxNav Error: {str(e)}"]

@st.cache_data(ttl=3600)
def fetch_openfda_info(drug_name):
    """OpenFDA API - Labeling information"""
    try:
        url = "https://api.fda.gov/drug/label.json"
        params = {"search": f"openfda.generic_name:{drug_name.lower()}", "limit": 1}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if not data.get("results"):
            return {"error": "No FDA label data found"}
        
        result = data["results"][0]
        return {
            "uses": result.get("indications_and_usage", ["Not available"])[0],
            "warnings": result.get("warnings", ["Not available"])[0],
            "side_effects": result.get("adverse_reactions", ["Not available"])[0]
        }
    except Exception as e:
        return {"error": f"FDA API Error: {str(e)}"}

@st.cache_data(ttl=3600)
def fetch_drugcentral_info(drug_name):
    """DrugCentral - Pharmacological data"""
    try:
        search_url = f"https://drugcentral.org/api/v1/drugs?q={drug_name}"
        search_resp = requests.get(search_url, timeout=10)
        search_data = search_resp.json()
        
        if not search_data:
            return {"error": "Drug not found in DrugCentral"}
        
        drug_id = search_data[0]["struct_id"]
        detail_url = f"https://drugcentral.org/api/v1/drug/{drug_id}"
        detail_resp = requests.get(detail_url, timeout=10)
        detail_data = detail_resp.json()
        
        return {
            "moa": detail_data.get("mechanism_of_action", "Not available"),
            "targets": [t["target_name"] for t in detail_data.get("targets", [])[:3]],
            "indications": [i["indication"] for i in detail_data.get("indications", [])[:2]]
        }
    except Exception as e:
        return {"error": f"DrugCentral Error: {str(e)}"}

@st.cache_data(ttl=3600)
def fetch_wikipedia_summary(drug_name):
    """Wikipedia - General drug summary"""
    try:
        search_results = wikipedia.search(drug_name)
        if not search_results:
            return "No Wikipedia page found"
        return wikipedia.summary(search_results[0], sentences=3)
    except Exception as e:
        return f"Wikipedia Error: {str(e)}"

@st.cache_data(ttl=3600)
def fetch_dailymed_info(drug_name):
    """DailyMed - Structured product labels"""
    try:
        url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
        params = {"drug_name": drug_name, "pagesize": 2}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return [{
            "title": item.get("title", "No title"),
            "url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={item.get('setid')}"
        } for item in data.get("data", [])[:2]] or ["No DailyMed entries found"]
    except Exception as e:
        return [f"DailyMed Error: {str(e)}"]

@st.cache_data(ttl=3600)
def fetch_chembl_info(drug_name):
    """ChEMBL - Bioactivity data"""
    try:
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={drug_name}"
        response = requests.get(url, timeout=10)
        data = response.json()
        molecules = data.get("molecules", [])[:3]
        return [{
            "name": mol.get("pref_name", "Unnamed compound"),
            "chembl_id": mol.get("molecule_chembl_id"),
            "type": mol.get("molecule_type")
        } for mol in molecules] or [{"error": "No ChEMBL records found"}]
    except Exception as e:
        return [{"error": f"ChEMBL Error: {str(e)}"}]

# ======================
# PLACEHOLDER APIS (NO AUTH)
# ======================

def fetch_who_atc_info(drug_name):
    return {
        "note": "Search WHO ATC/DDD Index:",
        "link": f"https://www.whocc.no/atc_ddd_index/?name={drug_name}&search=Search"
    }

def fetch_goodrx_info(drug_name):
    return {
        "note": "Visit GoodRx for pricing:",
        "link": f"https://www.goodrx.com/{drug_name.replace(' ', '-')}"
    }

def fetch_drugscom_info(drug_name):
    return {
        "note": "Search Drugs.com:",
        "link": f"https://www.drugs.com/search.php?searchterm={drug_name}"
    }

def fetch_chemspider_info(drug_name):
    return {
        "note": "Search ChemSpider:",
        "link": f"https://www.chemspider.com/Search.aspx?q={drug_name}"
    }

# ======================
# STREAMLIT UI
# ======================

st.set_page_config(
    page_title="Pharma API Explorer",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Comprehensive Drug Information Tool")
st.markdown("Search across 10+ pharmaceutical databases")

drug_query = st.text_input(
    "Enter drug name (e.g., Ibuprofen, Metformin):",
    key="drug_search"
)

if drug_query:
    with st.spinner("Gathering drug information from multiple sources..."):
        col1, col2 = st.columns(2)
        
        with col1:
            # Wikipedia Summary
            with st.expander("📚 Wikipedia Summary", expanded=True):
                st.write(fetch_wikipedia_summary(drug_query))
            
            # RxNav Identifiers
            with st.expander("🏷️ RxNav/RxCUI Identifiers"):
                st.write(fetch_rxnav_info(drug_query))
            
            # FDA Information
            with st.expander("⚠️ FDA Label Information"):
                fda_data = fetch_openfda_info(drug_query)
                if isinstance(fda_data, dict):
                    if "error" in fda_data:
                        st.error(fda_data["error"])
                    else:
                        st.subheader("Uses")
                        st.write(fda_data.get("uses"))
                        st.subheader("Warnings")
                        st.write(fda_data.get("warnings"))
            
            # DailyMed
            with st.expander("📄 DailyMed SPL Information"):
                dailymed_data = fetch_dailymed_info(drug_query)
                if isinstance(dailymed_data, list):
                    for item in dailymed_data:
                        if isinstance(item, dict):
                            st.markdown(f"**{item.get('title')}**")
                            st.markdown(f"[View Label]({item.get('url')})")
                        else:
                            st.write(item)
        
        with col2:
            # DrugCentral
            with st.expander("🧪 DrugCentral Pharmacology"):
                dc_data = fetch_drugcentral_info(drug_query)
                if isinstance(dc_data, dict):
                    if "error" in dc_data:
                        st.error(dc_data["error"])
                    else:
                        st.subheader("Mechanism of Action")
                        st.write(dc_data.get("moa"))
                        if dc_data.get("targets"):
                            st.subheader("Top Targets")
                            st.write(", ".join(dc_data["targets"]))
            
            # ChEMBL
            with st.expander("🔬 ChEMBL Bioactivity Data"):
                chembl_data = fetch_chembl_info(drug_query)
                if isinstance(chembl_data, list):
                    for compound in chembl_data:
                        if isinstance(compound, dict):
                            st.markdown(f"**{compound.get('name')}**")
                            st.write(f"ChEMBL ID: {compound.get('chembl_id')}")
            
            # External Resources
            with st.expander("🌍 External Resources"):
                st.markdown("**WHO ATC/DDD Index**")
                who_data = fetch_who_atc_info(drug_query)
                st.markdown(f"[{who_data['note']}]({who_data['link']})")
                
                st.markdown("**GoodRx Pricing**")
                grx_data = fetch_goodrx_info(drug_query)
                st.markdown(f"[{grx_data['note']}]({grx_data['link']})")

    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data cached for 1 hour")
