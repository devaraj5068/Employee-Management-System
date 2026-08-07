package com.ems.controller;

import com.ems.dto.AttendanceDTO;
import com.ems.dto.DashboardStatsDTO;
import com.ems.dto.EmployeeDTO;
import com.ems.dto.SalaryDTO;
import com.ems.security.CustomUserDetails;
import com.ems.service.AttendanceService;
import com.ems.service.EmployeeService;
import com.ems.service.LeaveService;
import com.ems.service.SalaryService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
@RequiredArgsConstructor
public class DashboardController {

    private final EmployeeService employeeService;
    private final AttendanceService attendanceService;
    private final SalaryService salaryService;
    private final LeaveService leaveService;

    @GetMapping("/dashboard")
    public String dashboard(@AuthenticationPrincipal CustomUserDetails userDetails, Model model) {
        boolean isAdminOrHR = userDetails.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN") || a.getAuthority().equals("ROLE_HR") || a.getAuthority().equals("ROLE_MANAGER"));

        if (isAdminOrHR) {
            DashboardStatsDTO stats = employeeService.getDashboardStats();
            model.addAttribute("stats", stats);
            return "dashboard/admin-dashboard";
        } else {
            // Employee specific dashboard
            try {
                EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
                model.addAttribute("employee", emp);

                AttendanceDTO todayAttendance = attendanceService.getTodayAttendance(emp.getId());
                model.addAttribute("todayAttendance", todayAttendance);

                List<SalaryDTO> salaries = salaryService.getSalaryHistoryByEmployee(emp.getId());
                model.addAttribute("salaries", salaries);
                if (!salaries.isEmpty()) {
                    model.addAttribute("latestSalary", salaries.get(0));
                }

                model.addAttribute("leaves", leaveService.getEmployeeLeaves(emp.getId()));
            } catch (Exception e) {
                model.addAttribute("warningMessage", "Profile details missing or not linked yet.");
            }
            return "dashboard/employee-dashboard";
        }
    }
}
