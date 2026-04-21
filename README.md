# Mac Intelligence Cleanup

Mac Intelligence Cleanup is an intelligent, automated background tool designed for macOS that identifies obsolete or unnecessary files to free up disk space. Utilizing the power of the Gemini 2.0 Flash AI, it intelligently categorizes files and provides recommendations for cleanup via a local web dashboard.

## Features

- **AI-Powered Analysis**: Uses `gemini-2.0-flash` to evaluate the relevance of files and determine if they are obsolete.
- **Background Scanning**: Seamlessly monitors `Downloads`, `Desktop`, `Documents`, and `Library/Caches` for files larger than 0.5MB in the background.
- **Interactive Web Dashboard**: Review AI findings, preview images, and securely delete unnecessary files right from your browser.
- **RAW Image Previews**: Built-in support for rendering RAW image formats (like `.cr2`, `.nef`, `.arw`, etc.) so you can preview photos before deciding to delete them.
- **Native Finder Integration**: Easily reveal files in macOS Finder straight from the web interface.

## Prerequisites

- Python 3.7+
- A Google Gemini API Key

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Environment:**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

Start the application by running:

```bash
python app.py
```

The application will automatically launch your default web browser and open `http://127.0.0.1:8080`. From there, you can view the items being scanned and manage them through the user-friendly interface.

## Notes

- Ensure you have appropriate read/write permissions for the folders being scanned.
- The web server runs locally on `127.0.0.1:8080`.

## License

This project is open-source and available under the standard MIT License.
