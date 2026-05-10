import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  MessageCircle, Target, CreditCard, TrendingUp,
  Shield, Users, ArrowRight, Sparkles
} from 'lucide-react'

const features = [
  {
    icon: MessageCircle,
    title: 'AI Financial Coach',
    desc: 'Chat with our AI trained on Indian financial laws, schemes, and youth challenges.',
    color: 'bg-purple-100 text-purple-600',
  },
  {
    icon: Target,
    title: 'Goal Optimizer',
    desc: 'Set savings goals and get an AI-powered monthly plan to achieve them.',
    color: 'bg-blue-100 text-blue-600',
  },
  {
    icon: CreditCard,
    title: 'Debt Manager',
    desc: 'Analyse your loans, calculate EMIs, and get debt payoff strategies.',
    color: 'bg-green-100 text-green-600',
  },
  {
    icon: TrendingUp,
    title: 'Spending Analyser',
    desc: 'Upload your spending data and get AI insights on where your money goes.',
    color: 'bg-yellow-100 text-yellow-600',
  },
  {
    icon: Shield,
    title: 'Betting Risk Detector',
    desc: 'Understand the real financial risk of gambling and betting apps.',
    color: 'bg-red-100 text-red-600',
  },
  {
    icon: Users,
    title: 'Counsellor Connect',
    desc: 'Get matched with a real financial counsellor for personalised help.',
    color: 'bg-pink-100 text-pink-600',
  },
]

const stats = [
  { value: '10K+', label: 'Youth Helped' },
  { value: '₹2Cr+', label: 'Debt Resolved' },
  { value: '500+', label: 'Counsellors' },
  { value: '4.9★', label: 'App Rating' },
]

export default function LandingPage() {
  return (
    <div className="overflow-x-hidden">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center justify-center
                          bg-gradient-to-br from-primary-50 via-white to-blue-50
                          dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
        {/* Background blobs */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary-200 rounded-full
                        blur-3xl opacity-30 animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-200 rounded-full
                        blur-3xl opacity-20 animate-pulse" />

        <div className="relative max-w-4xl mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full
                             bg-primary-100 text-primary-700 text-sm font-medium mb-6">
              <Sparkles size={14} />
              AI-Powered Financial Wellness for Indian Youth
            </span>

            <h1 className="text-5xl md:text-7xl font-extrabold text-slate-900
                           dark:text-white leading-tight mb-6">
              Take Control of
              <span className="text-transparent bg-clip-text
                               bg-gradient-to-r from-primary to-blue-500">
                {' '}Your Money
              </span>
            </h1>

            <p className="text-xl text-slate-600 dark:text-slate-300 max-w-2xl
                          mx-auto mb-10 leading-relaxed">
              Get personalised financial guidance, manage debt, set goals,
              and connect with counsellors — all in one place.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/register" className="btn-primary text-base px-8 py-3
                                              flex items-center gap-2">
                Get Started Free
                <ArrowRight size={18} />
              </Link>
              <Link to="/guest" className="btn-secondary text-base px-8 py-3">
                Try as Guest
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-white dark:bg-slate-800">
        <div className="max-w-5xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <p className="text-4xl font-extrabold text-primary mb-1">
                  {stat.value}
                </p>
                <p className="text-slate-500 text-sm">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-slate-50 dark:bg-slate-900">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-4">
              Everything you need
            </h2>
            <p className="text-slate-500 text-lg max-w-xl mx-auto">
              Powerful tools designed specifically for young Indians navigating
              financial challenges.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="card hover:scale-[1.02] transition-transform cursor-default"
              >
                <div className={`w-12 h-12 rounded-xl ${f.color}
                                 flex items-center justify-center mb-4`}>
                  <f.icon size={22} />
                </div>
                <h3 className="font-bold text-lg text-slate-900 dark:text-white mb-2">
                  {f.title}
                </h3>
                <p className="text-slate-500 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-gradient-to-r from-primary to-blue-500">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-extrabold text-white mb-4">
              Ready to start your journey?
            </h2>
            <p className="text-primary-100 text-lg mb-8">
              Join thousands of young Indians building better financial habits.
            </p>
            <Link
              to="/register"
              className="inline-flex items-center gap-2 bg-white text-primary
                         font-bold px-8 py-3 rounded-xl hover:bg-primary-50
                         transition-colors duration-200"
            >
              Create Free Account
              <ArrowRight size={18} />
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  )
}