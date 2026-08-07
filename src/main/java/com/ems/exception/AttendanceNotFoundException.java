package com.ems.exception;

public class AttendanceNotFoundException extends ResourceNotFoundException {
    public AttendanceNotFoundException(String message) {
        super(message);
    }
}
