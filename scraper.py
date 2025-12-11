import requests
import urllib.parse
import matplotlib.pyplot as plt

def runQuery(query, start_year=1800, end_year=2020, corpus=26, smoothing=3):
    """
    Scrapes data from Google Ngram Viewer using the method described by GeeksforGeeks.
    """
    # Convert the query to a URL-safe format
    query_encoded = urllib.parse.quote(query)
    
    # Construct the URL for the JSON data
    url = (f'https://books.google.com/ngrams/json?content={query_encoded}'
           f'&year_start={start_year}&year_end={end_year}'
           f'&corpus={corpus}&smoothing={smoothing}')
    
    print(f"Fetching data for: {query}...")
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for HTTP errors
        output = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    return_data = []
    if not output:
        print("No data available for this Ngram.")
    else:
        for item in output:
            # specific handling to ensure we get the name and the data points
            return_data.append((item['ngram'], item['timeseries']))
            
    return return_data

def plot_ngram_data(data, start_year, end_year):
    """
    Plots the scraped Ngram data using Matplotlib.
    """
    if not data:
        print("Nothing to plot.")
        return

    # Create the range of years for the x-axis
    years = list(range(start_year, end_year + 1))
    
    plt.figure(figsize=(12, 6))
    
    for name, timeseries in data:
        # Depending on smoothing, the returned list length might vary slightly; 
        # we slice or pad to match the year range if necessary.
        # Usually it matches exactly or is shorter by the smoothing window.
        
        # Plotting
        plt.plot(years[:len(timeseries)], timeseries, label=name, linewidth=2)

    plt.title("Google Ngram Viewer Analysis", fontsize=16)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Frequency (%)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Display the plot
    plt.show()

if __name__ == "__main__":
    # Define your search terms here (comma-separated)
    search_query = "Albert Einstein,Isaac Newton,Marie Curie"
    
    # Define the time range
    s_year = 1800
    e_year = 2019
    
    # 1. Scrape the data
    ngram_data = runQuery(search_query, start_year=s_year, end_year=e_year)
    
    # 2. Make the plot
    plot_ngram_data(ngram_data, start_year=s_year, end_year=e_year)