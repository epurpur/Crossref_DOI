import requests
import pandas as pd

df = pd.read_excel("/Users/ep9k/Downloads/SuperSecretHolidays2024.xlsx")

def get_doi_authors_count_and_affiliations(title, index, total):
    url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 1}  # Search for the title and limit results to 1
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        
        # Progress update
        print(f"Processing {index + 1}/{total}: '{title}'")
        
        # Extract DOI, authors, affiliations if available
        if data["message"]["items"]:
            item = data["message"]["items"][0]
            doi = item.get("DOI", "DOI not found")
            
            authors = item.get("author", [])
            author_names = [f"{author.get('family', '')} {author.get('given', '')}" for author in authors]
            author_count = len(authors)
            author_names_str = ", ".join(author_names) if author_names else "Authors not found"
            
            # Extract affiliations for each author
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

# Add a progress counter
total_titles = len(df)
progress_results = []

for idx, title in enumerate(df['Title']):
    result = get_doi_authors_count_and_affiliations(title, idx, total_titles)
    progress_results.append(result)

# Update the dataframe with results
df[['DOI', 'Authors', 'Number of Authors', 'Author Affiliation']] = pd.DataFrame(progress_results)


#Export final dataset to Excel
df.to_excel("/Users/ep9k/Desktop/Zhao_Heng Results v.1.xlsx")


