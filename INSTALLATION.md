# Installation & Setup Guide

This document outlines the step-by-step installation, build, and configuration instructions for the Employee Management System.

---

## Prerequisites

- **Java Development Kit (JDK)**: Java 17 or higher (`java -version`)
- **Build Tool**: Apache Maven 3.8+ (`mvn -v`)
- **Database** (Optional): MySQL 8.x (H2 is included out of the box for zero-setup execution)
- **IDE**: IntelliJ IDEA, Eclipse, or Visual Studio Code

---

## 1. Zero-Setup Mode (H2 In-Memory)

The project comes pre-configured with H2 database enabled by default so you can run the application immediately without installing or configuring MySQL.

1. Navigate to project root:
   ```bash
   cd "Employee Management System"
   ```
2. Build and run:
   ```bash
   mvn clean spring-boot:run
   ```
3. Access application: `http://localhost:8888`
4. Access H2 Console (if needed): `http://localhost:8888/h2-console`
   - **JDBC URL**: `jdbc:h2:mem:emsdb`
   - **User**: `sa`
   - **Password**: *(leave empty)*

---

## 2. Production Setup with MySQL 8

To connect the application to a local or remote MySQL 8 instance:

1. **Start MySQL Server** and execute the database script:
   ```sql
   SOURCE src/main/resources/mysql_schema.sql;
   SOURCE src/main/resources/mysql_data.sql;
   ```
   *(Or run `mysql_schema.sql` and `mysql_data.sql` in MySQL Workbench).*

2. **Configure `application.properties`**:
   Uncomment the MySQL configuration section in `src/main/resources/application.properties`:
   ```properties
   spring.datasource.url=jdbc:mysql://localhost:3306/ems_db?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
   spring.datasource.username=root
   spring.datasource.password=your_mysql_password
   spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

   spring.jpa.database-platform=org.hibernate.dialect.MySQLDialect
   spring.jpa.hibernate.ddl-auto=update
   ```

3. **Run Application**:
   ```bash
   mvn spring-boot:run
   ```

---

## 3. Importing into IDEs

### IntelliJ IDEA
1. Open IntelliJ IDEA -> `File` -> `Open...`
2. Select the `Employee Management System` folder.
3. IntelliJ will automatically detect Maven and download dependencies.
4. Run `EmployeeManagementSystemApplication.java`.

### Eclipse / STS
1. `File` -> `Import...` -> `Existing Maven Projects`.
2. Select project directory and finish import.
3. Right click project -> `Run As` -> `Spring Boot App`.
