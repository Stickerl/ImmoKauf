DROP TABLE IF EXISTS immobilienkauf.copy_price_trend_per_city_w_calculations ; 

CREATE TABLE  immobilienkauf.copy_price_trend_per_city_w_calculations AS
SELECT * FROM immobilienkauf.price_trend_per_city;

ALTER TABLE immobilienkauf.copy_price_trend_per_city_w_calculations
ADD COLUMN avg_percent_change DECIMAL(10, 8);
ALTER TABLE immobilienkauf.copy_price_trend_per_city_w_calculations
ADD COLUMN diff_from_avg DECIMAL(10, 8);

SET SQL_SAFE_UPDATES = 0;

UPDATE immobilienkauf.copy_price_trend_per_city_w_calculations c
JOIN (
    SELECT 
        city_name, 
        Round (AVG(price_change),8) AS avg_percent_change
    FROM 
        immobilienkauf.copy_price_trend_per_city_w_calculations
    GROUP BY 
        city_name
) AS avg_data
ON c.city_name = avg_data.city_name
SET c.avg_percent_change = avg_data.avg_percent_change
WHERE c.city_name IS NOT NULL; 

UPDATE immobilienkauf.copy_price_trend_per_city_w_calculations
SET diff_from_avg = price_change - avg_percent_change;

SET SQL_SAFE_UPDATES = 1;


