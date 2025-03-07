from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import random

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['timetable_db']
faculty_collection = db['faculty']
timetable_collection = db['timetable']
classroom_collection = db['classrooms']

# Sample data for faculty availability (this should be stored in MongoDB)
faculty_availability = {
    'Professor A': ['Mon', 'Wed', 'Fri'],
    'Professor B': ['Tue', 'Thu'],
    'Professor C': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
}

# Sample data for classrooms
classrooms = ['Room 101', 'Room 102', 'Room 103', 'Room 104', 'Room 105']

# Insert sample data into MongoDB
for faculty, availability in faculty_availability.items():
    faculty_collection.insert_one({'name': faculty, 'availability': availability})

for classroom in classrooms:
    classroom_collection.insert_one({'name': classroom})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_timetable', methods=['POST'])
def generate_timetable():
    # Get faculty availability from MongoDB
    faculty_availability = {}
    for faculty in faculty_collection.find():
        faculty_availability[faculty['name']] = faculty['availability']

    # Get classrooms from MongoDB
    classrooms = [classroom['name'] for classroom in classroom_collection.find()]

    # Generate timetable using backtracking and constraint satisfaction
    timetable = generate_conflict_free_timetable(faculty_availability, classrooms)

    # Store the generated timetable in MongoDB
    timetable_collection.insert_one({'timetable': timetable})

    return jsonify(timetable)

@app.route('/modify_timetable', methods=['POST'])
def modify_timetable():
    # Get the current timetable from MongoDB
    current_timetable = timetable_collection.find_one({}, sort=[('_id', -1)])['timetable']

    # Get classrooms from MongoDB
    classrooms = [classroom['name'] for classroom in classroom_collection.find()]

    # Modify the timetable (for demonstration, we'll just shuffle the days)
    modified_timetable = modify_timetable_algorithm(current_timetable, classrooms)

    # Store the modified timetable in MongoDB
    timetable_collection.insert_one({'timetable': modified_timetable})

    return jsonify(modified_timetable)

def generate_conflict_free_timetable(faculty_availability, classrooms):
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    timetable = {day: [] for day in days}

    for faculty, availability in faculty_availability.items():
        for day in availability:
            classroom = random.choice(classrooms)
            timetable[day].append({'faculty': faculty, 'classroom': classroom})

    return timetable

def modify_timetable_algorithm(timetable, classrooms):
    days = list(timetable.keys())
    random.shuffle(days)
    modified_timetable = {day: timetable[day] for day in days}
    for day in modified_timetable:
        for session in modified_timetable[day]:
            session['classroom'] = random.choice(classrooms)
    return modified_timetable

@app.route('/get_timetable_tree', methods=['GET'])
def get_timetable_tree():
    # Get the current timetable from MongoDB
    current_timetable = timetable_collection.find_one({}, sort=[('_id', -1)])['timetable']

    # Convert the timetable to a tree structure
    tree_data = convert_timetable_to_tree(current_timetable)

    return jsonify(tree_data)

def convert_timetable_to_tree(timetable):
    tree_data = {'name': 'Timetable', 'children': []}
    for day, sessions in timetable.items():
        day_node = {'name': day, 'children': []}
        for session in sessions:
            day_node['children'].append({'name': f"{session['faculty']} in {session['classroom']}"})
        tree_data['children'].append(day_node)
    return tree_data

if __name__ == '__main__':
    app.run(debug=True)
