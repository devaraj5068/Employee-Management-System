package com.ems.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.servlet.resource.NoResourceFoundException;
import org.thymeleaf.exceptions.TemplateInputException;
import org.thymeleaf.exceptions.TemplateProcessingException;

@Slf4j
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public String handleResourceNotFound(ResourceNotFoundException ex, Model model) {
        log.warn("Resource not found exception: {}", ex.getMessage());
        model.addAttribute("status", 404);
        model.addAttribute("error", "Not Found");
        model.addAttribute("message", ex.getMessage());
        model.addAttribute("errorMessage", ex.getMessage());
        return "error/404";
    }

    @ExceptionHandler(ValidationException.class)
    public String handleValidationException(ValidationException ex, Model model) {
        log.warn("Validation exception: {}", ex.getMessage());
        model.addAttribute("status", 400);
        model.addAttribute("error", "Bad Request");
        model.addAttribute("message", ex.getMessage());
        model.addAttribute("errorMessage", ex.getMessage());
        return "error/500";
    }

    @ExceptionHandler(AccessDeniedException.class)
    public String handleAccessDenied(AccessDeniedException ex, Model model) {
        log.warn("Access denied exception: {}", ex.getMessage());
        model.addAttribute("status", 403);
        model.addAttribute("error", "Access Denied");
        model.addAttribute("message", "You do not have authorization to access this resource.");
        model.addAttribute("errorMessage", "You do not have authorization to access this resource.");
        return "error/403";
    }

    @ExceptionHandler({TemplateInputException.class, TemplateProcessingException.class})
    public String handleTemplateParsing(Exception ex, Model model) {
        log.error("Thymeleaf Template Exception: ", ex);
        model.addAttribute("status", 500);
        model.addAttribute("error", "Internal Server Error");
        model.addAttribute("message", "Unable to load Leave Application page. Please contact the administrator.");
        model.addAttribute("errorMessage", "Unable to load Leave Application page. Please contact the administrator.");
        return "error/500";
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public String handleNoResourceFound(NoResourceFoundException ex, Model model) {
        log.warn("Static resource not found: {}", ex.getResourcePath());
        model.addAttribute("status", 404);
        model.addAttribute("error", "Not Found");
        model.addAttribute("message", "Resource not found");
        model.addAttribute("errorMessage", "Resource not found");
        return "error/404";
    }

    @ExceptionHandler(Exception.class)
    public String handleGeneralException(Exception ex, Model model) {
        log.error("Unhandled global exception occurred: ", ex);
        String msg = ex.getMessage();
        if (msg == null || msg.trim().isEmpty()) {
            msg = "An unexpected error occurred. Please contact the administrator.";
        }
        model.addAttribute("status", 500);
        model.addAttribute("error", "Internal Server Error");
        model.addAttribute("message", msg);
        model.addAttribute("errorMessage", msg);
        return "error/500";
    }
}
