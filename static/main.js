document.addEventListener('DOMContentLoaded', () => {

    function showMessage(type, text) {
        const messageContainer = document.getElementById('message-container');
        const messageText = document.getElementById('message-text');
    
        // Set the message text
        messageText.textContent = text;
    
        // Adjust the styling based on the type of message
        if (type === 'success') {
            messageContainer.className = 'bg-green-500 p-2 rounded mb-4';
        } else if (type === 'error') {
            messageContainer.className = 'bg-red-500 p-2 rounded mb-4';
        } else if (type === 'info') {
            messageContainer.className = 'bg-blue-500 p-2 rounded mb-4';
        }
    
        // Show the message container
        messageContainer.classList.remove('hidden');
    
        // Automatically hide the message after 5 seconds
        setTimeout(() => {
            messageContainer.classList.add('hidden');
        }, 5000);
    }

    const socket = io();
    let token = localStorage.getItem('token');

    if (token) {
        fetchTodos();
    }

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('task_update', (data) => {
        console.log('Task update received:', data);
        fetchTodos();
        showMessage('info', 'Task list updated from the server');
    });

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            window.location.href = '/';
        } else {
            showMessage('error', 'Login failed: ' + data.message);
        }
    });
}
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Registration successful. Please log in.');
                window.location.href = '/auth/login';
            } else {
                alert('Registration failed: ' + data.message);
            }
        });
    }

    const addTodoForm = document.getElementById('add-todo-form');
    if (addTodoForm) {
        addTodoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const task = document.getElementById('new-todo').value;
            const response = await fetch('/todos/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ task }),
            });
            if (response.ok) {
                document.getElementById('new-todo').value = '';
                fetchTodos();
            } else if (response.status === 429) {
                showMessage('info', 'Too many requests, please try again later');
            } else {
                showMessage('error', 'Failed to add todo');
            }
        });
    }

    async function fetchTodos() {
        const response = await fetch('/todos/read', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        const data = await response.json();
        if (response.ok) {
            displayTodos(data.tasks);
            showMessage('success', 'Tasks fetched successfully');
        } else if (response.status === 429) {
            showMessage('info', 'Too many requests, please try again later');
        } else {
            showMessage('error', 'Failed to fetch todos');
        }
    }

    function displayTodos(todos) {
        const todoList = document.getElementById('todo-list');
        if (!todoList) return;
        
        todoList.innerHTML = '';
        todos.forEach(todo => {
            const todoItem = document.createElement('div');
            todoItem.className = 'flex items-center space-x-2 bg-white p-2 rounded shadow w-1/2';
            todoItem.setAttribute('data-id', todo.id); // Use id instead of _id
            todoItem.innerHTML = `
                <input type="checkbox" ${todo.completed ? 'checked' : ''} class="form-checkbox h-5 w-5 text-blue-600">
                <span class="${todo.completed ? 'line-through text-gray-500' : ''}">${todo.task}</span>
                <button class="delete-btn ml-auto bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600">Delete</button>
                <button class="edit-btn ml-auto bg-green-500 text-white px-2 py-1 rounded hover:bg-grey-400">Edit</button>
            `;
            todoList.appendChild(todoItem);
    
            const checkbox = todoItem.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', () => updateTodo(todo.id, { completed: checkbox.checked }));
    
            const deleteBtn = todoItem.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => deleteTodo(todo.id));
            const editBtn = todoItem.querySelector('.edit-btn');
            editBtn.addEventListener('click', () => editTodo(todo));
        });
    }

    function editTodo(todo) {
        const todoItem = document.querySelector(`[data-id="${todo.id}"]`);
        if (!todoItem) return;
        
        const taskSpan = todoItem.querySelector('span');
        const currentTask = taskSpan.textContent;
        const editBtn = todoItem.querySelector('.edit-btn');
    
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentTask;
        input.className = 'border p-2 rounded';
    
        function saveChanges() {
            const newTask = input.value.trim();
            if (newTask !== currentTask) {
                updateTodo(todo.id, { task: newTask })
                    .then(() => {
                        // Update the DOM with the new task after successful update
                        taskSpan.textContent = newTask;
                        input.replaceWith(taskSpan);
                        editBtn.textContent = 'Edit';
                        editBtn.removeEventListener('click', saveChanges);
                        editBtn.addEventListener('click', () => editTodo(todo));
                    })
                    .catch(() => {
                        alert('Failed to update todo');
                    });
            } else {
                input.replaceWith(taskSpan);
                editBtn.textContent = 'Edit';
                editBtn.removeEventListener('click', saveChanges);
                editBtn.addEventListener('click', () => editTodo(todo));
            }
        }
    
        taskSpan.replaceWith(input);
        input.focus();
    
        editBtn.textContent = 'Save';
        editBtn.removeEventListener('click', () => editTodo(todo));
        editBtn.addEventListener('click', saveChanges);
    
        input.addEventListener('blur', saveChanges);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                saveChanges();
            }
        });
    }
    
    async function updateTodo(id, update) {
        console.log(`Updating todo with ID: ${id}`);
        const response = await fetch(`/todos/tasks/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(update),
        });
         if(response.ok) {
            showMessage('success', 'Updated todo successfully');
        } else if (response.status === 429) {
            showMessage('info', 'Too many requests, please try again later');
        } else{
            showMessage('error', 'Failed to updated todo'); 
        }

        return response.json(); // Ensure to return the response for chaining in `editTodo`
    }
    
    async function deleteTodo(id) {
        const response = await fetch(`/todos/tasks/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        if (response.ok) {
            fetchTodos();
            showMessage('success', 'Task deleted successfully');
        } else if (response.status === 429) {
            showMessage('info', 'Too many requests, please try again later');
        } else {
            showMessage('error', 'Failed to delete todo');
        }
    }


});
