import random


def generate_unique_visitor_id():
    from .models import Consultation
    while True:
        visitor_id = random.randint(10000000, 99999999)  # 8 digits
        if not Consultation.objects.filter(visitor_id=visitor_id).exists():
            return visitor_id