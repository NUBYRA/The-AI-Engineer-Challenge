'use client';

import { useState } from 'react';
import styles from './page.module.css';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [apiKey, setApiKey] = useState('');
  const [currentMessage, setCurrentMessage] = useState('');
  const [conversationHistory, setConversationHistory] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;
    
    setIsLoading(true);

    // Add user message to conversation history
    const userMessage: ChatMessage = { role: 'user', content: currentMessage };
    const updatedHistory = [...conversationHistory, userMessage];
    setConversationHistory(updatedHistory);
    
    // Store the current message before clearing it
    const messageToSend = currentMessage;
    setCurrentMessage('');

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_history: updatedHistory,
          current_user_message: messageToSend,
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

  const handleFileUpload = async (file: File) => {
    setUploadStatus('Uploading...');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('api_key', apiKey);
    
    try {
      const response = await fetch('/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      if (result.message) {
        setUploadStatus(`✅ ${result.message} (${result.filename || 'File'}, ${result.file_size ? Math.round(result.file_size/1024) + 'KB' : 'Unknown size'})`);
      } else {
        setUploadStatus('✅ PDF uploaded successfully');
      }
    } catch (error) {
      setUploadStatus('❌ Upload failed - please try again');
      console.error('Upload error:', error);
    }
  };

  return (
    <main className={styles.main}>
      <div className={styles.chatContainer}>
        {/* Settings Panel */}
        <div className={styles.settingsPanel}>
          <h1 className={styles.title}>Health Assistant Chat</h1>
          
          <div className={styles.settingsForm}>
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
                     <label htmlFor="pdfUpload">Upload Health Record (PDF Only):</label>
                     <input
                       type="file"
                       id="pdfUpload"
                       accept=".pdf"
                       onChange={(e) => {
                         const file = e.target.files?.[0];
                         if (file) handleFileUpload(file);
                       }}
                       className={styles.input}
                     />
                     {uploadStatus && (
                       <div style={{ 
                         marginTop: '0.5rem', 
                         fontSize: '0.9rem',
                         padding: '0.5rem',
                         borderRadius: '4px',
                         backgroundColor: uploadStatus.includes('successfully') ? '#d4edda' : '#f8d7da',
                         color: uploadStatus.includes('successfully') ? '#155724' : '#721c24',
                         border: uploadStatus.includes('successfully') ? '1px solid #c3e6cb' : '1px solid #f5c6cb'
                       }}>
                         {uploadStatus}
                       </div>
                     )}
                   </div>

            <button 
              type="button" 
              onClick={clearConversation}
              className={styles.clearButton}
            >
              Clear Conversation
            </button>
          </div>
        </div>

        {/* Chat Interface */}
        <div className={styles.chatInterface}>
          {/* Messages Area */}
          <div className={styles.messagesArea}>
            {conversationHistory.length === 0 ? (
              <div className={styles.welcomeMessage}>
                <h3>Welcome to Health Assistant Chat</h3>
                <p>Start a conversation by typing a message below.</p>
              </div>
            ) : (
              <div className={styles.messagesList}>
                {conversationHistory.map((message, index) => (
                  <div 
                    key={index} 
                    className={`${styles.message} ${styles[message.role]}`}
                  >
                    <div className={styles.messageAvatar}>
                      {message.role === 'user' ? '👤' : '🏥'}
                    </div>
                    <div className={styles.messageContent}>
                      <div className={styles.messageRole}>
                        {message.role === 'user' ? 'You' : 'Health Assistant'}
                      </div>
                      <div className={styles.messageText}>
                        {message.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Input Area */}
          <form onSubmit={handleSubmit} className={styles.inputForm}>
            <div className={styles.inputContainer}>
              <textarea
                id="currentMessage"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Type your message here..."
                className={styles.messageInput}
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
              <button 
                type="submit" 
                disabled={isLoading || !currentMessage.trim()}
                className={styles.sendButton}
              >
                {isLoading ? '⏳' : '➤'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}
