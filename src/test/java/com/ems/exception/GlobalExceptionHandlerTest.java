package com.ems.exception;

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.ui.Model;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

class GlobalExceptionHandlerTest {

    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();
    private final Model model = mock(Model.class);

    @Test
    void handleResourceNotFound_returns404ViewAndPopulatesModel() {
        ResourceNotFoundException ex = new ResourceNotFoundException("Employee not found");

        String view = handler.handleResourceNotFound(ex, model);

        assertEquals("error/404", view);
        verify(model).addAttribute("status", 404);
        verify(model).addAttribute("error", "Not Found");
        verify(model).addAttribute("message", "Employee not found");
    }

    @Test
    void handleValidationException_returns500ViewAndPopulatesModel() {
        ValidationException ex = new ValidationException("Invalid input");

        String view = handler.handleValidationException(ex, model);

        assertEquals("error/500", view);
        verify(model).addAttribute("status", 400);
        verify(model).addAttribute("error", "Bad Request");
        verify(model).addAttribute("message", "Invalid input");
    }

    @Test
    void handleAccessDenied_returns403ViewAndPopulatesModel() {
        AccessDeniedException ex = new AccessDeniedException("Denied");

        String view = handler.handleAccessDenied(ex, model);

        assertEquals("error/403", view);
        verify(model).addAttribute("status", 403);
        verify(model).addAttribute("error", "Access Denied");
        verify(model).addAttribute("message", "You do not have authorization to access this resource.");
    }

    @Test
    void handleGeneralException_returns500ViewAndUsesFallbackMessageWhenNull() {
        Exception ex = new Exception((String) null);

        String view = handler.handleGeneralException(ex, model);

        assertEquals("error/500", view);
        verify(model).addAttribute("status", 500);
        verify(model).addAttribute("error", "Internal Server Error");
        verify(model).addAttribute("message", "An unexpected error occurred. Please contact the administrator.");
    }

    @Test
    void handleGeneralException_returns500ViewAndUsesExceptionMessage() {
        Exception ex = new Exception("Runtime failure");

        String view = handler.handleGeneralException(ex, model);

        assertEquals("error/500", view);
        verify(model).addAttribute("status", 500);
        verify(model).addAttribute("error", "Internal Server Error");
        verify(model).addAttribute("message", "Runtime failure");
    }
}
