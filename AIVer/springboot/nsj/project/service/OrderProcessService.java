package nsj.project.service;

import jakarta.persistence.*;
import jakarta.transaction.Transactional;
import java.math.BigDecimal;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import nsj.project.entity.CustomerEntity;
import nsj.project.entity.OrderEntity;
import nsj.project.exception.OrderProcessException;
import nsj.project.repository.CustomerRepository;
import nsj.project.repository.OrderRepository;
import nsj.project.service.OrderProcessService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;

public class OrderProcessService {

    private static final Logger log = LoggerFactory.getLogger(OrderProcessService.class);

    private static final String END_FLAG_YES = "Y";
    private static final String VIP_TYPE = "VIP";

    private final OrderRepository orderRepository;
    private final CustomerRepository customerRepository;

    // Work variables
    private String wsEndFlag;
    private int wsCount;
    private BigDecimal wsTotal;
    private Long wsCurrentCustomer;
    private String wsVipFlag;
    private String wsTempVar1;
    private String wsTempVar2;
    private String wsTempVar3;
    private String wsTempVar4;
    private String wsTempVar5;

    public OrderProcessService(OrderRepository orderRepository, CustomerRepository customerRepository) {
        this.orderRepository = orderRepository;
        this.customerRepository = customerRepository;
    }

    @Transactional
    public void mainProcess() {
        log.info("Start mainProcess");
        try {
            initProcess();
            readOrder();
            while (!END_FLAG_YES.equals(wsEndFlag)) {
                processOrder();
                readOrder();
            }
            endProcess();
        } catch (Exception e) {
            log.error("Exception in mainProcess", e);
            throw new OrderProcessException("Error in mainProcess", e);
        }
        log.info("End mainProcess");
    }

    private void initProcess() {
        log.info("Initializing process variables");
        wsEndFlag = "";
        wsCount = 0;
        wsTotal = BigDecimal.ZERO;
        wsCurrentCustomer = null;
        wsVipFlag = "";
        wsTempVar1 = "";
        wsTempVar2 = "";
        wsTempVar3 = "";
        wsTempVar4 = "";
        wsTempVar5 = "";
    }

    private void readOrder() {
        log.info("Reading next order");
        List<OrderEntity> orders = orderRepository.findAll();
        if (orders == null || orders.isEmpty() || wsCount >= orders.size()) {
            wsEndFlag = END_FLAG_YES;
            log.info("No more orders to process. Setting wsEndFlag=Y");
            return;
        }
        OrderEntity order = orders.get(wsCount);
        wsCurrentCustomer = order.getCustomerId();
        wsCount++;
        wsEndFlag = "";
        wsTempVar1 = order.getOrderId().toString();
        wsTempVar2 = order.getAmount().toString();
        log.info("Order read: orderId={}, customerId={}, amount={}", order.getOrderId(), order.getCustomerId(), order.getAmount());
    }

    private void processOrder() {
        log.info("Processing order for customerId={}", wsCurrentCustomer);
        findCustomer();
        checkVip();
        calcTotal();
        outputOrder();
    }

    private void findCustomer() {
        log.info("Finding customer: customerId={}", wsCurrentCustomer);
        if (wsCurrentCustomer == null) {
            log.warn("wsCurrentCustomer is null");
            throw new OrderProcessException("Current customer ID is null");
        }
        Optional<CustomerEntity> customerOpt = customerRepository.findByCustomerId(wsCurrentCustomer);
        if (customerOpt.isEmpty()) {
            log.warn("Customer not found: customerId={}", wsCurrentCustomer);
            throw new OrderProcessException("Customer not found: " + wsCurrentCustomer);
        }
        CustomerEntity customer = customerOpt.get();
        wsTempVar3 = customer.getCustomerName();
        wsTempVar4 = customer.getCustomerType();
        log.info("Customer found: name={}, type={}", wsTempVar3, wsTempVar4);
    }

    private void checkVip() {
        log.info("Checking VIP status for customerType={}", wsTempVar4);
        if (VIP_TYPE.equals(wsTempVar4)) {
            wsVipFlag = "Y";
            log.info("Customer is VIP");
        } else {
            wsVipFlag = "N";
            log.info("Customer is not VIP");
        }
    }

    private void calcTotal() {
        log.info("Calculating total");
        try {
            BigDecimal amount = new BigDecimal(wsTempVar2);
            wsTotal = wsTotal.add(amount);
            log.info("New total: {}", wsTotal);
        } catch (NumberFormatException e) {
            log.error("Invalid amount format: {}", wsTempVar2, e);
            throw new OrderProcessException("Invalid amount format: " + wsTempVar2, e);
        }
    }

    private void outputOrder() {
        log.info("Outputting order: orderId={}, customerId={}, customerName={}, customerType={}, amount={}, vipFlag={}",
                wsTempVar1, wsCurrentCustomer, wsTempVar3, wsTempVar4, wsTempVar2, wsVipFlag);
        // Output logic placeholder (e.g., write to file, send to API, etc.)
    }

    private void endProcess() {
        log.info("End of process. Total orders processed: {}, Total amount: {}", wsCount, wsTotal);
        // Finalization logic placeholder
    }
}