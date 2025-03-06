from models import session, Service, Appointment


def save_services(services):
    """
    Saves the list of services to the database.
    """
    for number, name, service_url in services:
        service = session.query(Service).filter_by(number=number).first()
        if not service:
            service = Service(number=number, name=name, url=service_url)
            session.add(service)
    session.commit()


def save_appointments(appointments):
    """
    Saves appointments to the database for services that are already in the database.
    """
    for number, status, additional_info, last_checked in appointments:
        appointment = session.query(Appointment).filter_by(
            service_number=number).first()
        if appointment:
            appointment.status = status
            appointment.additional_info = additional_info
            appointment.last_checked = last_checked
        else:
            appointment = Appointment(service_number=number, status=status,
                                      additional_info=additional_info, last_checked=last_checked)
            session.add(appointment)
    session.commit()


def get_appointments_new():
    """
    Fetches all stored appointments from the database.
    """
    appointments = session.query(Appointment).all()
    return [(appt.service_number, appt.status, appt.additional_info, appt.last_checked) for appt in appointments]
