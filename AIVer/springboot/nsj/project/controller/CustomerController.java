package nsj.project.controller;

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

public class CustomerController {
    private static final Logger logger = LoggerFactory.getLogger(CustomerController.class);

    private final CustomerService customerService;

    public CustomerController(CustomerService customerService) {
        this.customerService = customerService;
    }

    @GetMapping
    public List<CustomerDto> getAllCustomers() {
        logger.info("API: getAllCustomers");
        return customerService.getAllCustomers();
    }

    @GetMapping("/{id}")
    public CustomerDto getCustomerById(@PathVariable("id") Long id) {
        logger.info("API: getCustomerById {}", id);
        return customerService.getCustomerById(id);
    }

    @PostMapping
    public void createCustomer(@RequestBody CustomerDto dto) {
        logger.info("API: createCustomer {}", dto);
        customerService.createCustomer(dto);
    }

    @PutMapping("/{id}")
    public void updateCustomer(@PathVariable("id") Long id, @RequestBody CustomerDto dto) {
        logger.info("API: updateCustomer {} {}", id, dto);
        dto.setCuId(id);
        customerService.updateCustomer(dto);
    }

    @DeleteMapping("/{id}")
    public void deleteCustomer(@PathVariable("id") Long id) {
        logger.info("API: deleteCustomer {}", id);
        customerService.deleteCustomer(id);
    }
}