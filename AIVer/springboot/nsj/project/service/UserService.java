package nsj.project.service;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;
import nsj.project.dto.CustomerDto;
import nsj.project.dto.OrderDto;
import nsj.project.dto.UserDto;
import nsj.project.entity.CustomerEntity;
import nsj.project.entity.OrderEntity;
import nsj.project.entity.UserEntity;
import nsj.project.repository.CustomerRepository;
import nsj.project.repository.OrderRepository;
import nsj.project.repository.UserRepository;
import nsj.project.service.CustomerService;
import nsj.project.service.OrderService;
import nsj.project.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

public class UserService {
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Transactional(readOnly = true)
    public List<UserDto> getAllUsers() {
        logger.info("Fetching all users");
        List<UserEntity> entities = userRepository.selectAll();
        return entities.stream().map(this::toDto).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public UserDto getUserById(Long userId) {
        logger.info("Fetching user by id: {}", userId);
        UserEntity entity = userRepository.selectById(userId);
        if (entity == null) {
            logger.warn("User not found: {}", userId);
            throw new RuntimeException("User not found");
        }
        return toDto(entity);
    }

    @Transactional
    public void createUser(UserDto dto) {
        logger.info("Creating user: {}", dto);
        UserEntity entity = toEntity(dto);
        userRepository.insert(entity);
    }

    @Transactional
    public void updateUser(UserDto dto) {
        logger.info("Updating user: {}", dto);
        UserEntity entity = toEntity(dto);
        int updated = userRepository.update(entity);
        if (updated == 0) {
            logger.warn("User not found for update: {}", dto.getUserId());
            throw new RuntimeException("User not found for update");
        }
    }

    @Transactional
    public void deleteUser(Long userId) {
        logger.info("Deleting user: {}", userId);
        int deleted = userRepository.delete(userId);
        if (deleted == 0) {
            logger.warn("User not found for delete: {}", userId);
            throw new RuntimeException("User not found for delete");
        }
    }

    private UserDto toDto(UserEntity entity) {
        UserDto dto = new UserDto();
        dto.setUserId(entity.getUserId());
        dto.setUserName(entity.getUserName());
        dto.setUserType(entity.getUserType());
        return dto;
    }

    private UserEntity toEntity(UserDto dto) {
        UserEntity entity = new UserEntity();
        entity.setUserId(dto.getUserId());
        entity.setUserName(dto.getUserName());
        entity.setUserType(dto.getUserType());
        return entity;
    }
}