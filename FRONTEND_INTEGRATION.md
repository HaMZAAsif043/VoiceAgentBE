# Frontend Integration Guide - ElevenLabs Voice AI

## Overview
This document provides step-by-step instructions for integrating the secure ElevenLabs Voice AI backend with your frontend application (React, Next.js, or vanilla JavaScript).

## Architecture
```
Frontend (Browser)          Backend (Django)           ElevenLabs API
      |                            |                          |
      |---  POST /voice-ai/    --->|                          |
      |    signed-url/              |                          |
      |                             |--- Get Signed URL  ----->|
      |                             |<-- Returns Signed URL ---|
      |<-- Returns Signed URL  -----|                          |
      |                                                         |
      |================ WebSocket Connection ==================>|
      |                     (Using Signed URL)                  |
```

## Backend API Endpoints

### 1. Health Check
**Endpoint:** `GET /voice-ai/health/`

**Description:** Verify that the Voice AI service is operational and properly configured.

**Response:**
```json
{
  "success": true,
  "message": "Voice AI service is operational",
  "service": "ElevenLabs",
  "configured": true
}
```

### 2. Get Signed URL (Main Endpoint)
**Endpoint:** `POST /voice-ai/signed-url/`

**Description:** Generate a secure signed URL for browser-based voice chat. This endpoint hides your `ELEVENLABS_API_KEY` from the frontend.

**Request Body (Optional):**
```json
{
  "user_context": {
    "customer_name": "John Doe",
    "cart": [
      {"id": 1, "name": "Zinger Burger", "quantity": 2}
    ],
    "order_id": 123,
    "any_custom_data": "..."
  }
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Signed URL generated successfully",
  "data": {
    "signed_url": "wss://api.elevenlabs.io/v1/convai/conversation?agent_id=agent_xxx&conversation_signature=cvtkn_xxx",
    "conversation_id": "3a61213a-cbb8-4423-b5f0-49ee0aedd711"
  }
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "success": false,
  "message": "Failed to generate signed URL: ...",
  "error": "Error details here"
}
```

## Frontend Implementation

### Prerequisites
Install the ElevenLabs Conversational AI SDK in your frontend:
```bash
npm install @11labs/client
```

### React/Next.js Implementation

#### Step 1: Create a Voice AI Hook

```typescript
// hooks/useVoiceAI.ts
import { useState, useCallback, useRef } from 'react';
import { Conversation } from '@11labs/client';

interface UseVoiceAIReturn {
  isConnected: boolean;
  isAgentSpeaking: boolean;
  startConversation: (userContext?: any) => Promise<void>;
  stopConversation: () => void;
  error: string | null;
}

export const useVoiceAI = (): UseVoiceAIReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const conversationRef = useRef<Conversation | null>(null);

  const startConversation = useCallback(async (userContext = {}) => {
    try {
      setError(null);

      // Step 1: Get signed URL from your Django backend
      const response = await fetch('http://localhost:8000/voice-ai/signed-url/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_context: userContext }),
      });

      if (!response.ok) {
        throw new Error('Failed to get signed URL from backend');
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.message || 'Failed to generate signed URL');
      }

      const { signed_url } = data.data;

      // Step 2: Connect to ElevenLabs using the signed URL
      const conversation = await Conversation.startSession({
        signedUrl: signed_url,
        onConnect: () => {
          console.log('Connected to ElevenLabs');
          setIsConnected(true);
        },
        onDisconnect: () => {
          console.log('Disconnected from ElevenLabs');
          setIsConnected(false);
          setIsAgentSpeaking(false);
        },
        onMessage: (message) => {
          console.log('Received message:', message);
        },
        onError: (error) => {
          console.error('ElevenLabs error:', error);
          setError(error.message);
        },
        onModeChange: (mode) => {
          // mode can be 'speaking' or 'listening'
          setIsAgentSpeaking(mode.mode === 'speaking');
        },
      });

      conversationRef.current = conversation;
    } catch (err: any) {
      console.error('Error starting conversation:', err);
      setError(err.message);
    }
  }, []);

  const stopConversation = useCallback(async () => {
    if (conversationRef.current) {
      await conversationRef.current.endSession();
      conversationRef.current = null;
      setIsConnected(false);
      setIsAgentSpeaking(false);
    }
  }, []);

  return {
    isConnected,
    isAgentSpeaking,
    startConversation,
    stopConversation,
    error,
  };
};
```

#### Step 2: Create a Voice AI Component

```tsx
// components/VoiceAIButton.tsx
'use client'; // For Next.js 13+ with app directory

import { useVoiceAI } from '@/hooks/useVoiceAI';

export default function VoiceAIButton() {
  const { isConnected, isAgentSpeaking, startConversation, stopConversation, error } = useVoiceAI();

  const handleToggle = async () => {
    if (isConnected) {
      stopConversation();
    } else {
      // Optional: Pass user context to the agent
      const userContext = {
        customer_name: 'John Doe',
        cart: [
          { id: 1, name: 'Zinger Burger', quantity: 2 },
        ],
      };
      await startConversation(userContext);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={handleToggle}
        className={`px-6 py-3 rounded-lg font-semibold transition-all ${
          isConnected
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
        disabled={!!error}
      >
        {isConnected ? '🔴 End Call' : '🎤 Start Voice Chat'}
      </button>

      {isConnected && (
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isAgentSpeaking ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm text-gray-600">
            {isAgentSpeaking ? 'Agent is speaking...' : 'Listening...'}
          </span>
        </div>
      )}

      {error && (
        <div className="text-red-500 text-sm">
          Error: {error}
        </div>
      )}
    </div>
  );
}
```

#### Step 3: Use the Component

```tsx
// app/page.tsx or pages/index.tsx
import VoiceAIButton from '@/components/VoiceAIButton';

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-8">KFC Voice AI Order System</h1>
        <VoiceAIButton />
      </div>
    </main>
  );
}
```

### Vanilla JavaScript Implementation

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KFC Voice AI</title>
  <script type="module">
    import { Conversation } from 'https://esm.sh/@11labs/client';

    let conversation = null;
    let isConnected = false;

    async function startConversation() {
      try {
        // Get signed URL from backend
        const response = await fetch('http://localhost:8000/voice-ai/signed-url/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_context: { customer_name: 'Test User' }
          })
        });

        const data = await response.json();
        if (!data.success) throw new Error(data.message);

        // Connect to ElevenLabs
        conversation = await Conversation.startSession({
          signedUrl: data.data.signed_url,
          onConnect: () => {
            console.log('Connected');
            isConnected = true;
            updateUI();
          },
          onDisconnect: () => {
            console.log('Disconnected');
            isConnected = false;
            updateUI();
          },
          onError: (error) => console.error('Error:', error)
        });
      } catch (error) {
        console.error('Failed to start conversation:', error);
        alert('Failed to start conversation: ' + error.message);
      }
    }

    async function stopConversation() {
      if (conversation) {
        await conversation.endSession();
        conversation = null;
        isConnected = false;
        updateUI();
      }
    }

    function updateUI() {
      const button = document.getElementById('voiceButton');
      const status = document.getElementById('status');

      if (isConnected) {
        button.textContent = '🔴 End Call';
        button.classList.add('connected');
        status.textContent = 'Connected - You can start talking';
      } else {
        button.textContent = '🎤 Start Voice Chat';
        button.classList.remove('connected');
        status.textContent = 'Not connected';
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      const button = document.getElementById('voiceButton');
      button.addEventListener('click', () => {
        if (isConnected) {
          stopConversation();
        } else {
          startConversation();
        }
      });
    });
  </script>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      background: #f5f5f5;
    }
    .container {
      text-align: center;
      padding: 2rem;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    button {
      padding: 1rem 2rem;
      font-size: 1.125rem;
      font-weight: 600;
      border: none;
      border-radius: 8px;
      background: #3b82f6;
      color: white;
      cursor: pointer;
      transition: all 0.2s;
    }
    button:hover {
      background: #2563eb;
    }
    button.connected {
      background: #ef4444;
    }
    button.connected:hover {
      background: #dc2626;
    }
    #status {
      margin-top: 1rem;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>KFC Voice AI Order System</h1>
    <button id="voiceButton">🎤 Start Voice Chat</button>
    <p id="status">Not connected</p>
  </div>
</body>
</html>
```

## Environment Variables

Ensure your backend `.env` file is configured:
```env
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxx
AGENT_ID=agent_xxxxxxxxxxxxx
```

## CORS Configuration

If your frontend is running on a different domain/port, ensure CORS is properly configured in Django `settings.py`:

```python
# For development
CORS_ALLOW_ALL_ORIGINS = True

# For production (specific origins)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

## Security Best Practices

1. **Never expose your `ELEVENLABS_API_KEY` in frontend code**
   - Always fetch signed URLs from your backend
   - The signed URLs are temporary and expire automatically

2. **Validate user input on the backend**
   - Sanitize any user_context data before storing or processing

3. **Use HTTPS in production**
   - Ensures all communication is encrypted

4. **Implement rate limiting**
   - Prevent abuse of the signed URL endpoint
   - Consider adding authentication to the endpoint

## Testing

### Test the Backend Endpoint
```bash
# Health check
curl http://localhost:8000/voice-ai/health/

# Get signed URL
curl -X POST http://localhost:8000/voice-ai/signed-url/ \
  -H "Content-Type: application/json" \
  -d '{"user_context": {"customer_name": "Test User"}}'
```

### Expected Flow
1. User clicks "Start Voice Chat" button
2. Frontend calls `/voice-ai/signed-url/` endpoint
3. Backend generates signed URL from ElevenLabs API
4. Frontend receives signed URL
5. Frontend establishes WebSocket connection using signed URL
6. User can speak with the AI agent
7. User clicks "End Call" to disconnect

## Troubleshooting

### "Failed to get signed URL from backend"
- Check that your Django server is running on `http://localhost:8000`
- Verify CORS is configured correctly
- Check browser console for network errors

### "Connection failed" or "WebSocket error"
- Ensure `ELEVENLABS_API_KEY` and `AGENT_ID` are set correctly in `.env`
- Verify the agent is active in your ElevenLabs dashboard
- Check browser console for detailed error messages

### "No audio" or "Microphone not working"
- Ensure microphone permissions are granted in the browser
- Check that you're using HTTPS (or localhost for testing)
- Verify your browser supports Web Audio API

## Advanced Features

### Passing Dynamic Context
You can pass context about the user's current state to personalize the conversation:

```typescript
const userContext = {
  customer_name: user.name,
  cart: cart.items.map(item => ({
    id: item.id,
    name: item.name,
    quantity: item.quantity,
    price: item.price
  })),
  order_total: cart.total,
  delivery_address: user.address,
  is_returning_customer: user.orderCount > 0
};

await startConversation(userContext);
```

The AI agent can use this context to provide personalized responses about the user's order.

## Next Steps

1. **Run migrations** to enable call tracking:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Uncomment database tracking** in `voice_ai.py` to save conversation records

3. **Add authentication** to the endpoint to prevent unauthorized access

4. **Implement analytics** to track conversation metrics

5. **Add error logging** for production debugging

## Support

For ElevenLabs-specific issues, refer to:
- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [ElevenLabs Conversational AI SDK](https://github.com/elevenlabs/elevenlabs-js)

For backend issues, check:
- Django logs: `python manage.py runserver`
- Browser console for frontend errors
