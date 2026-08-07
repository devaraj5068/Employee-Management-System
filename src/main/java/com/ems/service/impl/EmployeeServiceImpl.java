package com.ems.service.impl;

import com.ems.constants.AttendanceStatus;
import com.ems.constants.EmploymentStatus;
import com.ems.dto.DashboardStatsDTO;
import com.ems.dto.EmployeeDTO;
import com.ems.entity.Department;
import com.ems.entity.Employee;
import com.ems.entity.Role;
import com.ems.exception.EmployeeNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.*;
import com.ems.service.EmployeeService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class EmployeeServiceImpl implements EmployeeService {

    private final EmployeeRepository employeeRepository;
    private final DepartmentRepository departmentRepository;
    private final RoleRepository roleRepository;
    private final AttendanceRepository attendanceRepository;
    private final SalaryRepository salaryRepository;

    @Override
    @Transactional
    public EmployeeDTO createEmployee(EmployeeDTO dto) {
        if (dto.getEmail() != null && employeeRepository.existsByEmail(dto.getEmail())) {
            throw new ValidationException("Email '" + dto.getEmail() + "' is already registered");
        }

        String empCode = dto.getEmployeeCode();
        if (empCode == null || empCode.trim().isEmpty()) {
            empCode = "EMP" + String.format("%04d", (employeeRepository.count() + 1));
        } else if (employeeRepository.existsByEmployeeCode(empCode)) {
            throw new ValidationException("Employee Code '" + empCode + "' already exists");
        }

        Department dept = null;
        if (dto.getDepartmentId() != null) {
            dept = departmentRepository.findById(dto.getDepartmentId())
                    .orElseThrow(() -> new ValidationException("Invalid Department ID: " + dto.getDepartmentId()));
        }

        Role role = null;
        if (dto.getRoleId() != null) {
            role = roleRepository.findById(dto.getRoleId())
                    .orElseThrow(() -> new ValidationException("Invalid Role ID: " + dto.getRoleId()));
        }

        Employee manager = null;
        if (dto.getManagerId() != null) {
            manager = employeeRepository.findById(dto.getManagerId()).orElse(null);
        }

        Employee employee = Employee.builder()
                .employeeCode(empCode)
                .firstName(dto.getFirstName())
                .lastName(dto.getLastName())
                .email(dto.getEmail())
                .mobileNumber(dto.getMobileNumber())
                .gender(dto.getGender())
                .dateOfBirth(dto.getDateOfBirth())
                .address(dto.getAddress())
                .city(dto.getCity())
                .state(dto.getState())
                .country(dto.getCountry())
                .joiningDate(dto.getJoiningDate() != null ? dto.getJoiningDate() : LocalDate.now())
                .emergencyContact(dto.getEmergencyContact())
                .bloodGroup(dto.getBloodGroup())
                .manager(manager)
                .department(dept)
                .role(role)
                .employmentStatus(dto.getEmploymentStatus() != null ? dto.getEmploymentStatus() : EmploymentStatus.ACTIVE)
                .profilePictureUrl(dto.getProfilePictureUrl() != null && !dto.getProfilePictureUrl().trim().isEmpty() ? dto.getProfilePictureUrl() : "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150")
                .build();

        Employee saved = employeeRepository.save(employee);
        log.info("Created employee profile: {} ({})", saved.getFullName(), saved.getEmployeeCode());
        return mapToDTO(saved);
    }

    @Override
    @Transactional
    public EmployeeDTO updateEmployee(Long id, EmployeeDTO dto) {
        Employee employee = getEmployeeEntityById(id);

        if (!employee.getEmail().equalsIgnoreCase(dto.getEmail()) && employeeRepository.existsByEmail(dto.getEmail())) {
            throw new ValidationException("Email '" + dto.getEmail() + "' is already registered to another employee");
        }

        Department dept = null;
        if (dto.getDepartmentId() != null) {
            dept = departmentRepository.findById(dto.getDepartmentId())
                    .orElseThrow(() -> new ValidationException("Invalid Department ID: " + dto.getDepartmentId()));
        }

        Role role = null;
        if (dto.getRoleId() != null) {
            role = roleRepository.findById(dto.getRoleId())
                    .orElseThrow(() -> new ValidationException("Invalid Role ID: " + dto.getRoleId()));
        }

        Employee manager = null;
        if (dto.getManagerId() != null) {
            manager = employeeRepository.findById(dto.getManagerId()).orElse(null);
        }

        employee.setFirstName(dto.getFirstName());
        employee.setLastName(dto.getLastName());
        employee.setEmail(dto.getEmail());
        employee.setMobileNumber(dto.getMobileNumber());
        employee.setGender(dto.getGender());
        employee.setDateOfBirth(dto.getDateOfBirth());
        employee.setAddress(dto.getAddress());
        employee.setCity(dto.getCity());
        employee.setState(dto.getState());
        employee.setCountry(dto.getCountry());
        if (dto.getJoiningDate() != null) employee.setJoiningDate(dto.getJoiningDate());
        employee.setEmergencyContact(dto.getEmergencyContact());
        employee.setBloodGroup(dto.getBloodGroup());
        employee.setManager(manager);
        employee.setDepartment(dept);
        employee.setRole(role);
        if (dto.getEmploymentStatus() != null) employee.setEmploymentStatus(dto.getEmploymentStatus());
        if (dto.getProfilePictureUrl() != null && !dto.getProfilePictureUrl().trim().isEmpty()) {
            employee.setProfilePictureUrl(dto.getProfilePictureUrl());
        }

        Employee updated = employeeRepository.save(employee);
        log.info("Updated employee profile ID: {}", updated.getId());
        return mapToDTO(updated);
    }

    @Override
    @Transactional
    public void deleteEmployee(Long id) {
        Employee employee = getEmployeeEntityById(id);
        employeeRepository.delete(employee);
        log.info("Deleted employee ID: {}", id);
    }

    @Override
    public EmployeeDTO getEmployeeById(Long id) {
        return mapToDTO(getEmployeeEntityById(id));
    }

    @Override
    public EmployeeDTO getEmployeeByCode(String code) {
        Employee employee = employeeRepository.findByEmployeeCode(code)
                .orElseThrow(() -> new EmployeeNotFoundException("Employee not found with code: " + code));
        return mapToDTO(employee);
    }

    @Override
    public EmployeeDTO getEmployeeByEmail(String email) {
        Employee employee = employeeRepository.findByEmail(email)
                .orElseThrow(() -> new EmployeeNotFoundException("Employee not found with email: " + email));
        return mapToDTO(employee);
    }

    @Override
    public EmployeeDTO getEmployeeByUserId(Long userId) {
        Employee employee = employeeRepository.findByUserId(userId)
                .orElseThrow(() -> new EmployeeNotFoundException("Employee profile not linked to user ID: " + userId));
        return mapToDTO(employee);
    }

    @Override
    public Employee getEmployeeEntityById(Long id) {
        return employeeRepository.findById(id)
                .orElseThrow(() -> new EmployeeNotFoundException("Employee not found with ID: " + id));
    }

    @Override
    public Page<EmployeeDTO> searchEmployees(String keyword, Long departmentId, Long roleId, EmploymentStatus status, Pageable pageable) {
        return employeeRepository.searchEmployees(keyword, departmentId, roleId, status, pageable)
                .map(this::mapToDTO);
    }

    @Override
    public List<EmployeeDTO> getAllEmployees() {
        return employeeRepository.findAll().stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public DashboardStatsDTO getDashboardStats() {
        long totalEmp = employeeRepository.count();
        long activeEmp = employeeRepository.countByEmploymentStatus(EmploymentStatus.ACTIVE);
        long totalDepts = departmentRepository.count();
        long totalRoles = roleRepository.count();

        LocalDate today = LocalDate.now();
        long presentToday = attendanceRepository.countByAttendanceDateAndStatus(today, AttendanceStatus.PRESENT);
        long absentToday = attendanceRepository.countByAttendanceDateAndStatus(today, AttendanceStatus.ABSENT);
        long leaveToday = attendanceRepository.countByAttendanceDateAndStatus(today, AttendanceStatus.LEAVE);

        String currentMonth = today.format(DateTimeFormatter.ofPattern("yyyy-MM"));
        BigDecimal monthlyExpense = salaryRepository.sumNetSalaryByPayMonth(currentMonth);
        if (monthlyExpense == null) monthlyExpense = BigDecimal.ZERO;

        Map<String, Long> deptBreakdown = new HashMap<>();
        departmentRepository.findAll().forEach(dept -> {
            long count = dept.getEmployees() != null ? dept.getEmployees().size() : 0;
            deptBreakdown.put(dept.getName(), count);
        });

        Map<String, Long> attBreakdown = new HashMap<>();
        attBreakdown.put("PRESENT", presentToday);
        attBreakdown.put("ABSENT", absentToday);
        attBreakdown.put("LEAVE", leaveToday);

        List<EmployeeDTO> recentEmployees = employeeRepository.findTop5ByOrderByCreatedAtDesc().stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());

        return DashboardStatsDTO.builder()
                .totalEmployees(totalEmp)
                .activeEmployees(activeEmp)
                .totalDepartments(totalDepts)
                .totalRoles(totalRoles)
                .todayPresentCount(presentToday)
                .todayAbsentCount(absentToday)
                .todayLeaveCount(leaveToday)
                .monthlySalaryExpense(monthlyExpense)
                .employeesByDepartment(deptBreakdown)
                .attendanceStatusBreakdown(attBreakdown)
                .recentEmployees(recentEmployees)
                .build();
    }

    private EmployeeDTO mapToDTO(Employee emp) {
        EmployeeDTO dto = new EmployeeDTO();
        dto.setId(emp.getId());
        dto.setEmployeeCode(emp.getEmployeeCode());
        dto.setFirstName(emp.getFirstName());
        dto.setLastName(emp.getLastName());
        dto.setEmail(emp.getEmail());
        dto.setMobileNumber(emp.getMobileNumber());
        dto.setGender(emp.getGender());
        dto.setDateOfBirth(emp.getDateOfBirth());
        dto.setAddress(emp.getAddress());
        dto.setCity(emp.getCity());
        dto.setState(emp.getState());
        dto.setCountry(emp.getCountry());
        dto.setJoiningDate(emp.getJoiningDate());
        dto.setEmergencyContact(emp.getEmergencyContact());
        dto.setBloodGroup(emp.getBloodGroup());
        if (emp.getManager() != null) {
            dto.setManagerId(emp.getManager().getId());
            dto.setManagerName(emp.getManager().getFullName());
        }
        if (emp.getDepartment() != null) {
            dto.setDepartmentId(emp.getDepartment().getId());
            dto.setDepartmentName(emp.getDepartment().getName());
        }
        if (emp.getRole() != null) {
            dto.setRoleId(emp.getRole().getId());
            dto.setRoleName(emp.getRole().getName());
        }
        dto.setEmploymentStatus(emp.getEmploymentStatus());
        dto.setProfilePictureUrl(emp.getProfilePictureUrl());
        return dto;
    }
}
