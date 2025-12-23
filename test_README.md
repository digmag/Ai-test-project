# Тесты для приложения hospital management

## Обзор

Этот проект содержит unit-тесты для приложения hospital management, написанного на Python с использованием фреймворка Tornado и базы данных Redis.

## Структура тестов

Тесты покрывают все основные обработчики приложения:

1. **TestMainHandler** - тесты для главной страницы
   - `test_get_main_page` - получение главной страницы

2. **TestHospitalHandler** - тесты для обработчика больниц
   - `test_get_hospitals_empty` - получение пустого списка больниц
   - `test_get_hospitals_with_data` - получение списка больниц с данными
   - `test_create_hospital_success` - успешное создание больницы
   - `test_create_hospital_missing_required_fields` - создание больницы с отсутствующими полями

3. **TestDoctorHandler** - тесты для обработчика врачей
   - `test_create_doctor_success` - успешное создание врача
   - `test_create_doctor_with_valid_hospital` - создание врача с указанием существующей больницы
   - `test_create_doctor_with_invalid_hospital` - создание врача с указанием несуществующей больницы
   - `test_create_doctor_missing_required_fields` - создание врача с отсутствующими полями

4. **TestPatientHandler** - тесты для обработчика пациентов
   - `test_create_patient_success` - успешное создание пациента
   - `test_create_patient_invalid_sex` - создание пациента с неправильным полом
   - `test_create_patient_missing_required_fields` - создание пациента с отсутствующими полями

5. **TestDiagnosisHandler** - тесты для обработчика диагнозов
   - `test_create_diagnosis_success` - успешное создание диагноза
   - `test_create_diagnosis_with_invalid_patient` - создание диагноза для несуществующего пациента
   - `test_create_diagnosis_missing_required_fields` - создание диагноза с отсутствующими полями

6. **TestDoctorPatientHandler** - тесты для обработчика связей врач-пациент
   - `test_create_doctor_patient_success` - успешное создание связи врач-пациент
   - `test_create_doctor_patient_with_invalid_doctor` - создание связи с несуществующим врачом
   - `test_create_doctor_patient_with_invalid_patient` - создание связи с несуществующим пациентом
   - `test_create_doctor_patient_missing_fields` - создание связи с отсутствующими полями

7. **TestRedisConnectionErrors** - тесты для проверки обработки ошибок подключения к Redis
   - `test_hospital_get_redis_error` - ошибка подключения при получении списка больниц
   - `test_hospital_post_redis_error` - ошибка подключения при создании больницы

## Запуск тестов

Для запуска тестов выполните:

```bash
python -m unittest test_app.py -v
```

## Особенности тестирования

- Все тесты используют моки для Redis, чтобы не зависеть от запущенного сервера Redis
- Для каждого теста создается изолированная тестовая среда
- Используются моки HTTP-запросов и обработчиков для избежания необходимости запускать HTTP-сервер
- Все тесты проверяют как успешные сценарии, так и граничные случаи и ошибки валидации