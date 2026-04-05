```java
package src.main.nsb.project.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "orders")
public class OrderEntity {

    @Id
    @Column(name = "order_id", nullable = false)
    private Integer orderId;

    @Column(name = "customer_id", nullable = false)
    private Integer customerId;

    @Column(name = "amount", nullable = false)
    private Integer amount;

    public Integer getOrderId() {
        return orderId;
    }

    public void setOrderId(Integer orderId) {
        this.orderId = orderId;
    }

    public Integer getCustomerId() {
        return customerId;
    }

    public void setCustomerId(Integer customerId) {
        this.customerId = customerId;
    }

    public Integer getAmount() {
        return amount;
    }

    public void setAmount(Integer amount) {
        this.amount = amount;
    }
}
```

```java
package src.main.nsb.project.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "customers")
public class CustomerEntity {

    @Id
    @Column(name = "customer_id", nullable = false)
    private Integer customerId;

    @Column(name = "name", nullable = false, length = 255)
    private String name;

    @Column(name = "type", nullable = false, length = 10)
    private String type;

    public Integer getCustomerId() {
        return customerId;
    }

    public void setCustomerId(Integer customerId) {
        this.customerId = customerId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }
}
```

```java
package src.main.nsb.project.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import src.main.nsb.project.entity.OrderEntity;

@Repository
public interface OrderRepository extends JpaRepository<OrderEntity, Integer> {
    Optional<OrderEntity> findByOrderId(Integer orderId);
}
```

```java
package src.main.nsb.project.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import src.main.nsb.project.entity.CustomerEntity;

@Repository
public interface CustomerRepository extends JpaRepository<CustomerEntity, Integer> {
    Optional<CustomerEntity> findByCustomerId(Integer customerId);
}
```

```java
package src.main.nsb.project.exception;

public class OrderProcessingException extends RuntimeException {
    public OrderProcessingException() {
        super();
    }

    public OrderProcessingException(String message) {
        super(message);
    }

    public OrderProcessingException(String message, Throwable cause) {
        super(message, cause);
    }

    public OrderProcessingException(Throwable cause) {
        super(cause);
    }
}
```

```java
package src.main.nsb.project.service;

import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import src.main.nsb.project.entity.CustomerEntity;
import src.main.nsb.project.entity.OrderEntity;
import src.main.nsb.project.exception.OrderProcessingException;
import src.main.nsb.project.repository.CustomerRepository;
import src.main.nsb.project.repository.OrderRepository;

@Service
public class OrderProcService {

    private static final Logger logger = LoggerFactory.getLogger(OrderProcService.class);

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    public OrderProcService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    @Transactional
    public void processOrders() {
        logger.info("Start processing orders");

        try {
            initProcess();

            boolean endFlag = false;

            while (!endFlag) {
                Optional<OrderEntity> orderOpt = readOrder();
                if (orderOpt.isEmpty()) {
                    endFlag = true;
                    continue;
                }
                OrderEntity order = orderOpt.get();

                processOrder(order);

                // Loop continues until no more orders
            }

            endProcess();

            logger.info("Finished processing orders");
        } catch (Exception e) {
            logger.error("Error during order processing", e);
            throw new OrderProcessingException("Failed to process orders", e);
        }
    }

    private void initProcess() {
        logger.debug("Initializing process");
        // Initialization logic if any
    }

    private Optional<OrderEntity> readOrder() {
        logger.debug("Reading next order");
        // Simulate reading order from repository or external source
        // Here we just fetch next order by some criteria or return empty if none
        // For demonstration, we assume repository.findAll() is not suitable for streaming,
        // so this method should be implemented properly in real case.
        // Here we return empty to end loop.
        return Optional.empty();
    }

    private void processOrder(OrderEntity order) {
        logger.debug("Processing order: {}", order.getOrderId());

        CustomerEntity customer = findCustomer(order.getCustomerId());

        boolean vipFlag = checkVip(customer);

        int total = calcTotal(order.getAmount(), vipFlag);

        outputOrder(order, customer, total);
    }

    private CustomerEntity findCustomer(Integer customerId) {
        logger.debug("Finding customer: {}", customerId);
        if (customerId == null) {
            throw new OrderProcessingException("Customer ID is null");
        }
        return customerRepository.findByCustomerId(customerId)
                .orElseThrow(() -> new OrderProcessingException("Customer not found: " + customerId));
    }

    private boolean checkVip(CustomerEntity customer) {
        logger.debug("Checking VIP status for customer: {}", customer.getCustomerId());
        if (customer.getType() == null) {
            return false;
        }
        return "VIP".equalsIgnoreCase(customer.getType());
    }

    private int calcTotal(Integer amount, boolean vipFlag) {
        logger.debug("Calculating total for amount: {} with VIP flag: {}", amount, vipFlag);
        if (amount == null) {
            throw new OrderProcessingException("Order amount is null");
        }
        int total = amount;
        if (vipFlag) {
            total = (int) (amount * 0.9); // 10% discount for VIP
        }
        return total;
    }

    private void outputOrder(OrderEntity order, CustomerEntity customer, int total) {
        logger.info("Order ID: {}, Customer: {} (ID: {}), Amount: {}, Total after discount: {}",
                order.getOrderId(), customer.getName(), customer.getCustomerId(), order.getAmount(), total);
        // Output logic, e.g. write to file or send message, omitted here
    }

    private void endProcess() {
        logger.debug("Ending process");
        // Cleanup logic if any
    }
}
```

```java
package src.main.nsb.project.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import src.main.nsb.project.service.OrderProcService;

@RestController
@RequestMapping("/api/orders")
public class OrderProcController {

    private static final Logger logger = LoggerFactory.getLogger(OrderProcController.class);

    private final OrderProcService orderProcService;

    public OrderProcController(OrderProcService orderProcService) {
        this.orderProcService = orderProcService;
    }

    @PostMapping("/process")
    public ResponseEntity<String> processOrders() {
        logger.info("Received request to process orders");
        try {
            orderProcService.processOrders();
            return ResponseEntity.ok("Order processing completed successfully");
        } catch (Exception e) {
            logger.error("Order processing failed", e);
            return ResponseEntity.status(500).body("Order processing failed: " + e.getMessage());
        }
    }
}
```