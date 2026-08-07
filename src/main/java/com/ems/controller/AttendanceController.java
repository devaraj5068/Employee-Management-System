package com.ems.controller;

import com.ems.constants.AttendanceStatus;
import com.ems.dto.AttendanceDTO;
import com.ems.dto.EmployeeDTO;
import com.ems.security.CustomUserDetails;
import com.ems.service.AttendanceService;
import com.ems.service.DepartmentService;
import com.ems.service.EmployeeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.time.LocalDate;

@Controller
@RequestMapping("/attendance")
@RequiredArgsConstructor
public class AttendanceController {

    private final AttendanceService attendanceService;
    private final EmployeeService employeeService;
    private final DepartmentService departmentService;

    @PostMapping("/checkin")
    public String checkIn(@AuthenticationPrincipal CustomUserDetails userDetails, RedirectAttributes redirectAttributes) {
        try {
            EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
            attendanceService.checkIn(emp.getId());
            redirectAttributes.addFlashAttribute("successMessage", "Checked in successfully!");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/dashboard";
    }

    @PostMapping("/checkout")
    public String checkOut(@AuthenticationPrincipal CustomUserDetails userDetails, RedirectAttributes redirectAttributes) {
        try {
            EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
            attendanceService.checkOut(emp.getId());
            redirectAttributes.addFlashAttribute("successMessage", "Checked out successfully!");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/dashboard";
    }

    @GetMapping("/my")
    public String myAttendance(@AuthenticationPrincipal CustomUserDetails userDetails,
                               @RequestParam(defaultValue = "0") int page,
                               @RequestParam(defaultValue = "10") int size,
                               Model model) {
        EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
        Page<AttendanceDTO> attendancePage = attendanceService.getEmployeeAttendanceHistory(
                emp.getId(), PageRequest.of(page, size, Sort.by("attendanceDate").descending()));

        model.addAttribute("attendancePage", attendancePage);
        model.addAttribute("employee", emp);
        model.addAttribute("todayAttendance", attendanceService.getTodayAttendance(emp.getId()));

        return "attendance/my-attendance";
    }

    @GetMapping("/all")
    public String listAllAttendance(
            @RequestParam(required = false) Long employeeId,
            @RequestParam(required = false) Long departmentId,
            @RequestParam(required = false) @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate date,
            @RequestParam(required = false) AttendanceStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            Model model) {

        Page<AttendanceDTO> attendancePage = attendanceService.searchAttendance(
                employeeId, departmentId, date, status,
                PageRequest.of(page, size, Sort.by("attendanceDate").descending()));

        model.addAttribute("attendancePage", attendancePage);
        model.addAttribute("employeeId", employeeId);
        model.addAttribute("departmentId", departmentId);
        model.addAttribute("date", date);
        model.addAttribute("status", status);

        model.addAttribute("employees", employeeService.getAllEmployees());
        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("statuses", AttendanceStatus.values());

        return "attendance/list";
    }

    @GetMapping("/mark")
    public String markAttendanceForm(Model model) {
        model.addAttribute("attendanceDto", new AttendanceDTO());
        model.addAttribute("employees", employeeService.getAllEmployees());
        model.addAttribute("statuses", AttendanceStatus.values());
        return "attendance/mark";
    }

    @PostMapping("/mark")
    public String processMarkAttendance(@Valid @ModelAttribute("attendanceDto") AttendanceDTO dto,
                                        BindingResult result,
                                        Model model,
                                        RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("employees", employeeService.getAllEmployees());
            model.addAttribute("statuses", AttendanceStatus.values());
            return "attendance/mark";
        }

        try {
            attendanceService.markAttendance(dto);
            redirectAttributes.addFlashAttribute("successMessage", "Attendance marked successfully.");
            return "redirect:/attendance/all";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("employees", employeeService.getAllEmployees());
            model.addAttribute("statuses", AttendanceStatus.values());
            return "attendance/mark";
        }
    }
}
