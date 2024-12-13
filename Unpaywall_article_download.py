import requests
import os

# Replace with your actual email address registered with Unpaywall
EMAIL = "ep9k@virginia.edu"

# List of DOIs
dois = [
    "10.5465/annals.2020.0230",
    '10.5465/amj.2017.1265',
    '10.5465/amr.2019.0441',
    '10.1177/00018392221078584',
    '10.1111/deci.12561',
    '10.1177/10596011221111505',
    '10.1177/00187267211070769',
    '10.1002/hrm.22102',
    '10.1037/apl0000994',
    '10.1016/j.jbusres.2021.09.061',
    '10.1016/j.jbusvent.2020.106031',
    '10.3368/jhr.0320-10762r1',
    '10.1057/s41267-021-00484-5',
    '10.1111/joms.12796',
    '10.1002/job.2608',
    '10.1177/01492063221081442'
]

# Directory to save PDFs
output_dir = "downloaded_articles"
os.makedirs(output_dir, exist_ok=True)

def get_pdf_url(doi):
    """Get the PDF URL using Unpaywall API."""
    url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('best_oa_location') and data['best_oa_location'].get('url_for_pdf'):
            return data['best_oa_location']['url_for_pdf']
    elif response.status_code == 404:
        print(f"DOI not found in Unpaywall: {doi}")
    else:
        print(f"Error fetching data for DOI {doi}: {response.status_code}")
    return None

def download_pdf(doi, output_dir):
    """Download PDF if available."""
    pdf_url = get_pdf_url(doi)
    if pdf_url:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            output_path = os.path.join(output_dir, f"{doi.replace('/', '_')}.pdf")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {output_path}")
        else:
            print(f"Failed to download PDF from {pdf_url} for DOI: {doi}")
    else:
        print(f"No open access PDF found for DOI: {doi}")

# Download PDFs for all DOIs
for doi in dois:
    download_pdf(doi, output_dir)


