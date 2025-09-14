# 🚀 Panduan Lengkap Deploy ke Railway

## ✅ Status Kesiapan Deployment

Aplikasi **Universal Toolkit** sudah siap untuk di-deploy ke Railway dengan:
- ✅ Semua dependencies sistem tersedia (ffmpeg, pandoc, imagemagick, sox)
- ✅ Konfigurasi Railway optimal (`railway.json`, `nixpacks.toml`)
- ✅ Environment variables template (`.env.example`)
- ✅ WSGI production-ready (`wsgi.py`)
- ✅ Semua fitur sudah ditest dan berfungsi

## 🔧 Langkah Deploy ke Railway

### 1. Persiapan Repository
```bash
# Pastikan semua file sudah di commit
git add .
git commit -m "Ready for Railway deployment with proper WSGI and system deps"
git push origin main
```

### 2. Setup Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login ke Railway
railway login

# Deploy dari directory ini
railway up
```

### ⚠️ Important: WSGI Entrypoint
Railway akan menggunakan `wsgi:app` sebagai entrypoint yang memastikan:
- ✅ Proper initialization (directories, cleanup scheduler)
- ✅ System dependencies check
- ✅ Production logging configuration
- ✅ Environment variables validation

### 3. Set Environment Variables di Railway
**WAJIB diset di Railway dashboard:**
```bash
SESSION_SECRET=your-super-secret-session-key-make-it-long-and-random
```

**Optional (sudah ada default yang baik):**
```bash
PORT=5000
DEBUG=false
```

### 4. Verifikasi Deployment
Setelah deploy berhasil, test endpoint berikut:
- `GET /` - Homepage dashboard
- `POST /api/qr/generate` - Test QR generator
- `GET /video` - Video tools page
- `GET /audio` - Audio tools page

## 🎯 Fitur yang Tersedia

### 📥 Downloader
- Download video dari YouTube, TikTok, Instagram, dll
- Download audio only dari video
- Download playlist (max 50 video)
- Download galeri gambar
- Info video tanpa download

### 🎥 Video Tools
- Convert format video (MP4, AVI, MOV, dll)
- Extract audio dari video
- Split/trim video
- Compress video dengan CRF control
- Info video lengkap

### 🎵 Audio Tools  
- Convert format audio (MP3, WAV, FLAC, dll)
- Extract metadata lengkap
- Control quality dan sample rate
- Info audio lengkap

### 🖼️ Image Tools
- Convert format gambar
- Resize dengan aspect ratio control
- Enhance brightness, contrast, saturation
- Apply filters (blur, sharpen, grayscale, dll)
- Info gambar lengkap

### 📄 Document Tools
- Convert dokumen (PDF, DOCX, HTML, Markdown, dll)
- Extract plain text
- Convert to Markdown
- Info dokumen (word count, pages)

### 🛠️ Utilities
- Generate QR code dengan customization
- Create/extract archives (ZIP, TAR, GZ)
- Generate file hashes (MD5, SHA256, dll)
- Convert text encoding

## 🚀 Optimasi Production

File `railway.json` sudah dioptimalkan dengan:
- ✅ Worker preloading untuk performa
- ✅ Max requests dengan jitter
- ✅ Health check endpoint
- ✅ Auto-restart pada failure
- ✅ Sleep prevention

File `nixpacks.toml` memastikan:
- ✅ Python 3.11
- ✅ Semua binary dependencies via NIXPACKS_PKGS (ffmpeg, pandoc, imagemagick, sox)
- ✅ Native Nixpacks package management untuk stability

## 🔄 Update & Maintenance

Railway akan auto-deploy dari Git push ke main branch.
File cleanup otomatis setiap jam untuk menghemat storage.

## ⚡ Performance Notes

- Upload limit: 100MB per file
- Worker count: 2 (optimal untuk Railway free tier)
- Request timeout: 120 detik
- Processing limit playlist: 50 video max
- Auto cleanup files older than 2 jam