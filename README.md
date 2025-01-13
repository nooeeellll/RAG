# PDF Knowledge Base & Chatbot

An AI-powered application that creates a searchable knowledge base from PDF documents and enables natural language interactions through a chat interface. Built with Python, leveraging Pinecone for vector storage and Google's Gemini model for response generation.

## Features

- 📄 Multi-PDF document processing
- 🔍 Semantic search capabilities
- 💬 Natural language chat interface
- 📊 Real-time upload progress tracking
- 🔄 Batch processing support
- 🎯 Contextual response generation

## Prerequisites

- Python 3.8+
- Pinecone API key
- Google AI (Gemini) API key
- PyTorch
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-knowledge-chatbot.git
cd pdf-knowledge-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:
```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
MODEL_NAME=your_model_name
GOOGLE_API_KEY=your_gemini_api_key
```

## Usage

### Running the Main Application

Start the web application:
```bash
python app.py
```

The application will be available at `http://localhost:8050`

### Utility Scripts

#### Bulk PDF Upload
Process multiple PDFs from a directory (edit directory in bulk_upload.py before running):
```bash
python scripts/bulk_upload.py
```

#### PubMed PDF Scraper
Download PDFs from PubMed Central:
```bash
python scripts/pubmed_scraper.py
```

## Project Structure

```
pdf-knowledge-chatbot/
├── core/               # Core functionality
│   ├── embedding.py    # Vector embedding management
│   ├── chatbot.py     # Chat interface logic
│   └── utils.py       # Utility functions
├── ui/                 # User interface
│   ├── templates.py    # Page templates
│   └── styles.css     # Styling
├── scripts/           # Utility scripts
│   ├── bulk_upload.py  # Bulk PDF processing
│   └── pubmed_scraper.py  # PubMed PDF downloader
├── app.py             # Main application
└── requirements.txt   # Dependencies
```

## How It Works

1. **Document Processing**
   - PDFs are uploaded through the web interface
   - Text is extracted and split into manageable chunks
   - Each chunk is converted to a vector embedding

2. **Vector Storage**
   - Embeddings are stored in Pinecone vector database
   - Each chunk maintains metadata including source file and position

3. **Chat Interface**
   - User queries are processed using semantic search
   - Relevant document chunks are retrieved
   - Gemini model generates contextual responses

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Dash](https://dash.plotly.com/)
- Vector storage powered by [Pinecone](https://www.pinecone.io/)
- Language model powered by [Google Gemini](https://ai.google.dev/)
