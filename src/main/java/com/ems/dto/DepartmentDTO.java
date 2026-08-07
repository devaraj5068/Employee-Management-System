package com.ems.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class DepartmentDTO {

    private Long id;

    @NotBlank(message = "Department code is required")
    @Size(max = 20, message = "Code must not exceed 20 characters")
    private String code;

    @NotBlank(message = "Department name is required")
    @Size(max = 100, message = "Name must not exceed 100 characters")
    private String name;

    private String description;
    private String location;
    private int employeeCount;
}
