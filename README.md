# 📸 EXIF Photo Analyzer

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-red.svg)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-3.0-38B2AC.svg)
![Vercel](https://img.shields.io/badge/deploy-vercel-black.svg)

**A beautiful web application to extract and display EXIF metadata from photos**

[Demo](#) • [Report Bug](https://github.com/Fidss/app-photo/issues) • [Request Feature](https://github.com/Fidss/app-photo/issues)

</div>

---

## ✨ About The Project

**EXIF Photo Analyzer** is a modern web application built with Python Flask and Tailwind CSS that allows users to upload photos and view detailed EXIF metadata including camera/phone model, capture time, ISO, aperture, shutter speed, GPS coordinates, and much more.

Created with love by **Myrielle** 🎀

### 🎯 Key Features

- 📤 **Easy Upload** - Drag & drop or click to upload photos
- 📱 **Device Information** - Shows camera/phone brand and model
- ⏰ **Capture Time** - Exact date and time when photo was taken
- 🎯 **Camera Settings** - ISO, aperture, shutter speed, focal length
- 📍 **GPS Location** - Extracts coordinates with Google Maps integration
- 🖼️ **Image Details** - File name, size, dimensions, format
- 🎨 **Beautiful UI** - Modern design with Tailwind CSS
- ⚡ **Fast Processing** - Serverless architecture on Vercel
- 🔒 **Privacy First** - No photos are stored permanently

---

## 🚀 Technologies Used

### Backend
- **Flask 2.3.3** - Lightweight WSGI web framework
- **Pillow 10.0.1** - Python Imaging Library for EXIF extraction
- **Piexif 1.1.3** - EXIF manipulation library
- **Werkzeug 2.3.7** - WSGI utility library

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **Font Awesome 6** - Icon library
- **Vanilla JavaScript** - No additional frameworks

### Deployment
- **Vercel** - Serverless deployment platform

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/myrielle/exif-analyzer.git
cd exif-analyzer
