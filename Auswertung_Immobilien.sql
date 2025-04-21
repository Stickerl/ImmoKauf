SELECT 
	
    pt_earlier.city_name AS Earlier_City_Name,
    pt_earlier.year AS Earlier_Year,
    pt_earlier.price AS Earlier_Price,
    pt_earlier.price_change AS Earlier_Price_Change,
    pt_2024.city_name AS 2024_City_Name,
    pt_2024.year AS 2024_Year,
    pt_2024.price AS 2024_price,
    pt_2024.price_change AS 2024_price_change,
    (pt_2024.price - pt_earlier.price) AS Price_Difference,
  ROUND(((pt_2024.price - pt_earlier.price) / pt_earlier.price) * 100, 2) AS Price_PTG_Difference

FROM immobilienkauf.price_trend_per_city AS pt_earlier
JOIN immobilienkauf.price_trend_per_city AS pt_2024
    ON pt_earlier.city_name = pt_2024.city_name
/* 
JOIN immobilienkauf.price_trend_per_city AS pt_2024_price_change
    ON pt_earlier.city_name = pt_2024_price_change.city_name 
    -- Funktioniert nicht wegen Doppelung der Werte
*/
WHERE pt_earlier.year = 2018
  AND pt_2024.year = 2024
  AND (pt_2024.price - pt_earlier.price) > 1
  AND pt_2024.price > 1
LIMIT 30000;
