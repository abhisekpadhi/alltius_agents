import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_support_urls():
    base_urls = [
        'https://www.angelone.in/support/add-and-withdraw-funds',
        'https://www.angelone.in/support/angel-one-recommendations', 
        'https://www.angelone.in/support/charges-and-cashbacks',
        'https://www.angelone.in/support/charts',
        'https://www.angelone.in/support/complaince',
        'https://www.angelone.in/support/fixed-deposits',
        'https://www.angelone.in/support/ipo-ofs',
        'https://www.angelone.in/support/loans',
        'https://www.angelone.in/support/margin-pledging-and-margin-trading-facility',
        'https://www.angelone.in/support/mutual-funds',
        'https://www.angelone.in/support/portfolio-and-corporate-actions',
        'https://www.angelone.in/support/reports-and-statements',
        'https://www.angelone.in/support/your-account',
        'https://www.angelone.in/support/your-orders'
    ]

    all_urls = set()
    
    for base_url in base_urls:
        try:
            response = requests.get(base_url)
            if response.status_code != 200:
                print(f"Failed to retrieve {base_url}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find links in sidebar section
            sidebar_links = soup.select('div.sidebar-section > div.list-item > ul > li > a')
            
            for link in sidebar_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    all_urls.add(full_url)

        except Exception as e:
            print(f"Error processing {base_url}: {str(e)}")

    return all_urls

# Extract and print the support URLs
support_urls = extract_support_urls()

print("\nAll unique URLs:")
for url in sorted(support_urls):
    print(url)
