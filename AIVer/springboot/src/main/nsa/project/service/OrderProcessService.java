package src.main.nsa.project.service;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import src.main.nsa.project.dto.OrderDto;
import src.main.nsa.project.entity.CustomerEntity;
import src.main.nsa.project.entity.OrderEntity;
import src.main.nsa.project.exception.OrderProcessException;
import src.main.nsa.project.repository.CustomerRepository;
import src.main.nsa.project.repository.OrderRepository;
import src.main.nsa.project.service.OrderProcessService;

public class OrderProcessService {

    private static final Logger log = LoggerFactory.getLogger(OrderProcessService.class);

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    private static final String VIP_TYPE = "VIP";

    public OrderProcessService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    @Transactional
    public void processAllOrders() {
        log.info("Start processing all orders.");
        List<OrderEntity> orders = orderRepository.findAll();
        if (orders == null) {
            log.error("Order list is null.");
            throw new OrderProcessException("Order list is null.");
        }

        BigDecimal totalAmount = BigDecimal.ZERO;
        int count = 0;

        for (OrderEntity order : orders) {
            if (order == null) {
                log.warn("Order is null. Skipping.");
                continue;
            }
            try {
                OrderDto orderDto = processOrder(order);
                totalAmount = totalAmount.add(orderDto.getAmount() != null ? orderDto.getAmount() : BigDecimal.ZERO);
                count++;
                outputOrder(orderDto);
            } catch (OrderProcessException ex) {
                log.error("Order processing failed: {}", ex.getMessage(), ex);
                // Continue processing next order
            }
        }

        log.info("Processed {} orders. Total amount: {}", count, totalAmount);
    }

    private OrderDto processOrder(OrderEntity order) {
        if (order == null) {
            log.error("Order is null.");
            throw new OrderProcessException("Order is null.");
        }

        OrderDto dto = new OrderDto();
        dto.setOrderId(order.getOrderId());
        dto.setCustomerId(order.getCustomerId());
        dto.setAmount(order.getAmount());

        CustomerEntity customer = findCustomer(order.getCustomerId());
        dto.setCustomerName(customer.getName());
        dto.setCustomerType(customer.getType());

        boolean isVip = checkVip(customer);
        dto.setVip(isVip);

        return dto;
    }

    private CustomerEntity findCustomer(Long customerId) {
        if (customerId == null) {
            log.error("Customer ID is null.");
            throw new OrderProcessException("Customer ID is null.");
        }
        Optional<CustomerEntity> customerOpt = customerRepository.findByCustomerId(customerId);
        if (customerOpt.isEmpty()) {
            log.error("Customer not found. ID: {}", customerId);
            throw new OrderProcessException("Customer not found. ID: " + customerId);
        }
        return customerOpt.get();
    }

    private boolean checkVip(CustomerEntity customer) {
        if (customer == null) {
            log.error("Customer is null.");
            throw new OrderProcessException("Customer is null.");
        }
        boolean isVip = VIP_TYPE.equals(customer.getType());
        log.debug("Customer {} VIP check: {}", customer.getCustomerId(), isVip);
        return isVip;
    }

    private void outputOrder(OrderDto orderDto) {
        if (orderDto == null) {
            log.warn("OrderDto is null. Skipping output.");
            return;
        }
        // Output logic placeholder (e.g., write to file, send to API, etc.)
        log.info("Output Order: orderId={}, customerId={}, amount={}, customerName={}, customerType={}, vip={}",
                orderDto.getOrderId(),
                orderDto.getCustomerId(),
                orderDto.getAmount(),
                orderDto.getCustomerName(),
                orderDto.getCustomerType(),
                orderDto.isVip());
    }

    // Extra procedures as private methods
    private void extraProc001() {
        log.debug("EXTRA-PROC-001 executed.");
    }

    private void extraProc002() {
        log.debug("EXTRA-PROC-002 executed.");
    }

    private void extraProc003() {
        log.debug("EXTRA-PROC-003 executed.");
    }

    private void extraProc004() {
        log.debug("EXTRA-PROC-004 executed.");
    }

    private void extraProc005() {
        log.debug("EXTRA-PROC-005 executed.");
    }
}