#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2 // Пин подключения OneWire шины
OneWire oneWire(ONE_WIRE_BUS); // Подключаем библиотеку OneWire
DallasTemperature sensors(&oneWire); // Подключаем библиотеку DallasTemperature

DeviceAddress temperatureSensors[3]; // Массив для хранения адресов датчиков
uint8_t deviceCount = 0;

// Функция вывода адреса датчика 
void printAddress(DeviceAddress deviceAddress) {
    for (uint8_t i = 0; i < 8; i++) {
        if (deviceAddress[i] < 16) Serial.print("0");
        Serial.print(deviceAddress[i], HEX); // Выводим адрес датчика в HEX формате 
    }
}

void setup() {
    Serial.begin(115200); // Задаем скорость соединения с последовательным портом 
    sensors.begin(); // Инициализируем датчики
    deviceCount = sensors.getDeviceCount(); // Получаем количество обнаруженных датчиков

    for (uint8_t index = 0; index < deviceCount; index++) {
        sensors.getAddress(temperatureSensors[index], index);
    }
}

void loop() {
    sensors.requestTemperatures(); // Запрашиваем температуры
    String output = ""; // Создаем строку для вывода данных
    output += String(millis()); // Добавляем временную метку в миллисекундах

    for (int i = 0; i < deviceCount; i++) {
        output += ";"; // Разделитель для значений
        printAddress(temperatureSensors[i]); // Выводим адрес датчика
        output += String(sensors.getTempC(temperatureSensors[i])); // Добавляем температуру с датчика
    }
    
    Serial.println(output); // Отправляем данные в последовательный порт
    delay(1000); // Задержка между считываниями
}
