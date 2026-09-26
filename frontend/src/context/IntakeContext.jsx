import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const IntakeContext = createContext(null);

export const IntakeProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem('dia_session_id') || null);
  const [messages, setMessages] = useState([]);
  const [structuredState, setStructuredState] = useState({
    full_name: null,
    home_address: null,
    covers_worldwide_assets: null,
    has_children: null,
    children: [],
    executor: { name: null, relationship: null },
    specific_gifts: [],
    additional_wishes: null,
  });
  const [fieldStatuses, setFieldStatuses] = useState({});
  const [documentData, setDocumentData] = useState({
    document_html: '',
    document_text: '',
  });
  const [loading, setLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');

  // Check backend health on mount
  useEffect(() => {
    const checkServer = async () => {
      try {
        const health = await api.checkHealth();
        if (health.status === 'ok') {
          setBackendStatus('connected');
        } else {
          setBackendStatus('degraded');
        }
      } catch (err) {
        console.error('Backend health check error:', err);
        setBackendStatus('disconnected');
        setError('Unable to connect to the server. Please check that the backend and MongoDB are running.');
      }
    };
    checkServer();
  }, []);

  // Sync session ID to localStorage
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('dia_session_id', sessionId);
    } else {
      localStorage.removeItem('dia_session_id');
    }
  }, [sessionId]);

  // Load session data when sessionId is available
  const loadSession = useCallback(async (id) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      // 1. Load messages
      const msgs = await api.getMessages(id);
      setMessages(msgs);

      // 2. Load state
      const stateRes = await api.getState(id);
      if (stateRes && stateRes.state) {
        setStructuredState(stateRes.state);
        setFieldStatuses(stateRes.field_statuses || {});
      }

      // 3. Load document
      const docRes = await api.getDocument(id);
      if (docRes) {
        setDocumentData({
          document_html: docRes.document_html || '',
          document_text: docRes.document_text || '',
        });
      }
      setSessionId(id);
    } catch (err) {
      console.error('Failed to load session:', err);
      setError('Could not restore session. Starting fresh session might be needed.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-restore session on mount if ID exists
  useEffect(() => {
    if (sessionId) {
      loadSession(sessionId);
    }
  }, [sessionId, loadSession]);

  // Create a brand new session
  const createNewSession = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.createSession('Personal Wishes Document');
      setSessionId(res.session_id);
      setStructuredState(res.state);
      setDocumentData(res.document);
      // Initialize with welcome message
      setMessages([
        {
          id: 'initial',
          session_id: res.session_id,
          role: 'assistant',
          content: res.initial_message,
          quick_replies: [],
          created_at: new Date().toISOString(),
        },
      ]);
      return res.session_id;
    } catch (err) {
      console.error('Failed to create new session:', err);
      setError('Unable to create session. Ensure the backend and MongoDB are running.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Send a user message
  const sendMessage = async (text) => {
    if (!text.trim() || sendingMessage) return;

    let currentSid = sessionId;
    if (!currentSid) {
      currentSid = await createNewSession();
    }

    const optimisticUserMsg = {
      id: `client-${Date.now()}`,
      session_id: currentSid,
      role: 'user',
      content: text.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUserMsg]);
    setSendingMessage(true);
    setError(null);

    try {
      const res = await api.sendMessage(currentSid, text.trim());

      const assistantMsg = {
        id: `server-${Date.now()}`,
        session_id: currentSid,
        role: 'assistant',
        content: res.assistant_message,
        quick_replies: res.quick_replies || [],
        metadata: {
          needs_clarification: res.needs_clarification,
          is_correction: res.is_correction,
        },
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);

      if (res.state) {
        setStructuredState(res.state);
      }
      if (res.document) {
        setDocumentData(res.document);
      }

      return res;
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to process message. Please check server connectivity.');
      // Add a helpful assistant fallback error message
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          session_id: currentSid,
          role: 'assistant',
          content: 'Sorry, I encountered an issue communicating with the service. Please try again or verify your connection.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setSendingMessage(false);
    }
  };

  // Update structured state manually (from review page or inline edit modal)
  const updateStateField = async (updates) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.updateState(sessionId, updates);
      if (res.state) {
        setStructuredState(res.state);
      }
      if (res.field_statuses) {
        setFieldStatuses(res.field_statuses);
      }
      if (res.document) {
        setDocumentData(res.document);
      }
      return res;
    } catch (err) {
      console.error('Error updating state:', err);
      setError('Failed to update state. Please check your inputs.');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Regenerate document
  const regenerateDocument = async () => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await api.regenerateDocument(sessionId);
      if (res) {
        setDocumentData({
          document_html: res.document_html || '',
          document_text: res.document_text || '',
        });
      }
      return res;
    } catch (err) {
      console.error('Error regenerating document:', err);
      setError('Failed to regenerate document.');
    } finally {
      setLoading(false);
    }
  };

  // Clear conversation
  const clearChat = async () => {
    if (!sessionId) return;
    try {
      await api.resetMessages(sessionId);
      setMessages([
        {
          id: `reset-${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: "Hi! I'll help you create your Personal Wishes Document. Let's get started. What is your full legal name?",
          quick_replies: [],
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error('Failed to clear chat:', err);
    }
  };

  // Calculate current intake progress step (1 to 5)
  const calculateCurrentStep = () => {
    if (!structuredState.full_name || !structuredState.home_address || structuredState.covers_worldwide_assets === null) {
      return 1; // Personal Details
    }
    if (structuredState.has_children === null || (structuredState.has_children && structuredState.children.length === 0)) {
      return 2; // Family
    }
    if (!structuredState.executor.name || !structuredState.executor.relationship) {
      return 3; // Executor
    }
    if (structuredState.specific_gifts.length === 0 || !structuredState.additional_wishes) {
      return 4; // Gifts & Wishes
    }
    return 5; // Review
  };

  return (
    <IntakeContext.Provider
      value={{
        sessionId,
        messages,
        structuredState,
        fieldStatuses,
        documentData,
        loading,
        sendingMessage,
        error,
        backendStatus,
        activeStep: calculateCurrentStep(),
        createNewSession,
        loadSession,
        sendMessage,
        updateStateField,
        regenerateDocument,
        clearChat,
        setError,
      }}
    >
      {children}
    </IntakeContext.Provider>
  );
};

export const useIntake = () => {
  const context = useContext(IntakeContext);
  if (!context) {
    throw new Error('useIntake must be used within an IntakeProvider');
  }
  return context;
};
