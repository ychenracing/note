##175. Combine Two Tables##
Table: Person

```bash
+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| PersonId    | int     |
| FirstName   | varchar |
| LastName    | varchar |
+-------------+---------+
```

PersonId is the primary key column for this table.

Table: Address

```bash
+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| AddressId   | int     |
| PersonId    | int     |
| City        | varchar |
| State       | varchar |
+-------------+---------+
```

AddressId is the primary key column for this table.

Write a SQL query for a report that provides the following information for each person in the Person table, regardless if there is an address for each of those people:

```bash
FirstName, LastName, City, State
```

###解答###
思路一：

```bash
使用最常见的select+where语句，也即内连接的形式。将符合Person.PersonId=Address.PersonId条件的，
存在于两个表的四个字段FirstName, LastName, City, State的记录，形成连接。
```
         
```sql
select FirstName, LastName, City, State
from Person, Address
where Person.PersonId = Address.PersonId
```
     
问题：
当Address表为空时，Address表中没有匹配的记录，这样会出现连接错误。

思路二：

```bash
通过外连接发方式实现。外联结：分为外左联结和外右联结。
对于左表（右表）中没有匹配的记录时，右表（左表）中没有匹配的记录将被设置为null。
```

```sql 
select Person.FirstName, Person.LastName, Address.City, Address.State
from Person 
left join Address
on Person.PersonId = Address.PersonId
```

##176. Second Highest Salary##

Write a SQL query to get the second highest salary from the `Employee` table.

```bash
+----+--------+
| Id | Salary |
+----+--------+
| 1  | 100    |
| 2  | 200    |
| 3  | 300    |
+----+--------+
```

For example, given the above `Employee` table, the second highest salary is `200`. If there is no second highest salary, then the query should return `null`.

###解答###
1. 一开始是这样写的：

 ```sql
 select MAX(Salary)
 from (select * from Employee where Salary not in (select MAX(Salary) from Employee))
 ```
 
 爆出错误：
 
 ```bash
 Every derived table must have its own alias
 // 每个导出的表必须拥有别名
 
 {"headers": {"Employee": ["Id" "Salary"]}
  "rows": {"Employee": [[1 100]]}}
 ```
2. 把所有表加上别名，AC：
 
 ```sql
 select MAX(Salary)
 from (select * from Employee as B where Salary not in (select MAX(Salary) from Employee as C)) as A
 ```

##184. Department Highest Salary##
The `Employee` table holds all employees. Every employee has an Id, a salary, and there is also a column for the department Id.

| Id | Name  | Salary | DepartmentId |
|----|-------|--------|--------------|
| 1  | Joe   | 70000  | 1            |
| 2  | Henry | 80000  | 2            |
| 3  | Sam   | 60000  | 2            |
| 4  | Max   | 90000  | 1            |

The `Department` table holds all departments of the company.

| Id | Name     |
|----|----------|
| 1  | IT       |
| 2  | Sales    |

Write a SQL query to find employees who have the highest salary in each of the departments. For the above tables, Max has the highest salary in the IT department and Henry has the highest salary in the Sales department.

| Department | Employee | Salary |
|------------|----------|--------|
| IT         | Max      | 90000  |
| Sales      | Henry    | 80000  |

###解答###
思路：

1. 先找出Employee表中每个部门的最高薪水。
 
 ```sql
 #切记此处的max(Salary之后需要有 as Salary，要不然这样得出的alias表是没有Salary字段的！)
 #此处是按照DeparymentId来group by的，所以得出的max(Salary)是每个部门的最高薪水！这点容易搞模糊！
 select max(Salary) as Salary, DepartmentId
 from Employee
 group by DeparymentId
 ```
2. 因为第1步中使用了group by，select中的字段要么出现在聚合函数中要么出现在group by中，从而第1步里面获取不到name这个字段。所以需要在来一个内连接，使得得出的表中有name字段。

 ```sql
 select B.Name as Employee, B.Salary as Salary, B.DepartmentId as Id
 from Employee as B
 join (select MAX(Salary) as Salary, DepartmentId from Employee group by DepartmentId) as C 
 on B.DepartmentId = C.DepartmentId and B.Salary = C.Salary
 ```
 
3. 最后，再把Deparyment表和第2步中的结果使用内连接连起来。

 ```sql
 select A.name as Department, D.Employee as Employee, D.Salary as Salary 
 from Department as A
 join (select B.Name as Employee, B.Salary as Salary, B.DepartmentId as Id 
          from Employee as B 
          join (select MAX(Salary) as Salary,DepartmentId from Employee group by DepartmentId) as C 
          on B.DepartmentId = C.DepartmentId and B.Salary = C.Salary) as D
 on A.Id = D.Id
 ```
 
##196. Delete Duplicate Emails##
 Write a SQL query to delete all duplicate email entries in a table named `Person`, keeping only unique emails based on its smallest Id.

| Id | Email            |
|----|------------------|
| 1  | john@example.com |
| 2  | bob@example.com  |
| 3  | john@example.com |

Id is the primary key column for this table.
For example, after running your query, the above `Person` table should have the following rows:

| Id | Email            |
|----|------------------|
| 1  | john@example.com |
| 2  | bob@example.com  |

###解答###

思路：

1. 按照Email进行group by，这样Email就是distinct的了，同时找出id最小的记录：

 ```sql
 delete from Person 
 where Id not in (select MIN(A.Id) as Id from Person as A group by A.Email)
 ```
 但是，<font color="red">在删除和修改的语句中，修改的表和select中用的表不能是同一张表！</font>否则会爆出错误：
 
 ```sql
 You can't specify target table 'Person' for update in FROM clause
 ```
 
 所以，得再建一层视图。解答见2
2. sql如下：

 ```sql
delete from Person 
where Id not in (select Id from (select MIN(A.Id) as Id from Person as A group by A.Email) as B)
```

##181. Employees Earning More Than Their Managers##
The `Employee` table holds all employees including their managers. Every employee has an Id, and there is also a column for the manager Id.

| Id | Name  | Salary | ManagerId |
|----|-------|--------|-----------|
| 1  | Joe   | 70000  | 3         |
| 2  | Henry | 80000  | 4         |
| 3  | Sam   | 60000  | NULL      |
| 4  | Max   | 90000  | NULL      |

Given the `Employee` table, write a SQL query that finds out employees who earn more than their managers. For the above table, Joe is the only employee who earns more than his manager.


| Employee |
|----------|
| Joe      |

###解答###

```sql
select A.Name as Employee
from Employee as A
where A.Salary > (select B.Salary as Salary from Employee as B where B.Id = A.ManagerId)
```