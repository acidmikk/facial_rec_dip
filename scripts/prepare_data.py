import os
import pickle
import cv2
import face_recognition
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from main.models import Event, PersonImage
from imutils import paths


def prepare_data(event_id):
    # Получаем мероприятие по ID
    event = Event.objects.get(id=event_id)
    participants = event.attendees.all()

    knownEncodings = []
    knownNames = []

    # Перебираем всех участников мероприятия
    for participant in participants:
        images = PersonImage.objects.filter(person=participant)

        for image in images:
            # Загрузка изображения из базы данных
            image_path = image.image.path
            name = f"{participant.last_name}_{participant.first_name}"

            # Загрузка и обработка изображения
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model='hog')
            encodings = face_recognition.face_encodings(rgb, boxes)

            # Сохранение эмбеддингов и имен
            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)

    # Сохранение эмбеддингов в файл
    data = {"encodings": knownEncodings, "names": knownNames}
    output_path = os.path.join(settings.MEDIA_ROOT, f"event_{event_id}_encodings.pkl")
    with open(output_path, "wb") as f:
        f.write(pickle.dumps(data))


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
    import django

    django.setup()
    # Пример вызова скрипта для конкретного мероприятия
    prepare_data(event_id=1)
