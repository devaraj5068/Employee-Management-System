package com.ems.service;

import com.ems.constants.AttendanceStatus;
import com.ems.dto.AttendanceDTO;
import com.ems.entity.Attendance;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.time.LocalDate;
import java.util.List;

public interface AttendanceService {
    AttendanceDTO checkIn(Long employeeId);
    AttendanceDTO checkOut(Long employeeId);
    AttendanceDTO getTodayAttendance(Long employeeId);
    AttendanceDTO markAttendance(AttendanceDTO dto);
    Page<AttendanceDTO> getEmployeeAttendanceHistory(Long employeeId, Pageable pageable);
    List<AttendanceDTO> getEmployeeAttendanceBetween(Long employeeId, LocalDate startDate, LocalDate endDate);
    Page<AttendanceDTO> searchAttendance(Long employeeId, Long departmentId, LocalDate date, AttendanceStatus status, Pageable pageable);
    Attendance getAttendanceEntityById(Long id);
}
