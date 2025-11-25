"""Document processing and text extraction module."""
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import fitz  

class DocumentProcessor:
    """Handles extraction of text from various document formats."""
    
    def __init__(self):
        self.processors = {
            ".md": self._process_markdown,
            ".txt": self._process_text,
            ".json": self._process_json,
            ".pdf": self._process_pdf,
            ".html": self._process_html,
            ".docx": self._process_docx
        }
    
    def process(self, file_path: Path, content: bytes = None) -> Dict[str, Any]:
        """Process a document and extract text with metadata."""
        ext = file_path.suffix.lower()
        processor = self.processors.get(ext, self._process_text)
        
        if content is None:
            with open(file_path, "rb") as f:
                content = f.read()
        
        text = processor(content, file_path)
        
        return {
            "filename": file_path.name,
            "extension": ext,
            "content": text,
            "source_document": file_path.name
        }
    
    def _process_markdown(self, content: bytes, path: Path) -> str:
        """Process Markdown files."""
        return content.decode("utf-8", errors="ignore")
    
    def _process_text(self, content: bytes, path: Path) -> str:
        """Process plain text files."""
        return content.decode("utf-8", errors="ignore")
    
    def _process_json(self, content: bytes, path: Path) -> str:
        """Process JSON files - convert to readable text."""
        try:
            data = json.loads(content.decode("utf-8"))
            return self._json_to_text(data)
        except json.JSONDecodeError:
            return content.decode("utf-8", errors="ignore")
    
    def _json_to_text(self, data: Any, indent: int = 0) -> str:
        """Recursively convert JSON to readable text."""
        lines = []
        prefix = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._json_to_text(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                lines.append(self._json_to_text(item, indent))
        else:
            lines.append(f"{prefix}{data}")
        
        return "\n".join(lines)
    
    def _process_pdf(self, content: bytes, path: Path) -> str:
        """Process PDF files using pymupdf."""
        text_parts = []
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
        return "\n\n".join(text_parts)
    
    def _process_html(self, content: bytes, path: Path) -> str:
        """Process HTML files - extract structure and text."""
        soup = BeautifulSoup(content, "lxml")
        
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()
        
        # Extract structured information
        lines = []
        lines.append(f"HTML STRUCTURE FOR {path.name}\n")
        
        # Extract all elements with IDs
        elements_with_ids = soup.find_all(id=True)
        if elements_with_ids:
            lines.append("ELEMENTS WITH IDs:")
            for el in elements_with_ids:
                tag = el.name
                el_id = el.get("id")
                classes = " ".join(el.get("class", []))
                text = el.get_text(strip=True)[:50] if el.get_text(strip=True) else ""
                lines.append(f"  - <{tag} id=\"{el_id}\" class=\"{classes}\"> {text}...")
        
        # Extract form elements
        forms = soup.find_all("form")
        inputs = soup.find_all("input")
        buttons = soup.find_all("button")
        textareas = soup.find_all("textarea")
        
        if inputs or buttons or textareas:
            lines.append("\nFORM ELEMENTS:")
            for inp in inputs:
                inp_type = inp.get("type", "text")
                inp_id = inp.get("id", "no-id")
                inp_name = inp.get("name", "no-name")
                lines.append(f"  - <input type=\"{inp_type}\" id=\"{inp_id}\" name=\"{inp_name}\">")
            for btn in buttons:
                btn_id = btn.get("id", "no-id")
                btn_text = btn.get_text(strip=True)
                lines.append(f"  - <button id=\"{btn_id}\">{btn_text}</button>")
            for ta in textareas:
                ta_id = ta.get("id", "no-id")
                ta_name = ta.get("name", "no-name")
                lines.append(f"  - <textarea id=\"{ta_id}\" name=\"{ta_name}\">")
        
        # Extract full HTML for reference
        lines.append("\n FULL HTML SOURCE \n")
        lines.append(content.decode("utf-8", errors="ignore"))
        
        return "\n".join(lines)
    
    def _process_docx(self, content: bytes, path: Path) -> str:
        """Process DOCX files."""
        try:
            from docx import Document
            from io import BytesIO
            doc = Document(BytesIO(content))
            return "\n\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error processing DOCX: {str(e)}"


class TextChunker:
    """Split text into chunks for embedding."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks with metadata."""
        if not text:
            return []
        
        # Split by paragraphs first, then by sentences if needed
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) <= self.chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + para
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, len(chunks), metadata))
                
                # Handle paragraphs larger than chunk_size
                if len(para) > self.chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    for sent in sentences:
                        if len(current_chunk) + len(sent) <= self.chunk_size:
                            current_chunk += (" " if current_chunk else "") + sent
                        else:
                            if current_chunk:
                                chunks.append(self._create_chunk(current_chunk, len(chunks), metadata))
                            current_chunk = sent
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, len(chunks), metadata))
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a chunk with metadata."""
        chunk_data = {
            "text": text,
            "chunk_index": index,
        }
        if metadata:
            chunk_data.update(metadata)
        return chunk_data