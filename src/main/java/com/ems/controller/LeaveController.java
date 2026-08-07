package com.ems.controller;

import com.ems.constants.LeaveType;
import com.ems.dto.EmployeeDTO;
import com.ems.dto.LeaveRequestDTO;
import com.ems.security.CustomUserDetails;
import com.ems.service.EmployeeService;
import com.ems.service.LeaveService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.Collections;
import java.util.List;
import java.util.Map;

@Controller
@RequiredArgsConstructor
public class LeaveController {

    private final LeaveService leaveService;
    private final EmployeeService employeeService;

    @GetMapping("/leave/apply")
    public String applyLeaveForm(@AuthenticationPrincipal CustomUserDetails userDetails, Model model) {
        LeaveRequestDTO leaveRequest = new LeaveRequestDTO();
        Long currentEmpId = null;

        if (userDetails != null) {
            try {
                EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
                if (emp != null) {
                    currentEmpId = emp.getId();
                    leaveRequest.setEmployeeId(emp.getId());
                }
            } catch (Exception ignored) {}
        }

        model.addAttribute("leaveRequest", leaveRequest);
        model.addAttribute("leaveTypes", LeaveType.values());
        List<EmployeeDTO> allEmployees = employeeService.getAllEmployees();
        model.addAttribute("employees", allEmployees != null ? allEmployees : Collections.emptyList());
        
        Map<String, Object> leaveBalance = leaveService.getLeaveBalance(currentEmpId);
        model.addAttribute("leaveBalance", leaveBalance);

        return "leave/apply";
    }

    @PostMapping("/leave/apply")
    public String processApplyLeave(@AuthenticationPrincipal CustomUserDetails userDetails,
                                    @Valid @ModelAttribute("leaveRequest") LeaveRequestDTO dto,
                                    BindingResult result,
                                    Model model,
                                    RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("leaveTypes", LeaveType.values());
            List<EmployeeDTO> allEmployees = employeeService.getAllEmployees();
            model.addAttribute("employees", allEmployees != null ? allEmployees : Collections.emptyList());
            model.addAttribute("leaveBalance", leaveService.getLeaveBalance(dto.getEmployeeId()));
            return "leave/apply";
        }

        try {
            if (dto.getEmployeeId() == null && userDetails != null) {
                EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
                dto.setEmployeeId(emp.getId());
            }

            leaveService.applyLeave(dto);
            redirectAttributes.addFlashAttribute("successMessage", "Leave request submitted successfully.");
            return "redirect:/leave/history";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("leaveTypes", LeaveType.values());
            List<EmployeeDTO> allEmployees = employeeService.getAllEmployees();
            model.addAttribute("employees", allEmployees != null ? allEmployees : Collections.emptyList());
            model.addAttribute("leaveBalance", leaveService.getLeaveBalance(dto.getEmployeeId()));
            return "leave/apply";
        }
    }

    @GetMapping({"/leave/history", "/leave/my"})
    public String leaveHistory(@AuthenticationPrincipal CustomUserDetails userDetails, Model model) {
        try {
            EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
            List<LeaveRequestDTO> history = leaveService.getLeaveHistory(emp.getId());
            model.addAttribute("leaves", history);
            model.addAttribute("leaveBalance", leaveService.getLeaveBalance(emp.getId()));
        } catch (Exception e) {
            model.addAttribute("errorMessage", "Unable to load leave history. Employee profile not found.");
        }
        return "leave/history";
    }

    @GetMapping({"/leave/list", "/leave/approvals"})
    public String pendingApprovals(@RequestParam(defaultValue = "0") int page,
                                   @RequestParam(defaultValue = "10") int size,
                                   Model model) {
        Page<LeaveRequestDTO> leavePage = leaveService.getPendingLeaveApprovals(
                PageRequest.of(page, size, Sort.by("createdAt").descending()));
        model.addAttribute("leavePage", leavePage);
        return "leave/list";
    }

    @PostMapping("/leave/approve/{id}")
    public String approveLeave(@PathVariable Long id,
                               @AuthenticationPrincipal CustomUserDetails userDetails,
                               @RequestParam(required = false) String remarks,
                               RedirectAttributes redirectAttributes) {
        try {
            leaveService.approveLeave(id, userDetails.getId(), remarks);
            redirectAttributes.addFlashAttribute("successMessage", "Leave request approved successfully.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/leave/list";
    }

    @PostMapping("/leave/reject/{id}")
    public String rejectLeave(@PathVariable Long id,
                              @AuthenticationPrincipal CustomUserDetails userDetails,
                              @RequestParam(required = false) String remarks,
                              RedirectAttributes redirectAttributes) {
        try {
            leaveService.rejectLeave(id, userDetails.getId(), remarks);
            redirectAttributes.addFlashAttribute("successMessage", "Leave request rejected.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/leave/list";
    }

    @PostMapping("/leave/cancel/{id}")
    public String cancelLeave(@PathVariable Long id,
                              @AuthenticationPrincipal CustomUserDetails userDetails,
                              RedirectAttributes redirectAttributes) {
        try {
            EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
            leaveService.cancelLeave(id, emp.getId());
            redirectAttributes.addFlashAttribute("successMessage", "Leave application cancelled.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/leave/history";
    }
}
