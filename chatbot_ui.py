import streamlit as st
import requests
import json

CHAT_API_BASE = "http://0.0.0.0:9001/api/v1/chat"
COMPANY_API_BASE = "http://0.0.0.0:9001/api/v1/company"

# Session state initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Human-in-the-Loop Chatbot", layout="centered")
st.title("🧠 Human-in-the-Loop Chatbot Interface")

# Sidebar - Start a new conversation
st.sidebar.header("🔄 Start New Conversation")
with st.sidebar.form("start_form"):
    message = st.text_input("Initial Message", "Hello!")
    company_id = st.text_input("Company ID", "company123")
    user_id = st.text_input("User ID", "user456")
    data_type = st.selectbox("Data Type", ["live", "test", "hold"])
    custom_instructions = st.text_area("Custom Instructions", "Be polite and helpful.")

    # Company Info
    company_name = st.text_input("Company Name", "Example Corp")
    company_website = st.text_input("Company Website", "https://example.com")
    assistant_role = st.text_input("Assistant Role", "Customer Support")
    assistant_name = st.text_input("Assistant Name", "Chatbot Assistant")
    main_domains = st.text_input("Main Domains", "Healthcare, Finance")
    sub_domains = st.text_input("Sub Domains", "Pharmaceuticals, Banking")
    support_contact_emails = st.text_input(
        "Support Contact Emails", "support@example.com"
    )
    support_phone_numbers = st.text_input("Support Phone Numbers", "+1-800-123-4567")
    support_page_url = st.text_input("Support Page URL", "https://example.com/support")
    help_center_url = st.text_input("Help Center URL", "https://example.com/help")

    start_btn = st.form_submit_button("Start Chat")

    if start_btn:
        payload = {
            "message": message,
            "company_id": company_id,
            "user_id": user_id,
            "data_type": data_type,
            "custom_user_instructions": custom_instructions,
            "company_name": company_name,
            "company_website": company_website,
            "assistant_role": assistant_role,
            "assistant_name": assistant_name,
            "main_domains": main_domains,
            "sub_domains": sub_domains,
            "support_contact_emails": support_contact_emails,
            "support_phone_numbers": support_phone_numbers,
            "support_page_url": support_page_url,
            "help_center_url": help_center_url,
        }
        res = requests.post(f"{CHAT_API_BASE}/start", json=payload)
        if res.ok:
            data = res.json()["data"]
            st.session_state.thread_id = data.get("thread_id") or "mock-thread-id"
            st.session_state.messages = [{"role": "user", "message": message}]
            st.session_state.messages = [
                {"role": "bot", "message": data.get("response")}
            ]
            st.success("✅ Conversation started!")
            st.rerun()
        else:
            st.sidebar.error("❌ Failed to start conversation.")

# Vector Database Operations
st.sidebar.header("🧬 Vector DB Operations")
vector_action = st.sidebar.selectbox(
    "Choose Action",
    [
        "Add Document",
        "Query Documents",
        "List Collections",
        "List Documents",
        "Delete Document",
        "Delete Documents by Metadata",
        "Delete Company Collections",
    ],
)

with st.sidebar.form("vector_form"):
    if vector_action == "Add Document":
        documents = st.text_area(
            "Documents (in JSON format)",
            """[{
                    "page_content": "I had chocolate chip pancakes and scrambled eggs for breakfast this morning.",
                    "metadata": {"source": "tweet"},
                    "id": 1
                }]""",
        )
        if st.form_submit_button("Submit"):
            res = requests.post(
                f"{COMPANY_API_BASE}/add_document",
                json={
                    "company_id": company_id,
                    "data_type": data_type,
                    "documents": json.loads(documents),
                },
            )
            if res.ok:
                st.sidebar.success("✅ Added Document")
            else:
                st.sidebar.error("❌ Failed")

    elif vector_action == "Query Documents":
        query = st.text_input("Query", "Sample question?")
        k = st.number_input("K", 1, 10, 3)
        metadata_filter = st.text_input("Metadata Filter (JSON)", "{}")
        search_type = st.selectbox("Search Type", ["similarity", "mmr"])
        if st.form_submit_button("Submit"):
            res = requests.post(
                f"{COMPANY_API_BASE}/query",
                json={
                    "company_id": company_id,
                    "query": query,
                    "data_type": data_type,
                    "k": k,
                    "metadata_filter": eval(metadata_filter),
                    "search_type": search_type,
                },
            )
            st.sidebar.json(res.json()["data"] if res.ok else {"error": "Query failed"})

    elif vector_action == "List Collections":
        if st.form_submit_button("List"):
            res = requests.get(f"{COMPANY_API_BASE}/list_collections")
            st.sidebar.json(
                res.json()["data"]
                if res.ok
                else {"error": "Failed to list collections"}
            )

    elif vector_action == "List Documents":
        if st.form_submit_button("List"):
            res = requests.get(
                f"{COMPANY_API_BASE}/list_documents/{company_id}/{data_type}"
            )
            st.sidebar.json(
                res.json()["data"] if res.ok else {"error": "Failed to list documents"}
            )

    elif vector_action == "Delete Document":
        doc_id = st.text_input("Document ID to Delete")
        if st.form_submit_button("Delete"):
            res = requests.delete(
                f"{COMPANY_API_BASE}/delete_document",
                json={
                    "company_id": company_id,
                    "document_id": doc_id,
                    "data_type": data_type,
                },
            )
            (
                st.sidebar.success("✅ Deleted Document")
                if res.ok
                else st.sidebar.error("❌ Failed")
            )

    elif vector_action == "Delete Documents by Metadata":
        metadata_filter = st.text_input("Metadata Filter (JSON)", "{}")
        if st.form_submit_button("Delete"):
            res = requests.delete(
                f"{COMPANY_API_BASE}/delete_documents/{company_id}/{data_type}",
                json=eval(metadata_filter),
            )
            (
                st.sidebar.success("✅ Deleted Documents")
                if res.ok
                else st.sidebar.error("❌ Failed")
            )

    elif vector_action == "Delete Company Collections":
        if st.form_submit_button("Delete All Collections"):
            res = requests.delete(f"{COMPANY_API_BASE}/delete_company/{company_id}")
            (
                st.sidebar.success("✅ Deleted Collections")
                if res.ok
                else st.sidebar.error("❌ Failed")
            )

# Main Chat Interface
if st.session_state.thread_id:
    st.subheader("💬 Conversation")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["message"])

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "message": prompt})
        with st.spinner("🤖 Bot is typing..."):
            res = requests.post(
                f"{CHAT_API_BASE}/message",
                json={"thread_id": st.session_state.thread_id, "message": prompt},
            )
            if res.ok:
                reply = res.json()["data"].get("response", "No reply.")
                st.session_state.messages.append({"role": "bot", "message": reply})
            else:
                st.session_state.messages.append(
                    {"role": "bot", "message": "⚠️ Failed to get response."}
                )
        st.rerun()

# Feedback
if st.session_state.thread_id:
    st.subheader("📝 Submit Feedback")
    feedback_text = st.text_area("Share your feedback about this chat")
    if st.button("Submit Feedback"):
        payload = {"thread_id": st.session_state.thread_id, "feedback": feedback_text}
        res = requests.post(f"{CHAT_API_BASE}/feedback", json=payload)
        (
            st.success("✅ Feedback submitted. Thank you!")
            if res.ok
            else st.error("❌ Failed to submit feedback.")
        )
