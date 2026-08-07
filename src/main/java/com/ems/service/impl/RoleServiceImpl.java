package com.ems.service.impl;

import com.ems.dto.RoleDTO;
import com.ems.entity.Role;
import com.ems.exception.ResourceNotFoundException;
import com.ems.exception.ValidationException;
import com.ems.repository.RoleRepository;
import com.ems.service.RoleService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RoleServiceImpl implements RoleService {

    private final RoleRepository roleRepository;

    @Override
    public List<RoleDTO> getAllRoles() {
        return roleRepository.findAll().stream()
                .map(this::mapToDTO)
                .collect(Collectors.toList());
    }

    @Override
    public RoleDTO getRoleById(Long id) {
        return mapToDTO(getRoleEntityById(id));
    }

    @Override
    public RoleDTO createRole(RoleDTO roleDTO) {
        String roleName = roleDTO.getName().trim();
        if (!roleName.startsWith("ROLE_")) {
            roleName = "ROLE_" + roleName.toUpperCase();
        }
        if (roleRepository.existsByName(roleName)) {
            throw new ValidationException("Role with name '" + roleName + "' already exists");
        }

        Role role = Role.builder()
                .name(roleName)
                .description(roleDTO.getDescription())
                .build();

        return mapToDTO(roleRepository.save(role));
    }

    @Override
    public RoleDTO updateRole(Long id, RoleDTO roleDTO) {
        Role role = getRoleEntityById(id);
        String roleName = roleDTO.getName().trim();
        if (!roleName.startsWith("ROLE_")) {
            roleName = "ROLE_" + roleName.toUpperCase();
        }

        if (!role.getName().equalsIgnoreCase(roleName) && roleRepository.existsByName(roleName)) {
            throw new ValidationException("Role with name '" + roleName + "' already exists");
        }

        role.setName(roleName);
        role.setDescription(roleDTO.getDescription());

        return mapToDTO(roleRepository.save(role));
    }

    @Override
    public void deleteRole(Long id) {
        Role role = getRoleEntityById(id);
        roleRepository.delete(role);
    }

    @Override
    public Role getRoleEntityById(Long id) {
        return roleRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Role not found with ID: " + id));
    }

    private RoleDTO mapToDTO(Role role) {
        RoleDTO dto = new RoleDTO();
        dto.setId(role.getId());
        dto.setName(role.getName());
        dto.setDescription(role.getDescription());
        return dto;
    }
}
