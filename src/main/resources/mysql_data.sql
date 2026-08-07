-- MySQL Seed Data Script for Employee Management System (safe, auto-generated IDs)

-- Roles
INSERT IGNORE INTO roles (name, description) VALUES
('ROLE_ADMIN', 'Full Administrative Access'),
('ROLE_HR', 'Human Resources Management'),
('ROLE_EMPLOYEE', 'Standard Employee Portal Access');

-- Departments
INSERT IGNORE INTO departments (code, name, description, location) VALUES
('DEP-IT', 'Information Technology', 'Software development and IT infrastructure', 'Building A, 3rd Floor'),
('DEP-HR', 'Human Resources', 'Talent acquisition, employee relations & payroll', 'Building B, 1st Floor'),
('DEP-FIN', 'Finance', 'Financial planning & tax management', 'Building A, 2nd Floor'),
('DEP-MKT', 'Marketing', 'Brand strategies and corporate communication', 'Building C, 4th Floor'),
('DEP-SAL', 'Sales', 'Business development and client accounts', 'Building C, 2nd Floor'),
('DEP-OPS', 'Operations', 'Daily operations and facility management', 'Building B, Ground Floor');

-- Users (passwords may be updated by DataInitializer to ensure BCrypt encoding)
INSERT IGNORE INTO users (username, email, password, enabled, created_at) VALUES
('admin', 'admin@ems.com', '$2a$10$8.UnVuG9HHgffUDAlk8qfOuVGkqRzgVymY04J4JkU7n.HjV.9168W', TRUE, NOW()),
('hrmanager', 'hr@ems.com', '$2a$10$8.UnVuG9HHgffUDAlk8qfOuVGkqRzgVymY04J4JkU7n.HjV.9168W', TRUE, NOW()),
('employee', 'alex.johnson@ems.com', '$2a$10$8.UnVuG9HHgffUDAlk8qfOuVGkqRzgVymY04J4JkU7n.HjV.9168W', TRUE, NOW());

-- User Roles
INSERT IGNORE INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u JOIN roles r ON r.name = 'ROLE_ADMIN' WHERE u.username = 'admin';
INSERT IGNORE INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u JOIN roles r ON r.name = 'ROLE_HR' WHERE u.username = 'hrmanager';
INSERT IGNORE INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u JOIN roles r ON r.name = 'ROLE_EMPLOYEE' WHERE u.username = 'employee';

-- Employees
INSERT IGNORE INTO employees (employee_code, first_name, last_name, email, mobile_number, gender, date_of_birth, address, city, state, country, joining_date, department_id, role_id, user_id, employment_status, profile_picture_url)
SELECT 'EMP001', 'System', 'Admin', 'admin@ems.com', '+1-555-0101', 'MALE', '1990-01-15', '100 Tech Blvd', 'San Jose', 'CA', 'USA', '2020-01-01', d.id, r.id, u.id, 'ACTIVE', 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'
FROM departments d JOIN roles r JOIN users u
WHERE d.code = 'DEP-IT' AND r.name = 'ROLE_ADMIN' AND u.username = 'admin'
LIMIT 1;

INSERT IGNORE INTO employees (employee_code, first_name, last_name, email, mobile_number, gender, date_of_birth, address, city, state, country, joining_date, department_id, role_id, user_id, employment_status, profile_picture_url)
SELECT 'EMP002', 'Sarah', 'Jenkins', 'hr@ems.com', '+1-555-0102', 'FEMALE', '1992-05-20', '200 Corporate Way', 'San Jose', 'CA', 'USA', '2021-03-15', d.id, r.id, u.id, 'ACTIVE', 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150'
FROM departments d JOIN roles r JOIN users u
WHERE d.code = 'DEP-HR' AND r.name = 'ROLE_HR' AND u.username = 'hrmanager'
LIMIT 1;

INSERT IGNORE INTO employees (employee_code, first_name, last_name, email, mobile_number, gender, date_of_birth, address, city, state, country, joining_date, department_id, role_id, user_id, employment_status, profile_picture_url)
SELECT 'EMP003', 'Alex', 'Johnson', 'alex.johnson@ems.com', '+1-555-0103', 'MALE', '1995-08-10', '300 Innovation Ave', 'San Francisco', 'CA', 'USA', '2022-06-01', d.id, r.id, u.id, 'ACTIVE', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150'
FROM departments d JOIN roles r JOIN users u
WHERE d.code = 'DEP-IT' AND r.name = 'ROLE_EMPLOYEE' AND u.username = 'employee'
LIMIT 1;

-- Attendance and Salary records may reference employees by employee_code similarly if desired
