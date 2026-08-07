package com.ems.service.impl;

import com.ems.constants.EmploymentStatus;
import com.ems.dto.ChangePasswordDTO;
import com.ems.dto.UserRegistrationDTO;
import com.ems.entity.Department;
import com.ems.entity.Employee;
import com.ems.entity.Role;
import com.ems.entity.User;
import com.ems.exception.ResourceNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.DepartmentRepository;
import com.ems.repository.EmployeeRepository;
import com.ems.repository.RoleRepository;
import com.ems.repository.UserRepository;
import com.ems.service.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final DepartmentRepository departmentRepository;
    private final EmployeeRepository employeeRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional
    public User registerUser(UserRegistrationDTO dto) {
        if (!dto.getPassword().equals(dto.getConfirmPassword())) {
            throw new ValidationException("Password and confirm password do not match");
        }
        if (userRepository.existsByUsername(dto.getUsername())) {
            throw new ValidationException("Username '" + dto.getUsername() + "' is already taken");
        }
        if (userRepository.existsByEmail(dto.getEmail())) {
            throw new ValidationException("Email '" + dto.getEmail() + "' is already registered");
        }

        Role role;
        if (dto.getRoleId() != null) {
            role = roleRepository.findById(dto.getRoleId())
                    .orElseGet(() -> roleRepository.findByName("ROLE_EMPLOYEE")
                    .orElseThrow(() -> new ResourceNotFoundException("Default role ROLE_EMPLOYEE not found")));
        } else {
            role = roleRepository.findByName("ROLE_EMPLOYEE")
                    .orElseThrow(() -> new ResourceNotFoundException("Default role ROLE_EMPLOYEE not found"));
        }

        Set<Role> roles = new HashSet<>();
        roles.add(role);

        User user = User.builder()
                .username(dto.getUsername())
                .email(dto.getEmail())
                .password(passwordEncoder.encode(dto.getPassword()))
                .enabled(true)
                .roles(roles)
                .build();

        User savedUser = userRepository.save(user);

        // Auto-create attached Employee profile for user registration
        Department dept = null;
        if (dto.getDepartmentId() != null) {
            dept = departmentRepository.findById(dto.getDepartmentId()).orElse(null);
        }

        String empCode = "EMP" + String.format("%04d", (employeeRepository.count() + 1));

        Employee employee = Employee.builder()
                .employeeCode(empCode)
                .firstName(dto.getFirstName())
                .lastName(dto.getLastName())
                .email(dto.getEmail())
                .mobileNumber(dto.getMobileNumber())
                .gender("MALE")
                .joiningDate(LocalDate.now())
                .department(dept)
                .role(role)
                .user(savedUser)
                .employmentStatus(EmploymentStatus.ACTIVE)
                .build();

        employeeRepository.save(employee);
        log.info("Registered new user and employee profile for username: {}", dto.getUsername());

        return savedUser;
    }

    @Override
    public User findByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with username: " + username));
    }

    @Override
    public User findByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with email: " + email));
    }

    @Override
    public User findById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with ID: " + id));
    }

    @Override
    public List<User> findAllUsers() {
        return userRepository.findAll();
    }

    @Override
    @Transactional
    public void changePassword(String username, ChangePasswordDTO dto) {
        if (!dto.getNewPassword().equals(dto.getConfirmNewPassword())) {
            throw new ValidationException("New password and confirm password do not match");
        }

        User user = findByUsername(username);
        if (!passwordEncoder.matches(dto.getCurrentPassword(), user.getPassword())) {
            throw new ValidationException("Current password provided is incorrect");
        }

        user.setPassword(passwordEncoder.encode(dto.getNewPassword()));
        userRepository.save(user);
        log.info("Password changed successfully for user: {}", username);
    }

    @Override
    @Transactional
    public void toggleUserStatus(Long userId) {
        User user = findById(userId);
        user.setEnabled(!user.isEnabled());
        userRepository.save(user);
        log.info("Toggled enabled status to {} for userId: {}", user.isEnabled(), userId);
    }

    @Override
    public boolean existsByUsername(String username) {
        return userRepository.existsByUsername(username);
    }

    @Override
    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }
}
