export const appConfig = {
  name: import.meta.env.VITE_APP_NAME || 'Enterprise Agentic RAG',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api/v1',
} as const
