from typing import Optional, Tuple, Dict, Any
from app.models.state import StructuredState, FieldStatus
from app.models.gemini import NextAction

QUESTION_MAP: Dict[str, str] = {
    "full_name": "What is your full name?",
    "home_address": "What is your home address?",
    "covers_worldwide_assets": "Should your document cover assets worldwide?",
    "has_children": "Do you currently have any children?",
    "children": "What are your children's names?",
    "executor.name": "Who would you like to name as your executor?",
    "executor.relationship": "What is your relationship with your executor?",
    "specific_gifts": "Do you have any specific gifts you'd like to leave to particular people?",
    "additional_wishes": "Do you have any additional wishes you'd like to include?"
}

ASSISTIVE_GUIDANCE_MAP: Dict[str, Dict[str, str]] = {
    "full_name": {
        "needed": "your full legal name",
        "guidance": "Please provide your full legal name, including your first and last name (for example, 'Aarya Sharma' or 'Johnathan Doe') so your document can identify you accurately.",
        "example": "Aarya Sharma"
    },
    "home_address": {
        "needed": "your current residential address",
        "guidance": "Please provide your residential address, including house/flat number, street name, and city (for example, '123 MG Road, Indore' or '21 High Street, London').",
        "example": "123 MG Road, Indore"
    },
    "covers_worldwide_assets": {
        "needed": "whether your document covers assets worldwide or domestic only",
        "guidance": "Please specify whether this document should cover assets worldwide (including international property) or only domestic assets. You can answer 'Yes' for worldwide or 'No' for domestic only.",
        "example": "Yes, worldwide"
    },
    "has_children": {
        "needed": "whether you currently have any living children",
        "guidance": "Please let me know if you currently have any children. You can answer 'Yes, I have children' or 'No, I don't have children'.",
        "example": "No, I do not have children"
    },
    "children": {
        "needed": "the names of your children",
        "guidance": "Please list the names of your children (for example: 'Sarah and Michael').",
        "example": "Sarah and Michael"
    },
    "executor.name": {
        "needed": "the name of your chosen executor",
        "guidance": "An executor is the trusted person responsible for administering your wishes. Please provide their full name, and optionally your relationship to them (for example, 'My brother Rohit Sharma').",
        "example": "Rohit Sharma"
    },
    "executor.relationship": {
        "needed": "your relationship to the executor",
        "guidance": "Please let me know how you are related to your executor (for example: brother, sister, spouse, child, friend, or solicitor).",
        "example": "brother"
    },
    "specific_gifts": {
        "needed": "any specific gifts or individual items to leave to particular people",
        "guidance": "Specific gifts are individual items (such as a watch, jewellery, or car) left to a specific named beneficiary (for example: 'My watch to my brother Rohit'). If you don't have any specific individual gifts, simply say 'No specific gifts'. Note: General donations and wishes are recorded separately in the next step.",
        "example": "My watch to my brother Rohit"
    },
    "additional_wishes": {
        "needed": "any additional wishes, donations, or funeral preferences",
        "guidance": "Additional wishes are general desires such as donating books to charity, funeral/memorial preferences, or personal messages (for example: 'I would like my books donated to the library and to be cremated'). If you have no additional wishes, simply say 'No additional wishes'. Note: These are separate from specific gifts.",
        "example": "I would like my books donated to charity"
    }
}

INTERVIEW_FIELD_ORDER = [
    "full_name",
    "home_address",
    "covers_worldwide_assets",
    "has_children",
    "children",
    "executor.name",
    "executor.relationship",
    "specific_gifts",
    "additional_wishes",
]


class InterviewController:
    """
    Deterministic backend interview controller.
    Ensures that backend business rules strictly control the conversation flow:
    - Never asks completed questions.
    - Handles out-of-order answers by dynamically calculating missing fields.
    - Resolves ambiguity and contradictions before proceeding.
    - Evaluates complete interview status without relying solely on LLM decisions.
    """

    @classmethod
    def get_fallback_question(cls, field: str) -> str:
        return QUESTION_MAP.get(field, "Could you please provide this information?")

    @classmethod
    def get_assistive_message(cls, field: str) -> str:
        guidance = ASSISTIVE_GUIDANCE_MAP.get(field)
        if guidance:
            return (
                f"I still need {guidance['needed']}. "
                f"{guidance['guidance']}"
            )
        target_name = field.replace('_', ' ')
        return f"Could you please clarify your {target_name}? Please provide the required information so we can record it accurately."

    @classmethod
    def determine_next_action_and_field(
        cls,
        state: StructuredState,
        active_clarification_field: Optional[str] = None
    ) -> Tuple[NextAction, Optional[str], str]:
        """
        Determines the next interview action, target field, and fallback question.
        Returns:
            (next_action, next_field, fallback_question)
        """
        # 1. Prioritize active clarification if a field is flagged as AMBIGUOUS or CONTRADICTORY
        if active_clarification_field:
            fallback_q = cls.get_fallback_question(active_clarification_field)
            return NextAction.ASK_CLARIFICATION, active_clarification_field, fallback_q

        for field in INTERVIEW_FIELD_ORDER:
            status = state.field_statuses.get(field, FieldStatus.UNKNOWN)
            if status in (FieldStatus.AMBIGUOUS, FieldStatus.CONTRADICTORY):
                fallback_q = cls.get_fallback_question(field)
                return NextAction.ASK_CLARIFICATION, field, fallback_q

        # 2. Iterate through canonical sequence to find first non-complete field
        for field in INTERVIEW_FIELD_ORDER:
            # Special case: children is NOT_APPLICABLE if has_children is False
            if field == "children":
                if state.has_children is False:
                    continue
                if state.has_children is None:
                    # Must ask has_children first
                    continue

            status = state.field_statuses.get(field, FieldStatus.UNKNOWN)
            if status not in (FieldStatus.CONFIRMED, FieldStatus.NOT_APPLICABLE):
                fallback_q = cls.get_fallback_question(field)
                return NextAction.ASK_NEXT_QUESTION, field, fallback_q

        # 3. All fields confirmed or not applicable: Interview Complete!
        completion_msg = "Great! We've collected all the information needed. Let's review everything before generating your document."
        return NextAction.INTERVIEW_COMPLETE, None, completion_msg

    @classmethod
    def calculate_progress(cls, state: StructuredState) -> Dict[str, int]:
        """Returns completed count and total applicable field count"""
        total = 0
        completed = 0
        for field in INTERVIEW_FIELD_ORDER:
            if field == "children" and state.has_children is False:
                continue
            total += 1
            status = state.field_statuses.get(field, FieldStatus.UNKNOWN)
            if status in (FieldStatus.CONFIRMED, FieldStatus.NOT_APPLICABLE):
                completed += 1

        return {
            "completed": completed,
            "total": total,
            "percentage": int((completed / total * 100)) if total > 0 else 100
        }
