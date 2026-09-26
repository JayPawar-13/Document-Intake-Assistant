from app.models.state import StructuredState, Executor
from app.services.document_service import DocumentService


def test_document_generation_empty_state():
    state = StructuredState(session_id="test-1")
    text = DocumentService.generate_document_text(state)
    html = DocumentService.generate_document_html(state)

    assert "DRAFT — FICTIONAL DOCUMENT" in text
    assert "PERSONAL WISHES DOCUMENT" in text
    assert "This is a fictional document and not legal advice." in text
    assert "[Full Name Not Provided]" in text

    assert "DRAFT — FICTIONAL DOCUMENT" in html
    assert "PERSONAL WISHES DOCUMENT" in html
    assert "[Not provided]" in html


def test_document_generation_filled_state():
    state = StructuredState(
        session_id="test-2",
        full_name="Jane Smith",
        home_address="21 High Street, London",
        covers_worldwide_assets=True,
        has_children=True,
        children=["Sarah", "Michael"],
        executor=Executor(name="James Smith", relationship="brother"),
        specific_gifts=["My watch to Michael"],
        additional_wishes="My photographs to Sarah"
    )

    text = DocumentService.generate_document_text(state)
    html = DocumentService.generate_document_html(state)

    assert "Jane Smith" in text
    assert "21 High Street, London" in text
    assert "worldwide" in text.lower()
    assert "Sarah" in text
    assert "Michael" in text
    assert "James Smith" in text
    assert "brother" in text
    assert "My watch to Michael" in text
    assert "My photographs to Sarah" in text

    assert "Jane Smith" in html
    assert "21 High Street, London" in html
    assert "Worldwide Assets Covered" in html
    assert "James Smith" in html


def test_document_pdf_generation():
    # 1. Test empty state PDF generation
    empty_state = StructuredState(session_id="test-empty")
    pdf_bytes_empty = DocumentService.generate_document_pdf(empty_state)
    assert isinstance(pdf_bytes_empty, bytes)
    assert len(pdf_bytes_empty) > 1000
    assert pdf_bytes_empty.startswith(b"%PDF")

    # 2. Test filled state PDF generation
    filled_state = StructuredState(
        session_id="test-filled",
        full_name="Jane Smith",
        home_address="21 High Street, London",
        covers_worldwide_assets=True,
        has_children=True,
        children=["Sarah", "Michael"],
        executor=Executor(name="James Smith", relationship="brother"),
        specific_gifts=["My watch to Michael"],
        additional_wishes="My photographs to Sarah"
    )
    pdf_bytes_filled = DocumentService.generate_document_pdf(filled_state, session_id="test-filled")
    assert isinstance(pdf_bytes_filled, bytes)
    assert len(pdf_bytes_filled) > 2000
    assert pdf_bytes_filled.startswith(b"%PDF")
    # Verify alias
    alias_bytes = DocumentService.generate_pdf(filled_state)
    assert alias_bytes.startswith(b"%PDF")
