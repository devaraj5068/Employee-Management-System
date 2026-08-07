package com.ems.controller;

import com.ems.constants.EmploymentStatus;
import com.ems.dto.EmployeeDTO;
import com.ems.service.DepartmentService;
import com.ems.service.EmployeeService;
import com.ems.service.RoleService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/employees")
@RequiredArgsConstructor
public class EmployeeController {

    private final EmployeeService employeeService;
    private final DepartmentService departmentService;
    private final RoleService roleService;

    @GetMapping
    public String listEmployees(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Long departmentId,
            @RequestParam(required = false) Long roleId,
            @RequestParam(required = false) EmploymentStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "firstName") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir,
            Model model) {

        Sort sort = sortDir.equalsIgnoreCase("desc") ? Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        PageRequest pageable = PageRequest.of(page, size, sort);

        Page<EmployeeDTO> employeePage = employeeService.searchEmployees(keyword, departmentId, roleId, status, pageable);

        model.addAttribute("employeePage", employeePage);
        model.addAttribute("keyword", keyword);
        model.addAttribute("departmentId", departmentId);
        model.addAttribute("roleId", roleId);
        model.addAttribute("status", status);
        model.addAttribute("sortBy", sortBy);
        model.addAttribute("sortDir", sortDir);
        model.addAttribute("reverseSortDir", sortDir.equals("asc") ? "desc" : "asc");

        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("roles", roleService.getAllRoles());
        model.addAttribute("statuses", EmploymentStatus.values());

        return "employees/list";
    }

    @GetMapping("/add")
    public String addEmployeeForm(Model model) {
        model.addAttribute("employeeDto", new EmployeeDTO());
        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("roles", roleService.getAllRoles());
        model.addAttribute("statuses", EmploymentStatus.values());
        return "employees/add";
    }

    @PostMapping("/add")
    public String createEmployee(@Valid @ModelAttribute("employeeDto") EmployeeDTO dto,
                                 BindingResult result,
                                 Model model,
                                 RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("departments", departmentService.getAllDepartments());
            model.addAttribute("roles", roleService.getAllRoles());
            model.addAttribute("statuses", EmploymentStatus.values());
            return "employees/add";
        }

        try {
            EmployeeDTO created = employeeService.createEmployee(dto);
            redirectAttributes.addFlashAttribute("successMessage", "Employee " + created.getFullName() + " created successfully!");
            return "redirect:/employees";
        } catch (Exception ex) {
            model.addAttribute("errorMessage", ex.getMessage());
            model.addAttribute("departments", departmentService.getAllDepartments());
            model.addAttribute("roles", roleService.getAllRoles());
            model.addAttribute("statuses", EmploymentStatus.values());
            return "employees/add";
        }
    }

    @GetMapping("/view/{id}")
    public String viewEmployee(@PathVariable Long id, Model model) {
        EmployeeDTO employee = employeeService.getEmployeeById(id);
        model.addAttribute("employee", employee);
        return "employees/view";
    }

    @GetMapping("/edit/{id}")
    public String editEmployeeForm(@PathVariable Long id, Model model) {
        EmployeeDTO employee = employeeService.getEmployeeById(id);
        model.addAttribute("employeeDto", employee);
        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("roles", roleService.getAllRoles());
        model.addAttribute("statuses", EmploymentStatus.values());
        return "employees/edit";
    }

    @PostMapping("/edit/{id}")
    public String updateEmployee(@PathVariable Long id,
                                 @Valid @ModelAttribute("employeeDto") EmployeeDTO dto,
                                 BindingResult result,
                                 Model model,
                                 RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("departments", departmentService.getAllDepartments());
            model.addAttribute("roles", roleService.getAllRoles());
            model.addAttribute("statuses", EmploymentStatus.values());
            return "employees/edit";
        }

        try {
            EmployeeDTO updated = employeeService.updateEmployee(id, dto);
            redirectAttributes.addFlashAttribute("successMessage", "Employee " + updated.getFullName() + " updated successfully!");
            return "redirect:/employees";
        } catch (Exception ex) {
            model.addAttribute("errorMessage", ex.getMessage());
            model.addAttribute("departments", departmentService.getAllDepartments());
            model.addAttribute("roles", roleService.getAllRoles());
            model.addAttribute("statuses", EmploymentStatus.values());
            return "employees/edit";
        }
    }

    @PostMapping("/delete/{id}")
    public String deleteEmployee(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        try {
            employeeService.deleteEmployee(id);
            redirectAttributes.addFlashAttribute("successMessage", "Employee deleted successfully.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/employees";
    }
}
