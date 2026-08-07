package com.ems.service;

import com.ems.constants.LeaveStatus;
import com.ems.dto.LeaveRequestDTO;
import com.ems.entity.LeaveRequest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.Map;

public interface LeaveService {
    LeaveRequestDTO applyLeave(LeaveRequestDTO dto);
    LeaveRequestDTO cancelLeave(Long leaveId, Long employeeId);
    LeaveRequestDTO approveLeave(Long leaveId, Long approverUserId, String remarks);
    LeaveRequestDTO rejectLeave(Long leaveId, Long approverUserId, String remarks);
    List<LeaveRequestDTO> getEmployeeLeaves(Long employeeId);
    List<LeaveRequestDTO> getLeaveHistory(Long employeeId);
    Map<String, Object> getLeaveBalance(Long employeeId);
    Page<LeaveRequestDTO> getPendingLeaveApprovals(Pageable pageable);
    Page<LeaveRequestDTO> searchLeavesByStatus(LeaveStatus status, Pageable pageable);
    LeaveRequest getLeaveEntityById(Long id);
}
