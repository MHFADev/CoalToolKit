# Overview

Universal Toolkit is a comprehensive Flask-based web application that provides a unified platform for media processing, document conversion, and utility functions. The application serves as an all-in-one solution for users to download media from various platforms, convert between different file formats, and perform utility operations like QR code generation and metadata extraction. It features a modular architecture with separate processing engines for different file types and a responsive web interface with Indonesian language support.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templating with a base template structure extending across all pages
- **UI Framework**: Custom CSS with dark coal theme and responsive design patterns
- **JavaScript Architecture**: Vanilla JavaScript with object-oriented approach using UniversalToolkit class
- **File Upload**: Drag-and-drop interface with real-time progress tracking and file validation
- **User Interface Language**: Indonesian language support with centralized label management

## Backend Architecture
- **Web Framework**: Flask with Blueprint-based modular routing structure
- **Application Structure**: Factory pattern with `create_app()` function for application initialization
- **Route Organization**: Separate blueprints for each functional area (main, downloader, video, audio, image, document, utility)
- **Task Management**: Asynchronous processing using threading with unique task ID generation and progress tracking
- **File Handling**: Secure file upload with content validation, size limits (100MB), and temporary file management
- **Error Handling**: Comprehensive validation with Indonesian error messages

## Processing Engines
- **Video/Audio Processing**: FFmpeg wrapper (`ffmpeg_wrapper.py`) for comprehensive media conversion and manipulation
- **Image Processing**: Pillow-based processor (`image_wrapper.py`) with ImageMagick integration for format conversion and editing
- **Document Processing**: Pandoc wrapper (`pandoc_wrapper.py`) for document format conversion between PDF, DOCX, ODT, HTML, Markdown
- **Media Downloading**: yt-dlp and gallery-dl integration (`yt_dlp_wrapper.py`) for downloading from multiple platforms
- **Utility Functions**: Custom processor (`utility_wrapper.py`) for QR code generation, metadata extraction, and archive creation

## File Management
- **Upload Directory**: Temporary storage in `/uploads` with automatic cleanup
- **Output Directory**: Processed files stored in `/outputs` with task-based naming
- **File Validation**: MIME type checking, extension validation, and content verification
- **Cleanup Strategy**: Automatic removal of temporary files after processing completion

## Configuration Management
- **Environment Variables**: Session secrets and production configurations via environment variables
- **File Type Support**: Centralized configuration in `config.py` with allowed extensions and MIME types
- **Internationalization**: Indonesian language labels with fallback support

# External Dependencies

## Core Processing Libraries
- **FFmpeg**: Video and audio processing engine for format conversion, compression, and media manipulation
- **Pandoc**: Document conversion engine supporting multiple formats (PDF, DOCX, ODT, HTML, Markdown)
- **yt-dlp**: Enhanced YouTube downloader supporting multiple video platforms
- **gallery-dl**: Media gallery downloader for social media platforms

## Python Libraries
- **Flask**: Web framework with Blueprint support for modular routing
- **Pillow (PIL)**: Image processing library for format conversion and image manipulation
- **mutagen**: Audio metadata extraction and manipulation
- **qrcode**: QR code generation with customization options
- **pypandoc**: Python wrapper for Pandoc document conversion

## Production Infrastructure
- **WSGI**: Production deployment support with proper logging and error handling
- **File System**: Local file storage with automatic directory creation
- **Session Management**: Secure session handling with environment-based secret keys

## Third-party Integrations
- **YouTube and Social Media Platforms**: Content downloading via yt-dlp integration
- **Multiple Video Hosting Services**: Support for TikTok, Instagram, Facebook, Twitter, Vimeo
- **Document Formats**: Cross-platform document conversion supporting office and web formats
- **Image Formats**: Comprehensive image format support including modern formats like WebP