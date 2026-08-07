package com.ems.service.impl;

import com.ems.constants.LeaveStatus;
import com.ems.dto.LeaveRequestDTO;
import com.ems.entity.Employee;
import com.ems.entity.LeaveRequest;
import com.ems.exception.ResourceNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.EmployeeRepository;
import com.ems.repository.LeaveRequestRepository;
import com.ems.service.EmailService;
import com.ems.service.LeaveService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class LeaveServiceImpl implements LeaveService {

    private final LeaveRequestRepository leaveRequestRepository;
    private final EmployeeRepository employeeRepository;
    private final EmailService emailService;
    private static final int TOTAL_ANNUAL_LEAVE_QUOTA = 24;

    @Override
    @Transactional
    public LeaveRequestDTO applyLeave(LeaveRequestDTO dto) {
        if (dto.getEmployeeId() == null) {
            throw new ValidationException("Employee selection is required");
        }

        Employee employee = employeeRepository.findById(dto.getEmployeeId())
                .orElseThrow(() -> new ValidationException("Employee not found with ID: " + dto.getEmployeeId()));

        if (dto.getStartDate() == null || dto.getEndDate() == null) {
            throw new ValidationException("Start date and end date are required");
        }

        if (dto.getStartDate().isBefore(LocalDate.now())) {
            throw new ValidationException("Leave start date cannot be in the past");
        }

        if (dto.getEndDate().isBefore(dto.getStartDate())) {
            throw new ValidationException("Leave end date cannot be before start date");
        }

        int days = (int) ChronoUnit.DAYS.between(dto.getStartDate(), dto.getEndDate()) + 1;

        Map<String, Object> balance = getLeaveBalance(employee.getId());
        int remaining = (int) balance.get("remainingLeave");
        if (days > remaining) {
            throw new ValidationException("Insufficient leave balance. Requested: " + days + " days, Available: " + remaining + " days.");
        }

        LeaveRequest request = LeaveRequest.builder()
                .employee(employee)
                .leaveType(dto.getLeaveType())
                .startDate(dto.getStartDate())
                .endDate(dto.getEndDate())
                .numberOfDays(days)
                .reason(dto.getReason())
                .status(LeaveStatus.PENDING)
                .build();

        LeaveRequest saved = leaveRequestRepository.save(request);
        log.info("Leave request created for employee {} ({} days)", employee.getEmployeeCode(), days);
        return mapToDTO(saved);
    }

    @Override
    @Transactional
    public LeaveRequestDTO cancelLeave(Long leaveId, Long employeeId) {
        LeaveRequest request = getLeaveEntityById(leaveId);
        if (!request.getEmployee().getId().equals(employeeId)) {
            throw new ValidationException("You are not authorized to cancel this leave application");
        }

        if (request.getStatus() != LeaveStatus.PENDING) {
            throw new ValidationException("Only PENDING leave applications can be cancelled");
        }

        request.setStatus(LeaveStatus.CANCELLED);
        LeaveRequest updated = leaveRequestRepository.save(request);
        log.info("Cancelled leave request ID {}", leaveId);
        return mapToDTO(updated);
    }

    @Override
    @Transactional
    public LeaveRequestDTO approveLeave(Long leaveId, Long approverUserId, String remarks) {
        LeaveRequest request = getLeaveEntityById(leaveId);
        Employee approver = employeeRepository.findByUserId(approverUserId).orElse(null);

        request.setStatus(LeaveStatus.APPROVED);
        request.setApprovedBy(approver);
        request.setRemarks(remarks);

        LeaveRequest updated = leaveRequestRepository.save(request);
        log.info("Approved leave request ID {}", leaveId);

        emailService.sendLeaveStatusEmail(request.getEmployee().getEmail(), request.getLeaveType().name(), "APPROVED", remarks);
        return mapToDTO(updated);
    }

    @Override
    @Transactional
    public LeaveRequestDTO rejectLeave(Long leaveId, Long approverUserId, String remarks) {
        LeaveRequest request = getLeaveEntityById(leaveId);
        Employee approver = employeeRepository.findByUserId(approverUserId).orElse(null);

        request.setStatus(LeaveStatus.REJECTED);
        request.setApprovedBy(approver);
        request.setRemarks(remarks);

        LeaveRequest updated = leaveRequestRepository.save(request);
        log.info("Rejected leave request ID {}", leaveId);

        emailService.sendLeaveStatusEmail(request.getEmployee().getEmail(), request.getLeaveType().name(), "REJECTED", remarks);
        return mapToDTO(updated);
    }

    @Override
    public List<LeaveRequestDTO> getEmployeeLeaves(Long employeeId) {
        return getLeaveHistory(employeeId);
    }

    @Override
    public List<LeaveRequestDTO> getLeaveHistory(Long employeeId) {
        return leaveRequestRepository.findByEmployeeIdOrderByCreatedAtDesc(employeeId).stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public Map<String, Object> getLeaveBalance(Long employeeId) {
        Map<String, Object> balanceMap = new HashMap<>();
        if (employeeId == null) {
            balanceMap.put("totalLeave", TOTAL_ANNUAL_LEAVE_QUOTA);
            balanceMap.put("usedLeave", 0);
            balanceMap.put("pendingLeave", 0);
            balanceMap.put("remainingLeave", TOTAL_ANNUAL_LEAVE_QUOTA);
            return balanceMap;
        }

        int usedDays = leaveRequestRepository.sumDaysByEmployeeIdAndStatus(employeeId, LeaveStatus.APPROVED);
        int pendingDays = leaveRequestRepository.sumDaysByEmployeeIdAndStatus(employeeId, LeaveStatus.PENDING);
        int remainingDays = Math.max(0, TOTAL_ANNUAL_LEAVE_QUOTA - usedDays);

        balanceMap.put("totalLeave", TOTAL_ANNUAL_LEAVE_QUOTA);
        balanceMap.put("usedLeave", usedDays);
        balanceMap.put("pendingLeave", pendingDays);
        balanceMap.put("remainingLeave", remainingDays);
        return balanceMap;
    }

    @Override
    public Page<LeaveRequestDTO> getPendingLeaveApprovals(Pageable pageable) {
        return leaveRequestRepository.findByStatus(LeaveStatus.PENDING, pageable).map(this::mapToDTO);
    }

    @Override
    public Page<LeaveRequestDTO> searchLeavesByStatus(LeaveStatus status, Pageable pageable) {
        if (status == null) {
            return leaveRequestRepository.findAll(pageable).map(this::mapToDTO);
        }
        return leaveRequestRepository.findByStatus(status, pageable).map(this::mapToDTO);
    }

    @Override
    public LeaveRequest getLeaveEntityById(Long id) {
        return leaveRequestRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Leave request not found with ID: " + id));
    }

    private LeaveRequestDTO mapToDTO(LeaveRequest req) {
        LeaveRequestDTO dto = new LeaveRequestDTO();
        dto.setId(req.getId());
        dto.setEmployeeId(req.getEmployee().getId());
        dto.setEmployeeCode(req.getEmployee().getEmployeeCode());
        dto.setEmployeeName(req.getEmployee().getFullName());
        if (req.getEmployee().getDepartment() != null) {
            dto.setDepartmentName(req.getEmployee().getDepartment().getName());
        }
        dto.setLeaveType(req.getLeaveType());
        dto.setStartDate(req.getStartDate());
        dto.setEndDate(req.getEndDate());
        dto.setNumberOfDays(req.getNumberOfDays());
        dto.setReason(req.getReason());
        dto.setStatus(req.getStatus());
        if (req.getApprovedBy() != null) {
            dto.setApprovedById(req.getApprovedBy().getId());
            dto.setApprovedByName(req.getApprovedBy().getFullName());
        }
        dto.setRemarks(req.getRemarks());
        if (req.getCreatedAt() != null) {
            dto.setCreatedAtFormatted(req.getCreatedAt().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")));
        }
        return dto;
    }
}
