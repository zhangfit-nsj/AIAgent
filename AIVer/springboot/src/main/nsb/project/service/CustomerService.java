package src.main.nsb.project.service;

import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import src.main.nsb.project.entity.CustomerEntity;
import src.main.nsb.project.exception.OrderProcessingException;
import src.main.nsb.project.repository.CustomerRepository;

@Service
public class CustomerService {
    private static final Logger logger = LoggerFactory.getLogger(CustomerService.class);
    private final CustomerRepository customerRepository;

    public CustomerService(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    public List<CustomerEntity> findAll() {
        logger.info("Fetching all customers");
        return customerRepository.findAll();
    }

    public Optional<CustomerEntity> findById(Integer customerId) {
        logger.info("Fetching customer by id: {}", customerId);
        return customerRepository.findByCustomerId(customerId);
    }

    @Transactional
    public CustomerEntity create(CustomerEntity customer) {
        logger.info("Creating customer: {}", customer.getCustomerId());
        if (customerRepository.existsById(customer.getCustomerId())) {
            throw new OrderProcessingException("Customer already exists: " + customer.getCustomerId());
        }
        return customerRepository.save(customer);
    }

    @Transactional
    public CustomerEntity update(CustomerEntity customer) {
        logger.info("Updating customer: {}", customer.getCustomerId());
        if (!customerRepository.existsById(customer.getCustomerId())) {
            throw new OrderProcessingException("Customer not found: " + customer.getCustomerId());
        }
        return customerRepository.save(customer);
    }

    @Transactional
    public void delete(Integer customerId) {
        logger.info("Deleting customer: {}", customerId);
        if (!customerRepository.existsById(customerId)) {
            throw new OrderProcessingException("Customer not found: " + customerId);
        }
        customerRepository.deleteById(customerId);
    }
}