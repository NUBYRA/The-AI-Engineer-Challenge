# 🏥 Health Assistant Chat

> **AI-powered health companion that makes sense of your medical documents!**

Upload your health records and chat with an AI that actually reads them to answer your questions! 🤖

## ✨ Features

- **📄 PDF Upload**: Upload health records and lab results
- **🧠 AI Analysis**: Get intelligent answers about your medical data
- **💬 Natural Chat**: Ask questions like "What do these lab results mean?"
- **🛡️ Private**: Data stays in memory and disappears when you're done

## 🚀 Quick Start

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd The-AI-Engineer-Challenge
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

2. **Install dependencies**:
   ```bash
   # Frontend
   cd frontend && npm install
   
   # Backend  
   cd ../api && pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   # Terminal 1: Backend
   cd api && uvicorn app:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

4. **Open** `http://localhost:3000` and enter your OpenAI API key! 🎉

## 🎯 How to Use

1. **Enter your OpenAI API key**
2. **Upload a PDF** of your health records
3. **Ask questions** like "What do these lab results mean?"
4. **Get AI answers** based on your documents!

## 🛠️ Tech Stack

- **Frontend**: Next.js + React
- **Backend**: FastAPI  
- **PDF Processing**: PyMuPDF
- **AI**: OpenAI API (GPT-4o-mini + embeddings)
- **Deployment**: Vercel

## 🚀 Deployment

**Deploy to Vercel** (zero config!):
1. Connect your GitHub repo to Vercel
2. Set `OPENAI_API_KEY` environment variable
3. Deploy! ✨

## 🐛 Troubleshooting

- **PDF upload failed**: Check if PDF is password-protected or if API key has credits
- **No text extracted**: Some PDFs are image-based (OCR support coming soon!)
- **API key error**: Verify your OpenAI API key and credits

---

**Made with ❤️ for accessible health information!** 🏥
