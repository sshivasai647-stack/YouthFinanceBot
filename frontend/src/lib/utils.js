export function formatCurrency(amount) {
  if (amount == null) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getInitials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function crisisColor(level) {
  switch (level) {
    case 'HIGH':     return 'bg-red-100 text-red-700'
    case 'MEDIUM':   return 'bg-yellow-100 text-yellow-700'
    case 'LOW':      return 'bg-green-100 text-green-700'
    default:         return 'bg-slate-100 text-slate-700'
  }
}