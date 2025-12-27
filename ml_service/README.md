---
title: FloorEye ML Service
emoji: 🧹
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "20.10"
app_file: app.py
pinned: false
---

# FloorEye ML Service

Machine Learning inference service for **FloorEye** using **YOLO**  
This service runs on **Hugging Face Spaces (CPU-only)** and is responsible for detecting dirty floor conditions from image frames.

## Features
- YOLO-based object detection
- FastAPI REST API
- CPU-only (Hugging Face compatible)
- Designed to be called by FloorEye Backend (Railway)

## Endpoints

### Health Check
```http
GET /
