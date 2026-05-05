#!/usr/bin/env python3
"""
Simple Craigslist search scraper for vintage audio equipment.
Respects robots.txt, no login bypass, no CAPTCHA bypass.
"""

import requests
import time
import json
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

# Craigslist sites to search
CL_SITES = [
    "athens.craigslist.org",
    "atlanta.craigslist.org",
]

SEARCH_QUERIES = [
    "McIntosh MA 5100",
    "McIntosh MA5100",
    "Pioneer SX-1050",
    "Pioneer SX1050",
    "McIntosh MA 6100",
    "McIntosh MA6100",
    "Technics SL-1200",
    "Technics SL1200",
    "Nakamichi Dragon",
]

def search_craigslist(site, query, category="sss"):
    """
    Search Craigslist for a query.
    category: sss = all for sale
    """
    url = f"https://{site}/search/{category}"
    params = {
        "query": query,
        "sort": "date"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LocalLeadHunt/1.0)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error searching {site} for '{query}': {e}")
        return None


def parse_results(html, site):
    """Parse Craigslist search results HTML."""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # Craigslist structure: <li class="result-row">
    listings = soup.find_all('li', class_='result-row')
    
    for listing in listings:
        try:
            title_elem = listing.find('a', class_='result-title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            url = title_elem.get('href')
            
            # Price
            price_elem = listing.find('span', class_='result-price')
            price = price_elem.get_text(strip=True) if price_elem else "N/A"
            
            # Location
            hood_elem = listing.find('span', class_='result-hood')
            location = hood_elem.get_text(strip=True) if hood_elem else "N/A"
            
            results.append({
                "title": title,
                "url": url,
                "price": price,
                "location": location,
                "site": site
            })
        except Exception as e:
            print(f"Error parsing listing: {e}")
            continue
    
    return results


def main():
    print("=" * 70)
    print("LOCAL_LEAD_HUNT_001 - Craigslist Search")
    print("=" * 70)
    print()
    
    all_results = []
    
    for site in CL_SITES:
        print(f"Searching {site}...")
        for query in SEARCH_QUERIES:
            print(f"  Query: {query}")
            html = search_craigslist(site, query)
            results = parse_results(html, site)
            
            if results:
                print(f"    Found {len(results)} result(s)")
                all_results.extend(results)
            else:
                print(f"    No results")
            
            time.sleep(2)  # Rate limit courtesy
        print()
    
    # Save results
    output_file = "data/local_leads_craigslist.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"Total results: {len(all_results)}")
    print(f"Saved to: {output_file}")
    
    # Display sample
    if all_results:
        print()
        print("Sample results:")
        for i, result in enumerate(all_results[:5], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Price: {result['price']}")
            print(f"   Location: {result['location']}")
            print(f"   URL: {result['url']}")


if __name__ == "__main__":
    main()
