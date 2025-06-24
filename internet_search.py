import requests
from bs4 import BeautifulSoup
import logging
import urllib.parse
import time

logger = logging.getLogger(__name__)

def duckduckgo_search(query, max_results=3):
    """Search DuckDuckGo for recent information"""
    try:
        # Clean and encode the query
        clean_query = urllib.parse.quote_plus(query.strip())
        
        # DuckDuckGo Instant Answer API (limited but free)
        url = f"https://api.duckduckgo.com/?q={clean_query}&format=json&no_html=1&skip_disambig=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Get abstract if available
            if data.get('Abstract'):
                results.append(f"Summary: {data['Abstract']}")
            
            # Get related topics
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:max_results]:
                    if isinstance(topic, dict) and topic.get('Text'):
                        results.append(topic['Text'])
            
            # Get answer if available
            if data.get('Answer'):
                results.append(f"Answer: {data['Answer']}")
            
            logger.info(f"DuckDuckGo search returned {len(results)} results")
            return results[:max_results]
        
        else:
            logger.warning(f"DuckDuckGo search failed with status {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"Error in DuckDuckGo search: {e}")
        return []

def wikipedia_summary(query, sentences=3):
    """Get Wikipedia summary for a topic"""
    try:
        # Wikipedia API endpoint
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
        
        # Clean query for Wikipedia
        clean_query = query.strip().replace(' ', '_')
        
        headers = {
            'User-Agent': 'AVScript-Bot/1.0 (https://example.com/contact)'
        }
        
        response = requests.get(f"{url}{clean_query}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('extract'):
                # Limit to specified number of sentences
                extract = data['extract']
                sentences_list = extract.split('. ')
                limited_extract = '. '.join(sentences_list[:sentences])
                if not limited_extract.endswith('.'):
                    limited_extract += '.'
                
                logger.info(f"Wikipedia summary found for: {query}")
                return limited_extract
            else:
                logger.info(f"No Wikipedia summary found for: {query}")
                return ""
                
        elif response.status_code == 404:
            # Try search API if direct page not found
            return wikipedia_search_fallback(query)
        else:
            logger.warning(f"Wikipedia API failed with status {response.status_code}")
            return ""
            
    except Exception as e:
        logger.error(f"Error in Wikipedia search: {e}")
        return ""

def wikipedia_search_fallback(query):
    """Fallback Wikipedia search when direct page lookup fails"""
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': 1
        }
        
        headers = {
            'User-Agent': 'AVScript-Bot/1.0 (https://example.com/contact)'
        }
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('query', {}).get('search'):
                # Get the first search result
                first_result = data['query']['search'][0]
                page_title = first_result['title']
                
                # Now get the summary for this page
                return wikipedia_summary(page_title)
            
        return ""
        
    except Exception as e:
        logger.error(f"Error in Wikipedia search fallback: {e}")
        return ""

def google_search_fallback(query, max_results=3):
    """Fallback search method using web scraping (use carefully)"""
    try:
        # This is a basic implementation - consider using official APIs
        search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find search result snippets
            snippets = soup.find_all('span', class_='aCOpRe')
            
            for snippet in snippets[:max_results]:
                text = snippet.get_text().strip()
                if text and len(text) > 20:
                    results.append(text)
            
            logger.info(f"Google search returned {len(results)} results")
            return results
        
        return []
        
    except Exception as e:
        logger.error(f"Error in Google search fallback: {e}")
        return []

def search_news(query, max_results=2):
    """Search for recent news articles"""
    try:
        # Using a simple news API approach
        # You can replace this with NewsAPI, Bing News API, etc.
        
        search_query = f"{query} news recent"
        results = duckduckgo_search(search_query, max_results)
        
        if results:
            logger.info(f"Found {len(results)} news results")
            return [f"Recent news: {result}" for result in results]
        
        return []
        
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        return []

# Main search function that combines multiple sources
def comprehensive_search(query, max_results=5):
    """Perform comprehensive search using multiple sources"""
    all_results = []
    
    try:
        # DuckDuckGo search
        ddg_results = duckduckgo_search(query, 2)
        all_results.extend(ddg_results)
        
        # Wikipedia summary
        wiki_result = wikipedia_summary(query)
        if wiki_result:
            all_results.append(f"Wikipedia: {wiki_result}")
        
        # News search
        news_results = search_news(query, 1)
        all_results.extend(news_results)
        
        # Remove duplicates and limit results
        unique_results = []
        seen = set()
        
        for result in all_results:
            if result.lower() not in seen and len(result) > 20:
                unique_results.append(result)
                seen.add(result.lower())
                
                if len(unique_results) >= max_results:
                    break
        
        logger.info(f"Comprehensive search returned {len(unique_results)} unique results")
        return unique_results
        
    except Exception as e:
        logger.error(f"Error in comprehensive search: {e}")
        return []

if __name__ == "__main__":
    # Test the search functions
    test_query = "artificial intelligence"
    
    print("Testing DuckDuckGo search...")
    ddg_results = duckduckgo_search(test_query)
    for i, result in enumerate(ddg_results, 1):
        print(f"{i}. {result[:100]}...")
    
    print("\nTesting Wikipedia search...")
    wiki_result = wikipedia_summary(test_query)
    print(f"Wikipedia: {wiki_result[:200]}...")
    
    print("\nTesting comprehensive search...")
    comp_results = comprehensive_search(test_query)
    for i, result in enumerate(comp_results, 1):
        print(f"{i}. {result[:150]}...")
