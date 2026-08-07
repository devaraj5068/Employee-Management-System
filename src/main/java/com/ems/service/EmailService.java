package com.ems.service;

public interface EmailService {
    void sendWelcomeEmail(String toEmail, String fullName, String username);
    void sendPasswordResetEmail(String toEmail, String resetToken);
    void sendLeaveStatusEmail(String toEmail, String leaveType, String status, String remarks);
}
