import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from app.models.state import StructuredState


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer subtle divider line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(40, 36, 572, 36)

        # Footer Left: Privileged disclaimer
        self.setFont("Helvetica", 7.5)
        self.drawString(40, 24, "CONFIDENTIAL & PRIVILEGED  •  PERSONAL WISHES DOCUMENT  •  FOR LEGAL REVIEW")

        # Footer Right: Page X of Y
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1E293B"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 24, page_str)

        # Running Top Header on Page 2+
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(40, 756, "PERSONAL WISHES DOCUMENT")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(185, 756, "—  Executive Intake & Administrative Guidance")

            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(40, 748, 572, 748)

        self.restoreState()


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
    def generate_document_pdf(cls, state: StructuredState, session_id: str = "") -> bytes:
        """
        Generate an executive, publication-grade PDF version of the Personal Wishes Document.
        Features formal header, clean two-column key-value tables with section headings and dividers,
        legal review signature blocks, and a Page X of Y footer on every page.
        """
        effective_session_id = session_id or state.session_id or "DRAFT"

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=44,
            bottomMargin=46
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0F172A")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#475569")
        )
        badge_style = ParagraphStyle(
            "DraftBadge",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#1E40AF")
        )
        section_title_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=10,
            spaceAfter=4
        )
        table_label_style = ParagraphStyle(
            "TableLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#334155")
        )
        table_value_style = ParagraphStyle(
            "TableValue",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#0F172A")
        )
        disclaimer_style = ParagraphStyle(
            "DisclaimerText",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=11,
            textColor=colors.HexColor("#78350F")
        )
        decl_style = ParagraphStyle(
            "DeclarationText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12.5,
            textColor=colors.HexColor("#1E293B")
        )

        story = []

        # 1. Formal Document Header Banner
        badge_table = Table(
            [[Paragraph("ESTATE INTAKE & ADMINISTRATIVE GUIDANCE  •  CONFIDENTIAL DRAFT", badge_style)]],
            colWidths=[532]
        )
        badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#BFDBFE")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(badge_table)
        story.append(Spacer(1, 8))

        story.append(Paragraph("PERSONAL WISHES DOCUMENT", title_style))
        story.append(Spacer(1, 2))
        story.append(Paragraph("Formal Expression of Personal Intentions, Beneficiary Designations & Administrative Guidance", subtitle_style))
        story.append(Spacer(1, 10))

        # Header Meta Table (Session Ref ID, Date, Status, Jurisdiction)
        date_str = datetime.utcnow().strftime("%B %d, %Y")
        ref_id = f"#REF-{effective_session_id}"
        
        meta_data = [
            [
                Paragraph("<b>Document Reference:</b>", table_label_style),
                Paragraph(ref_id, table_value_style),
                Paragraph("<b>Date Prepared:</b>", table_label_style),
                Paragraph(date_str, table_value_style)
            ],
            [
                Paragraph("<b>Document Status:</b>", table_label_style),
                Paragraph("<font color='#047857'><b>Draft for Legal Review</b></font>", table_value_style),
                Paragraph("<b>Asset Jurisdiction:</b>", table_label_style),
                Paragraph("Worldwide Scope" if state.covers_worldwide_assets else ("Domestic Scope" if state.covers_worldwide_assets is False else "Not Specified"), table_value_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[110, 156, 110, 156])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8))

        # Legal Notice Callout Box
        disclaimer_p = Paragraph(
            "<b>LEGAL NOTICE & PURPOSE:</b> This document constitutes a structured, AI-assisted record of personal wishes and executor instructions. It is designed to assist professional advisers and executors in estate administration and does not substitute for a formal statutory Will or legal counsel.",
            disclaimer_style
        )
        disclaimer_table = Table([[disclaimer_p]], colWidths=[532])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFBEB")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#FDE68A")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(disclaimer_table)
        story.append(Spacer(1, 10))

        # Helper function to create clean two-column key-value tables
        def create_section_table(rows: List[List[str]]):
            table_content = []
            for label, val in rows:
                table_content.append([
                    Paragraph(label, table_label_style),
                    Paragraph(val, table_value_style)
                ])
            t = Table(table_content, colWidths=[150, 382])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor("#FFFFFF")),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            return t

        def add_section_header(title: str):
            story.append(Paragraph(title, section_title_style))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=5))

        # 1. Personal Details
        add_section_header("1. PERSONAL DETAILS")
        name_str = state.full_name or "[Not Provided]"
        addr_str = state.home_address or "[Not Provided]"
        if state.covers_worldwide_assets is True:
            world_str = "<b>Worldwide Assets Covered</b> — Governs assets situated in the United Kingdom and internationally."
        elif state.covers_worldwide_assets is False:
            world_str = "<b>Domestic Jurisdiction Only</b> — Strictly limited to assets situated in primary national jurisdiction."
        else:
            world_str = "[Asset Coverage Scope Not Specified]"
        story.append(create_section_table([
            ("Full Legal Name", name_str),
            ("Primary Residence", addr_str),
            ("Asset Coverage Scope", world_str)
        ]))
        story.append(Spacer(1, 8))

        # 2. Family Details
        add_section_header("2. FAMILY & BENEFICIARIES")
        if state.has_children is True:
            has_child_str = "Yes — Children recorded"
            children_val = "<br/>".join([f"• {c}" for c in state.children]) if state.children else "Yes, but names not yet specified."
        elif state.has_children is False:
            has_child_str = "No children recorded"
            children_val = "Not applicable"
        else:
            has_child_str = "[Not Provided]"
            children_val = "[Not Provided]"
        story.append(create_section_table([
            ("Has Children / Dependents", has_child_str),
            ("Identified Children", children_val)
        ]))
        story.append(Spacer(1, 8))

        # 3. Appointment of Executor
        add_section_header("3. APPOINTMENT OF EXECUTOR")
        exec_name = state.executor.name or "[Executor Name Not Provided]"
        exec_rel = state.executor.relationship.capitalize() if state.executor.relationship else "[Relationship Not Provided]"
        story.append(create_section_table([
            ("Nominated Primary Executor", f"<b>{exec_name}</b>"),
            ("Relationship to Testator", exec_rel),
            ("Administrative Authority", "Primary administrative executor authorized to execute wishes and coordinate estate distribution.")
        ]))
        story.append(Spacer(1, 8))

        # 4. Specific Gifts & Bequests
        add_section_header("4. SPECIFIC GIFTS & BEQUESTS")
        formatted_gifts = state.get_formatted_gifts()
        if formatted_gifts:
            gift_rows = []
            for i, g in enumerate(formatted_gifts, 1):
                gift_rows.append((f"Bequest #{i}", f"• {g}"))
            story.append(create_section_table(gift_rows))
        else:
            story.append(create_section_table([
                ("Specific Bequests", "No specific gifts recorded at this time. Residual estate to follow general legal distribution.")
            ]))
        story.append(Spacer(1, 8))

        # 5. Additional Wishes & Instructions
        add_section_header("5. ADDITIONAL WISHES & MEMORANDUM")
        formatted_wishes = state.get_formatted_wishes() or "No additional wishes specified."
        story.append(create_section_table([
            ("Special Instructions & Wishes", formatted_wishes.replace("\n", "<br/>"))
        ]))
        story.append(Spacer(1, 12))

        # 6. Declaration & Signatures for Legal Review
        sig_elements = []
        sig_elements.append(Paragraph("6. DECLARATION & EXECUTION FOR LEGAL REVIEW", section_title_style))
        sig_elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceBefore=2, spaceAfter=6))
        
        decl_text = f"I, <b>{name_str}</b>, confirm that I have reviewed the contents of this Personal Wishes Document. I declare that the nominations, asset scopes, beneficiary designations, and special instructions set forth above accurately reflect my intentions for administrative guidance."
        sig_elements.append(Paragraph(decl_text, decl_style))
        sig_elements.append(Spacer(1, 14))

        # Side-by-side signature table
        sig_data = [
            [
                Paragraph("<b>TESTATOR CONFIRMATION</b>", table_label_style),
                Paragraph("<b>WITNESS / LEGAL REVIEWER</b>", table_label_style)
            ],
            [
                Paragraph("Signature: ____________________________________", table_value_style),
                Paragraph("Signature: ____________________________________", table_value_style)
            ],
            [
                Paragraph(f"Printed Name: <b>{name_str}</b>", table_value_style),
                Paragraph("Reviewer Name: ________________________________", table_value_style)
            ],
            [
                Paragraph(f"Date: {date_str}", table_value_style),
                Paragraph("Date: _________________________________________", table_value_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[266, 266])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        sig_elements.append(sig_table)

        story.append(KeepTogether(sig_elements))

        doc.build(story, canvasmaker=NumberedCanvas)
        return buffer.getvalue()

    @classmethod
    def generate_pdf(cls, state: StructuredState, session_id: str = "") -> bytes:
        """Alias for generate_document_pdf"""
        return cls.generate_document_pdf(state, session_id=session_id)

    @classmethod
    def generate_document_bundle(cls, state: StructuredState, session_id: str = "") -> Dict[str, Any]:
        """Returns bundle containing html, plain text, and generated timestamp"""
        return {
            "document_html": cls.generate_document_html(state),
            "document_text": cls.generate_document_text(state),
            "has_pdf": True,
            "updated_at": datetime.utcnow().isoformat()
        }
