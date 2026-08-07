package com.ems.security;

import com.ems.entity.AuditLog;
import com.ems.entity.User;
import com.ems.repository.AuditLogRepository;
import com.ems.repository.UserRepository;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Optional;

@Slf4j
@Component
@RequiredArgsConstructor
public class CustomAuthenticationSuccessHandler implements AuthenticationSuccessHandler {

    private final AuditLogRepository auditLogRepository;
    private final UserRepository userRepository;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication)
            throws IOException, ServletException {
        
        String username = authentication.getName();
        String ipAddress = request.getRemoteAddr();

        log.info("User '{}' successfully logged in from IP {}", username, ipAddress);

        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isPresent()) {
            User user = userOpt.get();
            if (user.getFailedAttempt() > 0) {
                user.setFailedAttempt(0);
                user.setLockTime(null);
                userRepository.save(user);
            }
        }

        try {
            AuditLog auditLog = AuditLog.builder()
                    .username(username)
                    .action("USER_LOGIN")
                    .details("User successfully authenticated")
                    .ipAddress(ipAddress)
                    .build();
            auditLogRepository.save(auditLog);
        } catch (Exception e) {
            log.error("Failed to record login audit log", e);
        }

        response.sendRedirect(request.getContextPath() + "/dashboard");
    }
}
