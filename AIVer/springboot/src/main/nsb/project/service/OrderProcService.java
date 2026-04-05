package src.main.nsb.project.service;

import java.util.List;
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

            List<OrderEntity> orders = orderRepository.findAll();
            for (OrderEntity order : orders) {
                processOrder(order);
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