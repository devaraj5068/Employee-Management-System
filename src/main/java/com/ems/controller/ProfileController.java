package com.ems.controller;

import com.ems.dto.ChangePasswordDTO;
import com.ems.dto.EmployeeDTO;
import com.ems.security.CustomUserDetails;
import com.ems.service.EmployeeService;
import com.ems.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
@RequestMapping("/profile")
@RequiredArgsConstructor
public class ProfileController {

    private final EmployeeService employeeService;
    private final UserService userService;

    @GetMapping
    public String viewProfile(@AuthenticationPrincipal CustomUserDetails userDetails, Model model) {
        try {
            EmployeeDTO emp = employeeService.getEmployeeByUserId(userDetails.getId());
            model.addAttribute("employee", emp);
        } catch (Exception e) {
            model.addAttribute("warningMessage", "No employee profile linked to user account yet.");
        }
        model.addAttribute("user", userService.findById(userDetails.getId()));
        return "profile/view";
    }

    @GetMapping("/change-password")
    public String changePasswordForm(Model model) {
        model.addAttribute("changePasswordDto", new ChangePasswordDTO());
        return "profile/change-password";
    }

    @PostMapping("/change-password")
    public String processChangePassword(@AuthenticationPrincipal CustomUserDetails userDetails,
                                        @Valid @ModelAttribute("changePasswordDto") ChangePasswordDTO dto,
                                        BindingResult result,
                                        Model model,
                                        RedirectAttributes redirectAttributes) {
        if (result.hasErrors()) {
            return "profile/change-password";
        }

        try {
            userService.changePassword(userDetails.getUsername(), dto);
            redirectAttributes.addFlashAttribute("successMessage", "Password updated successfully!");
            return "redirect:/profile";
        } catch (Exception e) {
            model.addAttribute("errorMessage", e.getMessage());
            return "profile/change-password";
        }
    }
}
