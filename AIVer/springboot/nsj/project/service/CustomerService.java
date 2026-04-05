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

public class CustomerService {
    private static final Logger logger = LoggerFactory.getLogger(CustomerService.class);

    private final CustomerRepository customerRepository;

    public CustomerService(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @Transactional(readOnly = true)
    public List<CustomerDto> getAllCustomers() {
        logger.info("Fetching all customers");
        List<CustomerEntity> entities = customerRepository.selectAll();
        return entities.stream().map(this::toDto).collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public CustomerDto getCustomerById(Long cuId) {
        logger.info("Fetching customer by id: {}", cuId);
        CustomerEntity entity = customerRepository.selectById(cuId);
        if (entity == null) {
            logger.warn("Customer not found: {}", cuId);
            throw new RuntimeException("Customer not found");
        }
        return toDto(entity);
    }

    @Transactional
    public void createCustomer(CustomerDto dto) {
        logger.info("Creating customer: {}", dto);
        CustomerEntity entity = toEntity(dto);
        customerRepository.insert(entity);
    }

    @Transactional
    public void updateCustomer(CustomerDto dto) {
        logger.info("Updating customer: {}", dto);
        CustomerEntity entity = toEntity(dto);
        int updated = customerRepository.update(entity);
        if (updated == 0) {
            logger.warn("Customer not found for update: {}", dto.getCuId());
            throw new RuntimeException("Customer not found for update");
        }
    }

    @Transactional
    public void deleteCustomer(Long cuId) {
        logger.info("Deleting customer: {}", cuId);
        int deleted = customerRepository.delete(cuId);
        if (deleted == 0) {
            logger.warn("Customer not found for delete: {}", cuId);
            throw new RuntimeException("Customer not found for delete");
        }
    }

    private CustomerDto toDto(CustomerEntity entity) {
        CustomerDto dto = new CustomerDto();
        dto.setCuId(entity.getCuId());
        dto.setCuName(entity.getCuName());
        dto.setCuType(entity.getCuType());
        return dto;
    }

    private CustomerEntity toEntity(CustomerDto dto) {
        CustomerEntity entity = new CustomerEntity();
        entity.setCuId(dto.getCuId());
        entity.setCuName(dto.getCuName());
        entity.setCuType(dto.getCuType());
        return entity;
    }
}