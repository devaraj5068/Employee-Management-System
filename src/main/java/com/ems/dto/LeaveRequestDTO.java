package com.ems.dto;

import com.ems.constants.LeaveStatus;
import com.ems.constants.LeaveType;
import jakarta.validation.constraints.FutureOrPresent;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;

@Data
public class LeaveRequestDTO {

    private Long id;

    @NotNull(message = "Employee selection is required")
    private Long employeeId;

    private String employeeCode;
    private String employeeName;
    private String departmentName;

    @NotNull(message = "Leave type is required")
    private LeaveType leaveType;

    @NotNull(message = "Start date is required")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate startDate;

    @NotNull(message = "End date is required")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate endDate;

    private int numberOfDays;

    @NotBlank(message = "Reason for leave is required")
    private String reason;

    private LeaveStatus status = LeaveStatus.PENDING;

    private Long approvedById;
    private String approvedByName;

    private String remarks;
    private String createdAtFormatted;
}
