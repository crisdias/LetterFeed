import uuid
import xml.etree.ElementTree as ET

from sqlalchemy.orm import Session

from app.crud.entries import create_entry
from app.crud.newsletters import create_newsletter
from app.schemas.entries import EntryCreate
from app.schemas.newsletters import NewsletterCreate
from app.services.feed_generator import generate_feed, generate_master_feed, generate_opml


def test_generate_master_feed(db_session: Session):
    """Test the master feed generation for all newsletters."""
    # Create newsletters and entries
    nl1 = create_newsletter(
        db_session,
        NewsletterCreate(name="Newsletter A", sender_emails=["a@example.com"]),
    )
    create_entry(
        db_session,
        EntryCreate(
            subject="Entry A1", body="<p>Body A1</p>", message_id=f"<{uuid.uuid4()}>"
        ),
        nl1.id,
    )

    nl2 = create_newsletter(
        db_session,
        NewsletterCreate(name="Newsletter B", sender_emails=["b@example.com"]),
    )
    create_entry(
        db_session,
        EntryCreate(
            subject="Entry B1", body="<p>Body B1</p>", message_id=f"<{uuid.uuid4()}>"
        ),
        nl2.id,
    )

    # Generate the master feed
    feed_xml = generate_master_feed(db_session)
    assert feed_xml is not None

    # Parse and verify
    root = ET.fromstring(feed_xml)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    assert root.find("atom:title", ns).text == "LetterFeed: All Newsletters"
    assert root.find("atom:id", ns).text == "urn:letterfeed:master"

    entry_titles = {
        entry.find("atom:title", ns).text for entry in root.findall("atom:entry", ns)
    }
    assert "[Newsletter A] Entry A1" in entry_titles
    assert "[Newsletter B] Entry B1" in entry_titles


def test_generate_feed(db_session: Session):
    """Test the feed generation for a newsletter with entries."""
    # Create a newsletter
    newsletter_data = NewsletterCreate(
        name="Feed Test Newsletter", sender_emails=["feed@example.com"]
    )
    newsletter = create_newsletter(db_session, newsletter_data)

    # Create entries for the newsletter
    entry1_data = EntryCreate(
        subject="First Entry",
        body="<p>This is the first entry.</p>",
        message_id=f"<{uuid.uuid4()}@test.com>",
    )
    create_entry(db_session, entry1_data, newsletter.id)

    entry2_data = EntryCreate(
        subject="Second Entry",
        body="<p>This is the second entry.</p>",
        message_id=f"<{uuid.uuid4()}@test.com>",
    )
    create_entry(db_session, entry2_data, newsletter.id)

    # Generate the feed
    feed_xml = generate_feed(db_session, newsletter.id)
    assert feed_xml is not None

    # Parse the feed XML to verify content
    root = ET.fromstring(feed_xml)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # Check for top-level elements
    assert root.find("atom:title", ns).text == newsletter.name
    assert root.find("atom:id", ns).text == f"urn:letterfeed:newsletter:{newsletter.id}"
    assert root.find("atom:logo", ns).text.endswith("/logo.png")
    assert root.find("atom:icon", ns).text.endswith("/favicon.ico")

    # Check for the alternate link
    links = root.findall("atom:link", ns)
    assert any(link.get("rel") == "alternate" and link.get("href") for link in links)

    # Check for entries
    entry_titles = [
        entry.find("atom:title", ns).text for entry in root.findall("atom:entry", ns)
    ]
    assert "First Entry" in entry_titles
    assert "Second Entry" in entry_titles

    # Check content of one entry
    first_entry_element = root.find(".//atom:title[.='First Entry']/..", ns)
    assert (
        first_entry_element.find("atom:content", ns).text
        == "<p>This is the first entry.</p>"
    )


def test_generate_feed_nonexistent_newsletter(db_session: Session):
    """Test feed generation for a non-existent newsletter."""
    feed_xml = generate_feed(db_session, "nonexistent-id")
    assert feed_xml is None


def test_generate_opml(db_session: Session):
    """Test the OPML generation for all newsletters."""
    # Create newsletters
    nl1 = create_newsletter(
        db_session,
        NewsletterCreate(
            name="Newsletter A", slug="newsletter-a", sender_emails=["a@example.com"]
        ),
    )
    nl2 = create_newsletter(
        db_session,
        NewsletterCreate(name="Newsletter B", sender_emails=["b@example.com"]),
    )

    # Generate OPML
    opml_xml = generate_opml(db_session)
    assert opml_xml is not None

    # Parse and verify
    root = ET.fromstring(opml_xml)
    assert root.tag == "opml"
    assert root.get("version") == "2.0"

    # Check head
    head = root.find("head")
    assert head is not None
    title = head.find("title")
    assert title is not None
    assert title.text == "LetterFeed Newsletters"

    # Check body
    body = root.find("body")
    assert body is not None
    outlines = body.findall("outline")
    assert len(outlines) == 2

    # Check first newsletter - verify URL points to existing feed
    outline1 = next((o for o in outlines if o.get("text") == "Newsletter A"), None)
    assert outline1 is not None
    assert outline1.get("type") == "rss"
    assert outline1.get("title") == "Newsletter A"
    xml_url_1 = outline1.get("xmlUrl")
    assert "/api/feeds/newsletter-a" in xml_url_1
    # Verify the feed actually exists by generating it
    feed1 = generate_feed(db_session, "newsletter-a")
    assert feed1 is not None

    # Check second newsletter - verify URL points to existing feed
    outline2 = next((o for o in outlines if o.get("text") == "Newsletter B"), None)
    assert outline2 is not None
    assert outline2.get("type") == "rss"
    assert outline2.get("title") == "Newsletter B"
    xml_url_2 = outline2.get("xmlUrl")
    assert "/api/feeds/" in xml_url_2
    assert nl2.id in xml_url_2
    # Verify the feed actually exists by generating it
    feed2 = generate_feed(db_session, nl2.id)
    assert feed2 is not None
