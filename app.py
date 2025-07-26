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

{
  "openapi": "3.1.0",
  "info": {
    "title": "Europe PMC Search Tool",
    "version": "1.0.0"
  },
  "servers": [
    { "url": "https://my-gpt-evidence-api.onrender.com" }
  ],
  "paths": {
    "/epmc/search": {
      "get": {
        "operationId": "searchEuropePMC",
        "description": "Search Europe PMC articles by keywords.",
        "parameters": [
          { "name": "query", "in": "query", "required": true, "schema": { "type": "string" } },
          { "name": "max", "in": "query", "required": false, "schema": { "type": "integer", "default": 5 } }
        ],
        "responses": {
          "200": {
            "description": "Recent articles",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "articles": {
                      "type": "array",
                      "items": {
                        "type": "object",
                        "properties": {
                          "title": { "type": "string" },
                          "authors": { "type": "string" },
                          "journal": { "type": "string" },
                          "year": { "type": "string" },
                          "pmid": { "type": "string" },
                          "pmcid": { "type": "string" },
                          "doi": { "type": "string" },
                          "url": { "type": "string" },
                          "abstract": { "type": "string" }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
