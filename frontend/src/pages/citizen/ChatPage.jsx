import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { citizenApi } from '../../api/citizen'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Trash2, Sparkles } from 'lucide-react'
import { formatDate } from '../../lib/utils'
import toast from 'react-hot-toast'

export default function ChatPage() {
  const [input, setInput]   = useState('')
  const bottomRef           = useRef(null)
  const queryClient         = useQueryClient()

  const { data: history = [], isLoading } = useQuery({
    queryKey: ['chat-history'],
    queryFn:  () => citizenApi.chatHistory().then((r) => r.data.history ?? []),
  })

  const chatMutation = useMutation({
    mutationFn: (message) => citizenApi.chat({ message }),
    onSuccess: () => {
      queryClient.invalidateQueries(['chat-history'])
    },
    onError: (err) => {
      toast.error(err.response?.data?.error ?? 'Chat failed')
    },
  })

  const clearMutation = useMutation({
    mutationFn: () => citizenApi.clearHistory(),
    onSuccess: () => {
      queryClient.invalidateQueries(['chat-history'])
      toast.success('Chat history cleared')
    },
  })

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, chatMutation.isPending])

  async function sendMessage(e) {
    e.preventDefault()
    if (!input.trim() || chatMutation.isPending) return
    const msg = input.trim()
    setInput('')
    chatMutation.mutate(msg)
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-900 dark:text-white">
              YF-AI Chat
            </h1>
            <p className="text-xs text-slate-500">
              Powered by Claude · Unlimited messages
            </p>
          </div>
        </div>
        <button
          onClick={() => clearMutation.mutate()}
          disabled={clearMutation.isPending || history.length === 0}
          className="btn-ghost text-sm flex items-center gap-2 text-red-500
                     hover:bg-red-50 dark:hover:bg-red-900/20"
        >
          <Trash2 size={15} />
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {/* Welcome message */}
        {!isLoading && history.length === 0 && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-primary text-white
                            flex items-center justify-center flex-shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-white dark:bg-slate-800 px-4 py-3 rounded-2xl
                            shadow-card text-sm text-slate-800 dark:text-slate-100
                            max-w-[75%]">
              Hi! I'm YF-AI 👋 I can help with budgeting, debt management,
              savings goals, investment basics, and Indian government schemes.
              What would you like to know?
            </div>
          </div>
        )}

        <AnimatePresence initial={false}>
          {history.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center
                              justify-center
                              ${msg.role === 'assistant'
                                ? 'bg-primary text-white'
                                : 'bg-slate-200 text-slate-600'}`}>
                {msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
              </div>
              <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed
                              ${msg.role === 'assistant'
                                ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 shadow-card'
                                : 'bg-primary text-white'}`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.timestamp && (
                  <p className={`text-xs mt-1 opacity-60`}>
                    {formatDate(msg.timestamp)}
                  </p>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading bubble */}
        {chatMutation.isPending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-primary text-white
                            flex items-center justify-center flex-shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-white dark:bg-slate-800 px-4 py-3 rounded-2xl shadow-card">
              <div className="flex gap-1 items-center h-5">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-primary rounded-full"
                    animate={{ y: [0, -6, 0] }}
                    transition={{ repeat: Infinity, delay: i * 0.15, duration: 0.6 }}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="mt-4 flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about budgeting, debt, savings, schemes..."
          className="input flex-1"
          disabled={chatMutation.isPending}
        />
        <button
          type="submit"
          disabled={chatMutation.isPending || !input.trim()}
          className="btn-primary px-4 py-2.5"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}