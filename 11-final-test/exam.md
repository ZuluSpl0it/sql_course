# Northwind Final Test

Work from `12-data/northwind.db`. Inspect the schema before answering. Write and
run SQL for every question unless it explicitly asks for a written explanation.

## Section 1 — Schema discovery (1–6)

1. List Northwind's base tables, excluding SQLite's internal tables and views.
2. Show the columns, declared types, and primary-key markers for `Orders`.
3. What is the primary key of `Order Details`, and why is it composite?
4. Identify the columns that connect `Orders` to `Customers`, `Employees`, and
   `Shippers`.
5. Return the first and last `OrderDate` in the database.
6. Count orders and order-detail rows. Which table is the safer starting point
   for a report whose grain is one sold product line?

## Section 2 — Retrieval, filtering, and expressions (7–16)

7. List product name and unit price for products priced between 10 and 25
   inclusive, lowest first.
8. List German customers alphabetically by company name.
9. Return every discontinued product, including its category id.
10. List customers whose `Region` is missing.
11. Find orders shipped after their required date. Exclude orders with no ship
    date.
12. List orders whose freight is between 20 and 50 inclusive.
13. Count customers per country, most customers first.
14. Return order id, order date, and four-digit order year for orders in 2021.
15. List products whose name begins with `C`.
16. Return the five cheapest products, breaking price ties by product name.

## Section 3 — Joins and NULL handling (17–26)

17. List each order with its customer company name and order date.
18. List product, supplier, and category names for every product.
19. For each order-detail row, calculate the discounted line revenue.
20. Return the five products with the greatest total sold quantity.
21. List orders that have no matching shipper.
22. List every employee with their manager's full name; retain the top manager.
23. Find customers who have never placed an order.
24. Find products that have never appeared in `Order Details`.
25. Return every customer and their order count, including customers with zero
    orders.
26. List suppliers and the number of products they supply, retaining suppliers
    with zero products.

## Section 4 — Aggregation and report grain (27–35)

27. Calculate discounted line revenue by customer country; return the top five
    countries.
28. Return the five employees with the largest total order revenue. Explain why
    `Orders.Freight` is not the revenue column to sum.
29. Calculate average order value by order year. Do not average individual
    detail lines.
30. Return revenue by category, highest first.
31. Return countries whose revenue is above average country revenue.
32. Return every category and its product count, including categories with zero
    products.
33. By shipper, show shipped-order count and average freight. Exclude orders
    with no shipper.
34. Return monthly discounted revenue for 2021, oldest month first.
35. Return the ten customers with the highest lifetime revenue and their order
    count.

## Section 5 — Subqueries, CTEs, and set operations (36–42)

36. Use a CTE to return orders whose discounted line total is above the average
    order total.
37. List products priced above the average price of their own category.
38. Find customers who placed at least one order in 2023 using `EXISTS`.
39. Return customers who ordered in both 2020 and 2021 using `INTERSECT`.
40. Return active products that have never been ordered using `EXCEPT`.
41. Use a recursive CTE to list the employee reporting chain, with the top
    manager at depth 0.
42. Classify every order-detail row as `no discount`, `small discount`, or
    `large discount` with `CASE`, then count rows in each class.

## Section 6 — Plans, indexes, and integrated case studies (43–50)

43. In SQL Explorer's in-memory Northwind database, inspect the plan for an exact customer-country
    filter before and after an index on `Customers(Country)`. Drop the index.
44. Explain why an index on `Products(ProductName)` cannot narrow
    `ProductName LIKE '%tea%'` in the ordinary B-tree sense.
45. Use `sqlite_master` to list Northwind's existing non-auto indexes. Pick one
    and identify a query that could use it.
46. Explain why a `SCAN` → `SEARCH` plan change is not enough evidence to claim
    an index made a query faster.
47. **Sales director brief:** return the top five customer countries by
    discounted revenue, each country's share of total revenue, and its order
    count. State the row grain.
48. **Customer retention brief:** return customers who ordered in 2022 but not
    2023, with their 2022 revenue.
49. **Inventory brief:** list products where units in stock are at or below the
    reorder level, with supplier and category names. Handle a NULL reorder
    level explicitly.
50. **Shipping brief:** by shipper, return shipped-order count, late-order
    count, late percentage, and average freight. Explain how orders with NULL
    `ShippedDate` are treated.
