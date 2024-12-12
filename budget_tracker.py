from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import logging

app = Flask(__name__)
app.jinja_env.globals.update(enumerate=enumerate)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define absolute path to JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, 'budget_data.json')

def load_budget_data(filepath):
    if not os.path.exists(filepath):
        logging.debug(f"File {filepath} not found. Creating a new budget file.")
        return 0, []

    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            logging.debug(f"Loaded budget data: {data}")
    except json.JSONDecodeError:
        logging.debug(f"Error reading {filepath}. Creating a new budget file.")
        return 0, []

    initial_budget = data.get("budget", 0)
    expenses = data.get("expenses", [])
    return initial_budget, expenses

def save_budget_data(filepath, budget, expenses):
    data = {
        "budget": budget,
        "expenses": expenses
    }
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)
    logging.debug("Budget data saved.")

@app.route('/')
def index():
    initial_budget, expenses = load_budget_data(JSON_FILE)
    total_spent = sum(expense['amount'] for expense in expenses)
    remaining_budget = initial_budget - total_spent
    logging.debug(f"Initial Budget: {initial_budget}, Total Spent: {total_spent}, Remaining Budget: {remaining_budget}")
    return render_template('index.html', budget=initial_budget, expenses=expenses, total_spent=total_spent, remaining_budget=remaining_budget)

@app.route('/add', methods=['POST'])
def add_expense():
    try:
        description = request.form['description']
        amount = float(request.form['amount'])
        logging.debug(f"Received description: {description}, amount: {amount}")

        initial_budget, expenses = load_budget_data(JSON_FILE)
        expenses.append({"description": description, "amount": amount})
        logging.debug(f"Updated expenses: {expenses}")

        save_budget_data(JSON_FILE, initial_budget, expenses)
        logging.debug("Budget data saved successfully")
        return redirect(url_for('index'))
    except Exception as e:
        logging.error("Error adding expense: %s", e)
        return "Internal Server Error", 500

@app.route('/delete/<int:index>', methods=['POST'])
def delete_expense(index):
    try:
        initial_budget, expenses = load_budget_data(JSON_FILE)
        if 0 <= index < len(expenses):
            expenses.pop(index)
            save_budget_data(JSON_FILE, initial_budget, expenses)
        logging.debug("Expense deleted successfully")
        return redirect(url_for('index'))
    except Exception as e:
        logging.error("Error deleting expense: %s", e)
        return "Internal Server Error", 500

@app.route('/edit/<int:index>', methods=['POST'])
def edit_expense(index):
    try:
        description = request.form['description']
        amount = float(request.form['amount'])
        logging.debug(f"Received new description: {description}, amount: {amount}")

        initial_budget, expenses = load_budget_data(JSON_FILE)
        if 0 <= index < len(expenses):
            expenses[index] = {"description": description, "amount": amount}
            save_budget_data(JSON_FILE, initial_budget, expenses)
        logging.debug("Expense edited successfully")
        return redirect(url_for('index'))
    except Exception as e:
        logging.error("Error editing expense: %s", e)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
