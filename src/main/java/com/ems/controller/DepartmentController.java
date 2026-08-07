package com.ems.controller;

import com.ems.dto.DepartmentDTO;
import com.ems.service.DepartmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/departments")
@RequiredArgsConstructor
public class DepartmentController {

    private final DepartmentService departmentService;

    @GetMapping
    public String listDepartments(Model model) {
        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("departmentDto", new DepartmentDTO());
        return "departments/list";
    }

    @PostMapping("/add")
    public String addDepartment(@Valid @ModelAttribute("departmentDto") DepartmentDTO dto,
                                BindingResult result,
                                Model model,
                                RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("departments", departmentService.getAllDepartments());
            return "departments/list";
        }

        try {
            departmentService.createDepartment(dto);
            redirectAttributes.addFlashAttribute("successMessage", "Department created successfully.");
            return "redirect:/departments";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("departments", departmentService.getAllDepartments());
            return "departments/list";
        }
    }

    @GetMapping("/edit/{id}")
    public String editDepartmentForm(@PathVariable Long id, Model model) {
        DepartmentDTO dept = departmentService.getDepartmentById(id);
        model.addAttribute("departmentDto", dept);
        return "departments/edit";
    }

    @PostMapping("/edit/{id}")
    public String updateDepartment(@PathVariable Long id,
                                   @Valid @ModelAttribute("departmentDto") DepartmentDTO dto,
                                   BindingResult result,
                                   Model model,
                                   RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            return "departments/edit";
        }

        try {
            departmentService.updateDepartment(id, dto);
            redirectAttributes.addFlashAttribute("successMessage", "Department updated successfully.");
            return "redirect:/departments";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            return "departments/edit";
        }
    }

    @PostMapping("/delete/{id}")
    public String deleteDepartment(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        try {
            departmentService.deleteDepartment(id);
            redirectAttributes.addFlashAttribute("successMessage", "Department deleted successfully.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/departments";
    }
}
