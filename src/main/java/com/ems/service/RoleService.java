package com.ems.service;

import com.ems.dto.RoleDTO;
import com.ems.entity.Role;

import java.util.List;

public interface RoleService {
    List<RoleDTO> getAllRoles();
    RoleDTO getRoleById(Long id);
    RoleDTO createRole(RoleDTO roleDTO);
    RoleDTO updateRole(Long id, RoleDTO roleDTO);
    void deleteRole(Long id);
    Role getRoleEntityById(Long id);
}
