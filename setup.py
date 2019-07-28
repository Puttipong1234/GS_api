from Project.connect import create_connection
from Project.models import Session , db

if __name__ == '__main__':
    create_connection('Stock')
    current_sess = Session('none')
    db.session.add(current_sess)
    db.session.commit()
    