DROP TABLE IF EXISTS precalculated_price_trend;

CREATE TABLE precalculated_price_trend SELECT 
	
    pt_2018.city_name AS City_Name,
    pt_2018.year AS 2018_Year,
    pt_2018.price AS 2018_Price,
    
/*	pt_2019.city_name AS 2019_City_Name, */
    pt_2019.year AS 2019_Year,
    pt_2019.price AS 2019_Price,
	(pt_2019.price - pt_2018.price) AS 2019_Price_Difference,
	ROUND(((pt_2019.price - pt_2018.price) / pt_2018.price) * 100, 2) AS 2019_Price_PTG_Diff,

	/*	pt_2020.city_name AS 2020_City_Name,*/
    pt_2020.year AS 2020_Year,
    pt_2020.price AS 2020_Price,
	(pt_2020.price - pt_2019.price) AS 2020_Price_Difference,
	ROUND(((pt_2020.price - pt_2019.price) / pt_2019.price) * 100, 2) AS 2020_Price_PTG_Diff,
    
   /*	 pt_2021.city_name AS 2021_City_Name, */
    pt_2021.year AS 2021_Year,
    pt_2021.price AS 2021_Price,
    pt_2021.price_change AS 2021_Price_Change,
	(pt_2021.price - pt_2020.price) AS 2021_Price_Difference,
	ROUND(((pt_2021.price - pt_2020.price) / pt_2020.price) * 100, 2) AS 2021_Price_PTG_Diff,
    
	/*	pt_2022.city_name AS 2022_City_Name, */
    pt_2022.year AS 2022_Year,
    pt_2022.price AS 2022_Price,
	(pt_2022.price - pt_2021.price) AS 2022_Price_Difference,
	ROUND(((pt_2022.price - pt_2021.price) / pt_2021.price) * 100, 2) AS 2022_Price_PTG_Diff,
    
	/*	pt_2023.city_name AS 2023_City_Name, */
    pt_2023.year AS 2023_Year,
    pt_2023.price AS 2023_Price,
	(pt_2023.price - pt_2022.price) AS 2023_Price_Difference,
	ROUND(((pt_2023.price - pt_2022.price) / pt_2022.price) * 100, 2) AS 2023_Price_PTG_Diff,
    
    /*	pt_2024.city_name AS 2024_City_Name, */
    pt_2024.year AS 2024_Year,
    pt_2024.price AS 2024_price,
    (pt_2024.price - pt_2023.price) AS 2024_Price_Difference,
	ROUND(((pt_2024.price - pt_2023.price) / pt_2023.price) * 100, 2) AS 2024_Price_PTG_Diff

FROM immobilienkauf.price_trend_per_city AS pt_2018 
JOIN immobilienkauf.price_trend_per_city AS pt_2019 
    ON pt_2018.city_name = pt_2019.city_name AND pt_2019.year=2019
    
JOIN immobilienkauf.price_trend_per_city AS pt_2020
ON pt_2018.city_name = pt_2020.city_name AND pt_2020.year=2020

JOIN immobilienkauf.price_trend_per_city AS pt_2021
ON pt_2018.city_name = pt_2021.city_name AND pt_2021.year=2021

JOIN immobilienkauf.price_trend_per_city AS pt_2022
ON pt_2018.city_name = pt_2022.city_name AND pt_2022.year=2022

JOIN immobilienkauf.price_trend_per_city AS pt_2023
ON pt_2018.city_name = pt_2023.city_name AND pt_2023.year=2023

JOIN immobilienkauf.price_trend_per_city AS pt_2024
ON pt_2018.city_name = pt_2024.city_name AND pt_2024.year=2024

WHERE pt_2018.year = 2018
  AND (pt_2024.price - pt_2018.price) > 1
  AND pt_2024.price > 1
LIMIT 30000;
