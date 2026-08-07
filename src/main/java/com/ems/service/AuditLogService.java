package com.ems.service;

import com.ems.entity.AuditLog;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface AuditLogService {
    void logAction(String username, String action, String details, String ipAddress);
    Page<AuditLog> getRecentLogs(Pageable pageable);
}
