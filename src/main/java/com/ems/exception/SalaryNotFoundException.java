package com.ems.exception;

public class SalaryNotFoundException extends ResourceNotFoundException {
    public SalaryNotFoundException(String message) {
        super(message);
    }
}
