from datetime import datetime
from typing import Dict, Any
from app.models.state import StructuredState


class DocumentService:
    @staticmethod
    def generate_document_text(state: StructuredState) -> str:
        """Generate structured text version of the Personal Wishes Document"""
        name = state.full_name or "[Full Name Not Provided]"
        address = state.home_address or "[Address Not Provided]"
        
        if state.covers_worldwide_assets is True:
            worldwide = "Yes - This document governs assets situated both in the United Kingdom and worldwide."
        elif state.covers_worldwide_assets is False:
            worldwide = "No - This document is strictly limited to assets located in the primary jurisdiction."
        else:
            worldwide = "[Jurisdiction Scope Not Provided]"

        # Family
        if state.has_children is True:
            children_str = f"Yes, children identified:\n  - " + "\n  - ".join(state.children) if state.children else "Yes, but names not yet provided."
        elif state.has_children is False:
            children_str = "No children recorded."
        else:
            children_str = "[Family details not provided]"

        # Executor
        exec_name = state.executor.name or "[Executor Name Not Provided]"
        exec_rel = state.executor.relationship or "[Relationship Not Provided]"
        executor_str = f"Name: {exec_name}\nRelationship: {exec_rel}"

        # Gifts
        formatted_gifts = state.get_formatted_gifts()
        if formatted_gifts:
            gifts_str = "\n".join([f"  • {gift}" for gift in formatted_gifts])
        else:
            gifts_str = "  No specific gifts recorded at this time."

        # Additional wishes
        formatted_wishes = state.get_formatted_wishes()
        wishes_str = formatted_wishes or "No additional wishes specified."

        text = f"""================================================================================
DRAFT — FICTIONAL DOCUMENT
PERSONAL WISHES DOCUMENT
This is a fictional document and not legal advice.
Date Prepared: {datetime.utcnow().strftime('%B %d, %Y')}
================================================================================

1. PERSONAL DETAILS
--------------------------------------------------------------------------------
Full Name:        {name}
Home Address:     {address}
Asset Coverage:   {worldwide}

2. FAMILY DETAILS
--------------------------------------------------------------------------------
{children_str}

3. APPOINTMENT OF EXECUTOR
--------------------------------------------------------------------------------
{executor_str}

4. SPECIFIC GIFTS & BEQUESTS
--------------------------------------------------------------------------------
{gifts_str}

5. ADDITIONAL WISHES & MEMORANDUM
--------------------------------------------------------------------------------
{wishes_str}

================================================================================
DECLARATION & SIGNATURE PLACEHOLDER
I, {name}, declare that this document represents an expression of my personal 
wishes and intentions for administrative guidance.

Signature: ___________________________        Date: ________________________
================================================================================
"""
        return text

    @staticmethod
    def generate_document_html(state: StructuredState) -> str:
        """Generate formatted HTML version for the live preview and printing"""
        name = state.full_name or '<span class="text-slate-400 italic font-normal">[Not provided]</span>'
        address = state.home_address or '<span class="text-slate-400 italic font-normal">[Not provided]</span>'
        
        if state.covers_worldwide_assets is True:
            worldwide = '<span class="font-medium text-emerald-700">Worldwide Assets Covered</span> (United Kingdom and all international jurisdictions)'
        elif state.covers_worldwide_assets is False:
            worldwide = '<span class="font-medium text-slate-700">Domestic Jurisdiction Only</span> (Restricted to national assets)'
        else:
            worldwide = '<span class="text-slate-400 italic font-normal">[Not specified]</span>'

        # Family HTML
        if state.has_children is True:
            if state.children:
                children_items = "".join([f'<li class="py-1 text-slate-800 font-medium">• {c}</li>' for c in state.children])
                family_html = f'<p class="text-sm font-semibold text-slate-700 mb-1">Has Children: Yes</p><ul class="pl-2 space-y-1">{children_items}</ul>'
            else:
                family_html = '<p class="text-sm text-amber-700 font-medium">Has Children: Yes (names pending)</p>'
        elif state.has_children is False:
            family_html = '<p class="text-sm text-slate-700 font-medium">Has Children: No</p>'
        else:
            family_html = '<p class="text-sm text-slate-400 italic">[Family details not provided]</p>'

        # Executor HTML
        exec_name = state.executor.name or '<span class="text-slate-400 italic font-normal">[Name not provided]</span>'
        exec_rel = state.executor.relationship or '<span class="text-slate-400 italic font-normal">[Relationship not provided]</span>'
        executor_html = f"""
        <div class="grid grid-cols-2 gap-4 text-sm">
            <div><span class="text-slate-500 font-normal">Executor Name:</span> <div class="font-semibold text-slate-800">{exec_name}</div></div>
            <div><span class="text-slate-500 font-normal">Relationship:</span> <div class="font-semibold text-slate-800 capitalize">{exec_rel}</div></div>
        </div>
        """

        # Gifts HTML
        formatted_gifts = state.get_formatted_gifts()
        if formatted_gifts:
            gifts_items = "".join([f'<li class="py-1 text-slate-800 text-sm font-medium flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-blue-600"></span> {gift}</li>' for gift in formatted_gifts])
            gifts_html = f'<ul class="space-y-1">{gifts_items}</ul>'
        else:
            gifts_html = '<p class="text-sm text-slate-400 italic">No specific gifts or bequests recorded.</p>'

        # Wishes HTML
        formatted_wishes = state.get_formatted_wishes()
        if formatted_wishes and formatted_wishes.strip():
            wishes_html = f'<p class="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">{formatted_wishes}</p>'
        else:
            wishes_html = '<p class="text-sm text-slate-400 italic">No additional wishes specified.</p>'

        current_date = datetime.utcnow().strftime("%B %d, %Y")

        html = f"""
<div class="document-container bg-white p-8 md:p-12 max-w-3xl mx-auto rounded-xl shadow-lg border border-slate-200 text-slate-900 font-sans print:shadow-none print:border-none print:p-0">
    <div class="border-b-2 border-blue-600 pb-4 mb-6">
        <div class="flex items-center justify-between mb-2">
            <span class="inline-block px-3 py-1 bg-amber-100 text-amber-900 text-xs font-bold rounded-full tracking-wider uppercase">
                DRAFT — FICTIONAL DOCUMENT
            </span>
            <span class="text-xs text-slate-400 font-medium">Prepared on {current_date}</span>
        </div>
        <h1 class="text-2xl md:text-3xl font-serif font-bold text-slate-900 tracking-tight">PERSONAL WISHES DOCUMENT</h1>
        <p class="text-xs text-slate-500 mt-1 italic">This is a fictional document for administrative expression and does not constitute formal legal advice.</p>
    </div>

    <div class="space-y-6">
        <!-- 1. Personal Details -->
        <section class="border-b border-slate-100 pb-5">
            <h2 class="text-xs uppercase tracking-wider font-bold text-blue-800 mb-3 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span> 1. Personal Details
            </h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="text-slate-500 block text-xs">Full Legal Name</span>
                    <span class="font-semibold text-slate-800 text-base">{name}</span>
                </div>
                <div>
                    <span class="text-slate-500 block text-xs">Primary Home Address</span>
                    <span class="font-medium text-slate-800">{address}</span>
                </div>
                <div class="sm:col-span-2 mt-1 pt-2 border-t border-slate-50">
                    <span class="text-slate-500 block text-xs">Asset Coverage Scope</span>
                    <span class="text-sm">{worldwide}</span>
                </div>
            </div>
        </section>

        <!-- 2. Family Details -->
        <section class="border-b border-slate-100 pb-5">
            <h2 class="text-xs uppercase tracking-wider font-bold text-blue-800 mb-3 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span> 2. Family Details
            </h2>
            <div class="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
                {family_html}
            </div>
        </section>

        <!-- 3. Executor Appointment -->
        <section class="border-b border-slate-100 pb-5">
            <h2 class="text-xs uppercase tracking-wider font-bold text-blue-800 mb-3 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span> 3. Appointment of Executor
            </h2>
            <div class="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
                {executor_html}
            </div>
        </section>

        <!-- 4. Specific Gifts -->
        <section class="border-b border-slate-100 pb-5">
            <h2 class="text-xs uppercase tracking-wider font-bold text-blue-800 mb-3 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span> 4. Specific Gifts & Bequests
            </h2>
            <div class="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
                {gifts_html}
            </div>
        </section>

        <!-- 5. Additional Wishes -->
        <section class="border-b border-slate-100 pb-5">
            <h2 class="text-xs uppercase tracking-wider font-bold text-blue-800 mb-3 flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-600"></span> 5. Additional Wishes & Instructions
            </h2>
            <div class="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
                {wishes_html}
            </div>
        </section>

        <!-- Signature Section -->
        <section class="pt-4">
            <p class="text-xs text-slate-500 mb-6 italic">
                By signing below, I confirm that the information and wishes outlined above accurately represent my current preferences.
            </p>
            <div class="grid grid-cols-2 gap-8 pt-4">
                <div class="border-t border-slate-400 pt-2">
                    <span class="block text-xs text-slate-500 uppercase font-semibold">Testator Signature</span>
                    <span class="text-sm font-serif italic text-slate-700 mt-1 block">Signed by: {name}</span>
                </div>
                <div class="border-t border-slate-400 pt-2">
                    <span class="block text-xs text-slate-500 uppercase font-semibold">Date of Execution</span>
                    <span class="text-sm font-medium text-slate-700 mt-1 block">{current_date}</span>
                </div>
            </div>
        </section>
    </div>
</div>
        """
        return html

    @classmethod
    def generate_document_bundle(cls, state: StructuredState) -> Dict[str, Any]:
        """Returns bundle containing both html and plain text representation"""
        return {
            "document_html": cls.generate_document_html(state),
            "document_text": cls.generate_document_text(state),
            "updated_at": datetime.utcnow().isoformat()
        }
