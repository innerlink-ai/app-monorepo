// chatService.ts
import { useAuthStore } from "../stores/authStore";
import { axios,  } from '../composables/index'
import { config } from '@/config';
const BASE_URL = config.apiUrl;

// Helper function to check auth before making requests
const withAuth = async (apiCall: () => Promise<any>) => {
  const authStore = useAuthStore();
  await authStore.checkAuth();
  if (!authStore.isAuthenticated) {
    throw new Error("Not authenticated");
  }
  return apiCall();
};

export const fetchChat = async (chatId: string) => {
  return withAuth(async () => {
    try {
      const response = await axios.get(`${BASE_URL}/chats/${chatId}`, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching chat:", error);
      throw error;
    }
  });
};

export const createChat = async (payload?: {
  message?: string;
}) => {
  return withAuth(async () => {
    try {
      //console.log("Creating chat with payload:", JSON.stringify(payload, null, 2));
      const response = await axios.post(`${BASE_URL}/create_chat`, payload || null, {
        withCredentials: true
      });
      return response.data;
    } catch (error) {
      console.error("Error creating chat:", error);
      throw error;
    }
  });
};

export async function generateStreamResponse(
  chatId: string,
  userMessage: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void,
  onError: (error: any) => void,
  contextData?: {
    files?: Array<{name: string; content: string}>;
    collection?: {id: string; name: string};
  }
): Promise<void> {
  return withAuth(async () => {
    try {
      // Debug the incoming context data
      
      const requestPayload = {
        chat_id: chatId,
        prompt: userMessage,
        ...contextData
      };
      
      //console.log("Generating stream response with payload:", JSON.stringify(requestPayload, null, 2));
      
      const response = await fetch(`${BASE_URL}/generate_stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        credentials: 'include',
        mode: 'cors',
        body: JSON.stringify(requestPayload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body reader not available');
      }

      let buffer = '';
      
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          onComplete();
          break;
        }

        // Append new data to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete SSE events (separated by double newlines)
        const events = buffer.split('\n\n');
        // Keep the last possibly incomplete event in the buffer
        buffer = events.pop() || '';
        
        for (const event of events) {
          // Each event might contain multiple data lines
          const lines = event.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim();
              
              // Handle stream completion
              if (data === '[DONE]') {
                onComplete();
                return;
              }
              
              try {
                // Parse the JSON data
                const jsonData = JSON.parse(data);
                
                // Check for error messages
                if (jsonData.error) {
                  onError(new Error(jsonData.error));
                  continue;
                }
                
                // Extract token content
                if (jsonData.choices && 
                    jsonData.choices[0] && 
                    jsonData.choices[0].delta && 
                    jsonData.choices[0].delta.content !== undefined) {
                  
                  const content = jsonData.choices[0].delta.content;
                  
                  // Pass the content to the callback
                  onChunk(content);
                }
                
                // Check for completion
                if (jsonData.choices && 
                    jsonData.choices[0] && 
                    jsonData.choices[0].finish_reason === 'stop') {
                  onComplete();
                  return;
                }
              } catch (e) {
                // If parsing fails, pass the raw data
                console.warn('Failed to parse JSON:', data);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Error generating stream response:", error);
      onError(error);
      throw error;
    }
  });
}
// Error handler middleware
export const handleApiError = (error: any) => {
  const authStore = useAuthStore();
  if (error.response?.status === 401) {
    // If token expired, user will be logged out
    authStore.checkAuth();
  }
  throw error;
};