function get_keyword_tool_data(keyword, keyword_query) {
  const url = "https://erank.com/keyword-tool";
  const data = {
    "processFunc": "etsyCall",
    "keyword": keyword,
    "member_id": 1178565,
    "country": "USA",
    "sort_on": "score"
  };
  const headers = {
    "Referer": `https://erank.com/keyword-tool?keywords=${keyword_query}&country=USA`,
    "Origin": "https://erank.com"
  };
  const body = new URLSearchParams(data);
  return fetch(url, {
    "method": "POST",
    "headers": headers,
    "body": body
  }).then((response) => {
    if (!response.ok) {{
      throw new Error(`HTTP error! status: ${response.status}`);
    }}
    return response.text();
  });
}