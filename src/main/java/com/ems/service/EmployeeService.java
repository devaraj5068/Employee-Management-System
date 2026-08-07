package com.ems.service;

import com.ems.constants.EmploymentStatus;
import com.ems.dto.DashboardStatsDTO;
import com.ems.dto.EmployeeDTO;
import com.ems.entity.Employee;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface EmployeeService {
    EmployeeDTO createEmployee(EmployeeDTO employeeDTO);
    EmployeeDTO updateEmployee(Long id, EmployeeDTO employeeDTO);
    void deleteEmployee(Long id);
    EmployeeDTO getEmployeeById(Long id);
    EmployeeDTO getEmployeeByCode(String code);
    EmployeeDTO getEmployeeByEmail(String email);
    EmployeeDTO getEmployeeByUserId(Long userId);
    Employee getEmployeeEntityById(Long id);

    Page<EmployeeDTO> searchEmployees(String keyword, Long departmentId, Long roleId, EmploymentStatus status, Pageable pageable);
    List<EmployeeDTO> getAllEmployees();
    DashboardStatsDTO getDashboardStats();
}
