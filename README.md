# PyApplier (W.I.P.)

This Python-based system automates the process of finding job opportunities, generating cover letters, and sending applications via email. It integrates web scraping, AI-powered text generation, and email automation to streamline the job application process.

## Features

- **Web Scraping**: Scrapes company information and email addresses from search results.
- **AI-Powered Cover Letters**: Generates personalized cover letters using AI.
- **Email Automation**: Sends emails with attachments to potential employers.
- **Blacklist Management**: Allows users to blacklist certain emails or domains to avoid future contact.
- **Google Sheets Integration**: Logs application details to a Google Sheet for tracking purposes.

## Setup Instructions

### Prerequisites

- Python 3.x
- Google Sheets API credentials
- OpenAI API key (for AI-powered cover letter generation)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment**:
   - Create a `config.ini` file with your configuration settings, including API keys and email settings.
   - Ensure you have a `blacklist.json` file to manage blacklisted emails and domains.

4. **Google Sheets API**:
   - Enable the Google Sheets API in the Google Cloud Console.
   - Download the credentials JSON file and place it in your project directory.
   - Share your Google Sheet with the service account email from the credentials file.

5. **OpenAI API**:
    - Sign up for an OpenAI account and obtain an API key.
    - Add your OpenAI API key to the `config.ini` file under the `[openai]` section.
    - Ensure you have sufficient credits or a subscription plan to use the API for generating cover letters.

## Usage

1. **Run the Program**:
   ```bash
   python main.py
   ```

2. **Interactive Mode**:
   - The program will prompt you before sending each application, allowing you to review and approve each email.
   - You can choose to open the company's website before applying.

3. **Blacklist Management**:
   - Emails and domains can be added to the blacklist to avoid contacting them in the future.

4. **Logging to Google Sheets**:
   - Application details are logged to a Google Sheet for easy tracking and follow-up.

## Contributing

Feel free to contribute by opening issues or submitting pull requests. Your feedback and improvements are welcome!
