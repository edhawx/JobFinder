import requests
from bs4 import BeautifulSoup
import os
import glob
from dotenv import load_dotenv

#Load API keys from .env file

# Google API credentials
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")  # Replace with your actual Search Engine ID

# Function to generate a new numbered job results file
def get_new_filename():
    base_name = "job_results"
    existing_files = glob.glob(f"{base_name}*.txt")  # Find all job_results*.txt files

    if not existing_files:
        return f"{base_name}.txt"  # If no files exist, start with job_results.txt

    existing_numbers = [
        int(f.replace(base_name, "").replace(".txt", ""))
        for f in existing_files if f.replace(base_name, "").replace(".txt", "").isdigit()
    ]

    new_number = max(existing_numbers, default=0) + 1  # Find the next available number
    return f"{base_name}{new_number}.txt"  # Generate new filename

# Output file to store job results
output_file = get_new_filename()

# Function to search Google using API
def google_api_search(query, num_results=5):
    print(f"🔍 Searching Google for: {query}\n")
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}&num={num_results}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        results = response.json()
        links = [item["link"] for item in results.get("items", [])]
        print(f"🔎 Found {len(links)} results.")
        return links[:num_results]  # Limit results
    else:
        print(f"❌ Google API search failed: {response.status_code}")
        return []

# Function to scrape job postings (if needed)
def scrape_job_page(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})  # Get page content
        soup = BeautifulSoup(response.text, 'html.parser')  # Parse HTML

        # Try to extract the job title from an <h1> tag
        title_tag = soup.find('h1')
        job_title = title_tag.text.strip() if title_tag else "No job title found"

        return job_title
    except Exception as e:
        return f"Error fetching job details: {e}"

# Main script execution
if __name__ == "__main__":

    # Google search query to find employer-posted apprenticeships
    search_query = (
        '"Digital and Technology Solutions Professional" ("Level 6" OR "apprenticeship" OR "apprentice") '
        '(inurl:job OR inurl:careers OR inurl:vacancies OR inurl:apply OR intitle:career OR intitle:job OR intitle:hiring) '
        '-site:ac.uk -site:edu -site:.edu -site:.ac.uk'
    )

    # Ask user how many results they want
    num_results = input("How many job results do you want? (default 5): ").strip()
    num_results = int(num_results) if num_results.isdigit() else 5  # Default to 5 if input is empty or invalid

    # Get job listings from Google API
    job_results = google_api_search(search_query, num_results=num_results)

    if not job_results:
        print("\n❌ No job listings found. Google might not have enough results or API limits exceeded.")
        input("\nPress Enter to exit...")
        exit()

    # Write results to file and print to console
    print("\n✅ Jobs found! Writing results...\n")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("✅ Found job postings:\n\n")

    for idx, job_link in enumerate(job_results, 1):
        print(f"{idx}. {job_link}")
        job_title = scrape_job_page(job_link)

        # Append job info to the file
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"{idx}. {job_link}\n")
            f.write(f"   → Job Title: {job_title}\n\n")

        print(f"   → Job Title: {job_title}\n")

    # Open Notepad only once after all jobs are written
    print("\n✅ Job search complete! Press Enter to open Notepad and exit...")
    input()
    os.system(f"start /wait notepad {output_file}")  # Waits until Notepad is closed
    input("\nPress Enter to exit...")  # Now this will actually show before the terminal closes
