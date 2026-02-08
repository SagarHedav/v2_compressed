import axios from 'axios';

/**
 * Chatbot API Client
 * Connects to the Media Literacy Chatbot API running on localhost:8000
 */

const CHATBOT_API_URL = import.meta.env.VITE_CHATBOT_API_URL || 'http://localhost:8000';

// Debug: log which API URL is being used
console.log('CHATBOT_API_URL:', CHATBOT_API_URL);
console.log('VITE_CHATBOT_API_URL env:', import.meta.env.VITE_CHATBOT_API_URL);

const chatbotApi = axios.create({
    baseURL: CHATBOT_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 60000, // 60 second timeout for AI responses
});

/**
 * Send a message and get just the answer text
 * @param {string} question - The question to ask
 * @param {boolean} useHistory - Whether to use conversation history (default: true)
 * @returns {Promise<{answer: string}>}
 */
export const sendMessage = async (question, useHistory = true) => {
    const response = await chatbotApi.post('/chat/simple', {
        question,
        use_history: useHistory,
    });
    return response.data;
};

/**
 * Send a message and get full response with sources and metadata
 * @param {string} question - The question to ask
 * @param {boolean} useHistory - Whether to use conversation history (default: true)
 * @returns {Promise<{answer: string, sources: Array, expanded_queries: Array, validation: Object, metadata: Object}>}
 */
export const sendMessageWithSources = async (question, useHistory = true) => {
    const response = await chatbotApi.post('/chat', {
        question,
        use_history: useHistory,
    });
    return response.data;
};

/**
 * Clear the conversation history
 * @returns {Promise<{status: string, message: string}>}
 */
export const clearHistory = async () => {
    const response = await chatbotApi.post('/clear-history');
    return response.data;
};

/**
 * Get the current conversation history
 * @returns {Promise<{history: Array, count: number}>}
 */
export const getHistory = async () => {
    const response = await chatbotApi.get('/history');
    return response.data;
};

/**
 * Check if the chatbot API is healthy
 * @returns {Promise<{status: string, message: string}>}
 */
export const checkHealth = async () => {
    const response = await chatbotApi.get('/health');
    return response.data;
};

export default {
    sendMessage,
    sendMessageWithSources,
    clearHistory,
    getHistory,
    checkHealth,
};
