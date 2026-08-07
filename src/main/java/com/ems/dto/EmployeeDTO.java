package com.ems.dto;

import com.ems.constants.EmploymentStatus;
import jakarta.validation.constraints.*;
import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;

@Data
public class EmployeeDTO {

    private Long id;

    private String employeeCode;

    @NotBlank(message = "First name is required")
    @Size(max = 50, message = "First name must not exceed 50 characters")
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Size(max = 50, message = "Last name must not exceed 50 characters")
    private String lastName;

    @NotBlank(message = "Email is required")
    @Email(message = "Please enter a valid email address")
    private String email;

    @NotBlank(message = "Mobile number is required")
    @Pattern(regexp = "^[0-9+\\-\\s()]{7,20}$", message = "Please enter a valid mobile number")
    private String mobileNumber;

    @NotBlank(message = "Gender is required")
    private String gender;

    @DateTimeFormat(pattern = "yyyy-MM-dd")
    @Past(message = "Date of birth must be in the past")
    private LocalDate dateOfBirth;

    private String address;
    private String city;
    private String state;
    private String country;

    @NotNull(message = "Joining date is required")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate joiningDate;

    private String emergencyContact;
    private String bloodGroup;

    private Long managerId;
    private String managerName;

    @NotNull(message = "Department selection is required")
    private Long departmentId;

    private String departmentName;

    @NotNull(message = "Role selection is required")
    private Long roleId;

    private String roleName;

    private EmploymentStatus employmentStatus = EmploymentStatus.ACTIVE;

    private String profilePictureUrl;

    public String getFullName() {
        return (firstName != null ? firstName : "") + " " + (lastName != null ? lastName : "");
    }
}
