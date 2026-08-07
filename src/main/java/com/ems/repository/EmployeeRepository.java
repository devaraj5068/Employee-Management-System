package com.ems.repository;

import com.ems.constants.EmploymentStatus;
import com.ems.entity.Employee;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EmployeeRepository extends JpaRepository<Employee, Long> {
    Optional<Employee> findByEmployeeCode(String employeeCode);
    Optional<Employee> findByEmail(String email);
    Optional<Employee> findByUserId(Long userId);
    boolean existsByEmployeeCode(String employeeCode);
    boolean existsByEmail(String email);

    long countByEmploymentStatus(EmploymentStatus status);

    @Query("SELECT e FROM Employee e WHERE " +
           "(:keyword IS NULL OR :keyword = '' OR " +
           " LOWER(e.firstName) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           " LOWER(e.lastName) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           " LOWER(e.email) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           " LOWER(e.employeeCode) LIKE LOWER(CONCAT('%', :keyword, '%'))) AND " +
           "(:deptId IS NULL OR e.department.id = :deptId) AND " +
           "(:roleId IS NULL OR e.role.id = :roleId) AND " +
           "(:status IS NULL OR e.employmentStatus = :status)")
    Page<Employee> searchEmployees(
            @Param("keyword") String keyword,
            @Param("deptId") Long deptId,
            @Param("roleId") Long roleId,
            @Param("status") EmploymentStatus status,
            Pageable pageable
    );

    List<Employee> findTop5ByOrderByCreatedAtDesc();
}
