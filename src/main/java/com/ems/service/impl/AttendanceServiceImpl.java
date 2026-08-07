package com.ems.service.impl;

import com.ems.constants.AttendanceStatus;
import com.ems.dto.AttendanceDTO;
import com.ems.entity.Attendance;
import com.ems.entity.Employee;
import com.ems.exception.AttendanceNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.AttendanceRepository;
import com.ems.repository.EmployeeRepository;
import com.ems.service.AttendanceService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class AttendanceServiceImpl implements AttendanceService {

    private final AttendanceRepository attendanceRepository;
    private final EmployeeRepository employeeRepository;
    private static final LocalTime LATE_THRESHOLD = LocalTime.of(9, 30);

    @Override
    @Transactional
    public AttendanceDTO checkIn(Long employeeId) {
        LocalDate today = LocalDate.now();
        LocalTime now = LocalTime.now();

        Optional<Attendance> existingOpt = attendanceRepository.findByEmployeeIdAndAttendanceDate(employeeId, today);
        if (existingOpt.isPresent()) {
            Attendance existing = existingOpt.get();
            if (existing.getCheckInTime() != null) {
                throw new ValidationException("Already checked in for today at " + existing.getCheckInTime());
            }
            existing.setCheckInTime(now);
            boolean isLate = now.isAfter(LATE_THRESHOLD);
            existing.setLate(isLate);
            existing.setStatus(isLate ? AttendanceStatus.LATE : AttendanceStatus.PRESENT);
            return mapToDTO(attendanceRepository.save(existing));
        }

        Employee employee = employeeRepository.findById(employeeId)
                .orElseThrow(() -> new ValidationException("Employee not found with ID: " + employeeId));

        boolean isLate = now.isAfter(LATE_THRESHOLD);
        Attendance attendance = Attendance.builder()
                .employee(employee)
                .attendanceDate(today)
                .checkInTime(now)
                .isLate(isLate)
                .status(isLate ? AttendanceStatus.LATE : AttendanceStatus.PRESENT)
                .remarks(isLate ? "Late Arrival (Punched after 09:30 AM)" : "On-Time Check-In")
                .build();

        log.info("Check-in recorded for employee ID {} on {} (Late: {})", employeeId, today, isLate);
        return mapToDTO(attendanceRepository.save(attendance));
    }

    @Override
    @Transactional
    public AttendanceDTO checkOut(Long employeeId) {
        LocalDate today = LocalDate.now();
        Attendance attendance = attendanceRepository.findByEmployeeIdAndAttendanceDate(employeeId, today)
                .orElseThrow(() -> new ValidationException("No check-in record found for today. Please check in first."));

        if (attendance.getCheckOutTime() != null) {
            throw new ValidationException("Already checked out for today at " + attendance.getCheckOutTime());
        }

        LocalTime checkOutTime = LocalTime.now();
        attendance.setCheckOutTime(checkOutTime);

        if (attendance.getCheckInTime() != null) {
            long minutes = Duration.between(attendance.getCheckInTime(), checkOutTime).toMinutes();
            double hours = Math.round((minutes / 60.0) * 100.0) / 100.0;
            attendance.setWorkHours(hours);

            if (hours > 8.0) {
                attendance.setOvertimeHours(Math.round((hours - 8.0) * 100.0) / 100.0);
            }
            if (hours < 4.0 && !attendance.isLate()) {
                attendance.setStatus(AttendanceStatus.HALF_DAY);
            }
        }

        log.info("Check-out recorded for employee ID {} on {}", employeeId, today);
        return mapToDTO(attendanceRepository.save(attendance));
    }

    @Override
    public AttendanceDTO getTodayAttendance(Long employeeId) {
        LocalDate today = LocalDate.now();
        return attendanceRepository.findByEmployeeIdAndAttendanceDate(employeeId, today)
                .map(this::mapToDTO)
                .orElse(null);
    }

    @Override
    @Transactional
    public AttendanceDTO markAttendance(AttendanceDTO dto) {
        Employee employee = employeeRepository.findById(dto.getEmployeeId())
                .orElseThrow(() -> new ValidationException("Invalid Employee ID: " + dto.getEmployeeId()));

        Optional<Attendance> existing = attendanceRepository.findByEmployeeIdAndAttendanceDate(
                dto.getEmployeeId(), dto.getAttendanceDate());

        Attendance attendance = existing.orElseGet(Attendance::new);
        attendance.setEmployee(employee);
        attendance.setAttendanceDate(dto.getAttendanceDate());
        attendance.setCheckInTime(dto.getCheckInTime());
        attendance.setCheckOutTime(dto.getCheckOutTime());
        attendance.setStatus(dto.getStatus() != null ? dto.getStatus() : AttendanceStatus.PRESENT);
        attendance.setRemarks(dto.getRemarks());

        if (dto.getCheckInTime() != null && dto.getCheckOutTime() != null) {
            long minutes = Duration.between(dto.getCheckInTime(), dto.getCheckOutTime()).toMinutes();
            double hours = Math.round((minutes / 60.0) * 100.0) / 100.0;
            attendance.setWorkHours(hours);
            if (hours > 8.0) {
                attendance.setOvertimeHours(Math.round((hours - 8.0) * 100.0) / 100.0);
            }
        }

        log.info("Marked attendance for employee {} on date {}", employee.getEmployeeCode(), dto.getAttendanceDate());
        return mapToDTO(attendanceRepository.save(attendance));
    }

    @Override
    public Page<AttendanceDTO> getEmployeeAttendanceHistory(Long employeeId, Pageable pageable) {
        return attendanceRepository.findByEmployeeId(employeeId, pageable).map(this::mapToDTO);
    }

    @Override
    public List<AttendanceDTO> getEmployeeAttendanceBetween(Long employeeId, LocalDate startDate, LocalDate endDate) {
        return attendanceRepository.findByEmployeeIdAndAttendanceDateBetween(employeeId, startDate, endDate).stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public Page<AttendanceDTO> searchAttendance(Long employeeId, Long departmentId, LocalDate date, AttendanceStatus status, Pageable pageable) {
        return attendanceRepository.searchAttendance(employeeId, departmentId, date, status, pageable).map(this::mapToDTO);
    }

    @Override
    public Attendance getAttendanceEntityById(Long id) {
        return attendanceRepository.findById(id)
                .orElseThrow(() -> new AttendanceNotFoundException("Attendance record not found with ID: " + id));
    }

    private AttendanceDTO mapToDTO(Attendance att) {
        AttendanceDTO dto = new AttendanceDTO();
        dto.setId(att.getId());
        dto.setEmployeeId(att.getEmployee().getId());
        dto.setEmployeeCode(att.getEmployee().getEmployeeCode());
        dto.setEmployeeName(att.getEmployee().getFullName());
        if (att.getEmployee().getDepartment() != null) {
            dto.setDepartmentName(att.getEmployee().getDepartment().getName());
        }
        dto.setAttendanceDate(att.getAttendanceDate());
        dto.setCheckInTime(att.getCheckInTime());
        dto.setCheckOutTime(att.getCheckOutTime());
        dto.setWorkHours(att.getWorkHours());
        dto.setStatus(att.getStatus());
        dto.setRemarks(att.getRemarks());
        return dto;
    }
}
