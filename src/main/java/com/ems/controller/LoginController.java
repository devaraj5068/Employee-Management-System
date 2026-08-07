package com.ems.controller;

import com.ems.dto.UserRegistrationDTO;
import com.ems.service.DepartmentService;
import com.ems.service.RoleService;
import com.ems.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequiredArgsConstructor
public class LoginController {

    private final UserService userService;
    private final DepartmentService departmentService;
    private final RoleService roleService;

    @GetMapping("/login")
    public String loginPage() {
        return "public/login";
    }

    @GetMapping("/register")
    public String registerPage(Model model) {
        model.addAttribute("userDto", new UserRegistrationDTO());
        model.addAttribute("departments", departmentService.getAllDepartments());
        model.addAttribute("roles", roleService.getAllRoles());
        return "public/register";
    }

    @PostMapping("/register")
    public String processRegister(@Valid @ModelAttribute("userDto") UserRegistrationDTO userDto,
                                  BindingResult result,
                                  Model model,
                                  RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            model.addAttribute("departments", departmentService.getAllDepartments());
            model.addAttribute("roles", roleService.getAllRoles());
            return "public/register";
        }

        try {
            userService.registerUser(userDto);
            redirectAttributes.addFlashAttribute("successMessage", "Account created successfully! You can now log in.");
            return "redirect:/login";
        } catch (Exception ex) {
            model.addAttribute("errorMessage", ex.getMessage());
            model.addAttribute("departments", departmentService.getAllDepartments());
            model.addAttribute("roles", roleService.getAllRoles());
            return "public/register";
        }
    }

    @GetMapping("/forgot-password")
    public String forgotPasswordPage() {
        return "public/forgot-password";
    }

    @PostMapping("/forgot-password")
    public String processForgotPassword(String email, RedirectAttributes redirectAttributes) {
        redirectAttributes.addFlashAttribute("successMessage", "If an account exists with " + email + ", password reset instructions have been sent.");
        return "redirect:/login";
    }
}
