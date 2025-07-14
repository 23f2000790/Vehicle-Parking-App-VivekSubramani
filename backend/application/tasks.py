from celery import shared_task
import datetime
from .models import * 
import csv
from jinja2 import Template
from .mail import send_email
import requests


@shared_task(ignore_results = False, name = "download_csv_report")
def csv_report():
    user_details = Reservation.query.all()
    csv_file_name = f"card_{datetime.datetime.now().strftime('%s')}.csv"
    with open(f'static/{csv_file_name}', 'w', newline="") as csvfile:
        sr_no = 1
        user_csv = csv.writer(csvfile, delimiter=',')
        user_csv.writerow(['Sr No.', 'Lot ID', 'Spot ID', 'Price/Hour', 'Address', 'Parking Time', 'Leaving Time', 'Parking Charges', 'Vehicle Name', 'Vehicle Number'])
        for i in user_details:
            this_card = [sr_no, i.lotid, i.spotid, i.priceperhour, i.address, i.parkingts, i.leavingts, i.price, i.vehiclename, i.vehiclenp]
            user_csv.writerow(this_card)
            sr_no += 1

    return csv_file_name



@shared_task(ignore_results=False, name="monthly_report")
def monthly_report():
    users = Users.query.all()
    for user in users[1:]:
        user_data = {}
        user_data['username'] = user.username
        user_data['email'] = user.email
        details = []
        user_details = Reservation.query.filter_by(status = True, userid=user.id)
        for i in user_details:
            obj = {}
            obj["address"] = i.address
            obj["spotid"] = i.spotid
            obj["vehiclename"] = i.vehiclename
            obj["vehiclenp"] = i.vehiclenp
            details.append(obj)

        user_data["details"] = details

        mail_template = """
        <h3>Dear {{ user_data.username }}</h3>
        <p>Please find your active Spot Reservations</p>
        <p>Visit our ecard app at <a href="http://127.0.0.1:5173">http://127.0.0.1:5173</a> for details.</p>
        <table>
            <tr>
                <th>Address</th>
                <th>Spot ID</th>
                <th>Vehicle</th>
                <th>Vechile No.</th>
            </tr>
            {% for i in user_data.details %}
            <tr>
                <td>{{ i.address }}</td>
                <td>{{ i.spotid }}</td>
                <td>{{ i.vehiclename }}</td>
                <td>{{ i.vehiclenp }}</td>
            </tr>
            {% endfor %}
        </table>
        <br>
        <p>Regards,<br>Vehicle Parking App</p>
        """

        message = Template(mail_template).render(user_data=user_data)
        send_email(
            user.email,
            subject="Monthly active reservation report - Vehicle Parking",
            message=message
        )

    return "Monthly reports sent"



@shared_task(ignore_results=False, name="generate_msg")
def generate_msg(username, cardname):
    text = f"Hi {username}, your card '{cardname}' has been generated. Please check the app at http://127.0.0.1:5173"
    
    response = requests.post(
        "https://chat.googleapis.com/v1/spaces/AAAAMGxFsof/messages?key=API_KEY&token=TOKEN",
        json={"text": text}
    )
    
    print(response.status_code)
    return "The delivery is sent to user"

