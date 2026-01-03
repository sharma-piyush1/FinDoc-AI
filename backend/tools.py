import os
from dotenv import load_dotenv
from llama_parse import LlamaParse

# Load environment variables (API Keys)
load_dotenv()

def parse_pdf(file_path: str) -> str:
    """
    The Vision Tool: Uses LlamaParse (GenAI OCR) to read complex PDFs.
    
    Why LlamaParse? 
    Standard OCR (like Tesseract) reads line-by-line, destroying table structure.
    LlamaParse uses GenAI to reconstruct tables as Markdown, which is critical for 
    reading Bank Statements accurately.
    """
    print(f"👀 Parsing document: {file_path}...")

    try:
        # result_type="markdown" is CRITICAL.
        # It forces the OCR to format tables as Markdown tables (e.g. | Date | Description | Amount |)
        # LLMs understand Markdown tables perfectly. Plain text ruins financial data.
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",  # <--- The Secret Sauce
            verbose=True
        )

        # The actual API call to LlamaCloud
        documents = parser.load_data(file_path)

        # Combine all pages into one single string
        full_text = "\n\n".join([doc.text for doc in documents])
        
        print("✅ Parsing complete.")
        return full_text

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        # Return empty string so the graph can handle the error gracefully via the state
        return ""