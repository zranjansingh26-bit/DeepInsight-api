"use client";

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Bot, User, Loader2, MessageSquare, Plus, Menu, X,
  TrendingUp, AlertTriangle, BarChart2, Sparkles, Link2
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { fetchApi } from '@/lib/api';

export default function ChatPage() {
  const [messages, setMessages] = useState<{role: string, content: string, follow_up_questions?: string[]}[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string>('');
  const [askedQuestions, setAskedQuestions] = useState<Set<string>>(new Set());

  // Sidebar state
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [historySessions, setHistorySessions] = useState<any[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load datasets on mount
  useEffect(() => {
    fetchApi('/api/datasets/')
      .then(data => {
        setDatasets(data);
        if (data.length > 0) {
          setSelectedDataset(data[0].id);
        }
      })
      .catch(console.error);
  }, []);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleStartSession = async () => {
    if (!selectedDataset) return;
    try {
      const res = await fetchApi('/api/chat/sessions', {
        method: 'POST',
        body: JSON.stringify({ dataset_id: selectedDataset, title: `Analysis - ${new Date().toLocaleDateString()}` })
      });
      setSessionId(res.id);
      setMessages([{ role: 'assistant', content: "Hello! I'm your AI data analyst. I've loaded your dataset. What would you like to know about it?", follow_up_questions: ["What is the general trend?", "Can you show me a summary table?"] }]);
      
      // Update history list
      setHistorySessions(prev => [res, ...prev]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (userMessage: string) => {
    if (!userMessage.trim() || !sessionId || isStreaming) return;

    // Track asked questions for dedup
    setAskedQuestions(prev => new Set([...prev, userMessage.trim()]));

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsStreaming(true);
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chat/${sessionId}/message/stream`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userMessage }),
        }
      );

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullContent = '';
      let followUps: string[] = [];

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
              const data = line.slice(6);
              // Check for [FOLLOWUP] terminal event
              if (data.startsWith('[FOLLOWUP]')) {
                try {
                  const payload = JSON.parse(data.slice('[FOLLOWUP]'.length));
                  followUps = payload.questions || [];
                } catch {}
              } else {
                fullContent += data;
                setMessages(prev => {
                  const newMsgs = [...prev];
                  newMsgs[newMsgs.length - 1].content = fullContent;
                  return newMsgs;
                });
              }
            }
          }
        }
      }

      // Apply follow-up questions
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].follow_up_questions = followUps;
        return newMsgs;
      });

    } catch (error) {
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].content += '\n\n*(Error: Connection lost)*';
        return newMsgs;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(input);
    }
  };

  // Color-code chips by question intent
  const getChipStyle = (q: string): string => {
    const lower = q.toLowerCase();
    if (lower.includes('forecast') || lower.includes('predict') || lower.includes('future'))
      return 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 hover:shadow-[0_0_12px_rgba(6,182,212,0.2)]';
    if (lower.includes('anomal') || lower.includes('outlier') || lower.includes('unusual') || lower.includes('risk'))
      return 'bg-red-500/10 border-red-500/30 text-red-300 hover:bg-red-500/20 hover:shadow-[0_0_12px_rgba(239,68,68,0.2)]';
    if (lower.includes('correlat') || lower.includes('relation') || lower.includes('between'))
      return 'bg-purple-500/10 border-purple-500/30 text-purple-300 hover:bg-purple-500/20 hover:shadow-[0_0_12px_rgba(139,92,246,0.2)]';
    if (lower.includes('trend') || lower.includes('growth') || lower.includes('change') || lower.includes('over time'))
      return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 hover:shadow-[0_0_12px_rgba(16,185,129,0.2)]';
    if (lower.includes('model') || lower.includes('ml') || lower.includes('classif') || lower.includes('accuracy'))
      return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-300 hover:bg-yellow-500/20 hover:shadow-[0_0_12px_rgba(234,179,8,0.2)]';
    return 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/20 hover:shadow-[0_0_12px_rgba(99,102,241,0.2)]';
  };

  const getChipIcon = (q: string) => {
    const lower = q.toLowerCase();
    if (lower.includes('forecast') || lower.includes('predict')) return <BarChart2 size={11} />;
    if (lower.includes('anomal') || lower.includes('outlier') || lower.includes('risk')) return <AlertTriangle size={11} />;
    if (lower.includes('trend') || lower.includes('growth')) return <TrendingUp size={11} />;
    if (lower.includes('model') || lower.includes('ml')) return <Sparkles size={11} />;
    return <Link2 size={11} />;
  };

  return (
    <div className="flex-1 flex h-full max-h-[calc(100vh-6rem)] relative overflow-hidden bg-slate-900 rounded-xl border border-slate-700/50">
      
      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="border-r border-slate-700/50 bg-slate-900/80 flex flex-col shrink-0"
          >
            <div className="p-4 border-b border-slate-700/50 flex justify-between items-center">
              <button 
                onClick={() => setSessionId(null)}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors mr-2"
              >
                <Plus size={16} /> New Chat
              </button>
              <button onClick={() => setIsSidebarOpen(false)} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400">
                <X size={18} />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-1">
              <p className="text-xs font-semibold text-slate-500 mb-2 px-2 uppercase tracking-wider">Recent Sessions</p>
              {historySessions.length === 0 ? (
                <p className="text-sm text-slate-500 px-2 italic">No history</p>
              ) : (
                historySessions.map((session, i) => (
                  <button 
                    key={i}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate flex items-center gap-2 transition-colors ${sessionId === session.id ? 'bg-slate-800 text-indigo-400' : 'text-slate-300 hover:bg-slate-800/50'}`}
                  >
                    <MessageSquare size={14} />
                    {session.title || 'Analysis Session'}
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative min-w-0">
        
        {/* Mobile Sidebar Toggle */}
        {!isSidebarOpen && (
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="absolute top-4 left-4 z-20 p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg shadow-lg border border-slate-700/50"
          >
            <Menu size={18} />
          </button>
        )}

        {/* Session Setup Overlay */}
        {!sessionId && (
          <div className="absolute inset-0 z-10 bg-slate-900 flex items-center justify-center">
            <div className="glass-panel p-8 rounded-xl max-w-md w-full text-center">
              <Bot className="w-16 h-16 text-indigo-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">AI Data Assistant</h2>
              <p className="text-slate-400 mb-6">Select a dataset to begin a conversational analysis session.</p>
              
              <div className="mb-6">
                <select 
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  {datasets.length === 0 && <option value="">No datasets available</option>}
                  {datasets.map(d => (
                    <option key={d.id} value={d.id}>{d.file_name || d.name || 'Dataset ' + d.id}</option>
                  ))}
                </select>
              </div>
              
              <button 
                onClick={handleStartSession}
                disabled={!selectedDataset}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-lg font-medium disabled:opacity-50 transition-colors"
              >
                Start Chat
              </button>
            </div>
          </div>
        )}

        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.map((msg, idx) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={idx} 
              className={`flex gap-4 max-w-4xl mx-auto w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center shrink-0 border border-indigo-500/30">
                  <Bot size={18} className="text-indigo-400" />
                </div>
              )}
              
              <div className="flex flex-col gap-2 max-w-[85%]">
                <div className={`rounded-2xl p-4 ${
                  msg.role === 'user' 
                    ? 'bg-indigo-600 text-white rounded-br-none' 
                    : 'bg-transparent text-slate-200 prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-td:border-slate-700 prose-th:border-slate-700 prose-table:border-collapse'
                }`}>
                  {msg.role === 'user' ? (
                    <span className="whitespace-pre-wrap">{msg.content}</span>
                  ) : (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  )}
                </div>

                {/* Follow up question chips */}
                {msg.role === 'assistant' && msg.follow_up_questions && msg.follow_up_questions.length > 0 && idx === messages.length - 1 && !isStreaming && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.25 }}
                    className="mt-3"
                  >
                    <p className="text-xs text-slate-500 mb-2 flex items-center gap-1">
                      <Sparkles size={11} className="text-indigo-400" />
                      Suggested follow-ups
                    </p>
                    <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide flex-wrap">
                      {msg.follow_up_questions
                        .filter(q => !askedQuestions.has(q.trim()))
                        .map((q, qIdx) => {
                          const chipStyle = getChipStyle(q);
                          return (
                            <motion.button
                              key={qIdx}
                              initial={{ opacity: 0, scale: 0.85 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.1 + qIdx * 0.07 }}
                              whileHover={{ scale: 1.03, y: -1 }}
                              whileTap={{ scale: 0.97 }}
                              onClick={() => handleSendMessage(q)}
                              className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full border whitespace-nowrap transition-all font-medium shadow-sm ${chipStyle}`}
                            >
                              {getChipIcon(q)}
                              {q}
                            </motion.button>
                          );
                        })}
                    </div>
                  </motion.div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0">
                  <User size={18} className="text-slate-300" />
                </div>
              )}
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Box */}
        <div className="p-4 border-t border-slate-700/50 bg-slate-900 w-full">
          <div className="max-w-4xl mx-auto relative bg-slate-800 rounded-xl border border-slate-700 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-all overflow-hidden flex items-end shadow-lg">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              disabled={isStreaming || !sessionId}
              placeholder={isStreaming ? "AI is typing..." : "Ask about your data (Shift+Enter for new line)..."}
              className="w-full bg-transparent text-white pl-4 pr-12 py-4 max-h-48 resize-none focus:outline-none disabled:opacity-50"
              rows={1}
            />
            <button
              onClick={() => handleSendMessage(input)}
              disabled={!input.trim() || isStreaming || !sessionId}
              className="absolute right-2 bottom-2 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-lg flex items-center justify-center text-white transition-colors"
            >
              {isStreaming ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
            </button>
          </div>
          <div className="text-center mt-2">
            <p className="text-xs text-slate-500">AI can make mistakes. Verify important data insights.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
