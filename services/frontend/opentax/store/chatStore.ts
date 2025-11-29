import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { sendChatMessage } from '../lib/api/ai-assistant';
import type { AssistantResponse } from '../lib/api/ai-assistant';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  queryId?: string;
}

interface ChatState {
  // State
  messages: Message[];
  loading: boolean;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      messages: [],
      loading: false,

      // Send message to AI assistant
      sendMessage: async (content: string) => {
        if (!content.trim() || get().loading) return;

        const userMessage: Message = {
          id: Date.now().toString(),
          role: 'user',
          content,
          timestamp: new Date(),
        };

        // Add user message immediately
        set((state) => ({
          messages: [...state.messages, userMessage],
          loading: true,
        }));

        try {
          const response: AssistantResponse = await sendChatMessage(content);

          const assistantMessage: Message = {
            id: response.query_id,
            role: 'assistant',
            content: response.natural_language,
            timestamp: new Date(),
            queryId: response.query_id,
          };

          set((state) => ({
            messages: [...state.messages, assistantMessage],
            loading: false,
          }));
        } catch (error) {
          console.error('Failed to send message:', error);

          const errorMessage: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'Sorry, I encountered an error processing your request. Please try again.',
            timestamp: new Date(),
          };

          set((state) => ({
            messages: [...state.messages, errorMessage],
            loading: false,
          }));
        }
      },

      // Clear all messages
      clearMessages: () => {
        set({ messages: [] });
      },
    }),
    {
      name: 'chat-storage',
      storage: createJSONStorage(() => sessionStorage), // Use session storage for chat
    }
  )
);
