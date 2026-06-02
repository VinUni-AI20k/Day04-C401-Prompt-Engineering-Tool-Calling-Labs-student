from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

from tools._shared import ROOT, TIMEOUT, err


# arXiv specific constants and functions (reused from paper_text tool)
ARXIV_MIN_INTERVAL_SECONDS = 3.0
_last_arxiv_request_at = 0.0


def _arxiv_user_agent() -> str:
    return os.getenv("ARXIV_USER_AGENT", "AI20k-Day04-Research-Agent/1.0 (educational lab; contact: local)")


def _rate_limit_arxiv() -> None:
    global _last_arxiv_request_at
    elapsed = time.monotonic() - _last_arxiv_request_at
    if elapsed < ARXIV_MIN_INTERVAL_SECONDS:
        time.sleep(ARXIV_MIN_INTERVAL_SECONDS - elapsed)
    _last_arxiv_request_at = time.monotonic()


def _arxiv_id(value: str) -> str:
    """Extract arXiv ID from various formats."""
    match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", value or "")
    if not match:
        raise ValueError("Invalid arXiv ID or URL")
    return match.group(1)


def _is_arxiv_url(url: str) -> bool:
    """Check if URL is from arXiv."""
    return "arxiv.org" in url.lower() or re.search(r"\d{4}\.\d{4,5}", url)


def _download_arxiv_pdf(url_or_id: str, output_file: Path) -> tuple[str, str, int]:
    """Download PDF from arXiv with proper rate limiting."""
    try:
        arxiv_id = _arxiv_id(url_or_id)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        _rate_limit_arxiv()
        response = requests.get(
            pdf_url, 
            headers={"User-Agent": _arxiv_user_agent()}, 
            timeout=TIMEOUT, 
            stream=True
        )
        response.raise_for_status()
        
        total_size = 0
        with output_file.open("wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    total_size += len(chunk)
                    
        return arxiv_id, pdf_url, total_size
        
    except Exception as exc:
        raise RuntimeError(f"Failed to download from arXiv: {exc}") from exc


def _download_generic_pdf(url: str, output_file: Path) -> tuple[str, int]:
    """Download PDF from generic URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
    response.raise_for_status()
    
    # Check if response is actually a PDF
    content_type = response.headers.get('content-type', '').lower()
    if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
        # Try to detect PDF by content
        first_chunk = next(response.iter_content(chunk_size=1024), b'')
        if not first_chunk.startswith(b'%PDF'):
            raise ValueError("Downloaded content does not appear to be a PDF file")
        # Reset the response for full download
        response = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True)
        response.raise_for_status()
    
    # Write file
    total_size = 0
    with output_file.open("wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                total_size += len(chunk)
                
    return url, total_size


def download_pdf(url: str = "", filename: str = "", download_folder: str = "downloads") -> dict[str, Any]:
    """
    Downloads a PDF file from the given URL and saves it locally.
    Optimized for arXiv papers with fallback to generic PDF download.
    
    Args:
        url: URL of the PDF file to download (supports arXiv URLs/IDs and generic URLs)
        filename: Optional custom filename (without extension). If not provided, will extract from URL
        download_folder: Folder to save the file (relative to project root, default: "downloads")
    
    Returns:
        Dict containing download status, file path, and file size
    """
    try:
        if not url:
            raise ValueError("URL is required")
            
        # Validate URL
        if not _is_arxiv_url(url):
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")
            
        # Create download directory
        download_path = ROOT / download_folder
        download_path.mkdir(parents=True, exist_ok=True)
        
        # Determine filename
        if not filename:
            if _is_arxiv_url(url):
                try:
                    arxiv_id = _arxiv_id(url)
                    filename = f"arxiv_{arxiv_id}"
                except ValueError:
                    filename = "arxiv_paper"
            else:
                # Extract filename from URL
                url_path = Path(urlparse(url).path)
                filename = url_path.stem or "downloaded_file"
            
        # Ensure .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
            
        output_file = download_path / filename
        
        # Check if file already exists and create unique name
        original_file = output_file
        counter = 1
        while output_file.exists():
            base_name = original_file.stem
            output_file = download_path / f"{base_name}_{counter}.pdf"
            counter += 1
                
        # Try downloading based on URL type
        download_method = None
        source_url = None
        total_size = 0
        arxiv_id = None
        fallback_used = False
        
        try:
            if _is_arxiv_url(url):
                # Try arXiv optimized download first
                download_method = "arxiv_api"
                arxiv_id, source_url, total_size = _download_arxiv_pdf(url, output_file)
            else:
                # Use generic download for non-arXiv URLs
                download_method = "generic_http"
                source_url, total_size = _download_generic_pdf(url, output_file)
                
        except Exception as primary_exc:
            # Fallback: try generic download if arXiv failed
            if _is_arxiv_url(url) and download_method == "arxiv_api":
                try:
                    # Convert arXiv URL to direct PDF URL for fallback
                    if arxiv_id:
                        fallback_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    else:
                        # Try to construct direct PDF URL
                        try:
                            test_id = _arxiv_id(url)
                            fallback_url = f"https://arxiv.org/pdf/{test_id}.pdf"
                        except ValueError:
                            fallback_url = url
                    
                    download_method = "generic_fallback"
                    source_url, total_size = _download_generic_pdf(fallback_url, output_file)
                    fallback_used = True
                    
                except Exception as fallback_exc:
                    # Both methods failed
                    raise RuntimeError(
                        f"Download failed with both arXiv API and fallback methods. "
                        f"Primary error: {primary_exc}. Fallback error: {fallback_exc}"
                    ) from primary_exc
            else:
                # Re-raise original exception if not arXiv or fallback not applicable
                raise primary_exc
                    
        # Format file size
        def format_size(bytes_size: int) -> str:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024
            return f"{bytes_size:.1f} TB"
            
        result = {
            "tool": "download_pdf",
            "status": "success",
            "url": url,
            "source_url": source_url,
            "file_path": str(output_file),
            "filename": output_file.name,
            "file_size": total_size,
            "file_size_formatted": format_size(total_size),
            "download_folder": str(download_path),
            "download_method": download_method,
            "message": f"Successfully downloaded PDF: {output_file.name} ({format_size(total_size)})"
        }
        
        # Add arXiv specific info if applicable
        if arxiv_id:
            result["arxiv_id"] = arxiv_id
            result["arxiv_abstract_url"] = f"https://arxiv.org/abs/{arxiv_id}"
            
        # Add fallback info if used
        if fallback_used:
            result["fallback_used"] = True
            result["message"] += " (used fallback method)"
            
        return result
        
    except requests.exceptions.RequestException as exc:
        return {
            "tool": "download_pdf",
            "status": "error",
            "error_type": "network_error",
            "message": f"Network error while downloading PDF: {exc}",
            "url": url,
            "suggestion": "Check your internet connection and verify the URL is accessible. For arXiv papers, you can try using the paper ID directly (e.g., '2301.00001')."
        }
    except ValueError as exc:
        return {
            "tool": "download_pdf", 
            "status": "error",
            "error_type": "validation_error",
            "message": f"Invalid input: {exc}",
            "url": url,
            "suggestion": "Ensure the URL is valid. For arXiv papers, use formats like 'https://arxiv.org/abs/2301.00001' or just '2301.00001'."
        }
    except Exception as exc:
        return {
            "tool": "download_pdf",
            "status": "error", 
            "error_type": "unknown_error",
            "message": f"Unexpected error: {exc}",
            "url": url,
            "suggestion": "Try again later. If the problem persists, check if the PDF is publicly accessible and not behind authentication."
        }