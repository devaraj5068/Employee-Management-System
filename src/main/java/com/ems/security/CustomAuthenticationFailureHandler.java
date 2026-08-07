package com.ems.security;

import com.ems.entity.User;
import com.ems.repository.UserRepository;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationFailureHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Date;
import java.util.Optional;

@Slf4j
@Component
@RequiredArgsConstructor
public class CustomAuthenticationFailureHandler extends SimpleUrlAuthenticationFailureHandler {

    private final UserRepository userRepository;
    private static final int MAX_FAILED_ATTEMPTS = 5;

    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response, AuthenticationException exception)
            throws IOException, ServletException {
        
        String username = request.getParameter("username");
        if (username != null && !username.trim().isEmpty()) {
            Optional<User> userOpt = userRepository.findByUsernameOrEmail(username, username);
            if (userOpt.isPresent()) {
                User user = userOpt.get();
                if (user.isEnabled() && user.isAccountNonLocked()) {
                    int newFailedAttempts = user.getFailedAttempt() + 1;
                    user.setFailedAttempt(newFailedAttempts);
                    if (newFailedAttempts >= MAX_FAILED_ATTEMPTS) {
                        user.setAccountNonLocked(false);
                        user.setLockTime(new Date());
                        log.warn("Account for user '{}' locked due to {} failed login attempts.", username, newFailedAttempts);
                    }
                    userRepository.save(user);
                }
            }
        }

        super.setDefaultFailureUrl("/login?error=true");
        super.onAuthenticationFailure(request, response, exception);
    }
}
