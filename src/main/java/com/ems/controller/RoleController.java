package com.ems.controller;

import com.ems.dto.RoleDTO;
import com.ems.service.RoleService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/roles")
@RequiredArgsConstructor
public class RoleController {

    private final RoleService roleService;

    @GetMapping
    public String listRoles(Model model) {
        model.addAttribute("roles", roleService.getAllRoles());
        model.addAttribute("roleDto", new RoleDTO());
        return "roles/list";
    }

    @PostMapping("/add")
    public String addRole(@Valid @ModelAttribute("roleDto") RoleDTO dto,
                          BindingResult result,
                          Model model,
                          RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("roles", roleService.getAllRoles());
            return "roles/list";
        }

        try {
            roleService.createRole(dto);
            redirectAttributes.addFlashAttribute("successMessage", "Role created successfully.");
            return "redirect:/roles";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            model.addAttribute("roles", roleService.getAllRoles());
            return "roles/list";
        }
    }

    @GetMapping("/edit/{id}")
    public String editRoleForm(@PathVariable Long id, Model model) {
        RoleDTO role = roleService.getRoleById(id);
        model.addAttribute("roleDto", role);
        return "roles/edit";
    }

    @PostMapping("/edit/{id}")
    public String updateRole(@PathVariable Long id,
                             @Valid @ModelAttribute("roleDto") RoleDTO dto,
                             BindingResult result,
                             Model model,
                             RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            return "roles/edit";
        }

        try {
            roleService.updateRole(id, dto);
            redirectAttributes.addFlashAttribute("successMessage", "Role updated successfully.");
            return "redirect:/roles";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            return "roles/edit";
        }
    }

    @PostMapping("/delete/{id}")
    public String deleteRole(@PathVariable Long id, RedirectAttributes redirectAttributes) {
        try {
            roleService.deleteRole(id);
            redirectAttributes.addFlashAttribute("successMessage", "Role deleted successfully.");
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("errorMessage", e.getMessage());
        }
        return "redirect:/roles";
    }
}
