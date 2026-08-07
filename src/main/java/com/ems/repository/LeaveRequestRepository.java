package com.ems.repository;

import com.ems.constants.LeaveStatus;
import com.ems.entity.LeaveRequest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LeaveRequestRepository extends JpaRepository<LeaveRequest, Long> {
    List<LeaveRequest> findByEmployeeIdOrderByCreatedAtDesc(Long employeeId);
    Page<LeaveRequest> findByEmployeeId(Long employeeId, Pageable pageable);
    Page<LeaveRequest> findByStatus(LeaveStatus status, Pageable pageable);
    long countByStatus(LeaveStatus status);
    List<LeaveRequest> findByEmployeeIdAndStatus(Long employeeId, LeaveStatus status);

    @Query("SELECT COALESCE(SUM(l.numberOfDays), 0) FROM LeaveRequest l WHERE l.employee.id = :employeeId AND l.status = :status")
    int sumDaysByEmployeeIdAndStatus(@Param("employeeId") Long employeeId, @Param("status") LeaveStatus status);
}
