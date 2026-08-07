package com.ems.config;

import com.ems.constants.EmploymentStatus;
import com.ems.entity.*;
import com.ems.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.Set;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final PermissionRepository permissionRepository;
    private final DepartmentRepository departmentRepository;
    private final EmployeeRepository employeeRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional
    public void run(String... args) {
        log.info("Verifying and seeding system initialization data...");

        // 1. Permissions
        Permission readEmp = getOrCreatePermission("employee:read", "View employee records");
        Permission writeEmp = getOrCreatePermission("employee:write", "Create/Edit employee records");
        Permission approveLeave = getOrCreatePermission("leave:approve", "Approve or reject leave applications");
        Permission processPayroll = getOrCreatePermission("payroll:process", "Generate and edit payroll");

        // 2. Roles
        Set<Permission> adminPerms = new HashSet<>(permissionRepository.findAll());
        Role adminRole = getOrCreateRole("ROLE_ADMIN", "Full System Access", adminPerms);

        Set<Permission> hrPerms = Set.of(readEmp, writeEmp, approveLeave, processPayroll);
        Role hrRole = getOrCreateRole("ROLE_HR", "Human Resources Management", hrPerms);

        Set<Permission> mgrPerms = Set.of(readEmp, approveLeave);
        Role managerRole = getOrCreateRole("ROLE_MANAGER", "Department Manager Access", mgrPerms);

        Set<Permission> empPerms = Set.of(readEmp);
        Role empRole = getOrCreateRole("ROLE_EMPLOYEE", "Standard Employee Portal Access", empPerms);

        // 3. Departments
        Department itDept = getOrCreateDepartment("DEP-IT", "Information Technology", "Software development & infrastructure", "Building A, 3rd Floor");
        Department hrDept = getOrCreateDepartment("DEP-HR", "Human Resources", "Talent acquisition & payroll", "Building B, 1st Floor");
        getOrCreateDepartment("DEP-FIN", "Finance", "Financial planning & accounting", "Building A, 2nd Floor");
        getOrCreateDepartment("DEP-MKT", "Marketing", "Brand strategies & marketing", "Building C, 4th Floor");
        getOrCreateDepartment("DEP-SAL", "Sales", "Business development & sales", "Building C, 2nd Floor");
        getOrCreateDepartment("DEP-OPS", "Operations", "Facility management", "Building B, Ground Floor");

        // 4. Demo Users & Attached Employees
        // Admin
        User adminUser = getOrCreateUser("admin", "admin@ems.com", "admin123", adminRole);
        getOrCreateEmployee("EMP001", "System", "Admin", "admin@ems.com", "+1-555-0101", "MALE", LocalDate.of(1990, 1, 15), itDept, adminRole, adminUser, null);

        // HR Manager
        User hrUser = getOrCreateUser("hrmanager", "hr@ems.com", "hr123", hrRole);
        getOrCreateEmployee("EMP002", "Sarah", "Jenkins", "hr@ems.com", "+1-555-0102", "FEMALE", LocalDate.of(1992, 5, 20), hrDept, hrRole, hrUser, null);

        // Manager
        User mgrUser = getOrCreateUser("manager", "manager@ems.com", "mgr123", managerRole);
        Employee managerEmp = getOrCreateEmployee("EMP003", "Michael", "Scott", "manager@ems.com", "+1-555-0103", "MALE", LocalDate.of(1988, 3, 10), itDept, managerRole, mgrUser, null);

        // Regular Employee
        User regularUser = getOrCreateUser("employee", "alex.johnson@ems.com", "emp123", empRole);
        getOrCreateEmployee("EMP004", "Alex", "Johnson", "alex.johnson@ems.com", "+1-555-0104", "MALE", LocalDate.of(1995, 8, 10), itDept, empRole, regularUser, managerEmp);

        log.info("System initialization complete. All demo accounts verified!");
    }

    private Permission getOrCreatePermission(String name, String description) {
        return permissionRepository.findByName(name).orElseGet(() ->
                permissionRepository.save(Permission.builder().name(name).description(description).build()));
    }

    private Role getOrCreateRole(String name, String description, Set<Permission> permissions) {
        return roleRepository.findByName(name).orElseGet(() ->
                roleRepository.save(Role.builder().name(name).description(description).permissions(permissions).build()));
    }

    private Department getOrCreateDepartment(String code, String name, String description, String location) {
        return departmentRepository.findByCode(code).orElseGet(() ->
                departmentRepository.save(Department.builder().code(code).name(name).description(description).location(location).build()));
    }

    private User getOrCreateUser(String username, String email, String rawPassword, Role role) {
        return userRepository.findByUsername(username).orElseGet(() -> {
            Set<Role> roles = new HashSet<>();
            roles.add(role);
            return userRepository.save(User.builder()
                    .username(username)
                    .email(email)
                    .password(passwordEncoder.encode(rawPassword))
                    .enabled(true)
                    .accountNonLocked(true)
                    .roles(roles)
                    .build());
        });
    }

    private Employee getOrCreateEmployee(String code, String firstName, String lastName, String email, String mobile,
                                        String gender, LocalDate dob, Department dept, Role role, User user, Employee manager) {
        return employeeRepository.findByEmployeeCode(code).orElseGet(() ->
                employeeRepository.save(Employee.builder()
                        .employeeCode(code)
                        .firstName(firstName)
                        .lastName(lastName)
                        .email(email)
                        .mobileNumber(mobile)
                        .gender(gender)
                        .dateOfBirth(dob)
                        .address("100 Enterprise Way")
                        .city("San Jose")
                        .state("CA")
                        .country("USA")
                        .joiningDate(LocalDate.of(2021, 1, 1))
                        .department(dept)
                        .role(role)
                        .user(user)
                        .manager(manager)
                        .employmentStatus(EmploymentStatus.ACTIVE)
                        .profilePictureUrl("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150")
                        .build()));
    }
}
