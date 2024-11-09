package com.decorate.design.repository;

import com.decorate.design.model.User;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface UserRepository extends MongoRepository<User, String> {
    // Custom queries can be added here if necessary
}


