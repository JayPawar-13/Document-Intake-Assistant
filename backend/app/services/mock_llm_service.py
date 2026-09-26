import re
from typing import List, Dict, Any, Optional
from app.models.gemini import (
    GeminiExtractionResult,
    ExtractedInformation,
    ExecutorExtraction,
    GiftExtraction,
    UserIntent,
)
from app.models.state import StructuredState, SpecificGift
from app.services.contradiction_service import ContradictionService
from app.services.interview_controller import QUESTION_MAP


class MockLLMService:
    """
    Deterministic mock LLM engine that accurately simulates the Gemini extraction pipeline
    when GEMINI_API_KEY is not configured or in automated tests.
    """

    @classmethod
    async def process_message(
        cls,
        message: str,
        conversation_history: List[Dict[str, str]],
        structured_state: StructuredState,
        last_question: Optional[str] = None
    ) -> GeminiExtractionResult:
        cleaned_msg = message.strip()
        msg_lower = cleaned_msg.lower()

        # Find last assistant message if not passed
        if not last_question:
            last_question = cls._get_last_assistant_msg(conversation_history)

        last_q_lower = (last_question or "").lower()

        # -------------------------------------------------------------
        # 1. Irrelevant / Nonsense Answer Detection (Section 14 & 20)
        # -------------------------------------------------------------
        irrelevant_phrases = [
            "favorite color", "like playing cricket", "like football", "play football",
            "weather is nice", "like pizza", "i like blue", "my dog", "my cat"
        ]
        if any(irr in msg_lower for irr in irrelevant_phrases):
            target_field = "home_address" if "address" in last_q_lower else ("has_children" if "children" in last_q_lower else "full_name")
            return GeminiExtractionResult(
                status="invalid",
                user_intent=UserIntent.IRRELEVANT,
                extracted_information=ExtractedInformation(),
                invalid_fields=[target_field],
                clarification_needed=False,
                assistant_message=f"Thanks! I still need your {target_field.replace('_', ' ')} to continue. Could you please provide that?",
                suggested_quick_replies=[]
            )

        # -------------------------------------------------------------
        # 2. Ambiguity & Unclear Response Handling (Section 15 & 17)
        # -------------------------------------------------------------
        ambiguity_cues = ["not sure", "don't know", "dont know", "maybe", "perhaps", "i'm unsure", "undecided", "someday"]
        if any(cue in msg_lower for cue in ambiguity_cues):
            if "children" in last_q_lower or "child" in last_q_lower:
                return GeminiExtractionResult(
                    status="ambiguous",
                    user_intent=UserIntent.AMBIGUOUS,
                    extracted_information=ExtractedInformation(),
                    ambiguous_fields=["has_children"],
                    clarification_needed=True,
                    clarification_reason="Just to confirm, do you currently have any children, or should I record this as 'No' for now?",
                    clarification_question="Just to confirm, do you currently have any children, or should I record this as 'No' for now?",
                    assistant_message="Just to confirm, do you currently have any children, or should I record this as 'No' for now?",
                    suggested_quick_replies=[
                        "No, I do not have children",
                        "Yes, I have children"
                    ]
                )
            elif "worldwide" in last_q_lower or "assets" in last_q_lower:
                return GeminiExtractionResult(
                    status="ambiguous",
                    user_intent=UserIntent.AMBIGUOUS,
                    extracted_information=ExtractedInformation(),
                    ambiguous_fields=["covers_worldwide_assets"],
                    clarification_needed=True,
                    clarification_reason="Could you clarify whether you would like this document to cover worldwide assets or domestic assets only?",
                    clarification_question="Could you clarify whether you would like this document to cover worldwide assets or domestic assets only?",
                    assistant_message="Could you clarify whether you would like this document to cover worldwide assets or domestic assets only?",
                    suggested_quick_replies=[
                        "Yes, cover worldwide assets",
                        "No, domestic assets only"
                    ]
                )

        # -------------------------------------------------------------
        # 3. Extraction - Multi-Field and Specific Extractions
        # -------------------------------------------------------------
        info = ExtractedInformation()
        is_correction = ContradictionService.is_explicit_correction(cleaned_msg)

        # Name
        name_patterns = [
            r"my name is ([a-zA-Z\s\.\-\']+?)(?:\.|\,|$|\band\b|\bmy\b|\bi\b)",
            r"i am ([a-zA-Z\s\.\-\']+?)(?:\.|\,|$|\band\b)",
            r"i'm ([a-zA-Z\s\.\-\']+?)(?:\.|\,|$|\band\b|\bi live\b)",
            r"^name:\s*([a-zA-Z\s\.\-\']+)$",
        ]
        for pat in name_patterns:
            m = re.search(pat, cleaned_msg, re.IGNORECASE)
            if m:
                extracted_name = m.group(1).strip()
                if len(extracted_name.split()) <= 4 and len(extracted_name) > 1:
                    info.full_name = extracted_name
                    break

        if not info.full_name and not structured_state.full_name:
            if "name" in last_q_lower and len(cleaned_msg.split()) <= 4 and not any(k in msg_lower for k in ["address", "live", "street", "child", "executor"]):
                info.full_name = cleaned_msg.strip(" .")

        # Address
        address_patterns = [
            r"i live at ([^\.\n]+?)(?:\.|$|\band\b|\byes\b|\bi don't\b|\bi have\b)",
            r"my (?:home )?address is ([^\.\n]+)",
            r"address:\s*([^\.\n]+)",
            r"(\d+[\w\s,]+(?:street|road|avenue|lane|close|way|drive|crescent|boulevard|london|manchester|birmingham|indore|madhya pradesh|uk|england)[^\.\n]*)",
        ]
        for pat in address_patterns:
            m = re.search(pat, cleaned_msg, re.IGNORECASE)
            if m:
                info.home_address = m.group(1).strip()
                break

        if not info.home_address and not structured_state.home_address:
            if "address" in last_q_lower and len(cleaned_msg) > 3 and not any(k in msg_lower for k in ["name is", "my brother"]):
                info.home_address = cleaned_msg.strip(" .")

        # Worldwide Assets
        if "worldwide" in msg_lower or "all assets" in msg_lower:
            if "not worldwide" in msg_lower or ("no" in msg_lower and "worldwide" in msg_lower and len(msg_lower.split()) < 4):
                info.covers_worldwide_assets = False
            else:
                info.covers_worldwide_assets = True
        elif msg_lower in ["yes", "yes please", "sure", "definitely", "yes it should"]:
            if "worldwide" in last_q_lower or "assets" in last_q_lower:
                info.covers_worldwide_assets = True
        elif msg_lower in ["no", "no thanks", "domestic only", "uk only", "no, only domestic"]:
            if "worldwide" in last_q_lower or "assets" in last_q_lower:
                info.covers_worldwide_assets = False

        # Children
        if any(neg in msg_lower for neg in ["no children", "don't have any children", "do not have children", "don't have children", "i have no children", "no, i do not have children", "i don't have kids"]):
            info.has_children = False
            info.children = []
        else:
            child_match = re.search(r"(?:have|got)\s+(?:two|three|four|\d+)?\s*children[,:\s]+([a-zA-Z\s,and]+)", cleaned_msg, re.IGNORECASE)
            if not child_match:
                child_match = re.search(r"my children\s+(?:are\s+)?([a-zA-Z\s,and]+)", cleaned_msg, re.IGNORECASE)
            if not child_match:
                child_match = re.search(r"children are\s+([a-zA-Z\s,and]+)", cleaned_msg, re.IGNORECASE)

            if child_match:
                raw_names = child_match.group(1).strip(" .")
                names = [n.strip() for n in re.split(r",|\band\b", raw_names) if n.strip() and n.strip().lower() not in ["my", "the", "are"]]
                if names:
                    info.has_children = True
                    info.children = names
            elif "children" in last_q_lower and msg_lower in ["yes", "yes i do", "yes, i have children"]:
                info.has_children = True

        # Executor & Relationship
        exec_match = re.search(r"my\s+([a-zA-Z]+)\s+([a-zA-Z\s]+?)\s+(?:should be|is|will be|to be)\s+(?:my\s+)?executor", cleaned_msg, re.IGNORECASE)
        if exec_match:
            rel = exec_match.group(1).strip()
            name = exec_match.group(2).strip()
            info.executor = ExecutorExtraction(name=name, relationship=rel)
        else:
            exec_simple = re.search(r"([a-zA-Z\s]+?)\s+(?:should be|is|will be)\s+(?:my\s+)?executor", cleaned_msg, re.IGNORECASE)
            if exec_simple:
                candidate_name = exec_simple.group(1).replace("actually,", "").replace("actually", "").strip()
                rel = None
                for r in ["sister", "brother", "friend", "spouse", "wife", "husband", "partner", "daughter", "son", "solicitor", "lawyer"]:
                    if r in msg_lower:
                        rel = r
                        break
                info.executor = ExecutorExtraction(name=candidate_name, relationship=rel)
            elif "executor" in last_q_lower and "name" in last_q_lower and len(cleaned_msg.split()) <= 4:
                info.executor = ExecutorExtraction(name=cleaned_msg.strip(" ."))
            elif "relationship" in last_q_lower:
                rel_val = cleaned_msg.strip(" .").lower()
                existing_name = structured_state.executor.name
                info.executor = ExecutorExtraction(name=existing_name, relationship=rel_val)

        is_answering_wishes = "wishes" in last_q_lower or "additional" in last_q_lower

        # Specific Gifts (Structured extraction: item, recipient_name, relationship, description)
        if not is_answering_wishes:
            if "no specific gifts" in msg_lower or "no gifts" in msg_lower or "i don't have any specific gifts" in msg_lower or "no, i don't have gifts" in msg_lower:
                info.has_no_gifts = True
            else:
                # Pattern: "I want my watch to go to my brother Rohit and my laptop to my sister Priya."
                gift_matches = re.finditer(r"(?:my\s+)?([a-zA-Z0-9\s]+?)\s+(?:to go to|to|goes to)\s+(?:my\s+([a-zA-Z]+)\s+)?([a-zA-Z\s]+?)(?=\.|\band\b|$)", cleaned_msg, re.IGNORECASE)
                extracted_gifts = []
                for gm in gift_matches:
                    item = gm.group(1).strip().replace("i want ", "").replace("i would like ", "")
                    rel = gm.group(2).strip() if gm.group(2) else None
                    recip = gm.group(3).strip() if gm.group(3) else None
                    if item and (recip or rel):
                        desc = f"My {item} to {f'my {rel} ' if rel else ''}{recip}.".strip()
                        extracted_gifts.append(GiftExtraction(
                            item=item,
                            recipient_name=recip,
                            relationship=rel,
                            description=desc
                        ))
                if extracted_gifts:
                    info.specific_gifts = extracted_gifts

        # Additional Wishes
        if is_answering_wishes or any(w in msg_lower for w in ["wishes", "books donated", "photograph", "photos", "cremated", "charity", "buried", "funeral"]):
            if "no additional wishes" in msg_lower or "no wishes" in msg_lower or "no, i don't" in msg_lower or msg_lower in ["no", "none", "nothing"]:
                info.has_no_additional_wishes = True
            else:
                wish_str = cleaned_msg.strip()
                if wish_str:
                    info.additional_wishes = [wish_str]

        # -------------------------------------------------------------
        # 4. Generate next assistant response based on state & next field
        # -------------------------------------------------------------
        # Determine next question preview
        target_name = info.full_name or structured_state.full_name
        next_q = "What is your full legal name?"
        quick_replies = []

        if not target_name:
            next_q = "What is your full legal name?"
        elif not (info.home_address or structured_state.home_address):
            next_q = f"Thanks, {target_name}. What is your current home address?"
        elif info.covers_worldwide_assets is None and structured_state.covers_worldwide_assets is None:
            next_q = "Should your document cover assets worldwide?"
            quick_replies = ["Yes, cover assets worldwide", "No, domestic assets only"]
        elif info.has_children is None and structured_state.has_children is None:
            next_q = "Do you currently have any children?"
            quick_replies = ["Yes, I have children", "No, I do not have children"]
        elif (info.has_children or structured_state.has_children) and not (info.children or structured_state.children):
            next_q = "What are your children's names?"
        elif not (info.executor and info.executor.name or structured_state.executor.name):
            next_q = "Who would you like to name as your executor?"
        elif not (info.executor and info.executor.relationship or structured_state.executor.relationship):
            exec_name = (info.executor and info.executor.name) or structured_state.executor.name
            next_q = f"What is your relationship with {exec_name}?"
            quick_replies = ["Brother", "Sister", "Spouse", "Friend"]
        elif not (info.specific_gifts or structured_state.specific_gifts or info.has_no_gifts):
            next_q = "Do you have any specific gifts you'd like to leave to particular people?"
            quick_replies = ["No specific gifts"]
        elif not (info.additional_wishes or structured_state.additional_wishes or info.has_no_additional_wishes):
            next_q = "Do you have any additional wishes you'd like to include?"
            quick_replies = ["No additional wishes"]
        else:
            next_q = "Great! We've collected all the information needed. Let's review everything before generating your document."

        return GeminiExtractionResult(
            status="valid",
            user_intent=UserIntent.ANSWER,
            extracted_information=info,
            ambiguous_fields=[],
            contradictory_fields=[],
            invalid_fields=[],
            clarification_needed=False,
            is_explicit_correction=is_correction,
            assistant_message=next_q,
            suggested_quick_replies=quick_replies
        )

    @staticmethod
    def _get_last_assistant_msg(history: List[Dict[str, str]]) -> str:
        for item in reversed(history):
            if item.get("role") == "assistant":
                return item.get("content", "")
        return ""
