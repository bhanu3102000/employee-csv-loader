-- Run in SSMS against your personal practice SQL Server.
IF DB_ID(N'PracticeDB') IS NULL
    EXEC(N'CREATE DATABASE PracticeDB');
GO
USE PracticeDB;
GO
IF OBJECT_ID(N'dbo.employees', N'U') IS NULL
CREATE TABLE dbo.employees (
    employee_id INT PRIMARY KEY,
    employee_name NVARCHAR(100) NOT NULL,
    department NVARCHAR(100) NOT NULL,
    salary DECIMAL(12,2) NOT NULL
);
GO
SELECT * FROM dbo.employees;
