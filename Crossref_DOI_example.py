
import requests
import pandas as pd



df = pd.read_excel("/Users/ep9k/Downloads/Copy of Top cited article per year.xlsx")
df = df.head(30)
# article_titles = df['Title'].tolist()
# article_titles = article_titles[:30]


def get_doi_from_title(title):
    url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 1}  # Search for the title and limit results to 1
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        
        # print()
        # print()
        # print(data)
        # print()
        # print()
        
        # Extract DOI if available
        if data["message"]["items"]:
            return data["message"]["items"][0]["DOI"]
            # return data["message"]["items"][0]["author"]

        else:
            return "DOI not found for the given title."
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# Add DOI information into the 'DOI' column
df['DOI'] = df['Title'].apply(get_doi_from_title)


# # Example Usage
# for title in article_titles:
#     doi = get_doi_from_title(title)
#     print(f"DOI for '{title}': {doi}")
