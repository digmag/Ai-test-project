#!/usr/bin/env python3
"""
Hospital Management Application - Рефакторинг
"""

import logging
import os
import redis
import tornado.ioloop
import tornado.web
from tornado.options import parse_command_line
from typing import Dict, List, Optional, Any
import json

# Настройки порта
PORT = 8888

class RedisManager:
    """Класс для управления подключением к Redis"""

    def __init__(self):
        self.connection = redis.StrictRedis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=0,
            decode_responses=False  # Оставляем как есть для совместимости
        )

    def get_connection(self):
        return self.connection


# Глобальный экземпляр Redis
redis_manager = RedisManager()
r = redis_manager.get_connection()


class BaseHandler(tornado.web.RequestHandler):
    """Базовый обработчик с общими методами"""

    def get_redis(self):
        return r

    def handle_redis_error(self, error: Exception, message: str = "Redis connection refused"):
        """Обработка ошибок Redis"""
        logging.error(f"Redis error: {str(error)}")
        self.set_status(400)
        self.write(message)

    def validate_required_fields(self, fields_func, required: List[str]) -> bool:
        """Проверка обязательных полей"""
        for field in required:
            try:
                value = fields_func(field)
                if not value:
                    return False
            except:
                return False
        return True


class MainHandler(BaseHandler):
    def get(self):
        self.render('templates/index.html')


class HospitalHandler(BaseHandler):
    MODEL_NAME = "hospital"
    REQUIRED_FIELDS = ["name", "address"]

    def get(self):
        items = []
        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID")
            if auto_id:
                auto_id = auto_id.decode()

                for i in range(int(auto_id)):
                    result = self.get_redis().hgetall(f"{self.MODEL_NAME}:{i}")
                    if result:
                        items.append(result)

            self.render(f'templates/{self.MODEL_NAME}.html', items=items)
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)

    def post(self):
        # Получаем аргументы
        data = {
            'name': self.get_argument('name'),
            'address': self.get_argument('address'),
            'phone': self.get_argument('phone'),
            'beds_number': self.get_argument('beds_number')
        }

        # Проверяем обязательные поля
        if not self.validate_required_fields(self.get_argument, self.REQUIRED_FIELDS):
            self.set_status(400)
            self.write(f"{self.MODEL_NAME.capitalize()} name and address required")
            return

        logging.debug(f"{data['name']} {data['address']} {data['phone']} {data['beds_number']}")

        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID").decode()

            # Сохраняем данные
            fields_set = 0
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "name", data['name'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "address", data['address'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "phone", data['phone'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "beds_number", data['beds_number'])

            self.get_redis().incr(f"{self.MODEL_NAME}:autoID")
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)
        else:
            if fields_set != 4:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                self.write(f'OK: ID {auto_id} for {data["name"]}')


class DoctorHandler(BaseHandler):
    MODEL_NAME = "doctor"
    REQUIRED_FIELDS = ["surname", "profession"]

    def get(self):
        items = []
        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID")
            if auto_id:
                auto_id = auto_id.decode()

                for i in range(int(auto_id)):
                    result = self.get_redis().hgetall(f"{self.MODEL_NAME}:{i}")
                    if result:
                        items.append(result)

            self.render(f'templates/{self.MODEL_NAME}.html', items=items)
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)

    def post(self):
        # Получаем аргументы
        data = {
            'surname': self.get_argument('surname'),
            'profession': self.get_argument('profession'),
            'hospital_ID': self.get_argument('hospital_ID')
        }

        # Проверяем обязательные поля
        if not self.validate_required_fields(self.get_argument, self.REQUIRED_FIELDS):
            self.set_status(400)
            self.write("Surname and profession required")
            return

        logging.debug(f"{data['surname']} {data['profession']}")

        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID").decode()

            # Проверяем существование больницы, если указан ID
            if data['hospital_ID']:
                hospital = self.get_redis().hgetall(f"hospital:{data['hospital_ID']}")
                if not hospital:
                    self.set_status(400)
                    self.write("No hospital with such ID")
                    return

            # Сохраняем данные
            fields_set = 0
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "surname", data['surname'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "profession", data['profession'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "hospital_ID", data['hospital_ID'])

            self.get_redis().incr(f"{self.MODEL_NAME}:autoID")
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)
        else:
            if fields_set != 3:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                self.write(f'OK: ID {auto_id} for {data["surname"]}')


class PatientHandler(BaseHandler):
    MODEL_NAME = "patient"
    REQUIRED_FIELDS = ["surname", "born_date", "sex", "mpn"]

    def get(self):
        items = []
        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID")
            if auto_id:
                auto_id = auto_id.decode()

                for i in range(int(auto_id)):
                    result = self.get_redis().hgetall(f"{self.MODEL_NAME}:{i}")
                    if result:
                        items.append(result)

            self.render(f'templates/{self.MODEL_NAME}.html', items=items)
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)

    def post(self):
        # Получаем аргументы
        data = {
            'surname': self.get_argument('surname'),
            'born_date': self.get_argument('born_date'),
            'sex': self.get_argument('sex'),
            'mpn': self.get_argument('mpn')
        }

        # Проверяем обязательные поля
        if not self.validate_required_fields(self.get_argument, self.REQUIRED_FIELDS):
            self.set_status(400)
            self.write("All fields required")
            return

        # Проверяем пол
        if data['sex'] not in ['M', 'F']:
            self.set_status(400)
            self.write("Sex must be 'M' or 'F'")
            return

        logging.debug(f"{data['surname']} {data['born_date']} {data['sex']} {data['mpn']}")

        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID").decode()

            # Сохраняем данные
            fields_set = 0
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "surname", data['surname'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "born_date", data['born_date'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "sex", data['sex'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "mpn", data['mpn'])

            self.get_redis().incr(f"{self.MODEL_NAME}:autoID")
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)
        else:
            if fields_set != 4:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                self.write(f'OK: ID {auto_id} for {data["surname"]}')


class DiagnosisHandler(BaseHandler):
    MODEL_NAME = "diagnosis"
    REQUIRED_FIELDS = ["patient_ID", "type"]

    def get(self):
        items = []
        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID")
            if auto_id:
                auto_id = auto_id.decode()

                for i in range(int(auto_id)):
                    result = self.get_redis().hgetall(f"{self.MODEL_NAME}:{i}")
                    if result:
                        items.append(result)

            self.render(f'templates/{self.MODEL_NAME}.html', items=items)
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)

    def post(self):
        # Получаем аргументы
        data = {
            'patient_ID': self.get_argument('patient_ID'),
            'type': self.get_argument('type'),
            'information': self.get_argument('information')
        }

        # Проверяем обязательные поля
        if not self.validate_required_fields(self.get_argument, self.REQUIRED_FIELDS):
            self.set_status(400)
            self.write("Patiend ID and diagnosis type required")
            return

        logging.debug(f"{data['patient_ID']} {data['type']} {data['information']}")

        try:
            auto_id = self.get_redis().get(f"{self.MODEL_NAME}:autoID").decode()

            # Проверяем существование пациента
            patient = self.get_redis().hgetall(f"patient:{data['patient_ID']}")
            if not patient:
                self.set_status(400)
                self.write("No patient with such ID")
                return

            # Сохраняем данные
            fields_set = 0
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "patient_ID", data['patient_ID'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "type", data['type'])
            fields_set += self.get_redis().hset(f"{self.MODEL_NAME}:{auto_id}", "information", data['information'])

            self.get_redis().incr(f"{self.MODEL_NAME}:autoID")
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)
        else:
            if fields_set != 3:
                self.set_status(500)
                self.write("Something went terribly wrong")
            else:
                patient_surname = patient.get(b'surname', b'Unknown').decode()
                self.write(f'OK: ID {auto_id} for patient {patient_surname}')


class DoctorPatientHandler(BaseHandler):
    MODEL_NAME = "doctor-patient"

    def get(self):
        items = {}
        try:
            auto_id = self.get_redis().get("doctor:autoID")
            if auto_id:
                auto_id = auto_id.decode()

                for i in range(int(auto_id)):
                    result = self.get_redis().smembers(f"doctor-patient:{i}")
                    if result:
                        items[i] = result

            self.render(f'templates/{self.MODEL_NAME}.html', items=items)
        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)

    def post(self):
        # Получаем аргументы
        doctor_ID = self.get_argument('doctor_ID')
        patient_ID = self.get_argument('patient_ID')

        if not doctor_ID or not patient_ID:
            self.set_status(400)
            self.write("ID required")
            return

        logging.debug(f"{doctor_ID} {patient_ID}")

        try:
            patient = self.get_redis().hgetall(f"patient:{patient_ID}")
            doctor = self.get_redis().hgetall(f"doctor:{doctor_ID}")

            if not patient or not doctor:
                self.set_status(400)
                self.write("No such ID for doctor or patient")
                return

            self.get_redis().sadd(f"doctor-patient:{doctor_ID}", patient_ID)

        except redis.exceptions.ConnectionError as e:
            self.handle_redis_error(e)
        else:
            self.write(f"OK: doctor ID: {doctor_ID}, patient ID: {patient_ID}")


class AnalyticsHandler(BaseHandler):
    """Обработчик для аналитики"""

    def get(self):
        """Получение аналитической информации"""
        try:
            analytics = {}

            # Подсчет количества сущностей
            analytics['hospital_count'] = int(r.get("hospital:autoID").decode()) - 1 if r.get("hospital:autoID") else 0
            analytics['doctor_count'] = int(r.get("doctor:autoID").decode()) - 1 if r.get("doctor:autoID") else 0
            analytics['patient_count'] = int(r.get("patient:autoID").decode()) - 1 if r.get("patient:autoID") else 0
            analytics['diagnosis_count'] = int(r.get("diagnosis:autoID").decode()) - 1 if r.get("diagnosis:autoID") else 0

            # Подсчет связей врач-пациент
            doctor_auto_id = int(r.get("doctor:autoID").decode()) if r.get("doctor:autoID") else 0
            doctor_patient_count = 0
            for i in range(doctor_auto_id):
                connections = r.smembers(f"doctor-patient:{i}")
                doctor_patient_count += len(connections)

            analytics['doctor_patient_connections'] = doctor_patient_count

            # Дополнительная аналитика
            analytics['total_entities'] = (
                analytics['hospital_count'] +
                analytics['doctor_count'] +
                analytics['patient_count'] +
                analytics['diagnosis_count']
            )

            # Средняя нагрузка на одного врача
            if analytics['doctor_count'] > 0:
                analytics['avg_patients_per_doctor'] = round(analytics['doctor_patient_connections'] / analytics['doctor_count'], 2)
            else:
                analytics['avg_patients_per_doctor'] = 0

            # Среднее количество диагнозов на пациента
            if analytics['patient_count'] > 0:
                analytics['avg_diagnoses_per_patient'] = round(analytics['diagnosis_count'] / analytics['patient_count'], 2)
            else:
                analytics['avg_diagnoses_per_patient'] = 0

            # Подсчет количества сущностей в каждой больнице
            hospitals_with_stats = []
            for i in range(analytics['hospital_count']):
                hospital = r.hgetall(f"hospital:{i}")
                if hospital:
                    hospital_name = hospital.get(b'name', b'Unknown').decode()

                    # Подсчет врачей в этой больнице
                    doctors_in_hospital = 0
                    for j in range(analytics['doctor_count']):
                        doctor = r.hgetall(f"doctor:{j}")
                        if doctor and doctor.get(b'hospital_ID', b'').decode() == str(i):
                            doctors_in_hospital += 1

                    hospitals_with_stats.append({
                        'id': i,
                        'name': hospital_name,
                        'doctors_count': doctors_in_hospital
                    })

            analytics['hospitals_with_stats'] = hospitals_with_stats

            self.set_header("Content-Type", "application/json")
            self.write(analytics)

        except Exception as e:
            self.handle_redis_error(e, "Error retrieving analytics")


def init_db():
    """Инициализация базы данных"""
    db_initiated = r.get("db_initiated")
    if not db_initiated:
        r.set("hospital:autoID", 1)
        r.set("doctor:autoID", 1)
        r.set("patient:autoID", 1)
        r.set("diagnosis:autoID", 1)
        r.set("db_initiated", 1)


def make_app():
    """Создание приложения"""
    return tornado.web.Application([
        (r"/", MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r"/hospital", HospitalHandler),
        (r"/doctor", DoctorHandler),
        (r"/patient", PatientHandler),
        (r"/diagnosis", DiagnosisHandler),
        (r"/doctor-patient", DoctorPatientHandler),
        (r"/analytics", AnalyticsHandler)  # Новый эндпоинт для аналитики
    ],
    autoreload=True,
    debug=True,
    compiled_template_cache=False,
    serve_traceback=True)


if __name__ == "__main__":
    init_db()
    app = make_app()
    app.listen(PORT)
    tornado.options.parse_command_line()
    logging.info("Listening on " + str(PORT))
    tornado.ioloop.IOLoop.current().start()