package com.ems.service.impl;

import com.ems.service.EmailService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class EmailServiceImpl implements EmailService {

    @Override
    public void sendWelcomeEmail(String toEmail, String fullName, String username) {
        log.info("[EMAIL MOCK] Sending Welcome Email to: {} (User: {})", toEmail, username);
    }

    @Override
    public void sendPasswordResetEmail(String toEmail, String resetToken) {
        log.info("[EMAIL MOCK] Sending Password Reset Link to: {} (Token: {})", toEmail, resetToken);
    }

    @Override
    public void sendLeaveStatusEmail(String toEmail, String leaveType, String status, String remarks) {
        log.info("[EMAIL MOCK] Sending Leave Status Update to: {} (Type: {}, Status: {})", toEmail, leaveType, status);
    }
}
