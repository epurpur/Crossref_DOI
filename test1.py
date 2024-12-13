import requests
import pandas as pd
import os
import time

# Replace with your actual email address registered with Unpaywall
EMAIL = "ep9k@virginia.edu"

# Load the Excel file
df = pd.read_excel("/Users/ep9k/Downloads/SuperSecretHolidays2024.xlsx")

# Function to get DOI, authors count, and affiliations
def get_doi_authors_count_and_affiliations(title, index, total):
    url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 1}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Processing {index + 1}/{total}: '{title}'")
        
        if data["message"]["items"]:
            item = data["message"]["items"][0]
            doi = item.get("DOI", "DOI not found")
            
            authors = item.get("author", [])
            author_names = [f"{author.get('family', '')} {author.get('given', '')}" for author in authors]
            author_count = len(authors)
            author_names_str = ", ".join(author_names) if author_names else "Authors not found"
            
            affiliations = []
            for author in authors:
                if "affiliation" in author and author["affiliation"]:
                    affiliation_names = [aff["name"] for aff in author["affiliation"]]
                    affiliations.append("; ".join(affiliation_names))
                else:
                    affiliations.append("No affiliation provided")
            
            affiliations_str = "; ".join(affiliations)
            return doi, author_names_str, author_count, affiliations_str
        else:
            return "DOI not found", "Authors not found", 0, "No affiliation provided"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", f"Error: {e}", 0, f"Error: {e}"

# Update the dataframe with CrossRef data
total_titles = len(df)
progress_results = []

for idx, title in enumerate(df['Title']):
    result = get_doi_authors_count_and_affiliations(title, idx, total_titles)
    progress_results.append(result)

df[['DOI', 'Authors', 'Number of Authors', 'Author Affiliation']] = pd.DataFrame(progress_results)

# Add 'No Author Affiliation' column
df['No Author Affiliation'] = df['Author Affiliation'].apply(lambda x: 1 if "No affiliation provided" in x else 0)

# Directory to save PDFs
output_dir = "downloaded_articles"
os.makedirs(output_dir, exist_ok=True)

# Function to get PDF URL
def get_pdf_url(doi):
    time.sleep(2)
    url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('best_oa_location') and data['best_oa_location'].get('url_for_pdf'):
            return data['best_oa_location']['url_for_pdf']
    return None

# Function to download PDF
def download_pdf(doi):
    time.sleep(2)
    pdf_url = get_pdf_url(doi)
    if pdf_url:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            print(f'Downloaded .pdf for {doi}')
            output_path = os.path.join(output_dir, f"{doi.replace('/', '_')}.pdf")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
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
output_path = "/Users/ep9k/Desktop/Zhao_Heng_Results_v2.xlsx"
df.to_excel(output_path, index=False)

print(f"Results saved to {output_path}")
