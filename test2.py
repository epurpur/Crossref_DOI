import requests
import pandas as pd
import os
import time
from requests.exceptions import RequestException

# Load the dataset
df = pd.read_excel("/Users/ep9k/Desktop/Zhao_heng_Results_v2.xlsx")

# Replace with your actual email address registered with Unpaywall
EMAIL = "ep9k@virginia.edu"

# Directory to save PDFs
output_dir = "downloaded_articles"
os.makedirs(output_dir, exist_ok=True)

# Function to get PDF URL with retry logic
def get_pdf_url(doi, retries=3, backoff_factor=5):
    """Get the PDF URL using Unpaywall API with retry logic."""
    url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
    for attempt in range(retries):
        try:
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                data = response.json()
                if data.get('best_oa_location') and data['best_oa_location'].get('url_for_pdf'):
                    return data['best_oa_location']['url_for_pdf']
            elif response.status_code == 404:
                print(f"DOI not found: {doi}")
                return None
            else:
                print(f"Unexpected status code {response.status_code} for DOI {doi}")
        except RequestException as e:
            print(f"Error on attempt {attempt + 1} for DOI {doi}: {e}")
        # Exponential backoff
        time.sleep(backoff_factor * (attempt + 1))
    return None

# Function to download PDF with retry logic
def download_pdf(doi, retries=3):
    """Download the PDF if available."""
    pdf_url = get_pdf_url(doi, retries=retries)
    if pdf_url:
        for attempt in range(retries):
            try:
                response = requests.get(pdf_url, verify=False)
                if response.status_code == 200:
                    output_path = os.path.join(output_dir, f"{doi.replace('/', '_')}.pdf")
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {output_path}")
                    return True
            except RequestException as e:
                print(f"Download error on attempt {attempt + 1} for DOI {doi}: {e}")
            # Exponential backoff for retries
            time.sleep(2 ** (attempt + 1))
    return False

# Add '.pdf downloaded' column
download_status = []
for index, row in df.iterrows():
    if row['No Author Affiliation'] == 1:
        doi = row['DOI']
        if download_pdf(doi):
            download_status.append('yes')
        else:
            download_status.append('no')
    else:
        download_status.append('no')

df['.pdf downloaded'] = download_status

# Export the updated dataframe to an Excel file
output_path = "/Users/ep9k/Desktop/Zhao_Heng_Results_v3.xlsx"
df.to_excel(output_path, index=False)

print(f"Results saved to {output_path}")



