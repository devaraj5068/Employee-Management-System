package com.ems.repository;

import com.ems.entity.Salary;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Repository
public interface SalaryRepository extends JpaRepository<Salary, Long> {

    Optional<Salary> findByEmployeeIdAndPayMonth(Long employeeId, String payMonth);

    List<Salary> findByEmployeeIdOrderByPayMonthDesc(Long employeeId);

    Page<Salary> findByEmployeeId(Long employeeId, Pageable pageable);

    @Query("SELECT SUM(s.netSalary) FROM Salary s WHERE s.payMonth = :payMonth")
    BigDecimal sumNetSalaryByPayMonth(@Param("payMonth") String payMonth);

    @Query("SELECT s FROM Salary s WHERE " +
           "(:employeeId IS NULL OR s.employee.id = :employeeId) AND " +
           "(:deptId IS NULL OR s.employee.department.id = :deptId) AND " +
           "(:payMonth IS NULL OR :payMonth = '' OR s.payMonth = :payMonth)")
    Page<Salary> searchSalaries(
            @Param("employeeId") Long employeeId,
            @Param("deptId") Long deptId,
            @Param("payMonth") String payMonth,
            Pageable pageable
    );
}
