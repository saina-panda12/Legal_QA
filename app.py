# import streamlit as st
# import requests

# # Backend API URL
# BASE_URL = "http://127.0.0.1:8000"  # Change this if backend is deployed elsewhere

# # Streamlit session state for authentication
# st.session_state.setdefault("token", None)
# st.session_state.setdefault("logged_in", False)
# st.session_state.setdefault("chat_history", [])
# st.session_state.setdefault("documents", [])
# st.session_state.setdefault("show_register", False)
# st.session_state.setdefault("current_page", "Document Management")  # Default page

# # Function to register a user
# def register():
#     st.title("Register")
#     username = st.text_input("Username")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Register"):
#         response = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "email": email, "password": password})
#         if response.status_code == 200:
#             st.success("Registration successful. Please login.")
#             st.session_state.show_register = False
#             st.rerun()
#         else:
#             st.error(response.json().get("detail", "Registration failed"))

# # Function to login a user
# def login():
#     st.title("Login")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     if st.button("Login"):
#         response = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
#         if response.status_code == 200:
#             st.session_state.token = response.json()["access_token"]
#             st.session_state.logged_in = True
#             st.success("Login successful!")
#             st.rerun()
#         else:
#             st.error(response.json().get("detail", "Login failed"))

# # Function to logout a user
# def logout():
#     st.session_state.token = None
#     st.session_state.logged_in = False
#     st.rerun()

# # Function to fetch documents
# def fetch_documents():
#     response = requests.get(f"{BASE_URL}/documents/", headers={"Authorization": f"Bearer {st.session_state.token}"})
#     if response.status_code == 200:
#         st.session_state.documents = response.json()

# # Function to manage documents (upload & delete)
# def document_management():
#     st.title("Document Management")
#     fetch_documents()

#     uploaded_file = st.file_uploader("Upload a document", type=["pdf", "csv", "xlsx"])
#     if uploaded_file and st.button("Upload"):
#         files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
#         response = requests.post(f"{BASE_URL}/documents/upload", headers={"Authorization": f"Bearer {st.session_state.token}"}, files=files)
#         if response.status_code == 201:
#             st.success("Document uploaded successfully!")
#             fetch_documents()
#             st.rerun()
#         else:
#             st.error("Failed to upload document.")

#     st.subheader("Your Documents")
#     for doc in st.session_state.documents:
#         st.write(f"{doc['file_name']} ({doc['file_type']})")
#         if st.button(f"Delete {doc['file_name']}", key=doc['id']):
#             response = requests.delete(f"{BASE_URL}/documents/{doc['id']}", headers={"Authorization": f"Bearer {st.session_state.token}"})
#             if response.status_code == 204:
#                 st.success("Document deleted successfully!")
#                 fetch_documents()
#                 st.rerun()
#             else:
#                 st.error("Failed to delete document.")

# # Function to chat with a document
# def chat_with_document():
#     st.title("Chat with Document")
#     response = requests.get(f"{BASE_URL}/documents/", headers={"Authorization": f"Bearer {st.session_state.token}"})
#     if response.status_code == 200:
#         st.session_state.documents = response.json()

#     if not st.session_state.documents:
#         st.warning("No documents available. Please upload one first.")
#         return

#     document_options = {doc["file_name"]: doc["id"] for doc in st.session_state.documents}
#     document_name = st.selectbox("Select a document", list(document_options.keys()))
#     document_id = document_options[document_name]

#     # Fetch chat history for selected document
#     response = requests.get(f"{BASE_URL}/chat/history/{document_id}", headers={"Authorization": f"Bearer {st.session_state.token}"})
#     if response.status_code == 200:
#         st.session_state.chat_history = [(chat["message"], chat["response"]) for chat in response.json()]

#     st.subheader("Chat History")
#     chat_container = st.container()
#     with chat_container:
#         for user_msg, bot_msg in st.session_state.chat_history:
#             st.markdown(f'<div style="text-align: right;"><strong>👤:</strong> {user_msg}</div>', unsafe_allow_html=True)
#             st.markdown(f'<div style="text-align: left;"><strong>🤖:</strong> {bot_msg}</div>', unsafe_allow_html=True)
#             st.markdown("---")

#         message = st.text_area("Your Message", key="chat_input")
#         if st.button("Send"):
#             response = requests.post(f"{BASE_URL}/chat/", headers={"Authorization": f"Bearer {st.session_state.token}"}, json={"document_id": document_id, "message": message})
#             if response.status_code == 200:
#                 st.session_state.chat_history.append((message, response.json()["response"]))
#                 st.rerun()
#             else:
#                 st.error("Failed to chat with document.")
#         st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

# # Function to execute SQL queries
# def execute_sql_query():
#     st.title("SQL Query")
#     query = st.text_area("Enter your SQL Query")
#     if st.button("Submit Query"):
#         response = requests.post(f"{BASE_URL}/sqlquery/query", headers={"Authorization": f"Bearer {st.session_state.token}"}, json={"query": query})
#         if response.status_code == 200:
#             st.success(f"Query Result: {response.json()['response']}")
#         else:
#             st.error("Failed to execute query.")

# # Main function to handle navigation
# def main():
#     if st.session_state.logged_in:
#         st.sidebar.title("Navigation")
#         pages = ["Document Management", "Chat With Docs", "Query Database", "Logout"]
#         for page in pages:
#             if st.sidebar.button(page, key=page, use_container_width=True):
#                 if page == "Logout":
#                     logout()
#                 else:
#                     st.session_state.current_page = page
#         st.sidebar.markdown(f"<style>div.stButton > button:focus {{ background-color: #483D8B; color: white; }}</style>", unsafe_allow_html=True)
#         st.sidebar.markdown(f"<style>div.stButton > button:nth-child({pages.index(st.session_state.current_page)+1}) {{ background-color: #483D8B; color: white; }}</style>", unsafe_allow_html=True)

#         if st.session_state.current_page == "Document Management":
#             document_management()
#         elif st.session_state.current_page == "Chat With Docs":
#             chat_with_document()
#         elif st.session_state.current_page == "Query Database":
#             execute_sql_query()

#     else:
#         if st.session_state.show_register:
#             register()
#             if st.button("Already have an account? Login"):
#                 st.session_state.show_register = False
#                 st.rerun()
#         else:
#             login()
#             if st.button("Don't have an account? Register"):
#                 st.session_state.show_register = True
#                 st.rerun()

# if __name__ == "__main__":
#     main()


import streamlit as st
import requests
import traceback

# Backend API URL
BASE_URL = "http://127.0.0.1:8000"  # Change this if backend is deployed elsewhere

# Streamlit session state for authentication
st.session_state.setdefault("token", None)
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("documents", [])
st.session_state.setdefault("show_register", False)
st.session_state.setdefault("current_page", "Document Management")  # Default page

# Function to register a user
def register():
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        response = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "email": email, "password": password})
        if response.status_code == 200:
            st.success("Registration successful. Please login.")
            st.session_state.show_register = False
            st.rerun()
        else:
            # Safely handle JSON decoding errors
            try:
                error_msg = response.json().get("detail", "Registration failed")
            except requests.exceptions.JSONDecodeError:
                error_msg = f"Registration failed with status code: {response.status_code}"
            st.error(error_msg)

# Function to login a user
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": password})
        if response.status_code == 200:
            try:
                st.session_state.token = response.json()["access_token"]
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.rerun()
            except requests.exceptions.JSONDecodeError:
                st.error(f"Login failed: Invalid response format from server")
        else:
            try:
                error_msg = response.json().get("detail", "Login failed")
            except requests.exceptions.JSONDecodeError:
                error_msg = f"Login failed with status code: {response.status_code}"
            st.error(error_msg)

# Function to logout a user
def logout():
    st.session_state.token = None
    st.session_state.logged_in = False
    st.rerun()

# Function to fetch documents
def fetch_documents():
    try:
        response = requests.get(f"{BASE_URL}/documents/", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if response.status_code == 200:
            st.session_state.documents = response.json()
        else:
            st.error(f"Failed to fetch documents. Status code: {response.status_code}")
            st.session_state.documents = []
    except requests.exceptions.JSONDecodeError:
        st.error("Error parsing document data from server")
        st.session_state.documents = []
    except Exception as e:
        st.error(f"Error fetching documents: {str(e)}")
        st.session_state.documents = []

# Function to manage documents (upload & delete)
def document_management():
    st.title("Document Management")
    fetch_documents()

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "csv", "xlsx"])
    if uploaded_file and st.button("Upload"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(
                f"{BASE_URL}/documents/upload", 
                headers={"Authorization": f"Bearer {st.session_state.token}"}, 
                files=files
            )
            if response.status_code == 201:
                st.success("Document uploaded successfully!")
                fetch_documents()
                st.rerun()
            else:
                try:
                    error_msg = response.json().get("detail", "Failed to upload document.")
                except requests.exceptions.JSONDecodeError:
                    error_msg = f"Failed to upload document. Status code: {response.status_code}"
                st.error(error_msg)
        except Exception as e:
            st.error(f"Error uploading document: {str(e)}")

    st.subheader("Your Documents")
    if not st.session_state.documents:
        st.info("You have no documents. Upload one to get started.")
    else:
        for doc in st.session_state.documents:
            st.write(f"{doc['file_name']} ({doc['file_type']})")
            if st.button(f"Delete {doc['file_name']}", key=doc['id']):
                try:
                    response = requests.delete(
                        f"{BASE_URL}/documents/{doc['id']}", 
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    if response.status_code == 204:
                        st.success("Document deleted successfully!")
                        fetch_documents()
                        st.rerun()
                    else:
                        try:
                            error_msg = response.json().get("detail", "Failed to delete document.")
                        except requests.exceptions.JSONDecodeError:
                            error_msg = f"Failed to delete document. Status code: {response.status_code}"
                        st.error(error_msg)
                except Exception as e:
                    st.error(f"Error deleting document: {str(e)}")

# Function to chat with a document
def chat_with_document():
    st.title("Chat with Document")
    try:
        response = requests.get(f"{BASE_URL}/documents/", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if response.status_code == 200:
            st.session_state.documents = response.json()
        else:
            st.error("Failed to fetch documents. Please try again.")
            return
    except requests.exceptions.JSONDecodeError:
        st.error("Error fetching documents: Invalid response format")
        return

    if not st.session_state.documents:
        st.warning("No documents available. Please upload one first.")
        return

    document_options = {doc["file_name"]: doc["id"] for doc in st.session_state.documents}
    document_name = st.selectbox("Select a document", list(document_options.keys()))
    document_id = document_options[document_name]

    # Fetch chat history for selected document
    try:
        response = requests.get(f"{BASE_URL}/chat/history/{document_id}", headers={"Authorization": f"Bearer {st.session_state.token}"})
        if response.status_code == 200:
            st.session_state.chat_history = [(chat["message"], chat["response"]) for chat in response.json()]
        elif response.status_code == 404:
            st.session_state.chat_history = []  # Initialize empty history if none found
        else:
            st.error("Failed to fetch chat history.")
            return
    except requests.exceptions.JSONDecodeError:
        st.session_state.chat_history = []  # Initialize empty if response cannot be parsed

    st.subheader("Chat History")
    chat_container = st.container()
    with chat_container:
        for user_msg, bot_msg in st.session_state.chat_history:
            st.markdown(f'<div style="text-align: right;"><strong>👤:</strong> {user_msg}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: left;"><strong>🤖:</strong> {bot_msg}</div>', unsafe_allow_html=True)
            st.markdown("---")

        message = st.text_area("Your Message", key="chat_input")
        if st.button("Send"):
            try:
                response = requests.post(
                    f"{BASE_URL}/chat/", 
                    headers={"Authorization": f"Bearer {st.session_state.token}"}, 
                    json={"document_id": document_id, "message": message}
                )
                if response.status_code == 200:
                    st.session_state.chat_history.append((message, response.json()["response"]))
                    st.rerun()
                else:
                    try:
                        error_msg = response.json().get("detail", "Failed to chat with document.")
                    except requests.exceptions.JSONDecodeError:
                        error_msg = f"Failed to chat with document. Status code: {response.status_code}"
                    st.error(error_msg)
            except Exception as e:
                st.error(f"Error sending message: {str(e)}")
        st.markdown("<div style='height: 200px;'></div>", unsafe_allow_html=True)

# Main function to handle navigation
def main():
    try:
        if st.session_state.logged_in:
            st.sidebar.title("Navigation")
            pages = ["Document Management", "Chat With Docs", "Logout"]
            for page in pages:
                if st.sidebar.button(page, key=page, use_container_width=True):
                    if page == "Logout":
                        logout()
                    else:
                        st.session_state.current_page = page
            st.sidebar.markdown(f"<style>div.stButton > button:focus {{ background-color: #483D8B; color: white; }}</style>", unsafe_allow_html=True)
            # Use min to avoid index out of bounds error
            page_index = min(pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0, len(pages)-1)
            st.sidebar.markdown(f"<style>div.stButton > button:nth-child({page_index+1}) {{ background-color: #483D8B; color: white; }}</style>", unsafe_allow_html=True)

            if st.session_state.current_page == "Document Management":
                document_management()
            elif st.session_state.current_page == "Chat With Docs":
                chat_with_document()

        else:
            if st.session_state.show_register:
                register()
                if st.button("Already have an account? Login"):
                    st.session_state.show_register = False
                    st.rerun()
            else:
                login()
                if st.button("Don't have an account? Register"):
                    st.session_state.show_register = True
                    st.rerun()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()