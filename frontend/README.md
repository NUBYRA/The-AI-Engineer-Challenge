# OpenAI Chat Frontend

A modern, responsive Next.js frontend for interacting with the OpenAI Chat API.

## Features

- 🔐 Secure API key input (hidden field)
- 🤖 Multiple OpenAI model selection
- 💬 Real-time streaming responses
- 📱 Responsive design
- 🎨 Modern UI with gradient styling
- 🔄 Health check endpoint

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Your FastAPI backend running (locally or deployed)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
Create a `.env.local` file in the frontend directory:
```env
API_URL=http://localhost:8000
```

For production, set this to your deployed API URL:
```env
API_URL=https://your-api.vercel.app
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **Enter your OpenAI API Key**: Paste your API key in the password field
2. **Select a Model**: Choose from available OpenAI models
3. **Developer Message**: Enter the system/developer message to set context
4. **User Message**: Enter your question or prompt
5. **Send**: Click the button to get a streaming response

## Available Models

- gpt-4.1-mini (default)
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-3.5-turbo

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set the `API_URL` environment variable in Vercel dashboard
4. Deploy!

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- DigitalOcean App Platform
- AWS Amplify

## API Routes

- `POST /api/chat` - Forwards requests to your FastAPI chat endpoint
- `GET /api/health` - Health check endpoint

## Development

### Project Structure

```
src/
├── app/
│   ├── api/
│   │   ├── chat/
│   │   │   └── route.ts      # Chat API proxy
│   │   └── health/
│   │       └── route.ts      # Health check proxy
│   ├── page.tsx              # Main chat interface
│   ├── layout.tsx            # App layout
│   ├── globals.css           # Global styles
│   └── page.module.css       # Component styles
```

### Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Troubleshooting

### API Connection Issues

1. Ensure your FastAPI backend is running
2. Check the `API_URL` environment variable
3. Verify CORS settings in your backend
4. Check browser console for errors

### Streaming Issues

If responses aren't streaming properly:
1. Ensure your backend supports streaming
2. Check network connectivity
3. Verify the API endpoint is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details
