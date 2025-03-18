# Lead Generation Automation

This project automates the process of lead generation, contact extraction, and personalized email outreach for real estate and construction-related businesses in Germany.

## Features
- **Google Search Scraping**: Uses Apify's Google Search Scraper to find potential leads.
- **Contact Extraction**: Retrieves email addresses from company websites using Apify's Contact Info Scraper.
- **AI-Generated Emails**: Generates personalized outreach emails in German using the Ollama AI model.
- **Automated Email Sending**: Sends emails via Gmail SMTP.

## Installation

### Prerequisites
- Python 3.8+
- An Apify account with API access
- Ollama with Llama3.2 for AI-powered email generation
- A Gmail account with App Password enabled for SMTP

### Setup
1. **Clone the repository**
   ```sh
   git clone https://github.com/Jubriel/Automatic-Lead-Generation.git
   cd Automatic-Lead-Generation
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** and add the following:
   ```sh
   APIFY_KEY=your_apify_api_key
   SENDER_EMAIL=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   RECIPIENT=default_recipient@example.com
   ```

## Usage
Run the script using:
```sh
python main.py
```

## Workflow
1. **Search for leads**: The script fetches business websites based on predefined keywords.
2. **Extract contact info**: The script scrapes email addresses from the websites.
3. **Generate email content**: An AI model generates a customized outreach email.
4. **Send emails**: The system automatically sends emails to the extracted contacts.

## Logging & Debugging
- Errors and warnings are logged for troubleshooting.
- Use `print` statements or logging to monitor progress.

## Contributing
Feel free to fork the repository and submit pull requests!

## License
This project is licensed under the MIT License.

