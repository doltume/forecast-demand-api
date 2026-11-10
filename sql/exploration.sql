-- First rows of the table
SELECT * FROM sales ORDER BY sale_date, store_id, item_id LIMIT 10;

-- Average sales per store
SELECT store_id, ROUND(AVG(quantity), 1) AS avg_sales
FROM sales
GROUP BY store_id
ORDER BY store_id;

-- Top 10 products by total sales
SELECT item_id, SUM(quantity) AS total_sales
FROM sales
GROUP BY item_id
ORDER BY total_sales DESC
LIMIT 10;

-- Monthly sales (seasonality)
SELECT DATE_TRUNC('month', sale_date)::date AS month, SUM(quantity) AS total_sales
FROM sales
GROUP BY month
ORDER BY month;