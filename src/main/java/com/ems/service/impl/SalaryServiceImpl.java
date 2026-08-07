package com.ems.service.impl;

import com.ems.constants.PaymentStatus;
import com.ems.dto.SalaryDTO;
import com.ems.entity.Employee;
import com.ems.entity.Salary;
import com.ems.exception.SalaryNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.EmployeeRepository;
import com.ems.repository.SalaryRepository;
import com.ems.service.SalaryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class SalaryServiceImpl implements SalaryService {

    private final SalaryRepository salaryRepository;
    private final EmployeeRepository employeeRepository;

    @Override
    @Transactional
    public SalaryDTO createSalary(SalaryDTO dto) {
        Employee employee = employeeRepository.findById(dto.getEmployeeId())
                .orElseThrow(() -> new ValidationException("Invalid Employee ID: " + dto.getEmployeeId()));

        Optional<Salary> existing = salaryRepository.findByEmployeeIdAndPayMonth(dto.getEmployeeId(), dto.getPayMonth());
        if (existing.isPresent()) {
            throw new ValidationException("Salary record already exists for employee " + employee.getFullName() + " for month " + dto.getPayMonth());
        }

        Salary salary = Salary.builder()
                .employee(employee)
                .payMonth(dto.getPayMonth())
                .basicSalary(dto.getBasicSalary())
                .hra(dto.getHra() != null ? dto.getHra() : BigDecimal.ZERO)
                .da(dto.getDa() != null ? dto.getDa() : BigDecimal.ZERO)
                .bonus(dto.getBonus() != null ? dto.getBonus() : BigDecimal.ZERO)
                .incentives(dto.getIncentives() != null ? dto.getIncentives() : BigDecimal.ZERO)
                .deductions(dto.getDeductions() != null ? dto.getDeductions() : BigDecimal.ZERO)
                .tax(dto.getTax() != null ? dto.getTax() : BigDecimal.ZERO)
                .paymentDate(dto.getPaymentDate() != null ? dto.getPaymentDate() : LocalDate.now())
                .paymentStatus(dto.getPaymentStatus() != null ? dto.getPaymentStatus() : PaymentStatus.PAID)
                .remarks(dto.getRemarks())
                .build();

        salary.calculateNetSalary();

        Salary saved = salaryRepository.save(salary);
        log.info("Created salary record ID {} for employee {} month {}", saved.getId(), employee.getEmployeeCode(), dto.getPayMonth());
        return mapToDTO(saved);
    }

    @Override
    @Transactional
    public SalaryDTO updateSalary(Long id, SalaryDTO dto) {
        Salary salary = getSalaryEntityById(id);

        salary.setBasicSalary(dto.getBasicSalary());
        salary.setHra(dto.getHra() != null ? dto.getHra() : BigDecimal.ZERO);
        salary.setDa(dto.getDa() != null ? dto.getDa() : BigDecimal.ZERO);
        salary.setBonus(dto.getBonus() != null ? dto.getBonus() : BigDecimal.ZERO);
        salary.setIncentives(dto.getIncentives() != null ? dto.getIncentives() : BigDecimal.ZERO);
        salary.setDeductions(dto.getDeductions() != null ? dto.getDeductions() : BigDecimal.ZERO);
        salary.setTax(dto.getTax() != null ? dto.getTax() : BigDecimal.ZERO);
        if (dto.getPaymentDate() != null) salary.setPaymentDate(dto.getPaymentDate());
        if (dto.getPaymentStatus() != null) salary.setPaymentStatus(dto.getPaymentStatus());
        salary.setRemarks(dto.getRemarks());

        salary.calculateNetSalary();

        Salary updated = salaryRepository.save(salary);
        log.info("Updated salary record ID {}", updated.getId());
        return mapToDTO(updated);
    }

    @Override
    @Transactional
    public void deleteSalary(Long id) {
        Salary salary = getSalaryEntityById(id);
        salaryRepository.delete(salary);
        log.info("Deleted salary record ID {}", id);
    }

    @Override
    public SalaryDTO getSalaryById(Long id) {
        return mapToDTO(getSalaryEntityById(id));
    }

    @Override
    public List<SalaryDTO> getSalaryHistoryByEmployee(Long employeeId) {
        return salaryRepository.findByEmployeeIdOrderByPayMonthDesc(employeeId).stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public Page<SalaryDTO> searchSalaries(Long employeeId, Long departmentId, String payMonth, Pageable pageable) {
        return salaryRepository.searchSalaries(employeeId, departmentId, payMonth, pageable).map(this::mapToDTO);
    }

    @Override
    public Salary getSalaryEntityById(Long id) {
        return salaryRepository.findById(id)
                .orElseThrow(() -> new SalaryNotFoundException("Salary record not found with ID: " + id));
    }

    private SalaryDTO mapToDTO(Salary sal) {
        SalaryDTO dto = new SalaryDTO();
        dto.setId(sal.getId());
        dto.setEmployeeId(sal.getEmployee().getId());
        dto.setEmployeeCode(sal.getEmployee().getEmployeeCode());
        dto.setEmployeeName(sal.getEmployee().getFullName());
        if (sal.getEmployee().getDepartment() != null) {
            dto.setDepartmentName(sal.getEmployee().getDepartment().getName());
        }
        if (sal.getEmployee().getRole() != null) {
            dto.setRoleName(sal.getEmployee().getRole().getName());
        }
        dto.setPayMonth(sal.getPayMonth());
        dto.setBasicSalary(sal.getBasicSalary());
        dto.setHra(sal.getHra());
        dto.setDa(sal.getDa());
        dto.setBonus(sal.getBonus());
        dto.setIncentives(sal.getIncentives());
        dto.setDeductions(sal.getDeductions());
        dto.setTax(sal.getTax());
        dto.setNetSalary(sal.getNetSalary());
        dto.setPaymentDate(sal.getPaymentDate());
        dto.setPaymentStatus(sal.getPaymentStatus());
        dto.setRemarks(sal.getRemarks());
        return dto;
    }
}
