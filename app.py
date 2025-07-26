from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

app = Flask(__name__)

def search_pubmed_api(query, max_results=10):
    """실제 PubMed API를 사용하여 논문 검색 (의료진을 위한 충분한 논문 제공)"""
    try:
        # 1단계: PubMed에서 논문 ID 검색
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml',
            'sort': 'pub_date',
            'reldate': 1095  # 최근 3년 이내 (의료 정보는 최신성이 중요)
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        search_root = ET.fromstring(search_response.content)
        
        # PMID 목록 추출
        pmids = [id_elem.text for id_elem in search_root.findall('.//Id')]
        
        if not pmids:
            return []
        
        # 2단계: 논문 상세 정보 가져오기 (배치로 처리하여 빠르게)
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=20)
        fetch_root = ET.fromstring(fetch_response.content)
        
        articles = []
        for article in fetch_root.findall('.//PubmedArticle'):
            try:
                # 제목 추출
                title_elem = article.find('.//ArticleTitle')
                title = title_elem.text if title_elem is not None else "No title available"
                
                # 저자 추출
                authors = []
                for author in article.findall('.//Author'):
                    lastname = author.find('LastName')
                    forename = author.find('ForeName')
                    if lastname is not None:
                        author_name = lastname.text
                        if forename is not None:
                            author_name = f"{forename.text} {author_name}"
                        authors.append(author_name)
                
                authors_str = ", ".join(authors[:3])  # 처음 3명만
                if len(authors) > 3:
                    authors_str += " et al."
                
                # 저널명 추출
                journal_elem = article.find('.//Journal/Title')
                journal = journal_elem.text if journal_elem is not None else "Unknown journal"
                
                # 연도 추출
                year_elem = article.find('.//PubDate/Year')
                year = year_elem.text if year_elem is not None else "Unknown year"
                
                # PMID 추출
                pmid_elem = article.find('.//PMID')
                pmid = pmid_elem.text if pmid_elem is not None else ""
                
                # DOI 추출
                doi = ""
                for article_id in article.findall('.//ArticleId'):
                    if article_id.get('IdType') == 'doi':
                        doi = article_id.text
                        break
                
                # 초록 추출 (의료진을 위해 충분한 정보 제공)
                abstract_elem = article.find('.//Abstract/AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
                
                # URL 생성 (실제 존재하는 PMID 기반)
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                
                articles.append({
                    "title": title,
                    "authors": authors_str,
                    "journal": journal,
                    "year": year,
                    "pmid": pmid,
                    "doi": doi,
                    "url": url,
                    "abstract": abstract[:800] + "..." if len(abstract) > 800 else abstract
                })
                
            except Exception as e:
                print(f"Error parsing article: {e}")
                continue
                
        return articles
        
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def search_europe_pmc_api(query, max_results=10):
    """실제 Europe PMC API를 사용하여 논문 검색 (의료진을 위한 충분한 논문 제공)"""
    try:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            'query': query,
            'format': 'json',
            'pageSize': max_results,
            'sort': 'P_PDATE_D',  # 최신순 정렬
            'synonym': 'true'
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        articles = []
        for result in data.get('resultList', {}).get('result', []):
            try:
                # URL 생성 (실제 존재하는 ID 기반)
                url = ""
                if result.get('pmid'):
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{result['pmid']}/"
                elif result.get('pmcid'):
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{result['pmcid']}/"
                elif result.get('doi'):
                    url = f"https://doi.org/{result['doi']}"
                
                articles.append({
                    "title": result.get('title', 'No title available'),
                    "authors": result.get('authorString', 'Unknown authors'),
                    "journal": result.get('journalTitle', 'Unknown journal'),
                    "year": str(result.get('pubYear', 'Unknown year')),
                    "pmid": result.get('pmid', ''),
                    "pmcid": result.get('pmcid', ''),
                    "doi": result.get('doi', ''),
                    "url": url,
                    "abstract": result.get('abstractText', 'No abstract available')
                })
            except Exception as e:
                print(f"Error parsing Europe PMC result: {e}")
                continue
                
        return articles
        
    except Exception as e:
        print(f"Error searching Europe PMC: {e}")
        return []

@app.route("/pubmed/search")
def search_pubmed():
    query = request.args.get("query")
    max_results = min(int(request.args.get("max", 10)), 20)  # 기본 10개, 최대 20개
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    articles = search_pubmed_api(query, max_results)
    return jsonify({"articles": articles})

@app.route("/epmc/search")
def search_europe_pmc():
    query = request.args.get("query")
    max_results = min(int(request.args.get("max", 10)), 20)  # 기본 10개, 최대 20개
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    articles = search_europe_pmc_api(query, max_results)
    return jsonify({"articles": articles})

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)