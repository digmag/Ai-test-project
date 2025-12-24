#!/usr/bin/env python3
"""
Unit-тесты для приложения hospital management
"""
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
import redis
import tornado.testing
import sys
import tempfile
from tornado.httputil import HTTPServerRequest
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.httputil import HTTPConnection
import asyncio

# Импортируем наше приложение
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main


class TestHospitalHandler(unittest.TestCase):
    """Тесты для обработчика больниц"""
    
    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r
        
        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis
        
        # Инициализируем тестовую базу данных
        main.init_db()
        
    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis
        
    def test_get_hospitals_empty(self):
        """Тест получения списка больниц когда он пуст"""
        # Настраиваем мок для возврата ID
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.hgetall.return_value = {}
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/hospital"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.HospitalHandler(app, request)
        
        # Мокаем методы для избежания HTTP-ответа
        handler.write = MagicMock()
        handler.render = MagicMock()
        
        # Вызываем метод get
        handler.get()
        
        # Проверяем, что render был вызван
        handler.render.assert_called_once()
        args, kwargs = handler.render.call_args
        self.assertEqual(args[0], 'templates/hospital.html')
        self.assertIn('items', kwargs)
        self.assertEqual(len(kwargs['items']), 0)
        
    def test_get_hospitals_with_data(self):
        """Тест получения списка больниц с данными"""
        # Настраиваем мок для возврата ID и данных
        self.mock_redis.get.return_value = b'1'
        self.mock_redis.hgetall.return_value = {
            b'name': b'TestHospital',
            b'address': b'TestAddress',
            b'phone': b'123456789',
            b'beds_number': b'50'
        }
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/hospital"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.HospitalHandler(app, request)
        
        # Мокаем методы для избежания HTTP-ответа
        handler.write = MagicMock()
        handler.render = MagicMock()
        
        # Вызываем метод get
        handler.get()
        
        # Проверяем, что render был вызван
        handler.render.assert_called_once()
        args, kwargs = handler.render.call_args
        self.assertEqual(args[0], 'templates/hospital.html')
        self.assertIn('items', kwargs)
        self.assertEqual(len(kwargs['items']), 1)
        
    def test_create_hospital_success(self):
        """Тест успешного создания больницы"""
        # Настраиваем мок для возврата ID
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.incr.return_value = 1
        self.mock_redis.hset.side_effect = [1, 1, 1, 1]  # name, address, phone, beds_number
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/hospital"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.HospitalHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'name': 'TestHospital',
            'address': 'TestAddress',
            'phone': '123456789',
            'beds_number': '50'
        }[arg]
        
        # Мокаем метод write для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что write был вызван с правильным сообщением
        handler.write.assert_called_once()
        args, kwargs = handler.write.call_args
        self.assertIn('OK: ID 0 for TestHospital', args[0])
        
        # Проверяем, что были вызваны методы Redis
        self.mock_redis.get.assert_called_with("hospital:autoID")
        self.assertEqual(self.mock_redis.hset.call_count, 4)  # name, address, phone, beds_number
        self.mock_redis.incr.assert_called_with("hospital:autoID")
        
    def test_create_hospital_missing_required_fields(self):
        """Тест создания больницы с отсутствующими обязательными полями"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/hospital"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.HospitalHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'name': 'TestHospital',
            'address': '',  # пустой адрес
            'phone': '123456789',
            'beds_number': '50'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Hospital name and address required")


class TestDoctorHandler(unittest.TestCase):
    """Тесты для обработчика врачей"""
    
    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r
        
        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis
        
        # Инициализируем тестовую базу данных
        main.init_db()
        
    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis
        
    def test_create_doctor_success(self):
        """Тест успешного создания врача"""
        # Настраиваем мок для возврата ID
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.incr.return_value = 1
        self.mock_redis.hset.side_effect = [1, 1, 1]  # surname, profession, hospital_ID
        self.mock_redis.hgetall.return_value = {}  # Пустой результат для проверки больницы
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestDoctor',
            'profession': 'Surgeon',
            'hospital_ID': ''
        }[arg]
        
        # Мокаем метод write для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что write был вызван с правильным сообщением
        handler.write.assert_called_once()
        args, kwargs = handler.write.call_args
        self.assertIn('OK: ID 0 for TestDoctor', args[0])
        
        # Проверяем, что были вызваны методы Redis
        self.mock_redis.get.assert_called_with("doctor:autoID")
        self.assertEqual(self.mock_redis.hset.call_count, 3)  # surname, profession, hospital_ID
        self.mock_redis.incr.assert_called_with("doctor:autoID")
        
    def test_create_doctor_with_valid_hospital(self):
        """Тест создания врача с указанием существующей больницы"""
        # Настраиваем мок для возврата ID и существующей больницы
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.incr.return_value = 1
        self.mock_redis.hset.side_effect = [1, 1, 1]  # surname, profession, hospital_ID
        self.mock_redis.hgetall.return_value = {b'name': b'ValidHospital'}  # Существующая больница
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestDoctor',
            'profession': 'Surgeon',
            'hospital_ID': '0'
        }[arg]
        
        # Мокаем метод write для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что write был вызван с правильным сообщением
        handler.write.assert_called_once()
        args, kwargs = handler.write.call_args
        self.assertIn('OK: ID 0 for TestDoctor', args[0])
        
    def test_create_doctor_with_invalid_hospital(self):
        """Тест создания врача с указанием несуществующей больницы"""
        # Настраиваем мок для возврата ID и пустой больницы
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.hgetall.return_value = {}  # Пустой результат для несуществующей больницы
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestDoctor',
            'profession': 'Surgeon',
            'hospital_ID': '999'
        }[arg]
        
        # Мокаем метод write для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("No hospital with such ID")
        
    def test_create_doctor_missing_required_fields(self):
        """Тест создания врача с отсутствующими обязательными полями"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestDoctor',
            'profession': '',  # пустая профессия
            'hospital_ID': ''
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Surname and profession required")


class TestPatientHandler(unittest.TestCase):
    """Тесты для обработчика пациентов"""
    
    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r
        
        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis
        
        # Инициализируем тестовую базу данных
        main.init_db()
        
    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis
        
    def test_create_patient_success(self):
        """Тест успешного создания пациента"""
        # Настраиваем мок для возврата ID
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.incr.return_value = 1
        self.mock_redis.hset.side_effect = [1, 1, 1, 1]  # surname, born_date, sex, mpn
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.PatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestPatient',
            'born_date': '1990-01-01',
            'sex': 'M',
            'mpn': '123456'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что write был вызван с правильным сообщением
        handler.write.assert_called_once()
        args, kwargs = handler.write.call_args
        self.assertIn('OK: ID 0 for TestPatient', args[0])
        
        # Проверяем, что были вызваны методы Redis
        self.mock_redis.get.assert_called_with("patient:autoID")
        self.assertEqual(self.mock_redis.hset.call_count, 4)  # surname, born_date, sex, mpn
        self.mock_redis.incr.assert_called_with("patient:autoID")
        
    def test_create_patient_invalid_sex(self):
        """Тест создания пациента с неправильным полом"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.PatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestPatient',
            'born_date': '1990-01-01',
            'sex': 'X',  # неправильный пол
            'mpn': '123456'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Sex must be 'M' or 'F'")
        
    def test_create_patient_missing_required_fields(self):
        """Тест создания пациента с отсутствующими обязательными полями"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.PatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'surname': 'TestPatient',
            'born_date': '',  # пустая дата рождения
            'sex': 'M',
            'mpn': '123456'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("All fields required")


class TestDiagnosisHandler(unittest.TestCase):
    """Тесты для обработчика диагнозов"""
    
    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r
        
        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis
        
        # Инициализируем тестовую базу данных
        main.init_db()
        
    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis
        
    def test_create_diagnosis_success(self):
        """Тест успешного создания диагноза"""
        # Настраиваем мок для возврата ID и существующего пациента
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.incr.return_value = 1
        self.mock_redis.hset.side_effect = [1, 1, 1]  # patient_ID, type, information
        self.mock_redis.hgetall.return_value = {b'surname': b'TestPatient'}  # Существующий пациент
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/diagnosis"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DiagnosisHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'patient_ID': '0',
            'type': 'Flu',
            'information': 'Common flu'
        }[arg]
        
        # Мокаем метод write для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что write был вызван с правильным сообщением
        handler.write.assert_called_once()
        args, kwargs = handler.write.call_args
        self.assertIn('OK: ID 0 for patient TestPatient', args[0])
        
        # Проверяем, что были вызваны методы Redis
        self.mock_redis.get.assert_called_with("diagnosis:autoID")
        self.assertEqual(self.mock_redis.hset.call_count, 3)  # patient_ID, type, information
        self.mock_redis.incr.assert_called_with("diagnosis:autoID")
        
    def test_create_diagnosis_with_invalid_patient(self):
        """Тест создания диагноза для несуществующего пациента"""
        # Настраиваем мок для возврата ID и пустого пациента
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.hgetall.return_value = {}  # Пустой результат для несуществующего пациента
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/diagnosis"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DiagnosisHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'patient_ID': '999',  # несуществующий пациент
            'type': 'Flu',
            'information': 'Common flu'
        }[arg]
        
        # Мокаем метод write для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("No patient with such ID")
        
    def test_create_diagnosis_missing_required_fields(self):
        """Тест создания диагноза с отсутствующими обязательными полями"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/diagnosis"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DiagnosisHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'patient_ID': '0',
            'type': '',  # пустой тип
            'information': 'Common flu'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Patiend ID and diagnosis type required")


class TestDoctorPatientHandler(unittest.TestCase):
    """Тесты для обработчика связей врач-пациент"""
    
    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r
        
        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis
        
        # Инициализируем тестовую базу данных
        main.init_db()
        
    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis
        
    def test_create_doctor_patient_success(self):
        """Тест успешного создания связи врач-пациент"""
        # Настраиваем мок для возврата существующих врачей и пациентов
        self.mock_redis.hgetall.side_effect = [
            {b'surname': b'TestPatient'},  # Первый вызов - пациент
            {b'surname': b'TestDoctor'}    # Второй вызов - врач
        ]
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor-patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorPatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'doctor_ID': '0',
            'patient_ID': '0'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что write был вызван с правильным сообщением
        handler.write.assert_called_once_with("OK: doctor ID: 0, patient ID: 0")
        
        # Проверяем, что были вызваны методы Redis
        self.mock_redis.sadd.assert_called_once_with("doctor-patient:0", "0")
        
    def test_create_doctor_patient_with_invalid_doctor(self):
        """Тест создания связи с несуществующим врачом"""
        # Настраиваем мок для возврата существующего пациента и пустого врача
        self.mock_redis.hgetall.side_effect = [
            {b'surname': b'TestPatient'},  # Первый вызов - пациент
            {}                           # Второй вызов - пустой (несуществующий) врач
        ]
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor-patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorPatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'doctor_ID': '999',  # несуществующий врач
            'patient_ID': '0'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("No such ID for doctor or patient")
        
    def test_create_doctor_patient_with_invalid_patient(self):
        """Тест создания связи с несуществующим пациентом"""
        # Настраиваем мок для возврата пустого пациента и существующего врача
        self.mock_redis.hgetall.side_effect = [
            {},                           # Первый вызов - пустой (несуществующий) пациент
            {b'surname': b'TestDoctor'}   # Второй вызов - врач
        ]
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor-patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorPatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'doctor_ID': '0',
            'patient_ID': '999'  # несуществующий пациент
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("No such ID for doctor or patient")
        
    def test_create_doctor_patient_missing_fields(self):
        """Тест создания связи с отсутствующими полями"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/doctor-patient"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.DoctorPatientHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'doctor_ID': '0',
            'patient_ID': ''  # пустой ID пациента
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("ID required")


class TestRedisConnectionErrors(unittest.TestCase):
    """Тесты для проверки обработки ошибок подключения к Redis"""
    
    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r
        
        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis
        
        # Инициализируем тестовую базу данных
        main.init_db()
        
    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis
    
    def test_hospital_get_redis_error(self):
        """Тест ошибки подключения к Redis при получении списка больниц"""
        # Настраиваем мок для выбрасывания исключения
        self.mock_redis.get.side_effect = redis.exceptions.ConnectionError()
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/hospital"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.HospitalHandler(app, request)
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод get
        handler.get()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Redis connection refused")
    
    def test_hospital_post_redis_error(self):
        """Тест ошибки подключения к Redis при создании больницы"""
        # Настраиваем мок для возврата ID, но выбрасывания исключения при hset
        self.mock_redis.get.return_value = b'0'
        self.mock_redis.incr.return_value = 1
        self.mock_redis.hset.side_effect = redis.exceptions.ConnectionError()
        
        # Создаем мок-запрос
        request = Mock()
        request.method = "POST"
        request.uri = "/hospital"
        request.headers = {}
        
        # Создаем обработчик
        app = Application()
        handler = main.HospitalHandler(app, request)
        
        # Мокаем методы получения аргументов
        handler.get_argument = lambda arg: {
            'name': 'TestHospital',
            'address': 'TestAddress',
            'phone': '123456789',
            'beds_number': '50'
        }[arg]
        
        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        
        # Вызываем метод post
        handler.post()
        
        # Проверяем, что был установлен статус 400
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Redis connection refused")


class TestMainHandler(unittest.TestCase):
    """Тесты для главной страницы"""

    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r

        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis

        # Инициализируем тестовую базу данных
        main.init_db()

    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis

    def test_get_main_page(self):
        """Тест получения главной страницы"""
        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/"
        request.headers = {}

        # Создаем обработчик
        app = Application()
        handler = main.MainHandler(app, request)

        # Мокаем методы для избежания HTTP-ответа
        handler.write = MagicMock()
        handler.render = MagicMock()

        # Вызываем метод get
        handler.get()

        # Проверяем, что render был вызван
        handler.render.assert_called_once_with('templates/index.html')


class TestAnalyticsHandler(unittest.TestCase):
    """Тесты для обработчика аналитики"""

    def setUp(self):
        # Сохраняем оригинальное соединение с Redis
        self.original_redis = main.r

        # Создаем мок-объект для Redis
        self.mock_redis = Mock()
        main.r = self.mock_redis

        # Инициализируем тестовую базу данных
        main.init_db()

    def tearDown(self):
        # Восстанавливаем оригинальное соединение
        main.r = self.original_redis

    def test_get_analytics_success(self):
        """Тест успешного получения аналитики"""
        # Настраиваем мок для возврата значений
        def get_side_effect(key):
            if key == "hospital:autoID":
                return b'1'
            elif key == "doctor:autoID":
                return b'1'
            elif key == "patient:autoID":
                return b'1'
            elif key == "diagnosis:autoID":
                return b'1'
            else:
                return None

        self.mock_redis.get.side_effect = get_side_effect
        self.mock_redis.hgetall.return_value = {}
        self.mock_redis.smembers.return_value = set()

        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/analytics"
        request.headers = {}

        # Создаем обработчик
        app = Application()
        handler = main.AnalyticsHandler(app, request)

        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        handler.set_header = MagicMock()

        # Вызываем метод get
        handler.get()

        # Проверяем, что write был вызван (возвращен JSON)
        handler.write.assert_called_once()
        # Проверяем, что заголовок Content-Type установлен
        handler.set_header.assert_called_with("Content-Type", "application/json")

    def test_get_analytics_with_data(self):
        """Тест получения аналитики с данными"""
        # Настраиваем мок для возврата значений с данными
        def get_side_effect(key):
            if key == "hospital:autoID":
                return b'2'
            elif key == "doctor:autoID":
                return b'2'
            elif key == "patient:autoID":
                return b'2'
            elif key == "diagnosis:autoID":
                return b'2'
            else:
                return None

        self.mock_redis.get.side_effect = get_side_effect

        # Возвращаем разные данные в зависимости от ключа
        def hgetall_side_effect(key):
            if key == "hospital:0":
                return {b'name': b'TestHospital', b'address': b'TestAddress'}
            elif key == "hospital:1":
                return {}
            elif key == "doctor:0":
                return {b'surname': b'TestDoctor', b'profession': b'Surgeon', b'hospital_ID': b'0'}
            elif key == "doctor:1":
                return {}
            elif key == "patient:0":
                return {b'surname': b'TestPatient', b'born_date': b'1990-01-01', b'sex': b'M', b'mpn': b'123456'}
            elif key == "patient:1":
                return {}
            else:
                return {}

        self.mock_redis.hgetall.side_effect = hgetall_side_effect
        self.mock_redis.smembers.return_value = {'0'}

        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/analytics"
        request.headers = {}

        # Создаем обработчик
        app = Application()
        handler = main.AnalyticsHandler(app, request)

        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        handler.set_header = MagicMock()

        # Вызываем метод get
        handler.get()

        # Проверяем, что write был вызван
        handler.write.assert_called_once()
        # Проверяем, что заголовок Content-Type установлен
        handler.set_header.assert_called_with("Content-Type", "application/json")

    def test_get_analytics_redis_error(self):
        """Тест ошибки Redis при получении аналитики"""
        # Настраиваем мок для выбрасывания исключения
        self.mock_redis.get.side_effect = Exception("Redis connection failed")

        # Создаем мок-запрос
        request = Mock()
        request.method = "GET"
        request.uri = "/analytics"
        request.headers = {}

        # Создаем обработчик
        app = Application()
        handler = main.AnalyticsHandler(app, request)

        # Мокаем методы для проверки результата
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        handler.set_header = MagicMock()

        # Вызываем метод get
        handler.get()

        # Проверяем, что был установлен статус 400 и сообщение об ошибке
        handler.set_status.assert_called_with(400)
        handler.write.assert_called_once_with("Error retrieving analytics")


if __name__ == '__main__':
    unittest.main()