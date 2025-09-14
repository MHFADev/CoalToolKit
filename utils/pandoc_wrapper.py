# Pandoc wrapper for comprehensive document conversion
import os
import pypandoc
import subprocess
import logging
from typing import Optional, Dict, List
from .common import update_progress

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Comprehensive document processing with pandoc"""
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        
    def convert_document(self, input_path: str, task_id: str, output_format: str = 'pdf',
                        extra_args: Optional[List[str]] = None) -> Optional[str]:
        """Convert document format using pandoc"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengonversi format dokumen...')
            
            output_filename = f'converted_document_{task_id}.{output_format}'
            output_path = os.path.join(self.output_folder, output_filename)
            
            # Get input format from file extension
            input_format = self._detect_input_format(input_path)
            
            update_progress(task_id, 40, 'processing', f'Mengonversi dari {input_format} ke {output_format}...')
            
            # Configure extra arguments based on output format
            args = extra_args or []
            if output_format == 'pdf':
                args.extend(['--pdf-engine=xelatex', '--variable', 'geometry:margin=1in'])
            elif output_format == 'docx':
                args.extend(['--reference-doc=default'])
            elif output_format == 'html':
                args.extend(['--standalone', '--self-contained'])
            elif output_format == 'epub':
                args.extend(['--epub-cover-image=default'])
                
            update_progress(task_id, 60, 'processing', 'Memproses konversi dokumen...')
            
            # Perform conversion
            pypandoc.convert_file(
                input_path, 
                output_format, 
                outputfile=output_path,
                format=input_format,
                extra_args=args
            )
            
            update_progress(task_id, 100, 'completed', f'Dokumen berhasil dikonversi ke {output_format}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Document conversion failed: {e}")
            update_progress(task_id, 0, 'error', f'Konversi dokumen gagal: {str(e)}')
            return None
    
    def extract_text(self, input_path: str, task_id: str) -> Optional[str]:
        """Extract plain text from document"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengekstrak teks dari dokumen...')
            
            output_filename = f'extracted_text_{task_id}.txt'
            output_path = os.path.join(self.output_folder, output_filename)
            
            input_format = self._detect_input_format(input_path)
            
            update_progress(task_id, 60, 'processing', 'Memproses ekstraksi teks...')
            
            pypandoc.convert_file(
                input_path, 
                'plain', 
                outputfile=output_path,
                format=input_format
            )
            
            update_progress(task_id, 100, 'completed', 'Teks berhasil diekstrak!')
            return output_path
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            update_progress(task_id, 0, 'error', f'Ekstraksi teks gagal: {str(e)}')
            return None
    
    def convert_to_markdown(self, input_path: str, task_id: str) -> Optional[str]:
        """Convert document to Markdown format"""
        try:
            update_progress(task_id, 20, 'processing', 'Mengonversi ke format Markdown...')
            
            output_filename = f'converted_markdown_{task_id}.md'
            output_path = os.path.join(self.output_folder, output_filename)
            
            input_format = self._detect_input_format(input_path)
            
            update_progress(task_id, 60, 'processing', 'Memproses konversi Markdown...')
            
            pypandoc.convert_file(
                input_path, 
                'markdown', 
                outputfile=output_path,
                format=input_format,
                extra_args=['--wrap=none']
            )
            
            update_progress(task_id, 100, 'completed', 'Dokumen berhasil dikonversi ke Markdown!')
            return output_path
            
        except Exception as e:
            logger.error(f"Markdown conversion failed: {e}")
            update_progress(task_id, 0, 'error', f'Konversi Markdown gagal: {str(e)}')
            return None
    
    def merge_documents(self, input_paths: List[str], task_id: str, 
                       output_format: str = 'pdf') -> Optional[str]:
        """Merge multiple documents into one"""
        try:
            update_progress(task_id, 20, 'processing', 'Menggabungkan dokumen...')
            
            output_filename = f'merged_document_{task_id}.{output_format}'
            output_path = os.path.join(self.output_folder, output_filename)
            
            # Create temporary markdown file to merge all documents
            temp_md_path = os.path.join(self.output_folder, f'temp_merge_{task_id}.md')
            
            update_progress(task_id, 40, 'processing', 'Memproses penggabungan...')
            
            with open(temp_md_path, 'w', encoding='utf-8') as merged_file:
                for i, input_path in enumerate(input_paths):
                    update_progress(task_id, 40 + (20 * i // len(input_paths)), 'processing', 
                                  f'Memproses dokumen {i+1} dari {len(input_paths)}...')
                    
                    # Convert each document to markdown and append
                    input_format = self._detect_input_format(input_path)
                    content = pypandoc.convert_file(input_path, 'markdown', format=input_format)
                    
                    merged_file.write(f"# Dokumen {i+1}\n\n")
                    merged_file.write(content)
                    merged_file.write("\n\n---\n\n")
            
            update_progress(task_id, 80, 'processing', f'Mengonversi ke format {output_format}...')
            
            # Convert merged markdown to final format
            args = []
            if output_format == 'pdf':
                args.extend(['--pdf-engine=xelatex', '--variable', 'geometry:margin=1in'])
            
            pypandoc.convert_file(
                temp_md_path, 
                output_format, 
                outputfile=output_path,
                extra_args=args
            )
            
            # Clean up temporary file
            os.remove(temp_md_path)
            
            update_progress(task_id, 100, 'completed', f'Dokumen berhasil digabungkan ke format {output_format}!')
            return output_path
            
        except Exception as e:
            logger.error(f"Document merge failed: {e}")
            update_progress(task_id, 0, 'error', f'Penggabungan dokumen gagal: {str(e)}')
            return None
    
    def split_document_by_headers(self, input_path: str, task_id: str) -> List[str]:
        """Split document by headers into separate files"""
        try:
            update_progress(task_id, 20, 'processing', 'Memisahkan dokumen berdasarkan header...')
            
            input_format = self._detect_input_format(input_path)
            
            # Convert to markdown first to analyze structure
            md_content = pypandoc.convert_file(input_path, 'markdown', format=input_format)
            
            # Split by level 1 headers
            sections = md_content.split('\n# ')[1:]  # Skip the first empty part
            
            output_paths = []
            
            for i, section in enumerate(sections):
                update_progress(task_id, 20 + (60 * i // len(sections)), 'processing', 
                              f'Memproses bagian {i+1} dari {len(sections)}...')
                
                # Create temporary markdown file for this section
                section_md_path = os.path.join(self.output_folder, f'temp_section_{task_id}_{i}.md')
                section_content = f"# {section}"
                
                with open(section_md_path, 'w', encoding='utf-8') as f:
                    f.write(section_content)
                
                # Convert to PDF
                section_pdf_path = os.path.join(self.output_folder, f'section_{task_id}_{i+1}.pdf')
                pypandoc.convert_file(
                    section_md_path,
                    'pdf',
                    outputfile=section_pdf_path,
                    extra_args=['--pdf-engine=xelatex', '--variable', 'geometry:margin=1in']
                )
                
                output_paths.append(section_pdf_path)
                os.remove(section_md_path)  # Clean up temp file
            
            update_progress(task_id, 100, 'completed', f'Dokumen berhasil dipisahkan menjadi {len(output_paths)} bagian!')
            return output_paths
            
        except Exception as e:
            logger.error(f"Document split failed: {e}")
            update_progress(task_id, 0, 'error', f'Pemisahan dokumen gagal: {str(e)}')
            return []
    
    def get_document_info(self, file_path: str) -> Optional[Dict]:
        """Get document information"""
        try:
            # Try to extract metadata using pandoc
            input_format = self._detect_input_format(file_path)
            
            # Get basic file info
            info = {
                'filename': os.path.basename(file_path),
                'file_size': os.path.getsize(file_path),
                'format': input_format,
            }
            
            try:
                # Try to get word count
                text_content = pypandoc.convert_file(file_path, 'plain', format=input_format)
                words = len(text_content.split())
                chars = len(text_content)
                lines = len(text_content.split('\n'))
                
                info.update({
                    'word_count': words,
                    'character_count': chars,
                    'line_count': lines,
                })
            except:
                pass  # Skip if can't extract text
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get document info: {e}")
            return None
    
    def _detect_input_format(self, file_path: str) -> str:
        """Detect input format from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        format_map = {
            '.docx': 'docx',
            '.doc': 'doc',
            '.odt': 'odt',
            '.pdf': 'pdf',
            '.txt': 'plain',
            '.md': 'markdown',
            '.html': 'html',
            '.htm': 'html',
            '.rtf': 'rtf',
            '.tex': 'latex',
            '.epub': 'epub',
        }
        
        return format_map.get(ext, 'markdown')