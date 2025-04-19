# Integracja Home Assistant: ORNO OR-WE-517

Integracja niestandardowa (`custom_component`) dla licznika energii **ORNO OR-WE-517** z komunikacją Modbus TCP.

## Autor
- **Autor:** SZA
- **GitHub:** [sza86](https://github.com/sza86)

## Funkcje:
- Obsługa Modbus TCP (IP, port, slave ID)
- Konfiguracja przez interfejs graficzny Home Assistant (config flow)
- Obsługa rejestrów typu `float32`, `int16`, `uint16`
- Opcja ustawienia interwału odpytywania (sekundy)
- Automatyczne tworzenie encji na podstawie listy rejestrów

## Instalacja ręczna
1. Skopiuj folder `orno_517` do katalogu `custom_components` w `/config`
2. Zrestartuj Home Assistant
3. Dodaj integrację `ORNO OR-WE-517` przez interfejs użytkownika

## Wymagania
- `pymodbus >= 3.0.0`

## Licencja
MIT
