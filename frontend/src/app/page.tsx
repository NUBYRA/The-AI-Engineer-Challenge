'use client';

import { useState } from 'react';
import styles from './page.module.css';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('gpt-4o-mini');
  const [systemMessage, setSystemMessage] = useState('You are a helpful assistant.');
  const [currentMessage, setCurrentMessage] = useState('');
  const [conversationHistory, setConversationHistory] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const models = [
    'gpt-4o-mini',
    'gpt-4o',
    'gpt-4-turbo',
    'gpt-4.1-mini',
    'gpt-3.5-turbo'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;
    
    setIsLoading(true);

    // Add user message to conversation history
    const userMessage: ChatMessage = { role: 'user', content: currentMessage };
    const updatedHistory = [...conversationHistory, userMessage];
    setConversationHistory(updatedHistory);
    setCurrentMessage('');

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_history: updatedHistory,
          current_user_message: currentMessage,
          system_message: systemMessage,
          model: model,
          api_key: apiKey,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      let assistantResponse = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        assistantResponse += chunk;
        
        // Update conversation with streaming response
        const assistantMessage: ChatMessage = { role: 'assistant', content: assistantResponse };
        setConversationHistory([...updatedHistory, assistantMessage]);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: ChatMessage = { 
        role: 'assistant', 
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
      setConversationHistory([...updatedHistory, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setConversationHistory([]);
  };

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>OpenAI Chat Interface</h1>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="apiKey">OpenAI API Key:</label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              required
              placeholder="Enter your OpenAI API key"
              className={styles.input}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="model">Model:</label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className={styles.select}
            >
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="systemMessage">System Message (Optional):</label>
            <textarea
              id="systemMessage"
              value={systemMessage}
              onChange={(e) => setSystemMessage(e.target.value)}
              placeholder="Enter the system message (optional)"
              className={styles.textarea}
              rows={2}
            />
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="currentMessage">Your Message:</label>
            <textarea
              id="currentMessage"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              required
              placeholder="Enter your message"
              className={styles.textarea}
              rows={3}
            />
          </div>

          <div className={styles.buttonGroup}>
            <button 
              type="submit" 
              disabled={isLoading || !currentMessage.trim()}
              className={styles.button}
            >
              {isLoading ? 'Sending...' : 'Send Message'}
            </button>
            <button 
              type="button" 
              onClick={clearConversation}
              className={styles.buttonSecondary}
            >
              Clear Conversation
            </button>
          </div>
        </form>

        {conversationHistory.length > 0 && (
          <div className={styles.conversation}>
            <h3>Conversation:</h3>
            <div className={styles.conversationHistory}>
              {conversationHistory.map((message, index) => (
                <div 
                  key={index} 
                  className={`${styles.message} ${styles[message.role]}`}
                >
                  <div className={styles.messageRole}>
                    {message.role === 'user' ? 'You' : 'Assistant'}:
                  </div>
                  <div className={styles.messageContent}>
                    {message.content}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
