/* Bei doppelten Werten kann mit dem folgenden SQL die doppelten Werte entfernt werden.

Vorgehen:
1. Erstellen einer 2. Tabelle
2. Kopieren der Einzelwerte in neue Tabelle
3. Löschen der alten Tabelle
4. Einfügen der Werte der kopierten Tabelle
5. Löschen der kopierten Tabelle  */

/*Erstellen einer neuen Tabelle*/
USE immobilienkauf;
CREATE TABLE copy_price_trend_per_city (
    city_name VARCHAR(255),
    year DECIMAL(4,0),
    price DECIMAL(10,2),
    unit VARCHAR(50),
    price_change DECIMAL(5,2)
);

/*Einfügen der gewünschten Werte*/
INSERT INTO copy_price_trend_per_city
SELECT DISTINCT *
FROM immobilienkauf.price_trend_per_city;

/*Ausstellen SQL Savemode und Löschen der Werte in der Originaltabelle*/
SET SQL_SAFE_UPDATES = 0;
DELETE FROM immobilienkauf.price_trend_per_city;

/*Einfügen der Werte in der Originaltabelle*/
INSERT INTO immobilienkauf.price_trend_per_city (city_name, year, price, unit, price_change)
SELECT city_name, year, price, unit, price_change
FROM immobilienkauf.copy_price_trend_per_city;

/*Löschen der Werte in neu erstellter Tabelle*/
DELETE FROM immobilienkauf.copy_price_trend_per_city;
/*Löschen der neu erstellten Tabelle*/
DROP TABLE immobilienkauf.copy_price_trend_per_city;

/*Einschalten des Save-Modes*/
SET SQL_SAFE_UPDATES = 1;
