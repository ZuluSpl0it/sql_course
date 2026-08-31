# Northwind Final Test — Answer Key

Compare results and reasoning, not query text. Each answer is a recommended solution; a different query earns credit when it meets the listed conditions.

## Section 1 — Schema discovery

### 1. Base tables

```sql
SELECT name
FROM   sqlite_master
WHERE  type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER  BY name;
```

**Credit:** lists tables only, not views or SQLite internals. **Review:** Lesson 09 — `sqlite_master`.

### 2. `Orders` schema

```sql
PRAGMA table_info(Orders);
```

**Credit:** uses schema metadata, not guessed columns. **Review:** Lesson 09 — `PRAGMA table_info`.

### 3. `Order Details` key

`OrderID` plus `ProductID` is the composite primary key: a product can appear once per order, while either value alone repeats. Verify with `PRAGMA table_info('Order Details');` **Review:** Lesson 09 — primary keys and constraints.

### 4. Order relationships

`Orders.CustomerID → Customers.CustomerID`, `Orders.EmployeeID → Employees.EmployeeID`, and `Orders.ShipVia → Shippers.ShipperID`.

```sql
PRAGMA foreign_key_list(Orders);
```

**Credit:** identifies all three mappings. **Review:** Lessons 05 and 09 — foreign keys and joins.

### 5. Order-date range

```sql
SELECT MIN(OrderDate) AS first_order,
       MAX(OrderDate) AS last_order
FROM   Orders;
```

**Credit:** aggregates `OrderDate`. **Review:** Lesson 04 — `MIN` and `MAX`.

### 6. Report grain

```sql
SELECT (SELECT COUNT(*) FROM Orders) AS orders,
       (SELECT COUNT(*) FROM 'Order Details') AS order_lines;
```

Start a sold-product-line report at `Order Details`: one row is one product on one order. **Review:** Lessons 04–05 — grain and fan-out.

## Section 2 — Retrieval, filtering, and expressions

### 7. Products above 50

```sql
SELECT ProductName, UnitPrice
FROM   Products
WHERE  UnitPrice > 50
ORDER  BY UnitPrice DESC, ProductName;
```

**Credit:** strict greater-than and deterministic order. **Review:** Lessons 01–02 — `WHERE`, `ORDER BY`.

### 8. German customers

```sql
SELECT CustomerID, CompanyName
FROM   Customers
WHERE  Country = 'Germany'
ORDER  BY CompanyName;
```

**Also valid:** select different identifying columns. **Review:** Lesson 02 — equality filters.

### 9. Discontinued products

```sql
SELECT ProductName, CategoryID
FROM   Products
WHERE  Discontinued = '1'
ORDER  BY ProductName;
```

**Credit:** filters the stored flag, not a made-up Boolean type. **Review:** Lessons 02 and 09 — values and storage.

### 10. Missing regions

```sql
SELECT CustomerID, CompanyName, Country
FROM   Customers
WHERE  Region IS NULL
ORDER  BY Country, CompanyName;
```

**Review:** Lesson 02 — `IS NULL`.

### 11. Late shipments

```sql
SELECT OrderID, RequiredDate, ShippedDate
FROM   Orders
WHERE  ShippedDate IS NOT NULL
  AND  ShippedDate > RequiredDate
ORDER  BY ShippedDate, OrderID;
```

**Credit:** excludes unknown shipping dates. **Review:** Lesson 02 — comparisons and NULL.

### 12. Freight range

```sql
SELECT OrderID, Freight
FROM   Orders
WHERE  Freight BETWEEN 20 AND 50
ORDER  BY Freight, OrderID;
```

**Review:** Lesson 02 — `BETWEEN` is inclusive.

### 13. Customers per country

```sql
SELECT Country, COUNT(*) AS customers
FROM   Customers
GROUP  BY Country
ORDER  BY customers DESC, Country;
```

**Review:** Lesson 04 — `GROUP BY`.

### 14. Orders in 2021

```sql
SELECT OrderID, OrderDate, substr(OrderDate, 1, 4) AS order_year
FROM   Orders
WHERE  OrderDate >= '2021-01-01' AND OrderDate < '2022-01-01'
ORDER  BY OrderDate, OrderID;
```

**Also valid:** filter with `strftime('%Y', OrderDate) = '2021'`; the range is recommended because it exposes a searchable date range. **Review:** Lessons 08 and 10.

### 15. Products beginning C

```sql
SELECT ProductID, ProductName
FROM   Products
WHERE  ProductName LIKE 'C%'
ORDER  BY ProductName;
```

**Review:** Lesson 02 — `LIKE`.

### 16. Five cheapest products

```sql
SELECT ProductName, UnitPrice
FROM   Products
ORDER  BY UnitPrice, ProductName
LIMIT  5;
```

**Review:** Lesson 01 — ordering and `LIMIT`.

## Section 3 — Joins and NULL handling

### 17. Orders with customer names

```sql
SELECT o.OrderID, c.CompanyName, o.OrderDate
FROM   Orders o
JOIN   Customers c ON c.CustomerID = o.CustomerID
ORDER  BY o.OrderDate, o.OrderID;
```

**Review:** Lesson 05 — `INNER JOIN` on key relationships.

### 18. Product, supplier, and category

```sql
SELECT p.ProductName, s.CompanyName AS supplier, c.CategoryName AS category
FROM   Products p
LEFT JOIN Suppliers s  ON s.SupplierID = p.SupplierID
LEFT JOIN Categories c ON c.CategoryID = p.CategoryID
ORDER  BY p.ProductName;
```

**Also valid:** `JOIN` if you first prove both foreign keys are always present. `LEFT JOIN` is recommended because product-side rows remain visible. **Review:** Lesson 05 — `LEFT JOIN`.

### 19. Discounted line revenue

```sql
SELECT OrderID, ProductID,
       ROUND(UnitPrice * Quantity * (1 - Discount), 2) AS line_revenue
FROM   'Order Details';
```

**Credit:** applies discount multiplicatively. **Review:** Lesson 08 — numeric expressions.

### 20. Top products by quantity

```sql
SELECT p.ProductName, SUM(od.Quantity) AS units_sold
FROM   'Order Details' od
JOIN   Products p ON p.ProductID = od.ProductID
GROUP  BY p.ProductID, p.ProductName
ORDER  BY units_sold DESC, p.ProductName
LIMIT  5;
```

**Review:** Lessons 04–05 — aggregate after the correct join.

### 21. Orders without a shipper

```sql
SELECT o.OrderID, o.ShipVia
FROM   Orders o
LEFT JOIN Shippers s ON s.ShipperID = o.ShipVia
WHERE  s.ShipperID IS NULL
ORDER  BY o.OrderID;
```

**Credit:** tests the right-side key after a `LEFT JOIN`. **Review:** Lesson 05 — unmatched rows.

### 22. Employee and manager

```sql
SELECT e.FirstName || ' ' || e.LastName AS employee,
       m.FirstName || ' ' || m.LastName AS manager
FROM   Employees e
LEFT JOIN Employees m ON m.EmployeeID = e.ReportsTo
ORDER  BY employee;
```

**Review:** Lesson 05 — self joins.

### 23. Customers with no orders

```sql
SELECT c.CustomerID, c.CompanyName
FROM   Customers c
WHERE  NOT EXISTS (
  SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID
)
ORDER  BY c.CompanyName;
```

**Also valid:** `LEFT JOIN ... WHERE o.OrderID IS NULL`. `NOT EXISTS` is recommended because it states the question directly. **Review:** Lesson 07 — `NOT EXISTS`.

### 24. Products never ordered

```sql
SELECT p.ProductID, p.ProductName
FROM   Products p
WHERE  NOT EXISTS (
  SELECT 1 FROM 'Order Details' od WHERE od.ProductID = p.ProductID
)
ORDER  BY p.ProductName;
```

**Review:** Lesson 07 — anti-join with `NOT EXISTS`.

### 25. Every customer and order count

```sql
SELECT c.CustomerID, c.CompanyName, COUNT(o.OrderID) AS order_count
FROM   Customers c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID
GROUP  BY c.CustomerID, c.CompanyName
ORDER  BY order_count DESC, c.CompanyName;
```

**Credit:** uses `COUNT(o.OrderID)`, not `COUNT(*)`, so unmatched customers receive zero. **Review:** Lessons 04–05 — NULL-aware counts and `LEFT JOIN`.

### 26. Suppliers and product count

```sql
SELECT s.SupplierID, s.CompanyName, COUNT(p.ProductID) AS product_count
FROM   Suppliers s
LEFT JOIN Products p ON p.SupplierID = s.SupplierID
GROUP  BY s.SupplierID, s.CompanyName
ORDER  BY product_count DESC, s.CompanyName;
```

**Review:** Lessons 04–05 — preserving zero-match parent rows.

## Section 4 — Aggregation and report grain

### 27. Revenue by customer country

```sql
SELECT c.Country,
       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS revenue
FROM   'Order Details' od
JOIN   Orders o    ON o.OrderID = od.OrderID
JOIN   Customers c ON c.CustomerID = o.CustomerID
GROUP  BY c.Country
ORDER  BY revenue DESC, c.Country
LIMIT  5;
```

**Grain:** one order-detail row before grouping. **Review:** Lessons 04–05 — aggregate grain.

### 28. Revenue by employee

```sql
SELECT e.FirstName || ' ' || e.LastName AS employee,
       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS revenue
FROM   'Order Details' od
JOIN   Orders o    ON o.OrderID = od.OrderID
JOIN   Employees e ON e.EmployeeID = o.EmployeeID
GROUP  BY e.EmployeeID, e.FirstName, e.LastName
ORDER  BY revenue DESC, employee
LIMIT  5;
```

`Freight` is shipping cost, not product revenue; summing it also becomes wrong after joining an order to many detail rows. **Review:** Lessons 04–05 — fan-out.

### 29. Average order value by year

```sql
WITH order_totals AS (
  SELECT o.OrderID,
         substr(o.OrderDate, 1, 4) AS order_year,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total
  FROM   Orders o
  JOIN   'Order Details' od ON od.OrderID = o.OrderID
  GROUP  BY o.OrderID, order_year
)
SELECT order_year, ROUND(AVG(order_total), 2) AS average_order_value
FROM   order_totals
GROUP  BY order_year
ORDER  BY order_year;
```

**Credit:** aggregates to one order before averaging. **Review:** Lessons 04, 07, and 10.

### 30. Revenue by category

```sql
SELECT c.CategoryName,
       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS revenue
FROM   'Order Details' od
JOIN   Products p   ON p.ProductID = od.ProductID
JOIN   Categories c ON c.CategoryID = p.CategoryID
GROUP  BY c.CategoryID, c.CategoryName
ORDER  BY revenue DESC, c.CategoryName;
```

**Review:** Lessons 04–05 — multi-table aggregate.

### 31. Countries above average revenue

```sql
WITH country_revenue AS (
  SELECT c.Country,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS revenue
  FROM   'Order Details' od
  JOIN   Orders o    ON o.OrderID = od.OrderID
  JOIN   Customers c ON c.CustomerID = o.CustomerID
  GROUP  BY c.Country
)
SELECT Country, ROUND(revenue, 2) AS revenue
FROM   country_revenue
WHERE  revenue > (SELECT AVG(revenue) FROM country_revenue)
ORDER  BY revenue DESC, Country;
```

**Review:** Lesson 07 — CTE plus scalar subquery.

### 32. Product count by category

```sql
SELECT c.CategoryName, COUNT(p.ProductID) AS product_count
FROM   Categories c
LEFT JOIN Products p ON p.CategoryID = c.CategoryID
GROUP  BY c.CategoryID, c.CategoryName
ORDER  BY c.CategoryName;
```

**Review:** Lessons 04–05 — zero-preserving aggregate.

### 33. Shipper count and freight

```sql
SELECT s.CompanyName,
       COUNT(o.OrderID) AS shipped_orders,
       ROUND(AVG(o.Freight), 2) AS average_freight
FROM   Orders o
JOIN   Shippers s ON s.ShipperID = o.ShipVia
GROUP  BY s.ShipperID, s.CompanyName
ORDER  BY shipped_orders DESC, s.CompanyName;
```

**Review:** Lessons 04–05 — aggregate after one-to-one order/shipper join.

### 34. Monthly 2021 revenue

```sql
SELECT substr(o.OrderDate, 1, 7) AS order_month,
       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS revenue
FROM   Orders o
JOIN   'Order Details' od ON od.OrderID = o.OrderID
WHERE  o.OrderDate >= '2021-01-01' AND o.OrderDate < '2022-01-01'
GROUP  BY order_month
ORDER  BY order_month;
```

**Review:** Lessons 04 and 08 — grouping expressions and date text.

### 35. Customer lifetime revenue

```sql
SELECT c.CompanyName,
       COUNT(DISTINCT o.OrderID) AS order_count,
       ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) AS revenue
FROM   Customers c
JOIN   Orders o            ON o.CustomerID = c.CustomerID
JOIN   'Order Details' od  ON od.OrderID = o.OrderID
GROUP  BY c.CustomerID, c.CompanyName
ORDER  BY revenue DESC, c.CompanyName
LIMIT  10;
```

**Credit:** `COUNT(DISTINCT o.OrderID)` prevents detail-line repetition. **Review:** Lessons 04–05.

## Section 5 — Subqueries, CTEs, and set operations

### 36. Orders above average total

```sql
WITH order_totals AS (
  SELECT od.OrderID,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total
  FROM   'Order Details' od
  GROUP  BY od.OrderID
)
SELECT OrderID, ROUND(order_total, 2) AS order_total
FROM   order_totals
WHERE  order_total > (SELECT AVG(order_total) FROM order_totals)
ORDER  BY order_total DESC, OrderID;
```

**Review:** Lesson 07 — CTE plus scalar subquery.

### 37. Products above their category average

```sql
SELECT p.ProductName, p.UnitPrice, c.CategoryName
FROM   Products p
JOIN   Categories c ON c.CategoryID = p.CategoryID
WHERE  p.UnitPrice > (
  SELECT AVG(p2.UnitPrice)
  FROM   Products p2
  WHERE  p2.CategoryID = p.CategoryID
)
ORDER  BY c.CategoryName, p.UnitPrice DESC, p.ProductName;
```

**Also valid:** a CTE of category averages joined back to products. The correlated form is recommended because it mirrors the question. **Review:** Lesson 07 — correlated subqueries.

### 38. Customers ordering in 2023

```sql
SELECT c.CustomerID, c.CompanyName
FROM   Customers c
WHERE  EXISTS (
  SELECT 1
  FROM   Orders o
  WHERE  o.CustomerID = c.CustomerID
    AND  o.OrderDate >= '2023-01-01'
    AND  o.OrderDate < '2024-01-01'
)
ORDER  BY c.CompanyName;
```

**Review:** Lesson 07 — `EXISTS`.

### 39. Customers ordering in both years

```sql
SELECT CustomerID
FROM   Orders
WHERE  OrderDate >= '2020-01-01' AND OrderDate < '2021-01-01'
INTERSECT
SELECT CustomerID
FROM   Orders
WHERE  OrderDate >= '2021-01-01' AND OrderDate < '2022-01-01'
ORDER  BY CustomerID;
```

**Review:** Lesson 06 — `INTERSECT` compares selected values.

### 40. Active products never ordered

```sql
WITH never_ordered AS (
  SELECT ProductID FROM Products WHERE Discontinued = '0'
  EXCEPT
  SELECT ProductID FROM 'Order Details'
)
SELECT p.ProductID, p.ProductName
FROM   Products p
JOIN   never_ordered n ON n.ProductID = p.ProductID
ORDER  BY p.ProductName;
```

**Also valid:** `NOT EXISTS`. This answer is recommended because the question requests set logic. **Review:** Lesson 06 — `EXCEPT`.

### 41. Employee reporting chain

```sql
WITH RECURSIVE org AS (
  SELECT EmployeeID, FirstName || ' ' || LastName AS employee,
         ReportsTo, 0 AS depth
  FROM   Employees
  WHERE  ReportsTo IS NULL
  UNION ALL
  SELECT e.EmployeeID, e.FirstName || ' ' || e.LastName,
         e.ReportsTo, org.depth + 1
  FROM   Employees e
  JOIN   org ON e.ReportsTo = org.EmployeeID
)
SELECT depth, employee
FROM   org
ORDER  BY depth, employee;
```

**Review:** Lesson 07 — `WITH RECURSIVE`.

### 42. Discount classes

```sql
SELECT CASE
         WHEN Discount = 0 THEN 'no discount'
         WHEN Discount < 0.15 THEN 'small discount'
         ELSE 'large discount'
       END AS discount_class,
       COUNT(*) AS detail_rows
FROM   'Order Details'
GROUP  BY discount_class
ORDER  BY discount_class;
```

**Credit:** assigns every row to one class. **Review:** Lessons 04 and 08 — `CASE` with aggregates.

## Section 6 — Plans, indexes, and integrated case studies

### 43. Country index experiment

Run only in a fresh Jasper session with `12-data/northwind.db` loaded:

```sql
EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM Customers WHERE Country = 'Germany';

CREATE INDEX idx_final_customer_country ON Customers(Country);

EXPLAIN QUERY PLAN
SELECT COUNT(*) FROM Customers WHERE Country = 'Germany';

DROP INDEX idx_final_customer_country;
```

**Credit:** compares plan shape, makes no unmeasured speed claim, and drops the temporary index. **Review:** Lessons 09–10 — plans and indexes.

### 44. Leading wildcard

`LIKE '%tea%'` has no known starting prefix, so an ordinary B-tree index cannot jump to the first candidate name. SQLite must scan candidates. `LIKE 'tea%'` exposes a starting range and is the contrasting case. **Review:** Lesson 10 — searchable predicates.

### 45. Existing indexes

```sql
SELECT name, tbl_name, sql
FROM   sqlite_master
WHERE  type = 'index'
  AND  name NOT LIKE 'sqlite_autoindex%'
ORDER  BY tbl_name, name;
```

One acceptable explanation names an index on an order foreign-key column and a query that filters or joins through that column. **Review:** Lessons 09–10 — schema data and plan evidence.

### 46. Why plan shape is not timing

`EXPLAIN QUERY PLAN` reports the chosen access route, not elapsed time. Data size, selectivity, cache state, write cost, and the cost of touching table rows still matter. **Review:** Lesson 10 — plan shape, not stopwatch.

### 47. Sales director brief

The grain is **one order-detail row** before country grouping.

```sql
WITH country_sales AS (
  SELECT c.Country,
         COUNT(DISTINCT o.OrderID) AS order_count,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS revenue
  FROM   'Order Details' od
  JOIN   Orders o    ON o.OrderID = od.OrderID
  JOIN   Customers c ON c.CustomerID = o.CustomerID
  GROUP  BY c.Country
), total_sales AS (
  SELECT SUM(revenue) AS total_revenue FROM country_sales
)
SELECT Country,
       order_count,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * revenue / total_revenue, 2) AS revenue_share_pct
FROM   country_sales
CROSS JOIN total_sales
ORDER  BY revenue DESC, Country
LIMIT  5;
```

**Also valid:** calculate the total with a scalar subquery. The CTE version is recommended because country revenue is defined once. **Review:** Lessons 04–07 and 10.

### 48. Customer retention brief

```sql
WITH sales_2022 AS (
  SELECT o.CustomerID,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS revenue_2022
  FROM   Orders o
  JOIN   'Order Details' od ON od.OrderID = o.OrderID
  WHERE  o.OrderDate >= '2022-01-01' AND o.OrderDate < '2023-01-01'
  GROUP  BY o.CustomerID
)
SELECT c.CustomerID, c.CompanyName, ROUND(s.revenue_2022, 2) AS revenue_2022
FROM   sales_2022 s
JOIN   Customers c ON c.CustomerID = s.CustomerID
WHERE  NOT EXISTS (
  SELECT 1
  FROM   Orders o
  WHERE  o.CustomerID = s.CustomerID
    AND  o.OrderDate >= '2023-01-01' AND o.OrderDate < '2024-01-01'
)
ORDER  BY revenue_2022 DESC, c.CompanyName;
```

**Review:** Lessons 04, 07, and 08 — grouping, `NOT EXISTS`, date ranges.

### 49. Inventory brief

```sql
SELECT p.ProductName,
       p.UnitsInStock,
       p.ReorderLevel,
       s.CompanyName AS supplier,
       c.CategoryName AS category
FROM   Products p
LEFT JOIN Suppliers s  ON s.SupplierID = p.SupplierID
LEFT JOIN Categories c ON c.CategoryID = p.CategoryID
WHERE  p.UnitsInStock <= COALESCE(p.ReorderLevel, 0)
ORDER  BY p.UnitsInStock, p.ProductName;
```

**Credit:** handles a NULL reorder level explicitly. **Review:** Lessons 05 and 08 — outer joins and `COALESCE`.

### 50. Shipping brief

```sql
SELECT s.CompanyName AS shipper,
       COUNT(*) AS shipped_orders,
       SUM(CASE WHEN o.ShippedDate > o.RequiredDate THEN 1 ELSE 0 END) AS late_orders,
       ROUND(100.0 * SUM(CASE WHEN o.ShippedDate > o.RequiredDate THEN 1 ELSE 0 END) / COUNT(*), 2) AS late_pct,
       ROUND(AVG(o.Freight), 2) AS average_freight
FROM   Orders o
JOIN   Shippers s ON s.ShipperID = o.ShipVia
WHERE  o.ShippedDate IS NOT NULL
GROUP  BY s.ShipperID, s.CompanyName
ORDER  BY late_pct DESC, shipper;
```

Orders with NULL `ShippedDate` are excluded because they have no known delivery outcome. **Review:** Lessons 04, 05, and 08 — aggregate grain, joins, `CASE`, and NULL.
