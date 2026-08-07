package com.ems.dto;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Data
@Builder
public class DashboardStatsDTO {
    private long totalEmployees;
    private long activeEmployees;
    private long totalDepartments;
    private long totalRoles;
    private long todayPresentCount;
    private long todayAbsentCount;
    private long todayLeaveCount;
    private BigDecimal monthlySalaryExpense;

    private Map<String, Long> employeesByDepartment;
    private Map<String, Long> attendanceStatusBreakdown;
    private List<EmployeeDTO> recentEmployees;
}
