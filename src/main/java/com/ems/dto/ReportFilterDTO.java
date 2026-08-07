package com.ems.dto;

import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;

@Data
public class ReportFilterDTO {
    private String reportType; // EMPLOYEE, ATTENDANCE, SALARY, DEPARTMENT
    private Long departmentId;
    private Long roleId;
    private String month; // YYYY-MM
    
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate startDate;

    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate endDate;

    private String exportFormat; // PDF or EXCEL
}
