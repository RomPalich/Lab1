import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Optional


# Собственные исключения
class TransportError(Exception):
    """Базовое исключение для транспортной системы"""
    pass


class VehicleNotFoundError(TransportError):
    """Ошибка при не найденном транспортном средстве"""
    pass


class InvalidDataError(TransportError):
    """Ошибка при неверных данных"""
    pass


class FileOperationError(TransportError):
    """Ошибка работы с файлом"""
    pass


class RouteNotFoundError(TransportError):
    """Ошибка при не найденном маршруте"""
    pass


# Основные классы
class Vehicle:
    """Класс транспортного средства"""

    def __init__(self, vehicle_id: int, model: str, capacity: int, vehicle_type: str):

        self.vehicle_id = vehicle_id
        self.model = model
        self.capacity = capacity
        self.type = vehicle_type


    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь"""
        return {
            'vehicle_id': self.vehicle_id,
            'model': self.model,
            'capacity': self.capacity,
            'type': self.type
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Vehicle':
        """Создание объекта из словаря"""
        return cls(
            vehicle_id=data['vehicle_id'],
            model=data['model'],
            capacity=data['capacity'],
            vehicle_type=data['type']
        )


class Route:
    """Класс маршрута"""

    def __init__(self, route_id: int, number: str, start_point: str, end_point: str):

        self.route_id = route_id
        self.number = number
        self.start_point = start_point
        self.end_point = end_point
        self.vehicles: List[Vehicle] = []


    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Добавление транспортного средства к маршруту"""
        if not isinstance(vehicle, Vehicle):
            raise InvalidDataError("Можно добавить только объект Vehicle")
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle_id: int) -> None:
        """Удаление транспортного средства из маршрута"""
        vehicle = self.find_vehicle(vehicle_id)
        if vehicle:
            self.vehicles.remove(vehicle)
        else:
            raise VehicleNotFoundError(f"Транспортное средство с ID {vehicle_id} не найдено в маршруте")

    def find_vehicle(self, vehicle_id: int) -> Optional[Vehicle]:
        """Поиск транспортного средства по ID"""
        for vehicle in self.vehicles:
            if vehicle.vehicle_id == vehicle_id:
                return vehicle
        return None

    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь"""
        return {
            'route_id': self.route_id,
            'number': self.number,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'vehicles': [vehicle.to_dict() for vehicle in self.vehicles]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Route':
        """Создание объекта из словаря"""
        route = cls(
            route_id=data['route_id'],
            number=data['number'],
            start_point=data['start_point'],
            end_point=data['end_point']
        )
        for vehicle_data in data.get('vehicles', []):
            route.add_vehicle(Vehicle.from_dict(vehicle_data))
        return route

    def __str__(self) -> str:
        vehicles_info = ", ".join([f"{v.model}(ID:{v.vehicle_id})" for v in self.vehicles])
        return f"Маршрут {self.number}: {self.start_point} - {self.end_point} | Транспорт: [{vehicles_info}]"


class Passenger:
    """Класс пассажира"""

    def __init__(self, passenger_id: int, name: str, card_number: str):

        self.passenger_id = passenger_id
        self.name = name
        self.card_number = card_number

    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь"""
        return {
            'passenger_id': self.passenger_id,
            'name': self.name,
            'card_number': self.card_number
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Passenger':
        """Создание объекта из словаря"""
        return cls(
            passenger_id=data['passenger_id'],
            name=data['name'],
            card_number=data['card_number']
        )

    def __str__(self) -> str:
        return f"Пассажир: {self.name} (Карта: {self.card_number}, ID: {self.passenger_id})"


class Schedule:
    """Класс расписания"""

    def __init__(self, schedule_id: int, route_id: int, departure_time: str, arrival_time: str):

        self.schedule_id = schedule_id
        self.route_id = route_id
        self.departure_time = departure_time
        self.arrival_time = arrival_time

    def to_dict(self) -> Dict:
        """Преобразование объекта в словарь"""
        return {
            'schedule_id': self.schedule_id,
            'route_id': self.route_id,
            'departure_time': self.departure_time,
            'arrival_time': self.arrival_time
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Schedule':
        """Создание объекта из словаря"""
        return cls(
            schedule_id=data['schedule_id'],
            route_id=data['route_id'],
            departure_time=data['departure_time'],
            arrival_time=data['arrival_time']
        )

    def __str__(self) -> str:
        return f"Расписание ID {self.schedule_id}: {self.departure_time} - {self.arrival_time} (Маршрут ID: {self.route_id})"


class TransportSystem:
    """Основной класс транспортной системы"""

    def __init__(self):
        self.routes: List[Route] = []
        self.passengers: List[Passenger] = []
        self.schedules: List[Schedule] = []

    # CRUD операции для маршрутов
    def create_route(self, route: Route) -> None:
        """Создание нового маршрута"""
        if not isinstance(route, Route):
            raise InvalidDataError("Можно добавить только объект Route")
        self.routes.append(route)

    def read_route(self, route_id: int) -> Route:
        """Чтение маршрута по ID"""
        route = self.find_route(route_id)
        if route:
            return route
        raise RouteNotFoundError(f"Маршрут с ID {route_id} не найден")

    def update_route(self, route_id: int, **kwargs) -> None:
        """Обновление маршрута"""
        route = self.read_route(route_id)
        for key, value in kwargs.items():
            if hasattr(route, key):
                setattr(route, key, value)

    def delete_route(self, route_id: int) -> None:
        """Удаление маршрута"""
        route = self.read_route(route_id)
        self.routes.remove(route)

    def find_route(self, route_id: int):
        """Поиск маршрута по ID"""
        for route in self.routes:
            if route.route_id == route_id:
                return route
        return None

    def create_passenger(self, passenger: Passenger) -> None:
        """Создание нового пассажира"""
        if not isinstance(passenger, Passenger):
            raise InvalidDataError("Можно добавить только объект Passenger")
        self.passengers.append(passenger)

    def read_passenger(self, passenger_id: int) -> Passenger:
        """Чтение пассажира по ID"""
        for passenger in self.passengers:
            if passenger.passenger_id == passenger_id:
                return passenger
        raise TransportError(f"Пассажир с ID {passenger_id} не найден")

    # Работа с файлами JSON
    def save_to_json(self, filename: str) -> None:
        """Сохранение данных в JSON файл"""
        try:
            data = {
                'routes': [route.to_dict() for route in self.routes],
                'passengers': [passenger.to_dict() for passenger in self.passengers],
                'schedules': [schedule.to_dict() for schedule in self.schedules],
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise FileOperationError(f"Ошибка сохранения JSON: {str(e)}")

    def load_from_json(self, filename: str) -> None:
        """Загрузка данных из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.routes = [Route.from_dict(route_data) for route_data in data.get('routes', [])]
            self.passengers = [Passenger.from_dict(passenger_data) for passenger_data in data.get('passengers', [])]
            self.schedules = [Schedule.from_dict(schedule_data) for schedule_data in data.get('schedules', [])]

        except Exception as e:
            raise FileOperationError(f"Ошибка загрузки JSON: {str(e)}")

    # Работа с файлами XML
    def save_to_xml(self, filename: str) -> None:
        """Сохранение данных в XML файл"""
        try:
            root = ET.Element('TransportSystem')

            # Маршруты
            routes_elem = ET.SubElement(root, 'Routes')
            for route in self.routes:
                route_elem = ET.SubElement(routes_elem, 'Route')
                for key, value in route.to_dict().items():
                    if key == 'vehicles':
                        vehicles_elem = ET.SubElement(route_elem, 'Vehicles')
                        for vehicle in value:
                            vehicle_elem = ET.SubElement(vehicles_elem, 'Vehicle')
                            for v_key, v_value in vehicle.items():
                                ET.SubElement(vehicle_elem, v_key).text = str(v_value)
                    else:
                        ET.SubElement(route_elem, key).text = str(value)

            # Пассажиры
            passengers_elem = ET.SubElement(root, 'Passengers')
            for passenger in self.passengers:
                passenger_elem = ET.SubElement(passengers_elem, 'Passenger')
                for key, value in passenger.to_dict().items():
                    ET.SubElement(passenger_elem, key).text = str(value)

            # Расписания
            schedules_elem = ET.SubElement(root, 'Schedules')
            for schedule in self.schedules:
                schedule_elem = ET.SubElement(schedules_elem, 'Schedule')
                for key, value in schedule.to_dict().items():
                    ET.SubElement(schedule_elem, key).text = str(value)

            # Форматирование и сохранение
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_str)
        except Exception as e:
            raise FileOperationError(f"Ошибка сохранения XML: {str(e)}")

    def display_all_data(self) -> None:
        """Отображение всех данных системы"""
        print("\n" + "=" * 50)
        print("ДАННЫЕ ТРАНСПОРТНОЙ СИСТЕМЫ")
        print("=" * 50)

        print("\nМАРШРУТЫ:")
        for route in self.routes:
            print(f"  {route}")

        print("\nПАССАЖИРЫ:")
        for passenger in self.passengers:
            print(f"  {passenger}")

        print("\nРАСПИСАНИЯ:")
        for schedule in self.schedules:
            print(f"  {schedule}")


# Демонстрация работы
def main():
    """Основная функция демонстрации"""
    transport_system = TransportSystem()

    try:
        # Создание объектов
        bus1 = Vehicle(1, "НефАЗ 5299", 77, "Автобус")
        bus2 = Vehicle(2, "МАЗ-203", 80, "Автобус")
        bus3 = Vehicle(3, "ЛиАЗ-6274", 35, "Электробус")
        tram = Vehicle(4, "Tatra T3SU",  95, "Трамвай")

        route1 = Route(1, "т77", "Ивановское", "МЦД Перово")
        route1.add_vehicle(bus1)
        route1.add_vehicle(bus2)

        route2 = Route(2, "37", "Курский вокзал", "3-я Владимирская")
        route2.add_vehicle(tram)

        route3 = Route(3, "141", "Молостовых", "Метро Семёновская")
        route3.add_vehicle(bus3)

        passenger1 = Passenger(1, "Иван Иванов", "0021095222")
        passenger2 = Passenger(2, "Мария Петрова", "0022112312")
        passenger3 = Passenger(3, "Петр Петров", "0023123312")

        schedule1 = Schedule(1, 1, "08:00", "08:45")
        schedule2 = Schedule(2, 1, "14:00", "14:45")
        schedule3 = Schedule(3, 3, "11:10", "11:25")

        # Добавление в систему
        transport_system.create_route(route1)
        transport_system.create_route(route2)
        transport_system.create_route(route3)
        transport_system.create_passenger(passenger1)
        transport_system.create_passenger(passenger2)
        transport_system.create_passenger(passenger3)
        transport_system.schedules.extend([schedule1, schedule2, schedule3])

        # Демонстрация данных
        transport_system.display_all_data()



        # Чтение маршрута
        print(f"\nЧтение маршрута 1: {transport_system.read_route(1)}")

        # Обновление маршрута
        transport_system.update_route(1, end_point="МЦД Новогиреево")
        print(f"После обновления: {transport_system.read_route(1)}")

        # Удаление маршрута
        print(f"\nУдаление маршрута 3...")
        transport_system.delete_route(3)
        print(f"Количество маршрутов после удаления: {len(transport_system.routes)}")

        # Сохранение в файлы
        transport_system.save_to_json('transport_data.json')
        transport_system.save_to_xml('transport_data.xml')
        print("\nДанные сохранены в JSON и XML файлы")

        # Создание новой системы и загрузка данных
        new_system = TransportSystem()
        new_system.load_from_json('transport_data.json')
        print("\nДанные загружены из JSON файла в новую систему:")
        new_system.display_all_data()

        # Демонстрация обработки ошибок
        print("\n" + "=" * 50)
        print("ДЕМОНСТРАЦИЯ ОБРАБОТКИ ОШИБОК")
        print("=" * 50)

        try:
            # Попытка найти несуществующий маршрут
            transport_system.read_route(3)
        except RouteNotFoundError as e:
            print(f"Ошибка: {e}")

        try:
            # Попытка добавить неверный тип данных
            transport_system.create_route("invalid_data")
        except InvalidDataError as e:
            print(f"Ошибка: {e}")

    except TransportError as e:
        print(f"Произошла ошибка транспортной системы: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()