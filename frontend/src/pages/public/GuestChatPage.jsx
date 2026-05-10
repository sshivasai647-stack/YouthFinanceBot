import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Sparkles, LogIn } from 'lucide-react'
import { guestApi } from '../../api/guest'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function GuestChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm YF-AI, your financial wellness assistant. I can help with budgeting, debt, savings goals, and more. What's on your mind? 💸",
    },
  ])
  const [input,   setInput]   = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(e) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input.trim() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await guestApi.chat({ message: userMsg.content })
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.data.response },
      ])
    } catch (err) {
      if (err.response?.status === 429) {
        toast.error('Guest limit reached. Please create a free account!')
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: "You've reached the guest message limit. Create a free account to continue! 🚀",
          },
        ])
      } else {
        toast.error('Something went wrong')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col h-[85vh]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-900 dark:text-white">
              YF-AI Guest Chat
            </h1>
            <p className="text-xs text-slate-500">5 free messages · No signup needed</p>
          </div>
        </div>
        <Link to="/register" className="btn-primary text-sm flex items-center gap-2">
          <LogIn size={15} />
          Sign Up Free
        </Link>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center
                              justify-center text-sm
                              ${msg.role === 'assistant'
                                ? 'bg-primary text-white'
                                : 'bg-slate-200 text-slate-600'}`}>
                {msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
              </div>

              {/* Bubble */}
              <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed
                              ${msg.role === 'assistant'
                                ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 shadow-card'
                                : 'bg-primary text-white'}`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading bubble */}
        {loading && (
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
          placeholder="Ask about budgeting, debt, savings..."
          className="input flex-1"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary px-4 py-2.5 flex items-center gap-2"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}