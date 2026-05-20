"""
chat_router.py
==============
Central router for the Youth Financial Guardian Chatbot AI modules.

Responsibilities:
- Route user queries to appropriate financial modules based on detected situation
- Maintain conversation history and context
- Orchestrate responses from multiple AI modules
- Handle crisis detection and escalation
- Provide structured, context-aware responses

Author: Youth Financial Guardian Project
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from llm_engine import (
    get_advice,
    build_messages_with_history,
    generate_with_retry,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    LLMError,
)
from situation_detector import (
    detect_situation,
    PATH_BETTING,
    PATH_DEBT,
    PATH_EXPENSE,
    PATH_INVEST,
    PATH_LEGAL,
    PATH_ZERO_INVESTMENT,
    PATH_MENTAL_HEALTH,
    PATH_UNKNOWN,
)
from crisis_detector import detect_crisis

# Optional module integrations
try:
    from betting_alternative import assess_betting_behavior
    BETTING_MODULE_AVAILABLE = True
except ImportError:
    BETTING_MODULE_AVAILABLE = False

try:
    from debt_handler import calculate_debt_burden, create_repayment_plan
    DEBT_MODULE_AVAILABLE = True
except ImportError:
    DEBT_MODULE_AVAILABLE = False

try:
    from earn_suggester import suggest_earning
    EARN_MODULE_AVAILABLE = True
except ImportError:
    EARN_MODULE_AVAILABLE = False

try:
    from investment_guide import recommend_investments
    INVEST_MODULE_AVAILABLE = True
except ImportError:
    INVEST_MODULE_AVAILABLE = False

try:
    from emergency_fund import calculate_emergency_fund
    EMERGENCY_MODULE_AVAILABLE = True
except ImportError:
    EMERGENCY_MODULE_AVAILABLE = False

try:
    from goal_tracker import create_goal, check_progress
    GOAL_MODULE_AVAILABLE = True
except ImportError:
    GOAL_MODULE_AVAILABLE = False

try:
    from mental_health_gaurdian import assess_mental_health
    MENTAL_HEALTH_MODULE_AVAILABLE = True
except ImportError:
    MENTAL_HEALTH_MODULE_AVAILABLE = False

try:
    from legal_protector import assess_legal_situation
    LEGAL_MODULE_AVAILABLE = True
except ImportError:
    LEGAL_MODULE_AVAILABLE = False

try:
    from analyzer import analyze_spending
    ANALYZER_MODULE_AVAILABLE = True
except ImportError:
    ANALYZER_MODULE_AVAILABLE = False

# ─── Setup Logging ──────────────────────────────────────────
logger = logging.getLogger(__name__)


# ─── Data Structures ────────────────────────────────────────

class ResponseType(Enum):
    """Classification of response type for UI rendering."""
    CRISIS = "crisis"              # Immediate mental health crisis
    DEBT_GUIDANCE = "debt_guidance"  # Debt & loan handling
    EARNING_TIP = "earning_tip"     # Income generation strategies
    INVESTMENT = "investment"       # Investment recommendations
    MENTAL_HEALTH = "mental_health" # Mental health support
    LEGAL = "legal"                 # Legal protection guidance
    BETTING_HELP = "betting_help"   # Gambling alternative
    EXPENSE_TRACKING = "expense_tracking"  # Expense analysis
    GENERAL_ADVICE = "general_advice"      # Generic financial advice
    CLARIFICATION = "clarification"        # Need more info


@dataclass
class ChatMessage:
    """Single message in conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[float] = None
    path: Optional[str] = None  # Detected situation path


@dataclass
class RouterResponse:
    """Structured response from the chat router."""
    message: str
    response_type: ResponseType
    path: Optional[str] = None  # Which situation path was triggered
    crisis_level: Optional[str] = None  # If crisis detected
    follow_up_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Module-specific data


@dataclass
class UserContext:
    """Persistent user context across conversation."""
    income: float = 0.0
    monthly_expenses: float = 0.0
    savings_rate: float = 0.0
    debt_amount: float = 0.0
    has_emergency_fund: bool = False
    goals: List[str] = field(default_factory=list)
    identified_issues: List[str] = field(default_factory=list)  # Detected issues


# ─── Chat Router Class ──────────────────────────────────────

class ChatRouter:
    """
    Main orchestrator for routing user queries to appropriate AI modules.
    
    Usage:
        router = ChatRouter()
        response = await router.process_message(
            user_message="I lost ₹5000 on Dream11 last month",
            context=UserContext(income=30000)
        )
    """

    def __init__(
        self,
        provider: str = DEFAULT_PROVIDER,
        model: str = DEFAULT_MODEL,
        max_history: int = 10,
    ):
        self.provider = provider
        self.model = model
        self.max_history = max_history
        self.chat_history: List[ChatMessage] = []
        self.user_context = UserContext()
        
        logger.info(
            f"ChatRouter initialized with provider={provider}, model={model}"
        )

    def set_user_context(self, context: UserContext) -> None:
        """Update user context (income, expenses, etc.)."""
        self.user_context = context
        logger.info(f"User context updated: {context}")

    def add_to_history(self, message: ChatMessage) -> None:
        """Add message to conversation history."""
        self.chat_history.append(message)
        
        # Keep history size bounded
        if len(self.chat_history) > self.max_history * 2:
            self.chat_history = self.chat_history[-self.max_history:]

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.chat_history.clear()
        logger.info("Chat history cleared")

    def _get_relevant_history(self, num_messages: int = 5) -> List[Dict[str, str]]:
        """Get last N messages in LLM format."""
        messages = []
        for msg in self.chat_history[-num_messages:]:
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    def _detect_situation(self, user_message: str) -> Optional[str]:
        """
        Detect user's financial situation using situation_detector.
        Returns PATH constant.
        """
        try:
            detection = detect_situation(user_message)
            path = detection.path
            logger.info(f"Detected situation path: {path}")
            return path
        except Exception as e:
            logger.warning(f"Situation detection failed: {e}")
            return None

    def _detect_crisis(self, user_message: str) -> Optional[str]:
        """
        Check for immediate crisis indicators.
        Returns crisis level string (Emergency, Alert, Watch, or None).
        """
        try:
            crisis_result = detect_crisis(
                income=self.user_context.income,
                expenses=self._expenses_dict(),
                debt=self.user_context.debt_amount,
                text=user_message
            )
            level = crisis_result.get("level", "Normal")
            
            if level in ("Emergency", "Immediate Crisis"):
                logger.warning(f"CRISIS DETECTED: {crisis_result.get('alerts', [])}")
                return "Emergency"
            elif level in ("Alert", "Medium Risk"):
                return "Alert"
            elif level == "Watch":
                return "Watch"
            else:
                return None
        except Exception as e:
            logger.warning(f"Crisis detection failed: {e}")
            return None
    
    def _expenses_dict(self) -> dict:
        """Convert expenses to a dict format for crisis detector."""
        return {
            "food": 0,
            "transport": 0,
            "education": 0,
            "utilities": 0,
            "entertainment": 0,
            "shopping": 0,
            "health": 0,
            "debt": 0,
            "savings": 0,
            "insurance": 0,
        }

    def _generate_crisis_response(self, user_message: str) -> RouterResponse:
        """Generate immediate crisis support response."""
        crisis_response = (
            "I'm concerned about what you shared. Your wellbeing is important.\n\n"
            "**Immediate Support Resources:**\n"
            "🆘 National Suicide Prevention Lifeline: +1-800-273-8255\n"
            "🇮🇳 India Suicide Prevention: AAFT 9820466726\n"
            "💚 Vandrevala Foundation: 9999 666 555\n"
            "💬 iCall: 9152987821\n\n"
            "Please reach out to someone you trust right now. Your life matters, "
            "and there is always hope. Would you like to discuss a specific issue "
            "after you've connected with support?"
        )
        
        return RouterResponse(
            message=crisis_response,
            response_type=ResponseType.CRISIS,
            crisis_level="Immediate Crisis",
            follow_up_suggestions=[
                "Talk to a trusted friend or family member",
                "Contact a mental health professional",
                "Call a crisis helpline immediately"
            ]
        )

    def _route_to_debt_handler(self, user_message: str) -> Optional[str]:
        """Route to debt handling module."""
        if not DEBT_MODULE_AVAILABLE:
            return None
        
        try:
            # Extract debt info and create guidance
            guidance = (
                "Based on your debt situation, here are steps to get relief:\n\n"
                "1. **List all debts** — loan apps, personal loans, credit cards\n"
                "2. **Calculate total burden** — interest rates and due dates\n"
                "3. **Create repayment plan** — pay high-interest first\n"
                "4. **Know your rights** — RBI sachet protects you\n"
                "5. **Report harassment** — don't pay illegal fees/threats\n\n"
                "Would you like help creating a specific repayment plan?"
            )
            return guidance
        except Exception as e:
            logger.error(f"Debt handler routing failed: {e}")
            return None

    def _route_to_betting_helper(self, user_message: str) -> Optional[str]:
        """Route to betting/gambling alternatives module."""
        if not BETTING_MODULE_AVAILABLE:
            return None
        
        try:
            guidance = (
                "I understand the draw of fantasy apps and sports betting. "
                "Here's a better path:\n\n"
                "**Why these apps are rigged:**\n"
                "- Odds favor the platform (house edge 15-30%)\n"
                "- Pro players dominate daily fantasy\n"
                "- You lose more over time\n\n"
                "**Profitable alternatives:**\n"
                "- Freelancing (₹500-2000/day) — Upwork, Fiverr\n"
                "- Content creation (YouTube, TikTok)\n"
                "- Skill building (coding, design)\n\n"
                "Let's build a real earning plan instead. What skills do you have?"
            )
            return guidance
        except Exception as e:
            logger.error(f"Betting helper routing failed: {e}")
            return None

    def _route_to_earning_suggester(self, user_message: str) -> Optional[str]:
        """Route to earning/income generation module."""
        if not EARN_MODULE_AVAILABLE:
            return None
        
        try:
            income = self.user_context.income
            guidance = (
                f"Based on your current income (₹{income}/month), here are ways to earn more:\n\n"
                "**Quick wins (₹500-2000/week):**\n"
                "- Social media management for local businesses\n"
                "- Data entry work\n"
                "- Content writing\n\n"
                "**Medium term (₹2000-10000/month):**\n"
                "- Freelance coding/design\n"
                "- Online tutoring\n"
                "- Virtual assistant work\n\n"
                "What skills or time do you have available?"
            )
            return guidance
        except Exception as e:
            logger.error(f"Earning suggester routing failed: {e}")
            return None

    def _route_to_investment_guide(self, user_message: str) -> Optional[str]:
        """Route to investment guidance module."""
        if not INVEST_MODULE_AVAILABLE:
            return None
        
        try:
            guidance = (
                "Great! You're ready to grow your wealth. Here's a safe path:\n\n"
                "**Step 1: Emergency Fund** — 3-6 months of expenses\n"
                "**Step 2: Tax-advantaged** — PPF (7.1% guaranteed), Sukanya Samriddhi\n"
                "**Step 3: Index Funds** — NIFTY 50, Sensex (passive, low-cost)\n"
                "**Step 4: Diversify** — Mix of debt & equity\n\n"
                "**Avoid these mistakes:**\n"
                "- Don't invest if you have high-interest debt\n"
                "- Avoid individual stocks if new to markets\n"
                "- Don't time the market — invest consistently\n\n"
                "How much can you invest monthly?"
            )
            return guidance
        except Exception as e:
            logger.error(f"Investment guide routing failed: {e}")
            return None

    def _route_to_legal_helper(self, user_message: str) -> Optional[str]:
        """Route to legal protection module."""
        if not LEGAL_MODULE_AVAILABLE:
            return None
        
        try:
            guidance = (
                "Your rights are protected. Here's what you need to know:\n\n"
                "**Illegal practices by loan apps:**\n"
                "- Accessing your contacts without consent (DPDPA 2023 violation)\n"
                "- Threatening family members (Harassment Act)\n"
                "- High penalty fees (RBI caps at 2%)\n"
                "- Interest rate >36% (Usury Act violation)\n\n"
                "**Your protections:**\n"
                "- File complaint on RBI SACHET\n"
                "- Report to NCRP (Nodal Cyber Crime)\n"
                "- Reach out to NCLAT (Consumer Protection)\n\n"
                "Would you like help filing a complaint?"
            )
            return guidance
        except Exception as e:
            logger.error(f"Legal helper routing failed: {e}")
            return None

    async def process_message(
        self,
        user_message: str,
        context: Optional[UserContext] = None,
    ) -> RouterResponse:
        """
        Main entry point for processing user messages.
        
        Args:
            user_message: User's input query
            context: Optional user context (income, expenses, etc.)
            
        Returns:
            RouterResponse with message, type, and metadata
        """
        if context:
            self.set_user_context(context)
        
        # Add user message to history
        user_msg = ChatMessage(role="user", content=user_message)
        self.add_to_history(user_msg)
        
        logger.info(f"Processing message: {user_message[:100]}...")
        
        # ✅ Step 1: Check for immediate crisis (highest priority)
        crisis_level = self._detect_crisis(user_message)
        if crisis_level == "Immediate Crisis":
            response = self._generate_crisis_response(user_message)
            self.add_to_history(
                ChatMessage(role="assistant", content=response.message, path=PATH_MENTAL_HEALTH)
            )
            return response
        
        # ✅ Step 2: Detect situation path
        path = self._detect_situation(user_message)
        
        # ✅ Step 3: Route to appropriate handler
        routed_response = None
        response_type = ResponseType.GENERAL_ADVICE
        
        if path == PATH_DEBT:
            routed_response = self._route_to_debt_handler(user_message)
            response_type = ResponseType.DEBT_GUIDANCE
            
        elif path == PATH_BETTING:
            routed_response = self._route_to_betting_helper(user_message)
            response_type = ResponseType.BETTING_HELP
            
        elif path == PATH_ZERO_INVESTMENT:
            routed_response = self._route_to_earning_suggester(user_message)
            response_type = ResponseType.EARNING_TIP
            
        elif path == PATH_INVEST:
            routed_response = self._route_to_investment_guide(user_message)
            response_type = ResponseType.INVESTMENT
            
        elif path == PATH_LEGAL:
            routed_response = self._route_to_legal_helper(user_message)
            response_type = ResponseType.LEGAL
            
        elif path == PATH_MENTAL_HEALTH:
            response_type = ResponseType.MENTAL_HEALTH
            
        elif path == PATH_EXPENSE:
            response_type = ResponseType.EXPENSE_TRACKING
            
        elif path == PATH_UNKNOWN:
            response_type = ResponseType.CLARIFICATION
        
        # ✅ Step 4: Use LLM to generate response if no routed response
        if routed_response:
            final_message = routed_response
        else:
            try:
                history = self._get_relevant_history(num_messages=3)
                messages = build_messages_with_history(
                    user_message=user_message,
                    chat_history=history,
                    income=self.user_context.income,
                    savings_rate=self.user_context.savings_rate,
                )
                
                final_message = generate_with_retry(
                    provider=self.provider,
                    model=self.model,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7,
                )
            except LLMError as e:
                logger.error(f"LLM generation failed: {e}")
                final_message = (
                    "I apologize, I'm having trouble processing your request right now. "
                    "Please try again in a moment."
                )
        
        # ✅ Step 5: Create response object
        response = RouterResponse(
            message=final_message,
            response_type=response_type,
            path=path,
            crisis_level=crisis_level,
        )
        
        # Add assistant response to history
        self.add_to_history(
            ChatMessage(
                role="assistant",
                content=final_message,
                path=path
            )
        )
        
        return response

    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation so far."""
        if not self.chat_history:
            return "No messages yet."
        
        summary_points = []
        detected_paths = set()
        
        for msg in self.chat_history:
            if msg.path:
                detected_paths.add(msg.path)
        
        if detected_paths:
            summary_points.append(f"Detected issues: {', '.join(detected_paths)}")
        
        summary_points.append(f"Messages exchanged: {len(self.chat_history)}")
        
        return " | ".join(summary_points)


# ─── Utility Functions ──────────────────────────────────────

def create_router(
    provider: str = DEFAULT_PROVIDER,
    model: str = DEFAULT_MODEL,
) -> ChatRouter:
    """Factory function to create a new ChatRouter instance."""
    return ChatRouter(provider=provider, model=model)


async def route_user_query(
    user_message: str,
    context: Optional[UserContext] = None,
    router: Optional[ChatRouter] = None,
) -> RouterResponse:
    """
    Convenience function for one-off query routing.
    
    Usage:
        response = await route_user_query(
            "I lost ₹5000 on Dream11",
            context=UserContext(income=30000)
        )
    """
    if router is None:
        router = create_router()
    
    return await router.process_message(user_message, context)
