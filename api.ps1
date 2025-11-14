curl.exe --cacert "C:/Users/12055/OneDrive/Desktop/25Fall/291A Agent/elasticsearch-9.2.0-windows-x86_64/elasticsearch-9.2.0/config/certs/http_ca.crt" ^
  -u elastic:"XQF5m_ITXGaf*JbcS1cE" ^
  -X POST "https://localhost:9200/_security/api_key" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"sports-kb-client\",\"role_descriptors\":{\"sports_kb_readwrite\":{\"cluster\":[\"monitor\"],\"index\":[{\"names\":[\"sports_kb\"],\"privileges\":[\"read\",\"write\",\"create_index\",\"view_index_metadata\"]}]}}}"



curl.exe -k -u elastic:"XQF5m_ITXGaf*JbcS1cE" -X POST "https://localhost:9200/_security/api_key" -H "Content-Type: application/json" --data-binary "@body.json"
