"""
FAZENIUM — Biological Database Parsing Tools
Allows Gemma 4 and users to fetch data from PubMed, UniProt, PubChem, and PDB.
"""
import requests
import xml.etree.ElementTree as ET


def fetch_pubmed_abstracts(query: str, max_results: int = 3) -> list[dict]:
    """Search PubMed and fetch recent abstracts."""
    try:
        # Step 1: Search for IDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
        resp = requests.get(search_url, params=params, timeout=10)
        resp.raise_for_status()
        id_list = resp.json().get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return []

        # Step 2: Fetch details for IDs
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {"db": "pubmed", "id": ",".join(id_list), "retmode": "xml"}
        fetch_resp = requests.get(fetch_url, params=fetch_params, timeout=10)
        fetch_resp.raise_for_status()
        
        root = ET.fromstring(fetch_resp.content)
        articles = []
        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", default="No title")
            abstract = article.findtext(".//AbstractText", default="No abstract available")
            year = article.findtext(".//PubDate/Year", default="Unknown")
            articles.append({"title": title, "abstract": abstract, "year": year})
        
        return articles
    except Exception as e:
        return [{"error": f"PubMed API error: {str(e)}"}]


def fetch_uniprot_info(query: str) -> dict:
    """Fetch basic protein information from UniProt."""
    try:
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {"query": query, "size": 1, "format": "json"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        
        if not results:
            return {"error": "Protein not found in UniProt."}
            
        prot = results[0]
        name = prot.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown")
        gene = prot.get("genes", [{}])[0].get("geneName", {}).get("value", "Unknown")
        organism = prot.get("organism", {}).get("scientificName", "Unknown")
        function = "Unknown function."
        
        for comment in prot.get("comments", []):
            if comment.get("commentType") == "FUNCTION":
                function = comment.get("texts", [{}])[0].get("value", function)
                break
                
        return {
            "name": name,
            "gene": gene,
            "organism": organism,
            "function": function
        }
    except Exception as e:
        return {"error": f"UniProt API error: {str(e)}"}


def fetch_pubchem_info(compound_name: str) -> dict:
    """Fetch chemical properties from PubChem."""
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/property/MolecularFormula,MolecularWeight,XLogP,IsomericSMILES/JSON"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        props = resp.json().get("PropertyTable", {}).get("Properties", [{}])[0]
        if not props:
            return {"error": "Compound not found."}
            
        return {
            "formula": props.get("MolecularFormula"),
            "weight": props.get("MolecularWeight"),
            "logp": props.get("XLogP"),
            "smiles": props.get("IsomericSMILES")
        }
    except Exception as e:
        return {"error": f"PubChem API error: {str(e)}"}


def fetch_pdb_summary(pdb_id: str) -> dict:
    """Fetch structural summary from RCSB PDB."""
    try:
        url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.upper()}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        title = data.get("struct", {}).get("title", "Unknown title")
        method = data.get("exptl", [{}])[0].get("method", "Unknown method")
        resolution = data.get("rcsb_entry_info", {}).get("resolution_combined", [None])[0]
        
        return {
            "pdb_id": pdb_id.upper(),
            "title": title,
            "method": method,
            "resolution": f"{resolution} Å" if resolution else "N/A"
        }
    except Exception as e:
        return {"error": f"PDB API error: {str(e)}"}
