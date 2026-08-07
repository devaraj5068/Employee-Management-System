package com.ems.service.impl;

import com.ems.dto.DepartmentDTO;
import com.ems.entity.Department;
import com.ems.exception.DepartmentNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.DepartmentRepository;
import com.ems.service.DepartmentService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DepartmentServiceImpl implements DepartmentService {

    private final DepartmentRepository departmentRepository;

    @Override
    public List<DepartmentDTO> getAllDepartments() {
        return departmentRepository.findAll().stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public DepartmentDTO getDepartmentById(Long id) {
        return mapToDTO(getDepartmentEntityById(id));
    }

    @Override
    public DepartmentDTO createDepartment(DepartmentDTO dto) {
        if (departmentRepository.existsByCode(dto.getCode())) {
            throw new ValidationException("Department code '" + dto.getCode() + "' is already registered");
        }
        if (departmentRepository.existsByName(dto.getName())) {
            throw new ValidationException("Department name '" + dto.getName() + "' already exists");
        }

        Department department = Department.builder()
                .code(dto.getCode().toUpperCase())
                .name(dto.getName())
                .description(dto.getDescription())
                .location(dto.getLocation())
                .build();

        return mapToDTO(departmentRepository.save(department));
    }

    @Override
    public DepartmentDTO updateDepartment(Long id, DepartmentDTO dto) {
        Department department = getDepartmentEntityById(id);

        if (!department.getCode().equalsIgnoreCase(dto.getCode()) && departmentRepository.existsByCode(dto.getCode())) {
            throw new ValidationException("Department code '" + dto.getCode() + "' is already registered");
        }
        if (!department.getName().equalsIgnoreCase(dto.getName()) && departmentRepository.existsByName(dto.getName())) {
            throw new ValidationException("Department name '" + dto.getName() + "' already exists");
        }

        department.setCode(dto.getCode().toUpperCase());
        department.setName(dto.getName());
        department.setDescription(dto.getDescription());
        department.setLocation(dto.getLocation());

        return mapToDTO(departmentRepository.save(department));
    }

    @Override
    public void deleteDepartment(Long id) {
        Department department = getDepartmentEntityById(id);
        departmentRepository.delete(department);
    }

    @Override
    public Department getDepartmentEntityById(Long id) {
        return departmentRepository.findById(id)
                .orElseThrow(() -> new DepartmentNotFoundException("Department not found with ID: " + id));
    }

    private DepartmentDTO mapToDTO(Department dept) {
        DepartmentDTO dto = new DepartmentDTO();
        dto.setId(dept.getId());
        dto.setCode(dept.getCode());
        dto.setName(dept.getName());
        dto.setDescription(dept.getDescription());
        dto.setLocation(dept.getLocation());
        dto.setEmployeeCount(dept.getEmployees() != null ? dept.getEmployees().size() : 0);
        return dto;
    }
}
