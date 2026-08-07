package com.ems.service;

import com.ems.dto.ChangePasswordDTO;
import com.ems.dto.UserRegistrationDTO;
import com.ems.entity.User;

import java.util.List;

public interface UserService {
    User registerUser(UserRegistrationDTO dto);
    User findByUsername(String username);
    User findByEmail(String email);
    User findById(Long id);
    List<User> findAllUsers();
    void changePassword(String username, ChangePasswordDTO dto);
    void toggleUserStatus(Long userId);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}
