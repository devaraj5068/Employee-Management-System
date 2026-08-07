package com.ems.service;

import com.ems.dto.SalaryDTO;
import com.ems.entity.Salary;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface SalaryService {
    SalaryDTO createSalary(SalaryDTO salaryDTO);
    SalaryDTO updateSalary(Long id, SalaryDTO salaryDTO);
    void deleteSalary(Long id);
    SalaryDTO getSalaryById(Long id);
    List<SalaryDTO> getSalaryHistoryByEmployee(Long employeeId);
    Page<SalaryDTO> searchSalaries(Long employeeId, Long departmentId, String payMonth, Pageable pageable);
    Salary getSalaryEntityById(Long id);
}
