from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/pubmed/search")
def search_pubmed():
    query = request.args.get("query")
    # 논문 검색 API 연동 코드는 나중에 추가
    return jsonify({"articles": [
        {
            "title": "Sample Title",
            "authors": "Smith J",
            "journal": "NEJM",
            "year": "2024",
            "pmid": "123456",
            "url": "https://pubmed.ncbi.nlm.nih.gov/123456/",
            "abstract": "Sample abstract."
        }
    ]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
