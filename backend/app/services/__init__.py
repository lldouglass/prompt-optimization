"""Services package."""

from .file_processor import process_file, FileContent, FileProcessingError

__all__ = ["process_file", "FileContent", "FileProcessingError"]
