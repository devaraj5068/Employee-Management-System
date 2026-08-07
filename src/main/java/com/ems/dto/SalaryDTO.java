package com.ems.dto;

import com.ems.constants.PaymentStatus;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class SalaryDTO {

    private Long id;

    @NotNull(message = "Employee selection is required")
    private Long employeeId;

    private String employeeCode;
    private String employeeName;
    private String departmentName;
    private String roleName;

    @NotBlank(message = "Pay month is required (YYYY-MM)")
    private String payMonth;

    @NotNull(message = "Basic salary is required")
    @Positive(message = "Basic salary must be greater than zero")
    private BigDecimal basicSalary;

    private BigDecimal hra = BigDecimal.ZERO;
    private BigDecimal da = BigDecimal.ZERO;
    private BigDecimal bonus = BigDecimal.ZERO;
    private BigDecimal incentives = BigDecimal.ZERO;
    private BigDecimal deductions = BigDecimal.ZERO;
    private BigDecimal tax = BigDecimal.ZERO;
    private BigDecimal netSalary;

    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate paymentDate;

    private PaymentStatus paymentStatus = PaymentStatus.PENDING;

    private String remarks;
}
