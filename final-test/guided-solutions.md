# Northwind Final Test — Guided Solutions

Use this after self-grading. These are guided paths for the hardest problems,
not the only valid answers.

## Problem 25 — every customer, including zero-order customers

**What it asks:** one row per customer. The report's row grain is a customer,
not an order.

**Build it:** start with `Customers`; that guarantees every customer exists in
the intermediate result. Add `Orders` with `LEFT JOIN`, then count the right
side's primary key.

```sql
SELECT c.CustomerID, c.CompanyName, COUNT(o.OrderID) AS order_count
FROM   Customers c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID
GROUP  BY c.CustomerID, c.CompanyName
ORDER  BY order_count DESC, c.CompanyName;
```

**Wrong turn:** `COUNT(*)` gives an unmatched customer one row from the left
join, so it reports 1 instead of 0. **Review:** Lessons 04–05.

## Problem 28 — employee revenue without fan-out

**What it asks:** total product revenue, attributed to the employee on the
order. `Freight` is shipping cost; it is not sales revenue.

**Build it:** start at `Order Details` (one sold product line), calculate each
line's discounted value, then join upward to `Orders` and `Employees`.

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

**Wrong turn:** joining a detail row to another one-to-many table before the
sum repeats revenue. **Review:** Lessons 04–05 and 08.

## Problem 29 — average order value, not average line value

**What it asks:** average of order totals. It needs two aggregation levels.

**Step 1:** reduce detail rows to one row per order. **Step 2:** average those
order rows by year.

```sql
WITH order_totals AS (
  SELECT o.OrderID, substr(o.OrderDate, 1, 4) AS order_year,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS order_total
  FROM Orders o JOIN 'Order Details' od ON od.OrderID = o.OrderID
  GROUP BY o.OrderID, order_year
)
SELECT order_year, ROUND(AVG(order_total), 2) AS average_order_value
FROM order_totals
GROUP BY order_year
ORDER BY order_year;
```

**Wrong turn:** `AVG(line value)` answers a different question because large
orders have more lines. **Review:** Lessons 04 and 07.

## Problem 31 — countries above the average country

First define revenue once per country, then compare each result to the average
of that same result set.

```sql
WITH country_revenue AS (
  SELECT c.Country, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS revenue
  FROM 'Order Details' od
  JOIN Orders o ON o.OrderID = od.OrderID
  JOIN Customers c ON c.CustomerID = o.CustomerID
  GROUP BY c.Country
)
SELECT Country, ROUND(revenue, 2) AS revenue
FROM country_revenue
WHERE revenue > (SELECT AVG(revenue) FROM country_revenue)
ORDER BY revenue DESC, Country;
```

**Wrong turn:** `HAVING revenue > AVG(revenue)` is not valid here because the
average needs the collection of grouped countries. **Review:** Lessons 04 and 07.

## Problem 36 — orders above average order total

The same two-level idea applies: detail rows first become order rows, then the
outer query compares order rows to their average.

```sql
WITH order_totals AS (
  SELECT OrderID, SUM(UnitPrice * Quantity * (1 - Discount)) AS order_total
  FROM 'Order Details'
  GROUP BY OrderID
)
SELECT OrderID, ROUND(order_total, 2) AS order_total
FROM order_totals
WHERE order_total > (SELECT AVG(order_total) FROM order_totals)
ORDER BY order_total DESC, OrderID;
```

**Also valid:** a derived table instead of a CTE. The CTE is easier to read
when the order-total definition appears more than once. **Review:** Lesson 07.

## Problem 47 — sales director brief

**Grain:** one order-detail row before grouping by country. Count distinct
orders because an order contains many detail rows.

```sql
WITH country_sales AS (
  SELECT c.Country, COUNT(DISTINCT o.OrderID) AS order_count,
         SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS revenue
  FROM 'Order Details' od
  JOIN Orders o ON o.OrderID = od.OrderID
  JOIN Customers c ON c.CustomerID = o.CustomerID
  GROUP BY c.Country
), total_sales AS (
  SELECT SUM(revenue) AS total_revenue FROM country_sales
)
SELECT Country, order_count, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * revenue / total_revenue, 2) AS revenue_share_pct
FROM country_sales CROSS JOIN total_sales
ORDER BY revenue DESC, Country
LIMIT 5;
```

**Wrong turn:** dividing by `SUM(revenue)` in the same grouped query uses the
wrong level of aggregation. **Review:** Lessons 04, 06, 07, and 10.

## Problem 48 — customer retention brief

Start from 2022 customers with their 2022 revenue. Then ask whether each has
any 2023 order. This makes the “ordered in 2022 but not 2023” rule explicit.

```sql
WITH sales_2022 AS (
  SELECT o.CustomerID, SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) AS revenue_2022
  FROM Orders o JOIN 'Order Details' od ON od.OrderID = o.OrderID
  WHERE o.OrderDate >= '2022-01-01' AND o.OrderDate < '2023-01-01'
  GROUP BY o.CustomerID
)
SELECT c.CompanyName, ROUND(s.revenue_2022, 2) AS revenue_2022
FROM sales_2022 s JOIN Customers c ON c.CustomerID = s.CustomerID
WHERE NOT EXISTS (
  SELECT 1 FROM Orders o
  WHERE o.CustomerID = s.CustomerID
    AND o.OrderDate >= '2023-01-01' AND o.OrderDate < '2024-01-01'
)
ORDER BY revenue_2022 DESC, c.CompanyName;
```

**Review:** Lessons 04, 07, and 08.

## Problem 50 — shipping brief

Exclude NULL `ShippedDate` first: a late/on-time classification requires an
actual delivery date. Then aggregate one row per order by shipper.

```sql
SELECT s.CompanyName AS shipper, COUNT(*) AS shipped_orders,
       SUM(CASE WHEN o.ShippedDate > o.RequiredDate THEN 1 ELSE 0 END) AS late_orders,
       ROUND(100.0 * SUM(CASE WHEN o.ShippedDate > o.RequiredDate THEN 1 ELSE 0 END) / COUNT(*), 2) AS late_pct,
       ROUND(AVG(o.Freight), 2) AS average_freight
FROM Orders o JOIN Shippers s ON s.ShipperID = o.ShipVia
WHERE o.ShippedDate IS NOT NULL
GROUP BY s.ShipperID, s.CompanyName
ORDER BY late_pct DESC, shipper;
```

**Wrong turn:** treating NULL `ShippedDate` as on time silently changes the
denominator. **Review:** Lessons 02, 04, 05, and 08.
