import streamlit as st
import requests
import subprocess

subprocess.Popen(['uvicorn', 'main:app', '--reload'])

BASE_URL = "http://127.0.0.1:8000"

# Streamlit app to interact with the FastAPI backend
st.title("To-Do List App")

# Create a new to-do item
st.header("Create a New To-Do Item")
todo_id = st.number_input("ID", min_value=1, step=1)
todo_title = st.text_input("Title")
todo_description = st.text_area("Description")
if st.button("Add To-Do"):
    response = requests.post(
        f"{BASE_URL}/todos/",
        json={"id": todo_id, "title": todo_title, "description": todo_description},
    )
    if response.status_code == 200:
        st.success("To-Do item added successfully!")
    else:
        st.error(f"Error: {response.json().get('detail')}")

# Fetch and display all to-do items
st.header("To-Do List")
response = requests.get(f"{BASE_URL}/todos/{todo_id}")
if response.status_code == 200:
    todo = response.json()
    st.write(f"ID: {todo['id']}")
    st.write(f"Title: {todo['title']}")
    st.write(f"Description: {todo['description']}")
else:
    st.write("To-Do item not found.")

# Update a to-do item
st.header("Update To-Do Item")
update_id = st.number_input("Enter To-Do ID to Update", min_value=1, step=1)
new_title = st.text_input("New Title")
new_description = st.text_area("New Description")
if st.button("Update To-Do"):
    response = requests.put(
        f"{BASE_URL}/todos/{update_id}",
        json={"id": update_id, "title": new_title, "description": new_description},
    )
    if response.status_code == 200:
        st.success("To-Do item updated successfully!")
    else:
        st.error(f"Error: {response.json().get('detail')}")

# Delete a to-do item
st.header("Delete To-Do Item")
delete_id = st.number_input("Enter To-Do ID to Delete", min_value=1, step=1)
if st.button("Delete To-Do"):
    response = requests.delete(f"{BASE_URL}/todos/{delete_id}")
    if response.status_code == 200:
        st.success("To-Do item deleted successfully!")
    else:
        st.error(f"Error: {response.json().get('detail')}")