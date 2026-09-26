import re
from typing import Tuple, Optional, List, Dict, Any
from app.models.state import StructuredState, FieldStatus


class ContradictionService:
    @staticmethod
    def is_explicit_correction(user_message: str) -> bool:
        """Check if user message explicitly signals an intentional correction or change"""
        correction_patterns = [
            r"\bactually\b",
            r"\binstead of\b",
            r"\brather than\b",
            r"\bchange (my|the|it)\b",
            r"\bcorrect (my|that|it)\b",
            r"\bupdate (my|the|it)\b",
            r"\bmake that\b",
            r"\bi meant\b",
            r"\bmy mistake\b",
            r"\breplace\b",
            r"\bnot .+ but\b",
            r"\bno, it'?s\b",
        ]
        message_lower = user_message.lower()
        for pattern in correction_patterns:
            if re.search(pattern, message_lower):
                return True
        return False

    @classmethod
    def check_for_contradictions(
        cls,
        current_state: StructuredState,
        candidate_updates: Dict[str, Any],
        user_message: str,
        is_gemini_correction: bool = False
    ) -> Tuple[bool, Optional[str], List[str], Dict[str, Any]]:
        """
        Evaluates proposed updates and user message against current state.
        Returns:
            (has_contradiction, clarification_question, suggested_quick_replies, filtered_updates)
        """
        is_correction = is_gemini_correction or cls.is_explicit_correction(user_message)

        # If the user explicitly stated it's a correction, accept it directly
        if is_correction:
            return False, None, [], candidate_updates

        msg_lower = user_message.lower()

        # 1. Contradiction: Previously stated has_children = False, but now provided children or mentioned son/daughter
        if current_state.has_children is False:
            new_has_children = candidate_updates.get("has_children")
            new_children = candidate_updates.get("children", [])
            child_mentions = re.search(r"\b(my son|my daughter|my child|my children)\b(?:\s+([a-zA-Z]+))?", msg_lower)

            if new_has_children is True or (new_children and len(new_children) > 0) or child_mentions:
                mentioned_name = ""
                if new_children:
                    mentioned_name = ", ".join(new_children)
                elif child_mentions and child_mentions.group(2):
                    mentioned_name = f"your child {child_mentions.group(2).capitalize()}"
                elif child_mentions:
                    mentioned_name = child_mentions.group(1)
                else:
                    mentioned_name = "children"

                question = (
                    f"Earlier you indicated that you do not have children, but you've now mentioned "
                    f"{mentioned_name}. Which information should I record?"
                )
                quick_replies = [
                    f"Yes, I have children",
                    "No, I do not have children"
                ]
                filtered = {k: v for k, v in candidate_updates.items() if k not in ["has_children", "children"]}
                return True, question, quick_replies, filtered

        # 2. Contradiction: Previously stated has_children = True with children, but now says has_children = False
        if current_state.has_children is True and current_state.children:
            new_has_children = candidate_updates.get("has_children")
            if new_has_children is False:
                existing_names = ", ".join(current_state.children)
                question = (
                    f"Earlier you mentioned your children ({existing_names}), but now stated you do not have children. "
                    f"Would you like to remove your children from the record, or keep them?"
                )
                quick_replies = [
                    f"Keep my children ({existing_names})",
                    "Remove children from document"
                ]
                filtered = {k: v for k, v in candidate_updates.items() if k != "has_children"}
                return True, question, quick_replies, filtered

        # 3. Contradiction: Executor change without explicit correction cue
        if current_state.executor.name and "executor" in candidate_updates:
            new_exec = candidate_updates.get("executor") or {}
            new_name = new_exec.get("name")
            if new_name and new_name.lower().strip() != current_state.executor.name.lower().strip():
                existing_name = current_state.executor.name
                question = (
                    f"You previously designated {existing_name} as your executor, but have now named {new_name}. "
                    f"Would you like to replace {existing_name} with {new_name} as your executor?"
                )
                quick_replies = [
                    f"Yes, set {new_name} as executor",
                    f"No, keep {existing_name} as executor"
                ]
                filtered = {k: v for k, v in candidate_updates.items() if k != "executor"}
                return True, question, quick_replies, filtered

        # 4. Contradiction: Worldwide assets coverage change without cue
        if current_state.covers_worldwide_assets is not None and "covers_worldwide_assets" in candidate_updates:
            new_worldwide = candidate_updates.get("covers_worldwide_assets")
            if new_worldwide is not None and new_worldwide != current_state.covers_worldwide_assets:
                old_desc = "worldwide assets" if current_state.covers_worldwide_assets else "domestic assets only"
                new_desc = "worldwide assets" if new_worldwide else "domestic assets only"
                question = (
                    f"You previously chose to cover {old_desc}, but just indicated {new_desc}. "
                    f"Which scope would you like your document to cover?"
                )
                quick_replies = [
                    "Cover worldwide assets",
                    "Cover domestic assets only"
                ]
                filtered = {k: v for k, v in candidate_updates.items() if k != "covers_worldwide_assets"}
                return True, question, quick_replies, filtered

        return False, None, [], candidate_updates
