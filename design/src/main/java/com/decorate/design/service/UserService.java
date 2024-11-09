package com.decorate.design.service;

import com.decorate.design.model.User;
import com.decorate.design.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    // Save a new user or update an existing user
    public User saveUser(User user) {
        return userRepository.save(user);
    }

    // Get a list of all users
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    // Get a user by their ID
    public Optional<User> getUserById(String id) {
        return userRepository.findById(id);
    }

    // Delete a user by their ID
    public void deleteUser(String id) {
        userRepository.deleteById(id);
    }
}



