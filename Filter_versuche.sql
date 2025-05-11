SELECT city_name, avg_percent_change, max_diff_from_avg, min_diff_from_avg FROM immobilienkauf.copy_price_trend_per_city_w_calculations WHERE avg_percent_change >= 6 GROUP BY city_name, avg_percent_change, max_diff_from_avg, min_diff_from_avg ORDER BY avg_percent_change DESC; 

