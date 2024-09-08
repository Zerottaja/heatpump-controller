import requests
from datetime import datetime

# Define the URL
start_param = datetime.now().strftime("%Y-%m-%d")+"T00%3A00%3A00.000Z"
end_param = datetime.now().strftime("%Y-%m-%d")+"T23%3A59%3A59.999Z"
url = 'https://dashboard.elering.ee/api/nps/price/csv?start={}&end={}&fields=fi'.format(start_param, end_param)
print(url)
# Fetch the CSV file from the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Define the local file name to save the CSV data
    filename = 'nps_price_data.csv'
    
    # Save the content to a local file
    with open(filename, 'wb') as file:
        file.write(response.content)
    
    print(f"CSV file successfully saved as {filename}")
else:
    print(f"Failed to fetch CSV file. Status code: {response.status_code}")

