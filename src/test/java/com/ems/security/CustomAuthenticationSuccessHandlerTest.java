package com.ems.security;

import com.ems.entity.AuditLog;
import com.ems.repository.AuditLogRepository;
import com.ems.repository.UserRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.security.core.Authentication;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class CustomAuthenticationSuccessHandlerTest {

    private AuditLogRepository auditLogRepository;
    private UserRepository userRepository;
    private CustomAuthenticationSuccessHandler handler;
    private HttpServletRequest request;
    private HttpServletResponse response;
    private Authentication authentication;

    @BeforeEach
    void setUp() {
        auditLogRepository = mock(AuditLogRepository.class);
        userRepository = mock(UserRepository.class);
        handler = new CustomAuthenticationSuccessHandler(auditLogRepository, userRepository);
        request = mock(HttpServletRequest.class);
        response = mock(HttpServletResponse.class);
        authentication = mock(Authentication.class);
    }

    @Test
    void onAuthenticationSuccess_savesAuditLogAndRedirects() throws Exception {
        when(authentication.getName()).thenReturn("alice");
        when(request.getRemoteAddr()).thenReturn("127.0.0.1");
        when(request.getContextPath()).thenReturn("/app");
        when(userRepository.findByUsername("alice")).thenReturn(Optional.empty());

        handler.onAuthenticationSuccess(request, response, authentication);

        ArgumentCaptor<AuditLog> auditCaptor = ArgumentCaptor.forClass(AuditLog.class);
        verify(auditLogRepository).save(auditCaptor.capture());
        AuditLog auditLog = auditCaptor.getValue();

        assertEquals("alice", auditLog.getUsername());
        assertEquals("USER_LOGIN", auditLog.getAction());
        assertEquals("User successfully authenticated", auditLog.getDetails());
        assertEquals("127.0.0.1", auditLog.getIpAddress());

        verify(response).sendRedirect("/app/dashboard");
    }

    @Test
    void onAuthenticationSuccess_redirectsEvenWhenAuditSaveFails() throws Exception {
        when(authentication.getName()).thenReturn("bob");
        when(request.getRemoteAddr()).thenReturn("192.168.0.2");
        when(request.getContextPath()).thenReturn("");
        when(userRepository.findByUsername("bob")).thenReturn(Optional.empty());
        when(auditLogRepository.save(any(AuditLog.class))).thenThrow(new RuntimeException("save failure"));

        handler.onAuthenticationSuccess(request, response, authentication);

        verify(response).sendRedirect("/dashboard");
        verify(auditLogRepository).save(any(AuditLog.class));
    }
}
