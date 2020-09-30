
import json
from app import db, Teacher


def get_teachers_list():
    with open('teachers.json', 'r') as f:
        contents = f.read()
        teachers_list = json.loads(contents)
    for teacher in teachers_list:
        teacher_add = Teacher(
            id = teacher['id'],
            name = teacher['name'],
            about = teacher['about'],
            rating = teacher['rating'],
            picture = teacher['picture'],
            price = teacher['price'],
            goals=";".join(teacher["goals"]),
            free=teacher['free']
        )
        
        db.session.add(teacher_add)
        db.session.commit()
   



