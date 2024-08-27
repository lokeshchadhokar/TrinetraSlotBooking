from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime, timedelta

app = Flask(__name__)


# Load booking data from JSON
def load_data():
    with open('bookings.json', 'r') as f:
        return json.load(f)


# Save booking data to JSON
def save_data(data):
    with open('bookings.json', 'w') as f:
        json.dump(data, f, indent=4)


# Initialize data
data = load_data()


# Generate upcoming dates
def get_upcoming_dates(days=8):
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(days)]


# Define the time slots for each mentor
mentor_time_slots = {
    "Chandra Sir": ["12pm-1pm", "1pm-2pm", "2pm-3pm", "3pm-4pm", "4pm-5pm", "5pm-6pm", "6pm-7pm"],
    "Tushar Sir": ["11am-12pm", "12pm-1pm", "1pm-2pm"],
    "Amir Sir": ["3pm-4pm", "4pm-5pm", "5pm-6pm"]
}


# Index page - Booking Form and Slots Display
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_name = request.form['user_name']
        technology = request.form['technology']
        company_name = request.form['company_name']
        round_name = request.form['round_name']
        mentor = request.form['mentor']
        booking_date = request.form['date']
        booking_time = request.form['time']
        invite_link = request.form['invite_link']

        # Generate unique code
        unique_code = f"{user_name[:3]}{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Update booking data
        if mentor not in data:
            data[mentor] = {}

        if booking_date not in data[mentor]:
            data[mentor][booking_date] = {}

        data[mentor][booking_date][booking_time] = {
            "status": "Booked",
            "user": user_name,
            "company": company_name,
            "round": round_name,
            "invite_link": invite_link,
            "unique_code": unique_code
        }

        save_data(data)

        return render_template('success.html', unique_code=unique_code)

    mentors = list(mentor_time_slots.keys())
    dates = get_upcoming_dates()
    return render_template('index.html', mentors=mentors, dates=dates, data=data, mentor_time_slots=mentor_time_slots)

# New route to handle booking cancellation
@app.route('/cancel', methods=['POST'])
def cancel_booking():
    unique_code = request.form['unique_code']

    # Search for the booking with the unique code
    for mentor in data:
        for date in data[mentor]:
            for time, booking in data[mentor][date].items():
                if booking.get('unique_code') == unique_code:
                    # Cancel the booking
                    del data[mentor][date][time]
                    save_data(data)
                    return f"Booking for {mentor} on {date} at {time} has been canceled."

    return "Invalid unique code. Please try again."

# Endpoint to get available times
@app.route('/available_times')
def available_times():
    mentor = request.args.get('mentor')
    date = request.args.get('date')

    available_times = []

    if mentor in mentor_time_slots:
        for time in mentor_time_slots[mentor]:
            if mentor in data and date in data[mentor] and time in data[mentor][date]:
                continue  # Skip booked times
            available_times.append(time)

    return jsonify({"available_times": available_times})
# New route to display the dashboard
@app.route('/dashboard')
def dashboard():
    # Create a copy of the data with unique codes removed
    sanitized_data = {}
    for mentor, dates in data.items():
        sanitized_data[mentor] = {}
        for date, times in dates.items():
            sanitized_data[mentor][date] = {}
            for time, booking in times.items():
                sanitized_data[mentor][date][time] = {k: v for k, v in booking.items() if k != 'unique_code'}

    return render_template('dashboard.html', data=sanitized_data, mentor_time_slots=mentor_time_slots)


@app.route('/table')
def table():
    return render_template('table.html', data=data, mentor_time_slots=mentor_time_slots)

if __name__ == '__main__':
    app.run(debug=True)
