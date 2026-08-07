package com.ems.dto;

import com.ems.constants.AttendanceStatus;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;
import java.time.LocalTime;

@Data
public class AttendanceDTO {

    private Long id;

    @NotNull(message = "Employee selection is required")
    private Long employeeId;

    private String employeeCode;
    private String employeeName;
    private String departmentName;

    @NotNull(message = "Attendance date is required")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate attendanceDate;

    @DateTimeFormat(pattern = "HH:mm")
    private LocalTime checkInTime;

    @DateTimeFormat(pattern = "HH:mm")
    private LocalTime checkOutTime;

    private Double workHours = 0.0;

    @NotNull(message = "Attendance status is required")
    private AttendanceStatus status = AttendanceStatus.PRESENT;

    private String remarks;
}
