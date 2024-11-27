from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Pydantic model to define the structure of a ToDo item
class ToDoItem(BaseModel):
    id: int
    title: str
    description: str = None

# Simulating an in-memory database with a dictionary
to_do_list = {}

# CRUD Operations

# Create a new to-do item
@app.post("/todos/", response_model=ToDoItem)
def create_todo_item(todo_item: ToDoItem):
    if todo_item.id in to_do_list:
        raise HTTPException(status_code=400, detail="To-do item already exists")
    to_do_list[todo_item.id] = todo_item
    return todo_item

# Get a single to-do item by ID
@app.get("/todos/{todo_id}", response_model=ToDoItem)
def read_todo_item(todo_id: int):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    return to_do_list[todo_id]

# Update an existing to-do item
@app.put("/todos/{todo_id}", response_model=ToDoItem)
def update_todo_item(todo_id: int, todo_item: ToDoItem):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    to_do_list[todo_id] = todo_item
    return todo_item

# Delete a to-do item
@app.delete("/todos/{todo_id}")
def delete_todo_item(todo_id: int):
    if todo_id not in to_do_list:
        raise HTTPException(status_code=404, detail="To-do item not found")
    del to_do_list[todo_id]
    return {"detail": "To-do item deleted"}