import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
MENU_FILE = 'menu.json'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, ' 'r') as f:
            return json.load(f)
    return []

def save_menu(menu):
    with open(MENU_FILE, 'w') as f:
        json.dump(menu, f)

@app.route('/api/menu', methods=['GET'])
def get_menu():
    return jsonify(load_menu())

@app.route('/api/upload', methods=['POST'])
def upload_menu_item():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image = request.files['image']

    if not image:
        return jsonify({"error": "Image required"}), 400

    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    menu = load_menu()
    menu.append({
        "name": name,
        "description": description,
        "price": price,
        "image": f"uploads/{filename}"
    })
    save_menu(menu)
    return jsonify({"status": "added"}), 200

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/api/edit/<int:index>', methods=['POST'])
def edit_dish(index):
    menu = load_menu()
    data = request.json
    if index < len(menu):
        menu[index]['name'] = data.get('name', menu[index]['name'])
        menu[index]['description'] = data.get('description', menu[index]['description'])
        menu[index]['price'] = data.get('price', menu[index]['price'])
        save_menu(menu)
        return jsonify({"status": "updated"}), 200
    return jsonify({"error": "Invalid index"}), 404

@app.route('/api/delete/<int:index>', methods=['DELETE'])
def delete_dish(index):
    menu = load_menu()
    if index < len(menu):
        menu.pop(index)
        save_menu(menu)
        return jsonify({"status": "deleted"}), 200
    return jsonify({"error": "Invalid index"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
