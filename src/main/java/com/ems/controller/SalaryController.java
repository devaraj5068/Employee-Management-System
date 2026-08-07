package com.ems.controller;

import com.ems.constants.PaymentStatus;
import com.ems.dto.EmployeeDTO;
import com.ems.dto.SalaryDTO;
import com.ems.security.CustomUserDetails;
import com.ems.service.DepartmentService;
import com.ems.service.EmployeeService;
import com.ems.service.SalaryService;
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

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Controller
@RequestMapping("/salary")
@RequiredArgsConstructor
public class SalaryController {

    private final SalaryService salaryService;
    private final EmployeeService employeeService;
    private final DepartmentService departmentService;

    @GetMapping("/all")
    public String listAllSalaries(
            @RequestParam(required = false) Long employeeId,
            @RequestParam(required = false) Long departmentId,
            @RequestParam(required = false) String payMonth,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            Model model) {

        Page<SalaryDTO> salaryPage = salaryService.searchSalaries(
                employeeId, departmentId, payMonth,
                PageRequest.of(page, size, Sort.by("payMonth").descending()));

        model.addAttribute("salaryPage", salaryPage);
        model.addAttribute("employeeId", employeeId);
        model.addAttribute("departmentId", departmentId);
        model.addAttribute("payMonth", payMonth);

        model.addAttribute("employees", employeeService.getAllEmployees());
        model.addAttribute("departments", departmentService.getAllDepartments());

        return "salary/list";
    }

    @GetMapping("/my")
    public String mySalaries(@AuthenticationPrincipal CustomUserDetails userDetails, Model model) {
        EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
        model.addAttribute("salaries", salaryService.getSalaryHistoryByEmployee(emp.getId()));
        model.addAttribute("employee", emp);
        return "salary/my-salaries";
    }

    @GetMapping("/create")
    public String createSalaryForm(Model model) {
        SalaryDTO dto = new SalaryDTO();
        dto.setPayMonth(LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM")));
        dto.setPaymentDate(LocalDate.now());

        model.addAttribute("salaryDto", dto);
        model.addAttribute("employees", employeeService.getAllEmployees());
        model.addAttribute("paymentStatuses", PaymentStatus.values());
        return "salary/form";
    }

    @PostMapping("/create")
    public String processCreateSalary(@Valid @ModelAttribute("salaryDto") SalaryDTO dto,
                                      BindingResult result,
                                      Model model,
                                      RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("employees", employeeService.getAllEmployees());
            model.addAttribute("paymentStatuses", PaymentStatus.values());
            return "salary/form";
        }

        try {
            salaryService.createSalary(dto);
            redirectAttributes.addFlashAttribute("successMessage", "Salary slip generated successfully.");
            return "redirect:/salary/all";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("employees", employeeService.getAllEmployees());
            model.addAttribute("paymentStatuses", PaymentStatus.values());
            return "salary/form";
        }
    }

    @GetMapping("/edit/{id}")
    public String editSalaryForm(@PathVariable Long id, Model model) {
        SalaryDTO salary = salaryService.getSalaryById(id);
        model.addAttribute("salaryDto", salary);
        model.addAttribute("employees", employeeService.getAllEmployees());
        model.addAttribute("paymentStatuses", PaymentStatus.values());
        return "salary/form";
    }

    @PostMapping("/edit/{id}")
    public String updateSalary(@PathVariable Long id,
                               @Valid @ModelAttribute("salaryDto") SalaryDTO dto,
                               BindingResult result,
                               Model model,
                               RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("employees", employeeService.getAllEmployees());
            model.addAttribute("paymentStatuses", PaymentStatus.values());
            return "salary/form";
        }

        try {
            salaryService.updateSalary(id, dto);
            redirectAttributes.addFlashAttribute("successMessage", "Salary details updated successfully.");
            return "redirect:/salary/all";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("employees", employeeService.getAllEmployees());
            model.addAttribute("paymentStatuses", PaymentStatus.values());
            return "salary/form";
        }
    }

    @GetMapping("/slip/{id}")
    public String viewSalarySlip(@PathVariable Long id, Model model) {
        SalaryDTO salary = salaryService.getSalaryById(id);
        EmployeeDTO employee = employeeService.getEmployeeById(salary.getEmployeeId());
        model.addAttribute("salary", salary);
        model.addAttribute("employee", employee);
        return "salary/slip";
    }

    @PostMapping("/delete/{id}")
    public String deleteSalary(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        try {
            salaryService.deleteSalary(id);
            redirectAttributes.addFlashAttribute("successMessage", "Salary record deleted.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/salary/all";
    }
}
