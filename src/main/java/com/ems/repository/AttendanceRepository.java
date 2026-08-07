package com.ems.repository;

import com.ems.constants.AttendanceStatus;
import com.ems.entity.Attendance;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface AttendanceRepository extends JpaRepository<Attendance, Long> {

    Optional<Attendance> findByEmployeeIdAndAttendanceDate(Long employeeId, LocalDate date);

    List<Attendance> findByEmployeeIdAndAttendanceDateBetween(Long employeeId, LocalDate startDate, LocalDate endDate);

    Page<Attendance> findByEmployeeId(Long employeeId, Pageable pageable);

    long countByAttendanceDateAndStatus(LocalDate date, AttendanceStatus status);

    @Query("SELECT a FROM Attendance a WHERE " +
           "(:employeeId IS NULL OR a.employee.id = :employeeId) AND " +
           "(:deptId IS NULL OR a.employee.department.id = :deptId) AND " +
           "(:date IS NULL OR a.attendanceDate = :date) AND " +
           "(:status IS NULL OR a.status = :status)")
    Page<Attendance> searchAttendance(
            @Param("employeeId") Long employeeId,
            @Param("deptId") Long deptId,
            @Param("date") LocalDate date,
            @Param("status") AttendanceStatus status,
            Pageable pageable
    );
}
